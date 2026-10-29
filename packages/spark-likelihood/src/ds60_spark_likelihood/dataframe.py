"""Explicit DataFrame schemas for row and complete-unit registered likelihoods.

Only canonical backend summaries reach the driver. Registered source/configuration
identities are checked in the driver and executor kernels. No global DataFrame
ordering is assumed or promised.
"""

from __future__ import annotations

import copy
import json
import math
import re
from functools import partial

from .contracts import ObjectiveError, finite_number, finite_vector
from .prediction import predict_batch
from .registry import RegisteredModel, resolve_model
from .spark_backend import SparkObjective
from .spark_units import SparkUnitObjective
from .torch_backend import TorchLoss
from .unit_backend import CompleteUnit, TorchUnitLoss

COLUMN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
NUMERIC = {"byte", "short", "integer", "long", "float", "double"}
INTEGER = {"byte", "short", "integer", "long"}


def resolved_model(model_or_id, configuration=None):
    if isinstance(model_or_id, RegisteredModel):
        if configuration is not None:
            raise ObjectiveError("A resolved model already owns its configuration")
        return model_or_id
    return resolve_model(model_or_id, configuration)


def check_model_identity(model, expected):
    if model.descriptor() != expected:
        raise ObjectiveError(
            "Registered model source/configuration differs from its bound descriptor"
        )


def schema_types(schema):
    names = [field.name for field in schema.fields]
    if len({name.casefold() for name in names}) != len(names):
        raise ObjectiveError("DataFrame contains duplicate or case-ambiguous columns")
    return {field.name: field.dataType.typeName() for field in schema.fields}


def feature_bindings(schema, model, feature_columns):
    if not isinstance(feature_columns, dict) or set(feature_columns) != set(model.feature_names):
        raise ObjectiveError("feature_columns must map exactly the registered feature names")
    types = schema_types(schema)
    for name, column in feature_columns.items():
        if (
            not isinstance(column, str)
            or not COLUMN.fullmatch(column)
            or types.get(column) not in NUMERIC
        ):
            raise ObjectiveError(f"Feature {name} needs an existing primitive numeric Spark column")
    if len(set(feature_columns.values())) != len(feature_columns):
        raise ObjectiveError(
            "Features must map to distinct columns; create an explicit alias if needed"
        )
    return types


def numeric_column(types, column, role):
    if (
        not isinstance(column, str)
        or not COLUMN.fullmatch(column)
        or types.get(column) not in NUMERIC
    ):
        raise ObjectiveError(f"{role} must be an existing primitive numeric Spark column")


def _row_guard(theta, features, targets, *, model, descriptor):
    check_model_identity(model, descriptor)
    return model.loss.per_observation(theta, features, targets)


def _unit_guard(theta, features, targets, *, model, descriptor):
    check_model_identity(model, descriptor)
    return model.loss.per_unit(theta, features, targets)


def _identity(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or value == "":
        raise ObjectiveError("Complete-group identity must be a nonempty string or exact integer")
    encoded = "group:" + json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    if len(encoded) > 128:
        raise ObjectiveError("Encoded group identity exceeds 128 characters")
    return encoded


def _order_key(values):
    result = []
    for value in values:
        if isinstance(value, str):
            result.append(("text", value))
        elif (
            not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
        ):
            result.append(("number", value))
        else:
            raise ObjectiveError("Order keys must be nonmissing strings or finite numbers")
    return tuple(result)


def _group_pair(row, *, width, order_count, weighted):
    values = tuple(row)
    data = tuple(finite_number(value, "complete-unit observation") for value in values[:width])
    identity = _identity(values[width])
    keys = _order_key(values[width + 1 : width + 1 + order_count]) if order_count else None
    weight = finite_number(values[-1], "unit weight") if weighted else 1.0
    if weight < 0:
        raise ObjectiveError("Unit weight must be nonnegative")
    return identity, (weight, keys, data)


def _new_group(value):
    weight, key, row = value
    return weight, [(key, row)]


def _append_group(group, value, *, limit):
    weight, rows = group
    other_weight, key, row = value
    if weight != other_weight:
        raise ObjectiveError("unit_weight_col must be constant within each complete group")
    if len(rows) >= limit:
        raise ObjectiveError("Complete unit exceeds its registered row bound; it may not be split")
    rows.append((key, row))
    return weight, rows


def _merge_groups(left, right, *, limit):
    if left[0] != right[0]:
        raise ObjectiveError("unit_weight_col must be constant within each complete group")
    if len(left[1]) + len(right[1]) > limit:
        raise ObjectiveError("Complete unit exceeds its registered row bound; it may not be split")
    return left[0], left[1] + right[1]


def _complete_units(iterator, *, model, descriptor, ordered):
    check_model_identity(model, descriptor)
    for identity, (weight, rows) in iterator:
        if ordered:
            keys = [key for key, _ in rows]
            if len(keys) != len(set(keys)):
                raise ObjectiveError("Explicit within-unit ordering keys must be unique")
            rows.sort(key=lambda item: item[0])
        else:
            # Only a model declared exchangeable may take this deterministic order.
            rows.sort(key=lambda item: item[1])
        yield CompleteUnit(identity, [row for _, row in rows], weight)


class DataFrameObjective:
    """One shared registered objective, with canonical row or joint-unit reduction.

    Row weights and unit weights have distinct arguments. For weighted_mean the
    canonical row backend divides by row-weight sum, while the unit backend
    divides by unit-weight sum. The global L2 penalty is added only once.
    """

    def __init__(
        self,
        dataset,
        model_or_id,
        *,
        feature_columns,
        label_col,
        configuration=None,
        weight_col=None,
        unit_weight_col=None,
        group_col=None,
        order_cols=(),
        batch_size=256,
        reduction="sum",
        l2_strength=0.0,
    ):
        self.registered = resolved_model(model_or_id, configuration)
        self.descriptor = copy.deepcopy(self.registered.descriptor())
        self._closed, self.backend = False, None
        model = self.registered
        types = feature_bindings(dataset.schema, model, feature_columns)
        numeric_column(types, label_col, "label_col")
        feature_names = [feature_columns[name] for name in model.feature_names]
        if label_col in feature_names:
            raise ObjectiveError("The label column must not be used as a feature")
        if type(batch_size) is not int or not 1 <= batch_size <= 8192:
            raise ObjectiveError("batch_size must be within 1..8192")
        if isinstance(order_cols, (str, bytes)) or not isinstance(order_cols, (list, tuple)):
            raise ObjectiveError("order_cols must be an explicit sequence of column names")
        if len(set(order_cols)) != len(order_cols):
            raise ObjectiveError("Ordering column names must be unique")
        if model.factorization == "independent_rows":
            if group_col is not None or order_cols or unit_weight_col is not None:
                raise ObjectiveError("Row-additive fitting does not accept complete-unit settings")
            from pyspark.sql.functions import lit

            selected = [dataset[name] for name in feature_names] + [dataset[label_col]]
            if weight_col is not None:
                numeric_column(types, weight_col, "weight_col")
                if weight_col in [*feature_names, label_col]:
                    raise ObjectiveError("Row weight must be a separate column")
                selected.append(dataset[weight_col])
            else:
                selected.append(lit(1.0))
            guarded = TorchLoss(
                model.model_id,
                model.parameter_count,
                model.feature_count,
                partial(_row_guard, model=model, descriptor=self.descriptor),
            )
            self.backend = SparkObjective(
                dataset.select(*selected).rdd,
                guarded,
                batch_size=batch_size,
                reduction=reduction,
                l2_strength=l2_strength,
            )
        elif model.factorization == "complete_groups":
            if weight_col is not None:
                raise ObjectiveError("A joint unit uses unit_weight_col, not observation weights")
            if (
                not isinstance(group_col, str)
                or not COLUMN.fullmatch(group_col)
                or types.get(group_col) not in INTEGER | {"string"}
            ):
                raise ObjectiveError(
                    "Complete-group models require an explicit string/integer group_col"
                )
            if model.requires_order and not order_cols:
                raise ObjectiveError("This joint model requires explicit within-unit order_cols")
            for column in order_cols:
                if (
                    not isinstance(column, str)
                    or not COLUMN.fullmatch(column)
                    or types.get(column) not in NUMERIC | {"string"}
                ):
                    raise ObjectiveError(
                        "Ordering columns must be numeric or strings; "
                        "convert temporal keys explicitly"
                    )
            selected = [dataset[name] for name in feature_names] + [
                dataset[label_col],
                dataset[group_col],
            ]
            selected.extend(dataset[name] for name in order_cols)
            if unit_weight_col is not None:
                numeric_column(types, unit_weight_col, "unit_weight_col")
                if unit_weight_col in [*feature_names, label_col, group_col, *order_cols]:
                    raise ObjectiveError("Unit weight must be a separate constant-per-unit column")
                selected.append(dataset[unit_weight_col])
            pairs = dataset.select(*selected).rdd.map(
                partial(
                    _group_pair,
                    width=model.feature_count + 1,
                    order_count=len(order_cols),
                    weighted=unit_weight_col is not None,
                )
            )
            grouped = pairs.combineByKey(
                _new_group,
                partial(_append_group, limit=model.loss.max_unit_rows),
                partial(_merge_groups, limit=model.loss.max_unit_rows),
                numPartitions=pairs.getNumPartitions(),
            )
            units = grouped.mapPartitions(
                partial(
                    _complete_units,
                    model=model,
                    descriptor=self.descriptor,
                    ordered=bool(order_cols),
                )
            )
            guarded = TorchUnitLoss(
                model.model_id,
                model.parameter_count,
                model.feature_count,
                partial(_unit_guard, model=model, descriptor=self.descriptor),
                model.loss.max_unit_rows,
            )
            self.backend = SparkUnitObjective(
                units, guarded, reduction=reduction, l2_strength=l2_strength
            )
        else:
            raise ObjectiveError("Unsupported registered factorization")

    def evaluate(self, parameters):
        if self._closed:
            raise ObjectiveError("This DataFrame objective is closed")
        check_model_identity(self.registered, self.descriptor)
        return self.backend.evaluate(parameters)

    @property
    def row_count(self):
        return self.backend.row_count

    @property
    def unit_count(self):
        return getattr(self.backend, "unit_count", None)

    def close(self):
        if not self._closed:
            self._closed = True
            if self.backend is not None:
                self.backend.close()

    def __enter__(self):
        if self._closed:
            raise ObjectiveError("This DataFrame objective is closed")
        return self

    def __exit__(self, kind, error, traceback):
        try:
            self.close()
        except Exception as cleanup:
            if error is None:
                raise
            error.add_note(f"Derived objective cache cleanup failed: {cleanup}")
        return False


def prediction_schema(schema, model, feature_columns, prediction_col, target=None):
    types = feature_bindings(schema, model, feature_columns)
    chosen = model.default_prediction if target is None else target
    if chosen not in {entry.name for entry in model.prediction_targets}:
        raise ObjectiveError(
            "The registered model does not declare this response-free prediction target"
        )
    if (
        not isinstance(prediction_col, str)
        or not COLUMN.fullmatch(prediction_col)
        or prediction_col.casefold() in {name.casefold() for name in types}
    ):
        raise ObjectiveError("prediction_col must be a new simple column name")
    return chosen


def _predict_rows(iterator, *, model, descriptor, theta, indices, target, batch_size):
    check_model_identity(model, descriptor)
    batch = []

    def emit(rows):
        check_model_identity(model, descriptor)
        features = [tuple(row[index] for index in indices) for row in rows]
        values = predict_batch(model, theta, features, target=target)
        for row, value in zip(rows, values, strict=True):
            yield (*tuple(row), value)

    for row in iterator:
        batch.append(row)
        if len(batch) == batch_size:
            yield from emit(batch)
            batch = []
    if batch:
        yield from emit(batch)


def predict_dataframe(
    dataset,
    model_or_id,
    parameters,
    *,
    feature_columns,
    configuration=None,
    prediction_col="prediction",
    target=None,
    batch_size=256,
    expected_descriptor=None,
):
    model = resolved_model(model_or_id, configuration)
    descriptor = model.descriptor()
    if expected_descriptor is not None and descriptor != expected_descriptor:
        raise ObjectiveError(
            "Saved/fitted model identity differs from the current registered source"
        )
    theta = finite_vector(parameters)
    if len(theta) != model.parameter_count:
        raise ObjectiveError("Prediction parameter layout differs from the registered model")
    if type(batch_size) is not int or not 1 <= batch_size <= 8192:
        raise ObjectiveError("Prediction batch_size must be within 1..8192")
    chosen = prediction_schema(dataset.schema, model, feature_columns, prediction_col, target)
    indices = [dataset.columns.index(feature_columns[name]) for name in model.feature_names]
    from pyspark.sql.types import DoubleType, StructField, StructType

    output_schema = StructType(
        [
            *dataset.schema.fields,
            StructField(
                prediction_col,
                DoubleType(),
                False,
                {
                    "modelId": model.model_id,
                    "target": chosen,
                    "fingerprint": descriptor["fingerprint"],
                },
            ),
        ]
    )
    output = dataset.rdd.mapPartitions(
        partial(
            _predict_rows,
            model=model,
            descriptor=descriptor,
            theta=theta,
            indices=indices,
            target=chosen,
            batch_size=batch_size,
        )
    )
    return dataset.sparkSession.createDataFrame(output, schema=output_schema)


def _fit_independent(
    iterator,
    *,
    model,
    descriptor,
    initial,
    bounds,
    ordered,
    batch_size,
    reduction,
    l2_strength,
    max_iterations,
    tolerance,
):
    from .contracts import combine_summaries
    from .optimization import minimize_lbfgsb
    from .torch_backend import evaluate_partition

    check_model_identity(model, descriptor)
    guarded = TorchLoss(
        model.model_id,
        model.parameter_count,
        model.feature_count,
        partial(_row_guard, model=model, descriptor=descriptor),
    )
    for identity, (_, keyed_rows) in iterator:
        if ordered:
            keys = [key for key, _ in keyed_rows]
            if len(set(keys)) != len(keys):
                raise ObjectiveError("Explicit within-unit ordering keys must be unique")
            keyed_rows.sort(key=lambda item: item[0])
        else:
            keyed_rows.sort(key=lambda item: item[1])
        rows = [row for _, row in keyed_rows]

        def evaluate(parameters, unit_rows=rows):
            summary = evaluate_partition(0, unit_rows, parameters, guarded, batch_size=batch_size)
            return combine_summaries(
                [summary],
                parameters=parameters,
                model_id=model.model_id,
                expected_partitions=1,
                expected_rows=len(unit_rows),
                reduction=reduction,
                l2_strength=l2_strength,
            )

        fit = minimize_lbfgsb(
            evaluate,
            initial,
            bounds=bounds,
            max_iterations=max_iterations,
            gradient_tolerance=tolerance,
            function_tolerance=1e-12,
        )
        if not fit.converged or fit.projected_gradient_inf_norm > tolerance:
            raise ObjectiveError(f"Independent fit failed for {identity}: {fit.message}")
        yield (
            json.loads(identity[len("group:") :]),
            list(model.parameter_names),
            list(fit.parameters),
            fit.evaluation.value,
            len(rows),
            fit.evaluation.weight_sum,
            fit.gradient_inf_norm,
            fit.projected_gradient_inf_norm,
            fit.objective_calls,
            list(fit.active_bounds),
            descriptor["fingerprint"],
        )


def fit_independent_groups(
    dataset,
    model_or_id,
    initial,
    *,
    feature_columns,
    label_col,
    group_col,
    configuration=None,
    weight_col=None,
    order_cols=(),
    bounds=None,
    max_group_rows=4096,
    batch_size=256,
    reduction="sum",
    l2_strength=0.0,
    max_iterations=100,
    tolerance=1e-6,
):
    """Return distinct per-group row-model fits as a DataFrame, never their average.

    Each executor needs the optional SciPy and Torch dependencies. Complete-unit
    random-effect models are deliberately excluded: one group's variance components
    generally do not identify the shared hierarchical model.
    """
    model = resolved_model(model_or_id, configuration)
    if model.factorization != "independent_rows":
        raise ObjectiveError("Independent group fits currently support row-additive models only")
    theta = finite_vector(initial)
    if len(theta) != model.parameter_count:
        raise ObjectiveError("Independent initial parameter layout differs")
    if type(max_group_rows) is not int or not 2 <= max_group_rows <= 4096:
        raise ObjectiveError("Independent group row bound must be within 2..4096")
    if type(batch_size) is not int or not 1 <= batch_size <= 8192:
        raise ObjectiveError("Invalid row batch size")
    if type(max_iterations) is not int or not 1 <= max_iterations <= 1000:
        raise ObjectiveError("Invalid iteration budget")
    tolerance = finite_number(tolerance, "fit tolerance")
    if tolerance <= 0:
        raise ObjectiveError("Fit tolerance must be positive")
    types = feature_bindings(dataset.schema, model, feature_columns)
    numeric_column(types, label_col, "label_col")
    feature_names = [feature_columns[name] for name in model.feature_names]
    if label_col in feature_names:
        raise ObjectiveError("The label column must not be used as a feature")
    if (
        not isinstance(group_col, str)
        or not COLUMN.fullmatch(group_col)
        or types.get(group_col) not in INTEGER | {"string"}
    ):
        raise ObjectiveError("An explicit string/integer group_col is required")
    if (
        isinstance(order_cols, (str, bytes))
        or not isinstance(order_cols, (list, tuple))
        or len(set(order_cols)) != len(order_cols)
    ):
        raise ObjectiveError("order_cols must be a distinct column sequence")
    for name in order_cols:
        if (
            not isinstance(name, str)
            or not COLUMN.fullmatch(name)
            or types.get(name) not in NUMERIC | {"string"}
        ):
            raise ObjectiveError("Invalid within-group ordering column")
    from pyspark.sql.functions import lit
    from pyspark.sql.types import (
        ArrayType,
        DoubleType,
        IntegerType,
        LongType,
        StringType,
        StructField,
        StructType,
    )

    selected = [dataset[name] for name in feature_names] + [dataset[label_col]]
    if weight_col is not None:
        numeric_column(types, weight_col, "weight_col")
        if weight_col in [*feature_names, label_col]:
            raise ObjectiveError("Row weight must be separate")
        selected.append(dataset[weight_col])
    else:
        selected.append(lit(1.0))
    selected.extend([dataset[group_col], *[dataset[name] for name in order_cols]])
    pairs = dataset.select(*selected).rdd.map(
        partial(
            _group_pair, width=model.feature_count + 2, order_count=len(order_cols), weighted=False
        )
    )
    grouped = pairs.combineByKey(
        _new_group,
        partial(_append_group, limit=max_group_rows),
        partial(_merge_groups, limit=max_group_rows),
        numPartitions=pairs.getNumPartitions(),
    )
    descriptor = model.descriptor()
    output = grouped.mapPartitions(
        partial(
            _fit_independent,
            model=model,
            descriptor=descriptor,
            initial=theta,
            bounds=bounds,
            ordered=bool(order_cols),
            batch_size=batch_size,
            reduction=reduction,
            l2_strength=l2_strength,
            max_iterations=max_iterations,
            tolerance=tolerance,
        )
    )
    schema = StructType(
        [
            StructField("group_id", dataset.schema[group_col].dataType, False),
            StructField("parameter_names", ArrayType(StringType(), False), False),
            StructField("parameters", ArrayType(DoubleType(), False), False),
            StructField("objective", DoubleType(), False),
            StructField("row_count", LongType(), False),
            StructField("weight_sum", DoubleType(), False),
            StructField("gradient_inf_norm", DoubleType(), False),
            StructField("projected_gradient_inf_norm", DoubleType(), False),
            StructField("objective_calls", IntegerType(), False),
            StructField("active_bounds", ArrayType(IntegerType(), False), False),
            StructField("model_fingerprint", StringType(), False),
        ]
    )
    return dataset.sparkSession.createDataFrame(output, schema=schema)
