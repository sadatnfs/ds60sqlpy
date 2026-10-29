"""Original custom-model authoring example, registered only by an explicit call."""

from __future__ import annotations

import math
from functools import partial

from .contracts import ObjectiveError, finite_number
from .registry import PredictionTarget, RegisteredModel
from .torch_backend import TorchLoss


def quadratic_loss(theta, features, targets, *, sigma):
    mean = theta[0] + theta[1] * features[:, 0].square()
    return math.log(sigma) + 0.5 * math.log(2 * math.pi) + 0.5 * ((targets - mean) / sigma).square()


def quadratic_prediction(theta, features):
    return theta[0] + theta[1] * features[:, 0].square()


def quadratic_model(configuration):
    if set(configuration) - {"sigma"}:
        raise ObjectiveError("quadratic example only accepts a known sigma")
    sigma = finite_number(configuration.get("sigma", 1.0), "known sigma")
    if sigma <= 0:
        raise ObjectiveError("known sigma must be positive")
    return RegisteredModel(
        TorchLoss("quadratic_mean", 2, 1, partial(quadratic_loss, sigma=sigma)),
        parameter_names=("intercept", "curvature"),
        feature_names=("time",),
        version="1",
        prediction_targets=(PredictionTarget("conditional_mean", quadratic_prediction),),
        default_prediction="conditional_mean",
    )
