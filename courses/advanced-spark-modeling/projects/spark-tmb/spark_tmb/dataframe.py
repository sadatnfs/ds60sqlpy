"""Typed Spark DataFrame boundaries for prepared, additive TMB models.

Only bounded unit metadata and value/gradient summaries reach the driver.
DataFrame rows have no implicit global order. Complete groups require explicit
unique within-group ordering keys; prediction preserves rows and columns without
claiming a global ordering.
"""

from __future__ import annotations

import copy
import json
import math
import os
import re
from functools import partial

from . import runtime
from .registry import ModelContractError, finite
from .spark import SparkTMBObjective

COLUMN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
DIGEST = re.compile(r"[a-f0-9]{64}\Z")
NUMERIC = {"byte", "short", "integer", "long", "float", "double"}
INTEGER = {"byte", "short", "integer", "long"}
MAX_BATCH = 4096


def artifact_identity(description):
    """Copy only the authoritative prepared identity, never executable pointers."""
    prepared = description.get("prepared", {})
    keys = {"source_sha256", "library_sha256", "registry_sha256", "abi"}
    if not isinstance(prepared, dict) or not keys <= set(prepared):
        raise ModelContractError("Missing authoritative prepared artifact descriptor")
    for key in keys - {"abi"}:
        if not isinstance(prepared[key], str) or not DIGEST.fullmatch(prepared[key]):
            raise ModelContractError("Invalid prepared artifact checksum")
    abi = prepared["abi"]
    if not isinstance(abi, dict) or not {"R", "TMB", "Matrix", "architecture"} <= set(abi):
        raise ModelContractError("Missing prepared R/TMB/Matrix/architecture identity")
    if not all(isinstance(value, str) and value for value in abi.values()):
        raise ModelContractError("Invalid prepared ABI metadata")
    return copy.deepcopy({key: prepared[key] for key in sorted(keys)})


def check_artifact(model_id, expected, root, build_dir):
    actual = runtime.describe_prepared(model_id, root=root, build_dir=build_dir)
    if artifact_identity(actual) != expected:
        raise ModelContractError("Prepared model artifact changed; refit or explicitly requalify")
    return actual


def schema_types(schema):
    fields = schema.fields
    names = [field.name for field in fields]
    if len({name.casefold() for name in names}) != len(names):
        raise ModelContractError("DataFrame has duplicate or case-ambiguous column names")
    return {field.name: field.dataType.typeName() for field in fields}


def validate_bindings(schema, fields, columns):
    if not isinstance(columns, dict) or set(columns) != set(fields):
        raise ModelContractError("dataCols must map exactly the declared observation fields")
    types = schema_types(schema)
    if len(set(columns.values())) != len(columns):
        raise ModelContractError("Observation fields must map to distinct Spark columns")
    for field, kind in fields.items():
        column = columns[field]
        if not isinstance(column, str) or not COLUMN.fullmatch(column):
            raise ModelContractError("Use simple explicit Spark column names")
        allowed = INTEGER if kind == "integer_vector" else NUMERIC
        if kind not in {"integer_vector", "real_vector"} or types.get(column) not in allowed:
            raise ModelContractError(
                f"Column {column} has an incompatible numeric type for {field}"
            )
    return types


def _number(value, kind):
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelContractError("Native observation values must be numeric and nonmissing")
    if kind == "integer_vector":
        if not isinstance(value, int) or not -2147483647 <= value <= 2147483647:
            raise ModelContractError("Integer observations must be exact non-NA signed32 values")
        return value
    return finite(value)


def _ordered_key(values):
    result = []
    for value in values:
        if isinstance(value, bool) or value is None:
            raise ModelContractError("Ordering keys must be nonmissing strings or finite numbers")
        if isinstance(value, str):
            result.append(("string", value))
        elif isinstance(value, (int, float)) and math.isfinite(value):
            result.append(("number", value))
        else:
            raise ModelContractError("Ordering keys must be strings or finite numbers")
    return tuple(result)


def _unit_id(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or value == "":
        raise ModelContractError("Group IDs must be nonempty strings or exact integers")
    identity = "group:" + json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    if len(identity) > 128:
        raise ModelContractError("Encoded group ID exceeds the bounded unit identity")
    return identity


def _build_data(rows, names, kinds):
    data = {
        name: [_number(row[index], kinds[name]) for row in rows] for index, name in enumerate(names)
    }
    return data


def _row_units(index, iterator, *, model_id, root, build_dir, expected, names, kinds, batch_size):
    check_artifact(model_id, expected, root, build_dir)
    batch, number = [], 0
    for row in iterator:
        batch.append(tuple(row))
        if len(batch) == batch_size:
            yield {
                "unit_id": f"partition:{index}:batch:{number}",
                "data": _build_data(batch, names, kinds),
            }
            batch, number = [], number + 1
    if batch:
        yield {
            "unit_id": f"partition:{index}:batch:{number}",
            "data": _build_data(batch, names, kinds),
        }


def _key_group(row, *, width, order_count):
    values = tuple(row)
    return _unit_id(values[width]), (
        _ordered_key(values[width + 1 : width + 1 + order_count]),
        values[:width],
    )


def _new_group(value):
    return [value]


def _append_group(group, value):
    if len(group) >= MAX_BATCH:
        raise ModelContractError("A complete group exceeds 4096 rows; do not split dependent units")
    group.append(value)
    return group


def _merge_groups(left, right):
    if len(left) + len(right) > MAX_BATCH:
        raise ModelContractError("A complete group exceeds 4096 rows; do not split dependent units")
    return left + right


def _group_units(iterator, *, model_id, root, build_dir, expected, names, kinds):
    check_artifact(model_id, expected, root, build_dir)
    for identity, ordered in iterator:
        ordered.sort(key=lambda pair: pair[0])
        keys = [item[0] for item in ordered]
        if len(keys) != len(set(keys)):
            raise ModelContractError("Complete groups require unique deterministic ordering keys")
        rows = [item[1] for item in ordered]
        yield {"unit_id": identity, "data": _build_data(rows, names, kinds)}


class DataFrameObjective:
    """Own only derived unit caching for one shared DataFrame likelihood fit."""

    def __init__(
        self,
        dataset,
        model_id,
        *,
        columns,
        group_col=None,
        order_cols=(),
        batch_size=256,
        root=None,
        build_dir=None,
    ):
        if type(batch_size) is not int or not 1 <= batch_size <= MAX_BATCH:
            raise ModelContractError("batch_size must be within 1..4096")
        self.root = str(runtime.PROJECT_ROOT if root is None else root)
        self.build_dir = str(
            build_dir or os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models")
        )
        self.model_id = model_id
        self.description = runtime.describe_prepared(
            model_id, root=self.root, build_dir=self.build_dir
        )
        self.prepared = artifact_identity(self.description)
        spec = self.description["spec"]
        self._closed, self.units = False, None
        random_field = None if spec.get("random") is None else spec["random"]["group_field"]
        # Complete-unit ownership and a model's internal group indices are distinct.
        # Map every declared field explicitly; do not invent latent grouping data.
        fields = dict(spec["data"])
        types = validate_bindings(dataset.schema, fields, columns)
        names = list(fields)
        selected = [dataset[columns[name]] for name in names]
        common = {
            "model_id": model_id,
            "root": self.root,
            "build_dir": self.build_dir,
            "expected": self.prepared,
            "names": names,
            "kinds": fields,
        }
        if spec["factorization"] == "independent_rows":
            if group_col is not None or order_cols:
                raise ModelContractError(
                    "Independent-row fitting uses chunks; "
                    "group/order settings are for complete-group models"
                )
            if random_field is not None:
                raise ModelContractError(
                    "Independent-row models cannot declare group random effects"
                )
            units = dataset.select(*selected).rdd.mapPartitionsWithIndex(
                partial(_row_units, batch_size=batch_size, **common)
            )
        elif spec["factorization"] == "complete_groups":
            if (
                not isinstance(group_col, str)
                or not COLUMN.fullmatch(group_col)
                or types.get(group_col) not in INTEGER | {"string"}
            ):
                raise ModelContractError(
                    "Complete-group models require an explicit string/integer groupCol"
                )
            if (
                isinstance(order_cols, (str, bytes))
                or not order_cols
                or len(set(order_cols)) != len(order_cols)
            ):
                raise ModelContractError("Complete-group models require explicit unique orderCols")
            for column in order_cols:
                if (
                    not isinstance(column, str)
                    or not COLUMN.fullmatch(column)
                    or types.get(column) not in NUMERIC | {"string"}
                ):
                    raise ModelContractError(
                        "orderCols must name numeric or string columns; "
                        "convert temporal keys explicitly"
                    )
            projection = dataset.select(
                *selected, dataset[group_col], *[dataset[name] for name in order_cols]
            )
            pairs = projection.rdd.map(
                partial(_key_group, width=len(names), order_count=len(order_cols))
            )
            partitions = min(max(pairs.getNumPartitions(), 1), 64)
            grouped = pairs.combineByKey(
                _new_group, _append_group, _merge_groups, numPartitions=partitions
            )
            units = grouped.mapPartitions(partial(_group_units, **common))
        else:
            raise ModelContractError("Unsupported factorization")
        from pyspark import StorageLevel

        self.units = units
        try:
            self.units.persist(StorageLevel.MEMORY_AND_DISK)
            self.objective = SparkTMBObjective(
                self.units, model_id, root=self.root, build_dir=self.build_dir
            )
        except BaseException as error:
            try:
                self.close()
            except Exception as cleanup:
                error.add_note(f"Derived unit cache cleanup failed: {cleanup}")
            raise

    def evaluate(self, parameters):
        if self._closed:
            raise ModelContractError("This DataFrame objective has been closed")
        check_artifact(self.model_id, self.prepared, self.root, self.build_dir)
        return self.objective.evaluate(parameters)

    def close(self):
        if not self._closed:
            self._closed = True
            if self.units is not None:
                self.units.unpersist(blocking=True)

    def __enter__(self):
        if self._closed:
            raise ModelContractError("This DataFrame objective has been closed")
        return self

    def __exit__(self, kind, exception, traceback):
        try:
            self.close()
        except Exception as cleanup:
            if exception is None:
                raise
            exception.add_note(f"Derived unit cache cleanup failed: {cleanup}")
        return False


def prediction_bindings(schema, specification, training_columns, output_column, target):
    prediction = specification.get("prediction")
    if not isinstance(prediction, dict):
        raise ModelContractError("This prepared model has no declared response-free prediction")
    expected_target = prediction["target"]
    if target is not None and target != expected_target:
        raise ModelContractError("Prediction target differs from the registered semantic target")
    types = schema_types(schema)
    if (
        not isinstance(output_column, str)
        or not COLUMN.fullmatch(output_column)
        or output_column.casefold() in {name.casefold() for name in types}
    ):
        raise ModelContractError("predictionCol must be a new simple column name")
    columns = {}
    for prediction_field, training_field in prediction["from_training"].items():
        if training_field not in training_columns:
            raise ModelContractError("Missing fitted training-column mapping for prediction")
        columns[prediction_field] = training_columns[training_field]
    validate_bindings(schema, prediction["inputs"], columns)
    return prediction, columns


def _predict_partition(
    iterator, *, model_id, theta, root, build_dir, expected, target, inputs, indices, batch_size
):
    check_artifact(model_id, expected, root, build_dir)
    batch = []

    def emit(rows):
        data = {
            field: [_number(row[indices[field]], kind) for row in rows]
            for field, kind in inputs.items()
        }
        result = runtime.predict_prepared(
            model_id, data, theta, n_rows=len(rows), target=target, root=root, build_dir=build_dir
        )
        observed = {
            "source_sha256": result.get("artifact_source_sha256"),
            "library_sha256": result.get("artifact_library_sha256"),
            "registry_sha256": result.get("artifact_registry_sha256"),
            "abi": result.get("abi"),
        }
        if (
            observed != expected
            or result.get("target") != target
            or result.get("nobs") != len(rows)
        ):
            raise ModelContractError("Worker prediction artifact or target changed")
        values = result.get("prediction")
        if not isinstance(values, list) or len(values) != len(rows):
            raise ModelContractError("Prediction must return exactly one scalar for each input row")
        for row, value in zip(rows, values, strict=True):
            yield (*tuple(row), finite(value))

    for row in iterator:
        batch.append(row)
        if len(batch) == batch_size:
            yield from emit(batch)
            batch = []
    if batch:
        yield from emit(batch)


def predict_dataframe(
    dataset,
    model_id,
    parameters,
    *,
    training_columns,
    prediction_col="prediction",
    target=None,
    batch_size=256,
    prepared=None,
    root=None,
    build_dir=None,
):
    """Append a declared prediction without collecting data or requiring responses."""
    if type(batch_size) is not int or not 1 <= batch_size <= MAX_BATCH:
        raise ModelContractError("batch_size must be within 1..4096")
    root = str(runtime.PROJECT_ROOT if root is None else root)
    build_dir = str(build_dir or os.environ.get("SPARK_TMB_BUILD_DIR", "/opt/spark-tmb-models"))
    description = runtime.describe_prepared(model_id, root=root, build_dir=build_dir)
    identity = artifact_identity(description)
    if prepared is not None and identity != prepared:
        raise ModelContractError("Fitted model artifact differs from current prepared runtime")
    theta = tuple(finite(value) for value in parameters)
    if len(theta) != len(description["spec"]["fixed_parameters"]):
        raise ModelContractError("Prediction parameter layout differs from the registered model")
    prediction, columns = prediction_bindings(
        dataset.schema, description["spec"], training_columns, prediction_col, target
    )
    indices = {field: dataset.columns.index(column) for field, column in columns.items()}
    from pyspark.sql.types import DoubleType, StructField, StructType

    schema = StructType(
        [
            *dataset.schema.fields,
            StructField(
                prediction_col,
                DoubleType(),
                nullable=False,
                metadata={"modelId": model_id, "target": prediction["target"]},
            ),
        ]
    )
    output = dataset.rdd.mapPartitions(
        partial(
            _predict_partition,
            model_id=model_id,
            theta=theta,
            root=root,
            build_dir=build_dir,
            expected=identity,
            target=prediction["target"],
            inputs=prediction["inputs"],
            indices=indices,
            batch_size=batch_size,
        )
    )
    return dataset.sparkSession.createDataFrame(output, schema=schema)
