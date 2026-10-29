"""R-free float64 differentiation for bounded complete independent units."""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .contracts import (
    DIGEST,
    MAX_PARAMETERS,
    MODEL_ID,
    CompensatedSum,
    ObjectiveError,
    PartitionSummary,
    finite_number,
    finite_vector,
    parameter_digest,
)

MAX_UNIT_ROWS = 4096


@dataclass(frozen=True)
class CompleteUnit:
    """One complete joint-likelihood unit, with a single nonnegative unit weight.

    Each row contains its ordered numeric features followed by one scalar target.
    Unit weighting is not observation weighting. A unit must never be split to
    satisfy a row batch limit, because doing so generally changes its likelihood.
    """

    unit_id: str
    rows: Sequence[Sequence[float]]
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.unit_id, str) or not 1 <= len(self.unit_id) <= 128:
            raise ObjectiveError("complete units need a nonempty ID of at most 128 characters")
        if not isinstance(self.rows, (list, tuple)) or not 1 <= len(self.rows) <= MAX_UNIT_ROWS:
            raise ObjectiveError("complete units require 1..4096 explicitly bounded rows")
        converted = []
        for row in self.rows:
            if isinstance(row, (str, bytes)) or not isinstance(row, Sequence):
                raise ObjectiveError("unit rows must be numeric sequences")
            if not 1 <= len(row) <= 257:
                raise ObjectiveError("unit rows require at most 256 features and one target")
            converted.append(tuple(finite_number(value, "unit row value") for value in row))
        weight = finite_number(self.weight, "unit weight")
        if weight < 0:
            raise ObjectiveError("unit weight must be nonnegative")
        object.__setattr__(self, "rows", tuple(converted))
        object.__setattr__(self, "weight", weight)


def unit_digest(unit: CompleteUnit) -> str:
    """Bind unit identity, order, rows and weight to exact normalized float64 values."""
    identifier = unit.unit_id.encode("utf-8")
    digest = hashlib.sha256(struct.pack(">I", len(identifier)) + identifier)
    digest.update(struct.pack(">dI", unit.weight, len(unit.rows)))
    for row in unit.rows:
        digest.update(struct.pack(">I", len(row)))
        for value in row:
            digest.update(struct.pack(">d", value))
    return digest.hexdigest()


@dataclass(frozen=True)
class TorchUnitLoss:
    """A scalar joint loss over one complete independent unit, never a row loss."""

    model_id: str
    parameter_count: int
    feature_count: int
    per_unit: Callable[[Any, Any, Any], Any]
    max_unit_rows: int = 256

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not MODEL_ID.fullmatch(self.model_id):
            raise ObjectiveError("invalid unit model identity")
        if type(self.parameter_count) is not int or not 1 <= self.parameter_count <= MAX_PARAMETERS:
            raise ObjectiveError("invalid unit parameter count")
        if type(self.feature_count) is not int or not 0 <= self.feature_count <= 256:
            raise ObjectiveError("unit feature count must be within 0..256")
        if type(self.max_unit_rows) is not int or not 1 <= self.max_unit_rows <= MAX_UNIT_ROWS:
            raise ObjectiveError("model unit row bound must be within 1..4096")
        if not callable(self.per_unit):
            raise ObjectiveError("a complete-unit model needs a scalar Torch callable")


def validate_unit(unit: CompleteUnit, model: TorchUnitLoss) -> CompleteUnit:
    if not isinstance(unit, CompleteUnit):
        raise ObjectiveError("provide explicit CompleteUnit objects")
    if len(unit.rows) > model.max_unit_rows:
        raise ObjectiveError("complete group exceeds the model bound; it cannot be row-batched")
    if any(len(row) != model.feature_count + 1 for row in unit.rows):
        raise ObjectiveError(
            "unit rows need declared features followed by one target, no row weight"
        )
    return unit


@dataclass(frozen=True)
class UnitPartitionSummary:
    summary: PartitionSummary
    unit_count: int
    membership_digest: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.summary, PartitionSummary)
            or type(self.unit_count) is not int
            or not 0 <= self.unit_count <= self.summary.row_count
            or (self.unit_count == 0 and self.summary.row_count != 0)
            or not isinstance(self.membership_digest, str)
            or not DIGEST.fullmatch(self.membership_digest)
        ):
            raise ObjectiveError("invalid complete-unit partition evidence")


def summarize_units(
    index: int, units: Iterable[CompleteUnit], model: TorchUnitLoss
) -> tuple[int, int, int, str]:
    count = rows = digest = 0
    for unit in units:
        validate_unit(unit, model)
        count += 1
        rows += len(unit.rows)
        digest = (digest + int(unit_digest(unit), 16)) % (1 << 256)
    return index, count, rows, f"{digest:064x}"


def evaluate_units(
    partition_id: int,
    units: Iterable[CompleteUnit],
    parameters: Sequence[float],
    model: TorchUnitLoss,
) -> UnitPartitionSummary:
    """Differentiate one bounded unit at a time and return only numeric summaries."""
    if not isinstance(model, TorchUnitLoss):
        raise ObjectiveError("scalar joint losses require TorchUnitLoss, not the row kernel")
    theta_values = finite_vector(parameters)
    if len(theta_values) != model.parameter_count:
        raise ObjectiveError("unit model and parameter dimensions disagree")
    try:
        torch = import_module("torch")
    except ImportError:
        raise ObjectiveError(
            "prepare the optional CPU Torch environment before execution"
        ) from None
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    total, weights = CompensatedSum(), CompensatedSum()
    gradients = [CompensatedSum() for _ in theta_values]
    unit_count = row_count = digest = 0
    try:
        with torch.enable_grad():
            theta = torch.tensor(theta_values, dtype=torch.float64, requires_grad=True)
            for unit in units:
                validate_unit(unit, model)
                tensor = torch.tensor(unit.rows, dtype=torch.float64)
                features, targets = tensor[:, : model.feature_count], tensor[:, -1]
                loss = model.per_unit(theta, features, targets)
                if (
                    not isinstance(loss, torch.Tensor)
                    or loss.ndim != 0
                    or loss.dtype != torch.float64
                    or loss.device.type != "cpu"
                ):
                    raise ObjectiveError("unit loss must be one scalar CPU float64 tensor")
                if not bool(torch.isfinite(loss)) or not loss.requires_grad:
                    raise ObjectiveError(
                        "unit loss must be finite and connected to the parameter graph"
                    )
                weighted = loss * unit.weight
                try:
                    gradient = torch.autograd.grad(weighted, theta, create_graph=False)[0]
                except RuntimeError as exc:
                    raise ObjectiveError("Torch could not differentiate the complete unit") from exc
                if not bool(torch.isfinite(gradient).all()):
                    raise ObjectiveError("nonfinite complete-unit gradient")
                total.add(float(weighted.detach()))
                weights.add(unit.weight)
                for accumulator, value in zip(gradients, gradient.detach().tolist(), strict=True):
                    accumulator.add(value)
                unit_count += 1
                row_count += len(unit.rows)
                digest = (digest + int(unit_digest(unit), 16)) % (1 << 256)
    finally:
        torch.set_num_threads(previous_threads)
    summary = PartitionSummary(
        partition_id,
        parameter_digest(theta_values),
        model.model_id,
        row_count,
        weights.value(),
        total.value(),
        tuple(value.value() for value in gradients),
    )
    return UnitPartitionSummary(summary, unit_count, f"{digest:064x}")
