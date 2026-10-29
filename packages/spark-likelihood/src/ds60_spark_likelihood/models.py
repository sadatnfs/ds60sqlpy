"""Original, normalized teaching likelihoods for the optional Torch adapter."""

from __future__ import annotations

import math
from importlib import import_module
from typing import Any

from .contracts import ObjectiveError
from .torch_backend import TorchLoss


def logistic_loss(theta: Any, features: Any, targets: Any) -> Any:
    torch = import_module("torch")

    if not bool(((targets == 0) | (targets == 1)).all()):
        raise ObjectiveError("logistic observations must be binary 0 or 1")
    logits = features @ theta
    return torch.nn.functional.softplus(logits) - targets * logits


def normal_mean_loss(theta: Any, features: Any, targets: Any) -> Any:
    torch = import_module("torch")

    del features
    scale = torch.exp(theta[1])
    return theta[1] + 0.5 * ((targets - theta[0]) / scale) ** 2 + 0.5 * math.log(2 * math.pi)


def nonlinear_gaussian_loss(theta: Any, features: Any, targets: Any) -> Any:
    torch = import_module("torch")

    times = features[:, 0]
    if not bool((times >= 0).all()):
        raise ObjectiveError("this exponential-decay model uses nonnegative times")
    rate = torch.exp(theta[1])
    scale = torch.exp(theta[3])
    mean = theta[0] * torch.exp(-rate * times) + theta[2]
    return theta[3] + 0.5 * ((targets - mean) / scale) ** 2 + 0.5 * math.log(2 * math.pi)


def poisson_exposure_loss(theta: Any, features: Any, targets: Any) -> Any:
    torch = import_module("torch")

    exposure = features[:, -1]
    if not bool((exposure > 0).all()):
        raise ObjectiveError("Poisson exposure must be strictly positive")
    if not bool(((targets >= 0) & (targets == torch.floor(targets))).all()):
        raise ObjectiveError("Poisson observations must be nonnegative counts")
    eta = features[:, :-1] @ theta + torch.log(exposure)
    return torch.exp(eta) - targets * eta + torch.lgamma(targets + 1)


def logistic(feature_count: int) -> TorchLoss:
    """Include an intercept column explicitly if the model needs one."""
    return TorchLoss("logistic", feature_count, feature_count, logistic_loss)


def normal_mean() -> TorchLoss:
    return TorchLoss("normal_mean", 2, 0, normal_mean_loss)


def nonlinear_gaussian() -> TorchLoss:
    return TorchLoss("nonlinear_gaussian", 4, 1, nonlinear_gaussian_loss)


def poisson_exposure(design_columns: int) -> TorchLoss:
    """The final feature is exposure; preceding columns form the linear design."""
    return TorchLoss("poisson_exposure", design_columns, design_columns + 1, poisson_exposure_loss)
