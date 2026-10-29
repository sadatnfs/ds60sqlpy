"""Validated constant-size partition results and global objective reduction."""

from __future__ import annotations

import hashlib
import math
import re
import struct
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Literal

Reduction = Literal["sum", "weighted_mean"]
MAX_PARAMETERS = 64
MAX_PARTITIONS = 4096
MODEL_ID = re.compile(r"[a-z][a-z0-9_-]{0,63}\Z")
DIGEST = re.compile(r"[a-f0-9]{64}\Z")


class ObjectiveError(ValueError):
    """The proposed objective or partition evidence violates its contract."""


def finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ObjectiveError(f"{name} must be a real number, not a boolean or coercible string")
    try:
        number = float(value)
    except OverflowError:
        raise ObjectiveError(f"{name} exceeds finite float64 range") from None
    if isinstance(value, Integral) and (not math.isfinite(number) or int(number) != int(value)):
        raise ObjectiveError(f"{name} is an integer not exactly representable as float64")
    if not math.isfinite(number):
        raise ObjectiveError(f"{name} must be finite")
    return number


def finite_vector(values: Sequence[float], name: str = "parameters") -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or not 1 <= len(values) <= MAX_PARAMETERS:
        raise ObjectiveError(f"{name} needs 1..{MAX_PARAMETERS} entries")
    return tuple(finite_number(value, name) for value in values)


def parameter_digest(parameters: Sequence[float]) -> str:
    """Bind results to exact float64 parameter bytes, including vector length."""
    values = finite_vector(parameters)
    raw = struct.pack(">I", len(values)) + b"".join(struct.pack(">d", value) for value in values)
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class PartitionSummary:
    partition_id: int
    parameter_digest: str
    model_id: str
    row_count: int
    weight_sum: float
    value: float
    gradient: tuple[float, ...]

    def __post_init__(self) -> None:
        if type(self.partition_id) is not int or not 0 <= self.partition_id < MAX_PARTITIONS:
            raise ObjectiveError("partition_id is outside the bounded driver-summary contract")
        if not isinstance(self.parameter_digest, str) or not DIGEST.fullmatch(
            self.parameter_digest
        ):
            raise ObjectiveError("partition summary has an invalid parameter digest")
        if not isinstance(self.model_id, str) or not MODEL_ID.fullmatch(self.model_id):
            raise ObjectiveError("partition summary has an invalid model identity")
        if type(self.row_count) is not int or self.row_count < 0:
            raise ObjectiveError("row_count must be a nonnegative integer")
        weight_sum = finite_number(self.weight_sum, "weight_sum")
        value = finite_number(self.value, "partition value")
        gradient = finite_vector(self.gradient, "partition gradient")
        if weight_sum < 0:
            raise ObjectiveError("partition weights cannot sum to a negative value")
        if (self.row_count == 0 or weight_sum == 0) and (
            weight_sum != 0 or value != 0 or any(item != 0 for item in gradient)
        ):
            raise ObjectiveError("empty or zero-weight partitions must contribute exactly zero")
        object.__setattr__(self, "weight_sum", weight_sum)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "gradient", gradient)


@dataclass(frozen=True)
class ObjectiveEvaluation:
    value: float
    gradient: tuple[float, ...]
    row_count: int
    weight_sum: float
    partition_count: int
    parameter_digest: str
    model_id: str
    reduction: Reduction
    penalty_value: float


def combine_summaries(
    summaries: Iterable[PartitionSummary],
    *,
    parameters: Sequence[float],
    model_id: str,
    expected_partitions: int,
    expected_rows: int,
    reduction: Reduction = "sum",
    l2_strength: float = 0.0,
) -> ObjectiveEvaluation:
    """Sum once, optionally divide by global weight, then add one L2 penalty.

    The penalty is lambda/2 * ||theta||^2 AFTER the selected data reduction.
    Changing sum to weighted_mean therefore changes the lambda interpretation.
    This function does not average independently fitted coefficients.
    """
    theta = finite_vector(parameters)
    digest = parameter_digest(theta)
    if not isinstance(model_id, str) or not MODEL_ID.fullmatch(model_id):
        raise ObjectiveError("model_id must be a bounded stable identifier")
    if type(expected_partitions) is not int or not 1 <= expected_partitions <= MAX_PARTITIONS:
        raise ObjectiveError("expected_partitions must be within the bounded driver contract")
    if type(expected_rows) is not int or expected_rows < 1:
        raise ObjectiveError("a global fit needs a positive expected row count")
    if reduction not in {"sum", "weighted_mean"}:
        raise ObjectiveError("reduction must be sum or weighted_mean")
    strength = finite_number(l2_strength, "L2 strength")
    if strength < 0:
        raise ObjectiveError("L2 strength cannot be negative")
    records: dict[int, PartitionSummary] = {}
    for summary in summaries:
        if not isinstance(summary, PartitionSummary):
            raise ObjectiveError("use validated PartitionSummary values")
        if summary.partition_id in records:
            raise ObjectiveError("duplicate partition result would double-count observations")
        if summary.partition_id >= expected_partitions:
            raise ObjectiveError("unexpected partition identity")
        if summary.parameter_digest != digest or summary.model_id != model_id:
            raise ObjectiveError("stale parameters or a different model in partition result")
        if len(summary.gradient) != len(theta):
            raise ObjectiveError("gradient dimension differs from the parameter vector")
        records[summary.partition_id] = summary
    if set(records) != set(range(expected_partitions)):
        raise ObjectiveError("missing partition result, including any empty partition")
    ordered = [records[key] for key in range(expected_partitions)]
    row_count = sum(item.row_count for item in ordered)
    if row_count != expected_rows:
        raise ObjectiveError("observed row count differs from the materialized input")
    try:
        weight_sum = math.fsum(item.weight_sum for item in ordered)
        if not math.isfinite(weight_sum) or weight_sum <= 0:
            raise ObjectiveError("global fit needs positive finite total weight")
        divisor = weight_sum if reduction == "weighted_mean" else 1.0
        data_value = math.fsum(item.value for item in ordered) / divisor
        data_gradient = tuple(
            math.fsum(item.gradient[column] for item in ordered) / divisor
            for column in range(len(theta))
        )
        penalty = strength * 0.5 * math.fsum(value * value for value in theta) if strength else 0.0
        value = finite_number(data_value + penalty, "combined objective")
        gradient = finite_vector(
            tuple(g + strength * t for g, t in zip(data_gradient, theta, strict=True)),
            "combined gradient",
        )
    except (OverflowError, FloatingPointError):
        raise ObjectiveError("objective accumulation overflowed float64") from None
    return ObjectiveEvaluation(
        value, gradient, row_count, weight_sum, len(ordered), digest, model_id, reduction, penalty
    )


class CompensatedSum:
    """Neumaier accumulation with constant memory and explicit overflow refusal."""

    def __init__(self) -> None:
        self.total = 0.0
        self.correction = 0.0

    def add(self, value: float) -> None:
        value = finite_number(value, "summand")
        combined = self.total + value
        if not math.isfinite(combined):
            raise ObjectiveError("float64 accumulation overflow")
        if abs(self.total) >= abs(value):
            self.correction += (self.total - combined) + value
        else:
            self.correction += (value - combined) + self.total
        self.total = combined
        if not math.isfinite(self.correction):
            raise ObjectiveError("float64 correction overflow")

    def value(self) -> float:
        return finite_number(self.total + self.correction, "compensated result")
