"""Original non-Gaussian complete-unit model with an exact shared-rate integral."""

from __future__ import annotations

from importlib import import_module

from .contracts import ObjectiveError
from .registry import PredictionTarget, RegisteredModel
from .unit_backend import TorchUnitLoss

MAX_TOTAL_COUNT = 10_000


def gamma_poisson_loss(theta, features, targets):
    torch = import_module("torch")
    exposure = features[:, 0]
    if not bool((exposure > 0).all()):
        raise ObjectiveError("Gamma-Poisson exposures must be strictly positive")
    if not bool(((targets >= 0) & (targets == torch.floor(targets))).all()):
        raise ObjectiveError("Gamma-Poisson observations must be nonnegative integer counts")
    if not bool((theta.abs() <= 300).all()):
        raise ObjectiveError("Gamma-Poisson reference log parameters must be in [-300, 300]")
    count, opportunity = targets.sum(), exposure.sum()
    if not bool(torch.isfinite(count) & torch.isfinite(opportunity)):
        raise ObjectiveError("Group count/exposure accumulation exceeded float64 range")
    if float(count) > MAX_TOTAL_COUNT:
        raise ObjectiveError("Gamma-Poisson reference model bounds total group count at 10000")
    # Integer-count gamma ratio avoids cancellation of enormous lgamma values.
    total = int(count)
    offsets = torch.arange(1, max(total, 1), dtype=torch.float64)
    correction = torch.logaddexp(torch.zeros_like(offsets), torch.log(offsets) - theta[0]).sum()
    log_ratio = torch.log(opportunity) - theta[1]
    # log(softplus(x)) tends to x; the discarded relative correction is below
    # float64 precision here. This also avoids exp(log_alpha) overflowing before
    # multiplication by a tiny exposure/rate ratio.
    if float(log_ratio.detach()) < -36.0:
        log_probability_term = log_ratio
    else:
        log_probability_term = torch.log(torch.logaddexp(torch.zeros_like(log_ratio), log_ratio))
    log_shape_plus_count = theta[0] if total == 0 else torch.logaddexp(theta[0], torch.log(count))
    integrated_term = torch.exp(log_shape_plus_count + log_probability_term)
    result = (
        count * (theta[1] - theta[0])
        - correction
        + integrated_term
        - (targets * torch.log(exposure) - torch.lgamma(targets + 1)).sum()
    )
    if not bool(torch.isfinite(result)):
        raise ObjectiveError("Gamma-Poisson likelihood exceeds supported float64 range")
    return result


def gamma_poisson_prediction(theta, features):
    torch = import_module("torch")
    exposure = features[:, 0]
    if not bool((exposure > 0).all()):
        raise ObjectiveError("New-group count prediction requires positive exposure")
    return torch.exp(torch.log(exposure) + theta[0] - theta[1])


def gamma_poisson_model(configuration):
    if set(configuration) - {"max_unit_rows"}:
        raise ObjectiveError("Gamma-Poisson example accepts only the explicit unit row bound")
    loss = TorchUnitLoss(
        "gamma_poisson_shared_rate",
        2,
        1,
        gamma_poisson_loss,
        max_unit_rows=configuration.get("max_unit_rows", 256),
    )
    return RegisteredModel(
        loss,
        ("log_alpha", "log_beta"),
        ("exposure",),
        version="1",
        prediction_targets=(
            PredictionTarget("new_group_expected_count", gamma_poisson_prediction),
        ),
        default_prediction="new_group_expected_count",
    )
