"""Additional original Torch likelihood and explicit prediction functions."""

from __future__ import annotations

import math
from importlib import import_module
from typing import Any

from .contracts import ObjectiveError
from .torch_backend import TorchLoss
from .unit_backend import TorchUnitLoss


def linear_gaussian_loss(theta: Any, features: Any, targets: Any) -> Any:
    torch = import_module("torch")
    log_scale = theta[-1]
    residual = targets - features @ theta[:-1]
    return (
        log_scale
        + 0.5 * residual.square() * torch.exp(-2 * log_scale)
        + 0.5 * math.log(2 * math.pi)
    )


def gaussian_random_intercept_loss(theta: Any, features: Any, targets: Any) -> Any:
    """Exact integrated group density; no generic Laplace approximation is implied."""
    torch = import_module("torch")
    del features
    variances = torch.exp(2 * theta[1:])
    if not bool(torch.isfinite(variances).all() & (variances > 0).all()):
        raise ObjectiveError("Gaussian group scales must be finite and strictly positive")
    count = targets.numel()
    covariance = variances[0] * torch.eye(count, dtype=torch.float64) + variances[1] * torch.ones(
        (count, count), dtype=torch.float64
    )
    distribution = torch.distributions.MultivariateNormal(
        theta[0].expand(count), covariance_matrix=covariance
    )
    return -distribution.log_prob(targets)


def linear_gaussian(feature_count: int) -> TorchLoss:
    if type(feature_count) is not int or feature_count < 1:
        raise ObjectiveError("linear Gaussian models require explicit design columns")
    return TorchLoss("linear_gaussian", feature_count + 1, feature_count, linear_gaussian_loss)


def gaussian_random_intercept(max_unit_rows: int = 256) -> TorchUnitLoss:
    return TorchUnitLoss(
        "gaussian_random_intercept",
        3,
        0,
        gaussian_random_intercept_loss,
        max_unit_rows=max_unit_rows,
    )


def normal_prediction(theta: Any, features: Any) -> Any:
    return theta[0].expand(features.shape[0])


def logistic_prediction(theta: Any, features: Any) -> Any:
    torch = import_module("torch")
    return torch.sigmoid(features @ theta)


def linear_prediction(theta: Any, features: Any) -> Any:
    return features @ theta[:-1]


def nonlinear_prediction(theta: Any, features: Any) -> Any:
    torch = import_module("torch")
    times = features[:, 0]
    if not bool((times >= 0).all()):
        raise ObjectiveError("decay predictions require nonnegative times")
    return theta[0] * torch.exp(-torch.exp(theta[1]) * times) + theta[2]


def poisson_prediction(theta: Any, features: Any) -> Any:
    torch = import_module("torch")
    exposure = features[:, -1]
    if not bool((exposure > 0).all()):
        raise ObjectiveError("count prediction requires positive exposure")
    return torch.exp(features[:, :-1] @ theta + torch.log(exposure))
