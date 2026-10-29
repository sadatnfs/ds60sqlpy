"""Native PySpark ML stages for prepared TMB likelihoods and declared predictions.

Persistence is bounded JSON on a local/shared filesystem visible to the driver.
It stores numerical state and artifact identities, never R pointers or pickles.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

from ds60_spark_likelihood.optimization import minimize_lbfgsb
from pyspark.ml import Estimator, Model
from pyspark.ml.param import Param, Params, TypeConverters
from pyspark.ml.util import DefaultParamsWriter, MLReadable, MLReader, MLWritable, MLWriter

from . import runtime
from .dataframe import DataFrameObjective, artifact_identity, predict_dataframe, prediction_bindings
from .registry import ModelContractError, finite

MAX_JSON = 1_000_000
PARAMETER_NAMES = frozenset(
    {
        "modelId",
        "dataCols",
        "initialParameters",
        "groupCol",
        "orderCols",
        "batchSize",
        "predictionCol",
        "predictionTarget",
        "maxIter",
        "tol",
        "parameterBounds",
    }
)


def _columns(value):
    if not isinstance(value, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    ):
        raise ValueError("dataCols must map registry field names to Spark column names")
    return dict(value)


def _numbers(value):
    if not isinstance(value, (list, tuple)):
        raise ValueError("Use an explicit list of numeric parameter values")
    return [finite(item) for item in value]


def _bounds(value):
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError("parameterBounds must be a list of lower/upper pairs")
    result = []
    for pair in value:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("Each parameter bound needs lower and upper endpoints")
        result.append([None if endpoint is None else finite(endpoint) for endpoint in pair])
    return result


def _finite_option(value):
    return finite(value)


class _TMBParams(Params):
    modelId = Param(
        Params._dummy(), "modelId", "Prepared registered model identifier", TypeConverters.toString
    )
    dataCols = Param(
        Params._dummy(), "dataCols", "Registry observation field to Spark column mapping", _columns
    )
    initialParameters = Param(
        Params._dummy(),
        "initialParameters",
        "Initial fixed parameters in canonical registered order",
        _numbers,
    )
    groupCol = Param(
        Params._dummy(),
        "groupCol",
        "Complete independent unit identity column",
        TypeConverters.toString,
    )
    orderCols = Param(
        Params._dummy(),
        "orderCols",
        "Unique deterministic ordering keys inside a complete unit",
        TypeConverters.toListString,
    )
    batchSize = Param(
        Params._dummy(),
        "batchSize",
        "Maximum independent rows per native evaluation",
        TypeConverters.toInt,
    )
    predictionCol = Param(
        Params._dummy(),
        "predictionCol",
        "New scalar prediction output column",
        TypeConverters.toString,
    )
    predictionTarget = Param(
        Params._dummy(),
        "predictionTarget",
        "Explicit registered prediction target or empty for its declared default",
        TypeConverters.toString,
    )
    maxIter = Param(
        Params._dummy(), "maxIter", "Bounded driver optimization iterations", TypeConverters.toInt
    )
    tol = Param(
        Params._dummy(),
        "tol",
        "Maximum projected score norm accepted for fitting",
        _finite_option,
    )
    parameterBounds = Param(
        Params._dummy(),
        "parameterBounds",
        "Explicit fixed-coordinate bounds; empty means unbounded",
        _bounds,
    )

    def _defaults(self):
        self._setDefault(
            modelId="",
            dataCols={},
            initialParameters=[],
            groupCol="",
            orderCols=[],
            batchSize=256,
            predictionCol="prediction",
            predictionTarget="",
            maxIter=100,
            tol=1e-6,
            parameterBounds=[],
        )

    def setParams(self, **parameters):
        if not set(parameters) <= PARAMETER_NAMES:
            raise ValueError("Unknown TMB ML parameter")
        return self._set(**parameters)

    def _parameter_values(self):
        return {name: copy.deepcopy(self.getOrDefault(name)) for name in sorted(PARAMETER_NAMES)}


class TMBEstimator(Estimator, _TMBParams, MLReadable, MLWritable):
    """Fit one shared likelihood through bounded Spark/R summaries and SciPy.

    This estimator never averages independent fitted coefficients. Its Model can
    transform only when the prepared registry declares a response-free target.
    """

    def __init__(
        self,
        *,
        modelId="",
        dataCols=None,
        initialParameters=(),
        groupCol="",
        orderCols=(),
        batchSize=256,
        predictionCol="prediction",
        predictionTarget="",
        maxIter=100,
        tol=1e-6,
        parameterBounds=None,
        root=None,
        build_dir=None,
    ):
        super().__init__()
        self._defaults()
        if isinstance(orderCols, (str, bytes)):
            raise ValueError("orderCols must be a sequence of column names")
        self.runtime_root = root
        self.runtime_build_dir = build_dir
        self._set(
            modelId=modelId,
            dataCols={} if dataCols is None else dataCols,
            initialParameters=list(initialParameters),
            groupCol=groupCol,
            orderCols=list(orderCols),
            batchSize=batchSize,
            predictionCol=predictionCol,
            predictionTarget=predictionTarget,
            maxIter=maxIter,
            tol=tol,
            parameterBounds=[] if parameterBounds is None else parameterBounds,
        )

    def _fit(self, dataset):
        import scipy

        if scipy.__version__ != "1.15.3":
            raise ModelContractError("Prepare the pinned SciPy1.15.3 driver environment")
        initial = self.getOrDefault(self.initialParameters)
        model_id = self.getOrDefault(self.modelId)
        bounds = self.getOrDefault(self.parameterBounds) or None
        tolerance = finite(self.getOrDefault(self.tol))
        with DataFrameObjective(
            dataset,
            model_id,
            columns=self.getOrDefault(self.dataCols),
            group_col=self.getOrDefault(self.groupCol) or None,
            order_cols=self.getOrDefault(self.orderCols),
            batch_size=self.getOrDefault(self.batchSize),
            root=self.runtime_root,
            build_dir=self.runtime_build_dir,
        ) as objective:
            if len(initial) != len(objective.description["spec"]["fixed_parameters"]):
                raise ModelContractError(
                    "initialParameters must follow the registered flat parameter layout"
                )
            fitted = minimize_lbfgsb(
                objective.evaluate,
                initial,
                bounds=bounds,
                max_iterations=self.getOrDefault(self.maxIter),
                gradient_tolerance=tolerance,
                function_tolerance=1e-12,
            )
            if not fitted.converged or fitted.projected_gradient_inf_norm > tolerance:
                raise ModelContractError(
                    "Shared optimization failed its convergence/score contract: "
                    f"status={fitted.status}, "
                    f"projected_score={fitted.projected_gradient_inf_norm}, "
                    f"message={fitted.message}"
                )
            summary = {
                "converged": fitted.converged,
                "status": fitted.status,
                "message": str(fitted.message)[:500],
                "iterations": fitted.iterations,
                "objective_calls": fitted.objective_calls,
                "objective": fitted.evaluation.value,
                "row_count": fitted.evaluation.row_count,
                "gradient_inf_norm": fitted.gradient_inf_norm,
                "projected_gradient_inf_norm": fitted.projected_gradient_inf_norm,
                "active_bounds": list(fitted.active_bounds),
                "trace_tail": [list(row) for row in fitted.trace[-16:]],
                "scipy_version": scipy.__version__,
                "target": "shared-sum-likelihood",
            }
            model = TMBModel(
                modelId=model_id,
                parameters=fitted.parameters,
                parameter_names=objective.description["spec"]["fixed_parameters"],
                prepared=objective.prepared,
                fit_summary=summary,
                root=self.runtime_root,
                build_dir=self.runtime_build_dir,
            )
        return self._copyValues(model)

    def write(self):
        return _TMBWriter(self)

    @classmethod
    def read(cls):
        return _TMBReader(cls)


class TMBModel(Model, _TMBParams, MLReadable, MLWritable):
    """Fitted numerical state pinned to its verified prepared native artifact."""

    def __init__(
        self,
        *,
        modelId="",
        parameters=(),
        parameter_names=(),
        prepared=None,
        fit_summary=None,
        root=None,
        build_dir=None,
    ):
        super().__init__()
        self._defaults()
        self._set(modelId=modelId)
        self.parameters = tuple(finite(value) for value in parameters)
        self.parameter_names = tuple(parameter_names)
        self.prepared = copy.deepcopy(prepared)
        self.fit_summary = copy.deepcopy(fit_summary or {})
        self.runtime_root, self.runtime_build_dir = root, build_dir

    def _current_description(self):
        description = runtime.describe_prepared(
            self.getOrDefault(self.modelId),
            root=self.runtime_root,
            build_dir=self.runtime_build_dir,
        )
        if self.prepared != artifact_identity(description):
            raise ModelContractError(
                "Saved/fitted artifact differs from the current prepared runtime"
            )
        if self.parameter_names != tuple(description["spec"]["fixed_parameters"]) or len(
            self.parameters
        ) != len(self.parameter_names):
            raise ModelContractError(
                "Saved fixed parameter layout differs from the registered model"
            )
        return description

    def _transform(self, dataset):
        self._current_description()
        return predict_dataframe(
            dataset,
            self.getOrDefault(self.modelId),
            self.parameters,
            training_columns=self.getOrDefault(self.dataCols),
            prediction_col=self.getOrDefault(self.predictionCol),
            target=self.getOrDefault(self.predictionTarget) or None,
            batch_size=self.getOrDefault(self.batchSize),
            prepared=self.prepared,
            root=self.runtime_root,
            build_dir=self.runtime_build_dir,
        )

    def transformSchema(self, schema):
        from pyspark.sql.types import DoubleType, StructField, StructType

        description = self._current_description()
        prediction, _ = prediction_bindings(
            schema,
            description["spec"],
            self.getOrDefault(self.dataCols),
            self.getOrDefault(self.predictionCol),
            self.getOrDefault(self.predictionTarget) or None,
        )
        return StructType(
            [
                *schema.fields,
                StructField(
                    self.getOrDefault(self.predictionCol),
                    DoubleType(),
                    nullable=False,
                    metadata={
                        "modelId": self.getOrDefault(self.modelId),
                        "target": prediction["target"],
                    },
                ),
            ]
        )

    def write(self):
        return _TMBWriter(self)

    @classmethod
    def read(cls):
        return _TMBReader(cls)


def _local_path(value):
    if not isinstance(value, str) or not value:
        raise ModelContractError("Use an explicit local/shared-filesystem model directory")
    parsed = urlparse(value)
    if parsed.scheme:
        if parsed.scheme != "file" or parsed.netloc not in {"", "localhost"}:
            raise ModelContractError(
                "TMB JSON persistence currently supports local file paths only"
            )
        value = unquote(parsed.path)
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ModelContractError("Model directory must not be a symbolic link")
    return path.absolute()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ModelContractError("Duplicate model JSON key")
        result[key] = value
    return result


def _read_payload(directory):
    path = directory / "model.json"
    if (
        directory.is_symlink()
        or path.is_symlink()
        or not path.is_file()
        or path.stat().st_size > MAX_JSON
    ):
        raise ModelContractError("Choose an ordinary bounded model.json file")
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_JSON:
            raise ModelContractError("Model JSON exceeds its size limit")
        record = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_float=lambda value: finite(float(value)),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ModelContractError("Nonfinite JSON value")
            ),
        )
    except (ValueError, UnicodeError) as error:
        raise ModelContractError("Invalid model JSON") from error
    required = {
        "schema_version",
        "kind",
        "uid",
        "params",
        "prepared",
        "parameters",
        "parameter_names",
        "fit_summary",
    }
    if (
        not isinstance(record, dict)
        or set(record) != required
        or type(record["schema_version"]) is not int
        or record["schema_version"] != 1
    ):
        raise ModelContractError("Unsupported TMB model JSON schema")
    if record["kind"] not in {"spark-tmb-estimator", "spark-tmb-model"}:
        raise ModelContractError("Unsupported TMB ML object kind")
    if not isinstance(record["uid"], str) or not re.fullmatch(
        r"[A-Za-z0-9_]{1,128}", record["uid"]
    ):
        raise ModelContractError("Invalid saved ML identity")
    if not isinstance(record["params"], dict) or set(record["params"]) != PARAMETER_NAMES:
        raise ModelContractError("Saved ML parameters differ from the supported schema")
    if not isinstance(record["fit_summary"], dict):
        raise ModelContractError("Saved fitting diagnostics must be structured JSON")
    return record


def _owned_directory(directory):
    _read_payload(directory)
    if {item.name for item in directory.iterdir()} != {"model.json", "metadata"}:
        raise ModelContractError("Overwrite refuses unrelated files in a model directory")
    metadata = directory / "metadata"
    if metadata.is_symlink() or not metadata.is_dir():
        raise ModelContractError("Invalid saved Spark ML metadata directory")
    entries = list(metadata.iterdir())
    allowed = re.compile(
        r"(?:part-[A-Za-z0-9_.-]+|\.part-[A-Za-z0-9_.-]+\.crc|_SUCCESS|\._SUCCESS\.crc)\Z"
    )
    if len(entries) > 32 or any(
        item.is_symlink()
        or not item.is_file()
        or item.stat().st_size > MAX_JSON
        or not allowed.fullmatch(item.name)
        for item in entries
    ):
        raise ModelContractError("Model metadata must contain only bounded Spark metadata files")


class _TMBWriter(MLWriter):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance

    def save(self, path):
        # Avoid MLWriter's general Hadoop overwrite before validating ownership.
        if self.optionMap:
            raise ModelContractError("No additional persistence options are supported")
        target = _local_path(path)
        if target.exists():
            if not self.shouldOverwrite:
                raise FileExistsError(f"Model directory already exists: {target}")
            _owned_directory(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        instance = self.instance
        description = runtime.describe_prepared(
            instance.getOrDefault(instance.modelId),
            root=instance.runtime_root,
            build_dir=instance.runtime_build_dir,
        )
        prepared = artifact_identity(description)
        is_model = isinstance(instance, TMBModel)
        if is_model:
            instance._current_description()
        record = {
            "schema_version": 1,
            "kind": "spark-tmb-model" if is_model else "spark-tmb-estimator",
            "uid": instance.uid,
            "params": instance._parameter_values(),
            "prepared": prepared,
            "parameters": list(instance.parameters) if is_model else [],
            "parameter_names": list(instance.parameter_names) if is_model else [],
            "fit_summary": instance.fit_summary if is_model else {},
        }
        payload = json.dumps(
            record, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode()
        if len(payload) > MAX_JSON:
            raise ModelContractError("Model JSON exceeds its size limit")
        stage = Path(tempfile.mkdtemp(prefix=f".{target.name}-tmb-stage-", dir=target.parent))
        backup = None
        try:
            (stage / "model.json").write_bytes(payload)
            DefaultParamsWriter.saveMetadata(instance, str(stage), self.sparkSession.sparkContext)
            if target.exists():
                if not self.shouldOverwrite:
                    raise FileExistsError(str(target))
                _owned_directory(target)
                backup = Path(
                    tempfile.mkdtemp(prefix=f".{target.name}-tmb-backup-", dir=target.parent)
                )
                backup.rmdir()
                target.rename(backup)
            stage.rename(target)
            if backup is not None:
                shutil.rmtree(backup)
        except BaseException:
            if backup is not None and backup.exists() and not target.exists():
                backup.rename(target)
            raise
        finally:
            if stage.exists():
                shutil.rmtree(stage)


class _TMBReader(MLReader):
    def __init__(self, cls):
        super().__init__()
        self.cls = cls
        self.root = self.build_dir = None

    def withRuntime(self, *, root=None, build_dir=None):
        """Select trusted installed runtime paths explicitly, never from saved JSON."""
        self.root, self.build_dir = root, build_dir
        return self

    def load(self, path):
        record = _read_payload(_local_path(path))
        expected_kind = "spark-tmb-model" if self.cls is TMBModel else "spark-tmb-estimator"
        if record["kind"] != expected_kind:
            raise ModelContractError("Saved object kind differs from the requested ML class")
        params = record["params"]
        description = runtime.describe_prepared(
            params["modelId"], root=self.root, build_dir=self.build_dir
        )
        if record["prepared"] != artifact_identity(description):
            raise ModelContractError(
                "Saved model artifact differs from the current prepared runtime"
            )
        if self.cls is TMBModel:
            model = self.cls(
                modelId=params["modelId"],
                parameters=record["parameters"],
                parameter_names=record["parameter_names"],
                prepared=record["prepared"],
                fit_summary=record["fit_summary"],
                root=self.root,
                build_dir=self.build_dir,
            )
            model._current_description()
        else:
            if record["parameters"] or record["parameter_names"] or record["fit_summary"]:
                raise ModelContractError(
                    "An estimator must not masquerade as fitted numerical state"
                )
            model = self.cls(root=self.root, build_dir=self.build_dir)
        model._resetUid(record["uid"])
        return model.setParams(**params)
