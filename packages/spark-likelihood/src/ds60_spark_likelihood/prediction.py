"""Explicit label-free point predictions from registered Torch model functions."""

from __future__ import annotations

from collections.abc import Sequence
from importlib import import_module
from typing import cast

from .contracts import ObjectiveError, finite_number, finite_vector
from .registry import RegisteredModel


def predict_batch(
    model: RegisteredModel,
    parameters: Sequence[float],
    feature_rows: Sequence[Sequence[float]],
    target: str | None = None,
) -> list[float]:
    if not isinstance(model, RegisteredModel):
        raise ObjectiveError("prediction requires an explicitly registered model")
    theta_values = finite_vector(parameters)
    if len(theta_values) != model.parameter_count:
        raise ObjectiveError("prediction parameters differ from the declared model shape")
    if not isinstance(feature_rows, (list, tuple)) or not 1 <= len(feature_rows) <= 8192:
        raise ObjectiveError("prediction batches must contain 1..8192 bounded feature rows")
    rows = []
    for row in feature_rows:
        if (
            isinstance(row, (str, bytes))
            or not isinstance(row, Sequence)
            or len(row) != model.feature_count
        ):
            raise ObjectiveError(
                "prediction input contains undeclared features or response columns"
            )
        rows.append(tuple(finite_number(value, "prediction feature") for value in row))
    chosen = model.default_prediction if target is None else target
    functions = {entry.name: entry.function for entry in model.prediction_targets}
    if not isinstance(chosen, str) or chosen not in functions:
        raise ObjectiveError("this model does not declare the requested prediction target")
    try:
        torch = import_module("torch")
    except ImportError:
        raise ObjectiveError("prepare the optional CPU Torch environment for prediction") from None
    with torch.no_grad():
        theta = torch.tensor(theta_values, dtype=torch.float64)
        features = torch.tensor(rows, dtype=torch.float64).reshape(len(rows), model.feature_count)
        values = functions[chosen](theta, features)
        if (
            not isinstance(values, torch.Tensor)
            or values.shape != (len(rows),)
            or values.dtype != torch.float64
            or values.device.type != "cpu"
            or not bool(torch.isfinite(values).all())
        ):
            raise ObjectiveError(
                "prediction callback must return one finite CPU float64 scalar per row"
            )
        return cast(list[float], values.tolist())
