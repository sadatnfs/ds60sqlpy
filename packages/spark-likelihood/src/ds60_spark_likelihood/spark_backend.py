"""Public Spark RDD adapter for additive low-dimensional Torch likelihoods.

Spark schedules data partitions. Torch differentiates each local batch, and a
driver optimizer consumes the summed objective and gradient. This is not a
differentiable Spark SQL plan, parameter-server training or a GPU scheduler.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from importlib import import_module
from typing import Any

from .contracts import (
    MAX_PARTITIONS,
    ObjectiveError,
    ObjectiveEvaluation,
    Reduction,
    combine_summaries,
    finite_number,
    finite_vector,
)
from .torch_backend import TorchLoss, evaluate_partition

COLUMN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
NUMERIC_TYPES = {"byte", "short", "integer", "long", "float", "double"}


class SparkObjective:
    """Own a derived RDD cache and return only bounded partition summaries.

    Rows contain model features, then target, then a nonnegative weight.
    Call close(), or use a context manager, to release only this object's cache.
    Input must be an immutable snapshot. A cache is neither a transaction nor a
    durable snapshot: lost partitions may be recomputed from their lineage.
    """

    def __init__(
        self,
        rows: Any,
        model: TorchLoss,
        *,
        batch_size: int = 256,
        reduction: Reduction = "sum",
        l2_strength: float = 0.0,
        persist: bool = True,
    ) -> None:
        if not isinstance(model, TorchLoss):
            raise ObjectiveError("provide an explicit TorchLoss")
        if type(batch_size) is not int or not 1 <= batch_size <= 8192:
            raise ObjectiveError("batch size must be within 1..8192")
        if reduction not in {"sum", "weighted_mean"}:
            raise ObjectiveError("reduction must be sum or weighted_mean")
        strength = finite_number(l2_strength, "L2 strength")
        if strength < 0 or type(persist) is not bool:
            raise ObjectiveError("L2 strength must be nonnegative and persist must be boolean")
        count = rows.getNumPartitions()
        if type(count) is not int or not 1 <= count <= MAX_PARTITIONS:
            raise ObjectiveError("partition count exceeds the bounded driver-summary contract")
        # A fresh transformation prevents unpersisting a caller-owned cache.
        self._rows = rows.map(lambda row: tuple(row))
        self._persisted = False
        self._closed = False
        self.model = model
        self.batch_size = batch_size
        self.reduction = reduction
        self.l2_strength = strength
        self.partition_count = count
        self.evaluation_count = 0
        self.last_evaluation: ObjectiveEvaluation | None = None
        try:
            if persist:
                spark = import_module("pyspark")
                self._rows.persist(spark.StorageLevel.MEMORY_AND_DISK)
                self._persisted = True
            counts = self._rows.mapPartitionsWithIndex(
                lambda index, items: iter([(index, sum(1 for _ in items))])
            ).collect()
            if len(counts) != count or {index for index, _ in counts} != set(range(count)):
                raise ObjectiveError("materialization returned inconsistent partition identities")
            self.partition_rows = tuple(value for _, value in sorted(counts))
            if any(type(value) is not int or value < 0 for value in self.partition_rows):
                raise ObjectiveError("materialization returned invalid partition counts")
            self.row_count = sum(self.partition_rows)
            if self.row_count == 0:
                raise ObjectiveError("cannot fit an empty dataset")
        except BaseException:
            self.close()
            raise

    @classmethod
    def from_dataframe(
        cls,
        frame: Any,
        model: TorchLoss,
        *,
        feature_columns: Sequence[str],
        target_column: str,
        weight_column: str | None = None,
        **options: Any,
    ) -> SparkObjective:
        """Select existing primitive numeric columns without silent casting.

        Null, nonfinite and negative-weight values fail during local evaluation.
        Decimal, boolean, array and string columns must be deliberately converted
        and validated by the learner before this boundary.
        """
        if isinstance(feature_columns, (str, bytes)):
            raise ObjectiveError("feature_columns must be a sequence of column names")
        names = list(feature_columns) + [target_column]
        if weight_column is not None:
            names.append(weight_column)
        if len(feature_columns) != model.feature_count:
            raise ObjectiveError("selected features disagree with the model shape")
        if any(not isinstance(name, str) or not COLUMN.fullmatch(name) for name in names):
            raise ObjectiveError("use simple explicit column names")
        if len(set(names)) != len(names):
            raise ObjectiveError("feature, target and weight columns must be distinct")
        fields = frame.schema.fields
        if len({field.name for field in fields}) != len(fields):
            raise ObjectiveError("DataFrame contains ambiguous duplicate column names")
        schema = {field.name: field.dataType.typeName() for field in fields}
        for name in names:
            if schema.get(name) not in NUMERIC_TYPES:
                raise ObjectiveError(f"{name} must be an existing primitive numeric column")
        selected = [frame[name] for name in names]
        if weight_column is None:
            functions = import_module("pyspark.sql.functions")
            selected.append(functions.lit(1.0))
        return cls(frame.select(*selected).rdd, model, **options)

    def evaluate(self, parameters: Sequence[float]) -> ObjectiveEvaluation:
        if self._closed:
            raise ObjectiveError("this objective has been closed")
        theta = finite_vector(parameters)
        if len(theta) != self.model.parameter_count:
            raise ObjectiveError("model and parameter dimensions disagree")
        # Capture no SparkContext or self in the executor closure.
        model, batch_size = self.model, self.batch_size

        def evaluate(index: int, items: Any) -> Any:
            yield evaluate_partition(index, items, theta, model, batch_size=batch_size)

        summaries = self._rows.mapPartitionsWithIndex(evaluate).collect()
        for item in summaries:
            if (
                not 0 <= item.partition_id < self.partition_count
                or item.row_count != self.partition_rows[item.partition_id]
            ):
                raise ObjectiveError("input partition counts changed after materialization")
        result = combine_summaries(
            summaries,
            parameters=theta,
            model_id=model.model_id,
            expected_partitions=self.partition_count,
            expected_rows=self.row_count,
            reduction=self.reduction,
            l2_strength=self.l2_strength,
        )
        self.evaluation_count += 1
        self.last_evaluation = result
        return result

    def close(self) -> None:
        if not self._closed:
            if self._persisted:
                self._rows.unpersist(blocking=True)
            self._closed = True

    def __enter__(self) -> SparkObjective:
        if self._closed:
            raise ObjectiveError("this objective has been closed")
        return self

    def __exit__(self, *unused: Any) -> None:
        self.close()
