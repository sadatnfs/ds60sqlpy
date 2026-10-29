"""Spark adapter for complete joint likelihoods with explicit unit-weight reduction."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from importlib import import_module
from typing import Any, Literal

from .contracts import (
    MAX_PARTITIONS,
    ObjectiveError,
    ObjectiveEvaluation,
    combine_summaries,
    finite_number,
    finite_vector,
)
from .unit_backend import (
    TorchUnitLoss,
    evaluate_units,
    summarize_units,
    validate_unit,
)


@dataclass(frozen=True)
class UnitObjectiveEvaluation(ObjectiveEvaluation):
    unit_count: int


class SparkUnitObjective:
    """Own only a derived cache; retain complete units and collect bounded metadata.

    The sum is over weighted joint unit likelihoods. weighted_mean divides by
    total unit weight, never row count. Unit IDs must be globally unique: two
    fragments of one group cannot silently masquerade as independent units.
    """

    def __init__(
        self,
        units: Any,
        model: TorchUnitLoss,
        *,
        reduction: Literal["sum", "weighted_mean"] = "sum",
        l2_strength: float = 0.0,
        persist: bool = True,
    ) -> None:
        if not isinstance(model, TorchUnitLoss):
            raise ObjectiveError("complete joint likelihoods require TorchUnitLoss")
        count = units.getNumPartitions()
        if type(count) is not int or not 1 <= count <= MAX_PARTITIONS:
            raise ObjectiveError("partition count exceeds bounded driver-summary capacity")
        if reduction not in {"sum", "weighted_mean"} or type(persist) is not bool:
            raise ObjectiveError("declare sum or unit-weighted mean and a boolean cache policy")
        strength = finite_number(l2_strength, "L2 strength")
        if strength < 0:
            raise ObjectiveError("L2 strength must be nonnegative")
        self._closed, self._persisted = False, False
        self.model, self.reduction, self.l2_strength = model, reduction, strength
        self.partition_count = count
        self.evaluation_count = 0
        self.last_evaluation: UnitObjectiveEvaluation | None = None
        self._units = units.map(lambda unit: validate_unit(unit, model))
        try:
            if persist:
                spark = import_module("pyspark")
                self._units.persist(spark.StorageLevel.MEMORY_AND_DISK)
                self._persisted = True
            metadata = self._units.mapPartitionsWithIndex(
                lambda index, values: iter([summarize_units(index, values, model)])
            ).collect()
            if len(metadata) != count or {row[0] for row in metadata} != set(range(count)):
                raise ObjectiveError(
                    "unit materialization returned inconsistent partition identities"
                )
            self._metadata = {row[0]: row[1:] for row in metadata}
            self.unit_count = sum(row[1] for row in metadata)
            self.row_count = sum(row[2] for row in metadata)
            if self.unit_count == 0:
                raise ObjectiveError("cannot fit an empty collection of complete units")
            duplicate = (
                self._units.map(lambda unit: (unit.unit_id, 1))
                .reduceByKey(lambda left, right: left + right)
                .filter(lambda pair: pair[1] != 1)
                .take(1)
            )
            if duplicate:
                raise ObjectiveError("duplicate unit ID: a complete group may not span units")
        except BaseException:
            self.close()
            raise

    def evaluate(self, parameters: Sequence[float]) -> UnitObjectiveEvaluation:
        if self._closed:
            raise ObjectiveError("this complete-unit objective has been closed")
        theta = finite_vector(parameters)
        if len(theta) != self.model.parameter_count:
            raise ObjectiveError("unit model parameter dimension mismatch")
        model = self.model
        summaries = self._units.mapPartitionsWithIndex(
            lambda index, units: iter([evaluate_units(index, units, theta, model)])
        ).collect()
        for item in summaries:
            expected = self._metadata.get(item.summary.partition_id)
            if expected != (item.unit_count, item.summary.row_count, item.membership_digest):
                raise ObjectiveError("complete units or numeric data changed after materialization")
        combined = combine_summaries(
            [item.summary for item in summaries],
            parameters=theta,
            model_id=model.model_id,
            expected_partitions=self.partition_count,
            expected_rows=self.row_count,
            reduction=self.reduction,
            l2_strength=self.l2_strength,
        )
        result = UnitObjectiveEvaluation(**asdict(combined), unit_count=self.unit_count)
        self.evaluation_count += 1
        self.last_evaluation = result
        return result

    def close(self) -> None:
        if not self._closed:
            if self._persisted:
                self._units.unpersist(blocking=True)
            self._closed = True

    def __enter__(self) -> SparkUnitObjective:
        if self._closed:
            raise ObjectiveError("this complete-unit objective has been closed")
        return self

    def __exit__(self, *unused: Any) -> None:
        self.close()
