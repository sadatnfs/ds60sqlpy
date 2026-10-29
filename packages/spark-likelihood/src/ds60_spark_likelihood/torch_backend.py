"""Streaming CPU float64 Torch differentiation inside one Spark partition."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from .contracts import (
    MAX_PARAMETERS,
    MODEL_ID,
    CompensatedSum,
    ObjectiveError,
    PartitionSummary,
    finite_number,
    finite_vector,
    parameter_digest,
)


@dataclass(frozen=True)
class TorchLoss:
    """A deterministic per-observation loss; it must not depend on batch composition."""

    model_id: str
    parameter_count: int
    feature_count: int
    per_observation: Callable[[Any, Any, Any], Any]

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not MODEL_ID.fullmatch(self.model_id):
            raise ObjectiveError("invalid Torch model identity")
        if type(self.parameter_count) is not int or not 1 <= self.parameter_count <= MAX_PARAMETERS:
            raise ObjectiveError("invalid Torch parameter count")
        if type(self.feature_count) is not int or not 0 <= self.feature_count <= 256:
            raise ObjectiveError("feature count must be within 0..256")
        if not callable(self.per_observation):
            raise ObjectiveError("a Torch model needs a per-observation callable")


def _batches(
    rows: Iterable[Sequence[float]], feature_count: int, batch_size: int
) -> Iterator[list[tuple[float, ...]]]:
    batch: list[tuple[float, ...]] = []
    for row in rows:
        if isinstance(row, (str, bytes)) or len(row) != feature_count + 2:
            raise ObjectiveError(
                "each row needs features followed by target and nonnegative weight"
            )
        values = tuple(finite_number(value, "input row value") for value in row)
        if values[-1] < 0:
            raise ObjectiveError("negative observation weight")
        batch.append(values)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def evaluate_partition(
    partition_id: int,
    rows: Iterable[Sequence[float]],
    parameters: Sequence[float],
    model: TorchLoss,
    *,
    batch_size: int = 256,
) -> PartitionSummary:
    """Return one summary, even for an empty partition; never retain a full dataset.

    Each backward pass consumes one bounded batch graph. No global penalty is
    applied here. Spark must run this once per successful partition result;
    driver combination verifies the resulting identities and counts.
    """
    if not isinstance(model, TorchLoss):
        raise ObjectiveError(
            "row evaluation requires TorchLoss; use evaluate_units for joint units"
        )
    theta_values = finite_vector(parameters)
    if len(theta_values) != model.parameter_count:
        raise ObjectiveError("model and parameter dimensions disagree")
    if type(batch_size) is not int or not 1 <= batch_size <= 8192:
        raise ObjectiveError("batch size must be within 1..8192")
    try:
        torch = import_module("torch")
    except ImportError:
        raise ObjectiveError(
            "prepare the explicit Torch CPU environment before execution"
        ) from None
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    total = CompensatedSum()
    weights = CompensatedSum()
    gradients = [CompensatedSum() for _ in theta_values]
    count = 0
    try:
        with torch.enable_grad():
            theta = torch.tensor(theta_values, dtype=torch.float64, requires_grad=True)
            for batch in _batches(rows, model.feature_count, batch_size):
                tensor = torch.tensor(batch, dtype=torch.float64)
                features = tensor[:, : model.feature_count]
                targets = tensor[:, model.feature_count]
                batch_weights = tensor[:, -1]
                losses = model.per_observation(theta, features, targets)
                if (
                    not isinstance(losses, torch.Tensor)
                    or losses.shape != targets.shape
                    or losses.dtype != torch.float64
                    or losses.device.type != "cpu"
                ):
                    raise ObjectiveError("loss must return one CPU float64 value per observation")
                if not bool(torch.isfinite(losses).all()):
                    raise ObjectiveError("nonfinite model loss at the proposed parameters")
                loss = (losses * batch_weights).sum()
                if not loss.requires_grad:
                    raise ObjectiveError("model loss is detached from the parameter graph")
                try:
                    gradient = torch.autograd.grad(loss, theta, create_graph=False)[0]
                except RuntimeError as error:
                    raise ObjectiveError("Torch could not differentiate the model loss") from error
                if not bool(torch.isfinite(gradient).all()):
                    raise ObjectiveError("nonfinite model gradient")
                total.add(float(loss.detach().item()))
                weights.add(float(batch_weights.sum().item()))
                for accumulator, value in zip(gradients, gradient.detach().tolist(), strict=True):
                    accumulator.add(value)
                count += len(batch)
    finally:
        torch.set_num_threads(previous_threads)
    return PartitionSummary(
        partition_id,
        parameter_digest(theta_values),
        model.model_id,
        count,
        weights.value(),
        total.value(),
        tuple(item.value() for item in gradients),
    )
