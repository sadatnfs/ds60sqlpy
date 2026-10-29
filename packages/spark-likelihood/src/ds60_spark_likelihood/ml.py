"""Actual PySpark ML stages with source-bound JSON persistence.

These optional stages use the canonical Spark/Torch reducers and driver optimizer.
Persisted models contain numerical state and registered identities, not executable
pickles. Trusted model factories must already be registered before loading.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

from pyspark.ml import Estimator, Model
from pyspark.ml.param import Param, Params, TypeConverters
from pyspark.ml.util import DefaultParamsWriter, MLReadable, MLReader, MLWritable, MLWriter

from .contracts import ObjectiveError, finite_number
from .dataframe import DataFrameObjective, predict_dataframe, prediction_schema
from .optimization import minimize_lbfgsb
from .registry import configuration_json, resolve_model

MAX_JSON = 1_000_000
PARAMETER_NAMES = frozenset(
    {
        "modelId",
        "modelConfig",
        "featureCols",
        "labelCol",
        "weightCol",
        "unitWeightCol",
        "groupCol",
        "orderCols",
        "initialParameters",
        "parameterBounds",
        "batchSize",
        "predictionCol",
        "predictionTarget",
        "maxIter",
        "tol",
        "reduction",
        "l2Strength",
    }
)


def _columns(value):
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise ValueError("featureCols must map canonical features to Spark column names")
    return dict(value)


def _configuration(value):
    return json.loads(configuration_json(value))


def _numbers(value):
    if not isinstance(value, (list, tuple)):
        raise ValueError("Use an explicit parameter list")
    return [finite_number(item, "parameter") for item in value]


def _bounds(value):
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError("Bounds must be a list of endpoint pairs")
    result = []
    for pair in value:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("Bounds need lower/upper pairs")
        result.append([None if item is None else finite_number(item, "bound") for item in pair])
    return result


def _finite_option(value):
    return finite_number(value, "numeric ML option")


class _LikelihoodParams(Params):
    modelId = Param(
        Params._dummy(), "modelId", "Trusted registered model ID", TypeConverters.toString
    )
    modelConfig = Param(
        Params._dummy(), "modelConfig", "Bounded registered model configuration", _configuration
    )
    featureCols = Param(
        Params._dummy(), "featureCols", "Canonical feature to Spark column mapping", _columns
    )
    labelCol = Param(
        Params._dummy(), "labelCol", "Observed scalar response column", TypeConverters.toString
    )
    weightCol = Param(
        Params._dummy(),
        "weightCol",
        "Per-observation weight for row likelihoods",
        TypeConverters.toString,
    )
    unitWeightCol = Param(
        Params._dummy(),
        "unitWeightCol",
        "Constant-per-group joint likelihood weight",
        TypeConverters.toString,
    )
    groupCol = Param(
        Params._dummy(), "groupCol", "Complete independent unit identifier", TypeConverters.toString
    )
    orderCols = Param(
        Params._dummy(),
        "orderCols",
        "Explicit unique within-unit ordering keys",
        TypeConverters.toListString,
    )
    initialParameters = Param(
        Params._dummy(), "initialParameters", "Canonical initial fixed coordinates", _numbers
    )
    parameterBounds = Param(
        Params._dummy(), "parameterBounds", "Canonical coordinate bounds", _bounds
    )
    batchSize = Param(
        Params._dummy(), "batchSize", "Row/prediction kernel batch size", TypeConverters.toInt
    )
    predictionCol = Param(
        Params._dummy(), "predictionCol", "New output column", TypeConverters.toString
    )
    predictionTarget = Param(
        Params._dummy(),
        "predictionTarget",
        "Declared response-free target",
        TypeConverters.toString,
    )
    maxIter = Param(
        Params._dummy(), "maxIter", "Bounded driver optimizer iterations", TypeConverters.toInt
    )
    tol = Param(Params._dummy(), "tol", "Maximum accepted projected gradient norm", _finite_option)
    reduction = Param(Params._dummy(), "reduction", "sum or weighted_mean", TypeConverters.toString)
    l2Strength = Param(
        Params._dummy(),
        "l2Strength",
        "Global L2 penalty after data reduction",
        _finite_option,
    )

    def _defaults(self):
        self._setDefault(
            modelId="",
            modelConfig={},
            featureCols={},
            labelCol="label",
            weightCol="",
            unitWeightCol="",
            groupCol="",
            orderCols=[],
            initialParameters=[],
            parameterBounds=[],
            batchSize=256,
            predictionCol="prediction",
            predictionTarget="",
            maxIter=100,
            tol=1e-6,
            reduction="sum",
            l2Strength=0.0,
        )

    def setParams(self, **parameters):
        if not set(parameters) <= PARAMETER_NAMES:
            raise ValueError("Unknown likelihood ML parameter")
        return self._set(**parameters)

    def _parameter_values(self):
        return {name: copy.deepcopy(self.getOrDefault(name)) for name in sorted(PARAMETER_NAMES)}


class SparkLikelihoodEstimator(Estimator, _LikelihoodParams, MLReadable, MLWritable):
    """One shared MLE/penalized objective, never averaged independent estimates."""

    def __init__(
        self,
        *,
        modelId="",
        modelConfig=None,
        featureCols=None,
        labelCol="label",
        weightCol="",
        unitWeightCol="",
        groupCol="",
        orderCols=(),
        initialParameters=(),
        parameterBounds=None,
        batchSize=256,
        predictionCol="prediction",
        predictionTarget="",
        maxIter=100,
        tol=1e-6,
        reduction="sum",
        l2Strength=0.0,
    ):
        super().__init__()
        self._defaults()
        if isinstance(orderCols, (str, bytes)):
            raise ValueError("orderCols must be a sequence")
        self._set(
            modelId=modelId,
            modelConfig={} if modelConfig is None else modelConfig,
            featureCols={} if featureCols is None else featureCols,
            labelCol=labelCol,
            weightCol=weightCol,
            unitWeightCol=unitWeightCol,
            groupCol=groupCol,
            orderCols=list(orderCols),
            initialParameters=list(initialParameters),
            parameterBounds=[] if parameterBounds is None else parameterBounds,
            batchSize=batchSize,
            predictionCol=predictionCol,
            predictionTarget=predictionTarget,
            maxIter=maxIter,
            tol=tol,
            reduction=reduction,
            l2Strength=l2Strength,
        )

    def _fit(self, dataset):
        import scipy

        registered = resolve_model(
            self.getOrDefault(self.modelId), self.getOrDefault(self.modelConfig)
        )
        initial = self.getOrDefault(self.initialParameters)
        if len(initial) != registered.parameter_count:
            raise ObjectiveError(
                "initialParameters must follow the canonical registered parameter order"
            )
        tolerance = finite_number(self.getOrDefault(self.tol), "fit tolerance")
        with DataFrameObjective(
            dataset,
            registered,
            feature_columns=self.getOrDefault(self.featureCols),
            label_col=self.getOrDefault(self.labelCol),
            weight_col=self.getOrDefault(self.weightCol) or None,
            unit_weight_col=self.getOrDefault(self.unitWeightCol) or None,
            group_col=self.getOrDefault(self.groupCol) or None,
            order_cols=self.getOrDefault(self.orderCols),
            batch_size=self.getOrDefault(self.batchSize),
            reduction=self.getOrDefault(self.reduction),
            l2_strength=self.getOrDefault(self.l2Strength),
        ) as objective:
            fitted = minimize_lbfgsb(
                objective.evaluate,
                initial,
                bounds=self.getOrDefault(self.parameterBounds) or None,
                max_iterations=self.getOrDefault(self.maxIter),
                gradient_tolerance=tolerance,
                function_tolerance=1e-12,
            )
            if not fitted.converged or fitted.projected_gradient_inf_norm > tolerance:
                raise ObjectiveError(
                    "Shared fit failed convergence/score criteria: "
                    f"status={fitted.status}, score={fitted.projected_gradient_inf_norm}, "
                    f"message={fitted.message}"
                )
            summary = {
                "converged": fitted.converged,
                "status": fitted.status,
                "message": str(fitted.message)[:500],
                "objective": fitted.evaluation.value,
                "row_count": fitted.evaluation.row_count,
                "unit_count": getattr(fitted.evaluation, "unit_count", None),
                "weight_sum": fitted.evaluation.weight_sum,
                "weight_kind": "unit"
                if registered.factorization == "complete_groups"
                else "observation",
                "reduction": fitted.evaluation.reduction,
                "penalty_value": fitted.evaluation.penalty_value,
                "gradient_inf_norm": fitted.gradient_inf_norm,
                "projected_gradient_inf_norm": fitted.projected_gradient_inf_norm,
                "iterations": fitted.iterations,
                "objective_calls": fitted.objective_calls,
                "active_bounds": list(fitted.active_bounds),
                "trace_tail": [list(row) for row in fitted.trace[-16:]],
                "scipy_version": scipy.__version__,
                "factorization": registered.factorization,
            }
            model = SparkLikelihoodModel(
                modelId=registered.model_id,
                modelConfig=registered.configuration,
                parameters=fitted.parameters,
                parameter_names=registered.parameter_names,
                descriptor=objective.descriptor,
                fit_summary=summary,
            )
        return self._copyValues(model)

    def write(self):
        return _LikelihoodWriter(self)

    @classmethod
    def read(cls):
        return _LikelihoodReader(cls)


class SparkLikelihoodModel(Model, _LikelihoodParams, MLReadable, MLWritable):
    """Fitted state with an explicit declared prediction and source/config identity."""

    def __init__(
        self,
        *,
        modelId="",
        modelConfig=None,
        parameters=(),
        parameter_names=(),
        descriptor=None,
        fit_summary=None,
    ):
        super().__init__()
        self._defaults()
        self._set(modelId=modelId, modelConfig={} if modelConfig is None else modelConfig)
        self.parameters = tuple(finite_number(value, "fitted parameter") for value in parameters)
        self.parameter_names = tuple(parameter_names)
        self.model_descriptor = copy.deepcopy(descriptor)
        self.fit_summary = copy.deepcopy(fit_summary or {})

    def _current_model(self):
        registered = resolve_model(
            self.getOrDefault(self.modelId), self.getOrDefault(self.modelConfig)
        )
        if registered.descriptor() != self.model_descriptor:
            raise ObjectiveError("Saved/fitted model source or configuration fingerprint changed")
        if (
            self.parameter_names != registered.parameter_names
            or len(self.parameters) != registered.parameter_count
        ):
            raise ObjectiveError("Saved parameter layout differs from the registered model")
        return registered

    def _transform(self, dataset):
        return predict_dataframe(
            dataset,
            self._current_model(),
            self.parameters,
            feature_columns=self.getOrDefault(self.featureCols),
            prediction_col=self.getOrDefault(self.predictionCol),
            target=self.getOrDefault(self.predictionTarget) or None,
            batch_size=self.getOrDefault(self.batchSize),
            expected_descriptor=self.model_descriptor,
        )

    def transformSchema(self, schema):
        from pyspark.sql.types import DoubleType, StructField, StructType

        model = self._current_model()
        chosen = prediction_schema(
            schema,
            model,
            self.getOrDefault(self.featureCols),
            self.getOrDefault(self.predictionCol),
            self.getOrDefault(self.predictionTarget) or None,
        )
        return StructType(
            [
                *schema.fields,
                StructField(
                    self.getOrDefault(self.predictionCol),
                    DoubleType(),
                    False,
                    {
                        "modelId": model.model_id,
                        "target": chosen,
                        "fingerprint": self.model_descriptor["fingerprint"],
                    },
                ),
            ]
        )

    def write(self):
        return _LikelihoodWriter(self)

    @classmethod
    def read(cls):
        return _LikelihoodReader(cls)


def _local_path(value):
    if not isinstance(value, str) or not value:
        raise ObjectiveError("Use an explicit local/shared-filesystem model directory")
    parsed = urlparse(value)
    if parsed.scheme:
        if parsed.scheme != "file" or parsed.netloc not in {"", "localhost"}:
            raise ObjectiveError(
                "likelihood JSON persistence currently supports local file paths only"
            )
        value = unquote(parsed.path)
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ObjectiveError("Model directory must not be a symbolic link")
    return path.absolute()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ObjectiveError("Duplicate model JSON key")
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
        raise ObjectiveError("Choose an ordinary bounded model.json file")
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_JSON:
            raise ObjectiveError("Model JSON exceeds its size limit")
        record = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_float=lambda value: finite_number(float(value), "JSON value"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ObjectiveError("Nonfinite JSON value")
            ),
        )
    except (ValueError, UnicodeError) as error:
        raise ObjectiveError("Invalid model JSON") from error
    required = {
        "schema_version",
        "kind",
        "uid",
        "params",
        "descriptor",
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
        raise ObjectiveError("Unsupported likelihood model JSON schema")
    if record["kind"] not in {"ds60-spark-likelihood-estimator", "ds60-spark-likelihood-model"}:
        raise ObjectiveError("Unsupported likelihood ML object kind")
    if not isinstance(record["uid"], str) or not re.fullmatch(
        r"[A-Za-z0-9_]{1,128}", record["uid"]
    ):
        raise ObjectiveError("Invalid saved ML identity")
    if not isinstance(record["params"], dict) or set(record["params"]) != PARAMETER_NAMES:
        raise ObjectiveError("Saved ML parameters differ from the supported schema")
    if not isinstance(record["fit_summary"], dict):
        raise ObjectiveError("Saved fitting diagnostics must be structured JSON")
    return record


def _owned_directory(directory):
    _read_payload(directory)
    if {item.name for item in directory.iterdir()} != {"model.json", "metadata"}:
        raise ObjectiveError("Overwrite refuses unrelated files in a model directory")
    metadata = directory / "metadata"
    if metadata.is_symlink() or not metadata.is_dir():
        raise ObjectiveError("Invalid saved Spark ML metadata directory")
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
        raise ObjectiveError("Model metadata must contain only bounded Spark metadata files")


class _LikelihoodWriter(MLWriter):
    def __init__(self, instance):
        super().__init__()
        self.instance = instance

    def save(self, path):
        if self.optionMap:
            raise ObjectiveError("Additional persistence options are unsupported")
        target = _local_path(path)
        if target.exists():
            if not self.shouldOverwrite:
                raise FileExistsError(str(target))
            _owned_directory(target)
        instance = self.instance
        registered = resolve_model(
            instance.getOrDefault(instance.modelId), instance.getOrDefault(instance.modelConfig)
        )
        is_model = isinstance(instance, SparkLikelihoodModel)
        if is_model:
            instance._current_model()
        record = {
            "schema_version": 1,
            "kind": "ds60-spark-likelihood-model"
            if is_model
            else "ds60-spark-likelihood-estimator",
            "uid": instance.uid,
            "params": instance._parameter_values(),
            "descriptor": registered.descriptor(),
            "parameters": list(instance.parameters) if is_model else [],
            "parameter_names": list(instance.parameter_names) if is_model else [],
            "fit_summary": instance.fit_summary if is_model else {},
        }
        payload = json.dumps(
            record, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode()
        if len(payload) > MAX_JSON:
            raise ObjectiveError("Model JSON exceeds its size bound")
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(
            tempfile.mkdtemp(prefix=f".{target.name}-likelihood-stage-", dir=target.parent)
        )
        backup = None
        try:
            (stage / "model.json").write_bytes(payload)
            DefaultParamsWriter.saveMetadata(instance, str(stage), self.sparkSession.sparkContext)
            if target.exists():
                if not self.shouldOverwrite:
                    raise FileExistsError(str(target))
                _owned_directory(target)
                backup = Path(
                    tempfile.mkdtemp(prefix=f".{target.name}-likelihood-backup-", dir=target.parent)
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


class _LikelihoodReader(MLReader):
    def __init__(self, cls):
        super().__init__()
        self.cls = cls

    def load(self, path):
        record = _read_payload(_local_path(path))
        expected = (
            "ds60-spark-likelihood-model"
            if self.cls is SparkLikelihoodModel
            else "ds60-spark-likelihood-estimator"
        )
        if record["kind"] != expected:
            raise ObjectiveError("Saved ML object kind differs")
        params = record["params"]
        registered = resolve_model(params["modelId"], params["modelConfig"])
        if record["descriptor"] != registered.descriptor():
            raise ObjectiveError(
                "Saved model source/configuration fingerprint differs from the trusted registry"
            )
        if self.cls is SparkLikelihoodModel:
            instance = self.cls(
                modelId=params["modelId"],
                modelConfig=params["modelConfig"],
                parameters=record["parameters"],
                parameter_names=record["parameter_names"],
                descriptor=record["descriptor"],
                fit_summary=record["fit_summary"],
            )
            instance._current_model()
        else:
            if record["parameters"] or record["parameter_names"] or record["fit_summary"]:
                raise ObjectiveError("Estimator metadata cannot masquerade as a fitted model")
            instance = self.cls()
        instance._resetUid(record["uid"])
        return instance.setParams(**params)
