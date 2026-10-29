"""Actual label-free prediction and optimizer checks from the installed package."""

from __future__ import annotations

import json
import math

from .contracts import ObjectiveError, PartitionSummary, combine_summaries, parameter_digest
from .example_models import quadratic_model
from .models import normal_mean
from .optimization import minimize_lbfgsb
from .prediction import predict_batch
from .registry import RegisteredModel, register_model_factory, resolve_model
from .torch_backend import evaluate_partition


def run():
    errors = []
    cases = [
        ("normal_mean", {}, [3.5, 0.1], [(), ()], None, [3.5, 3.5]),
        (
            "linear_gaussian",
            {"feature_count": 2},
            [1.0, 2.0, 0.0],
            [(1.0, -1.0), (1.0, 2.0)],
            None,
            [-1.0, 5.0],
        ),
        (
            "logistic",
            {"feature_count": 2},
            [0.2, -0.3],
            [(1.0, -2.0), (1.0, 2.0)],
            None,
            [1 / (1 + math.exp(-0.8)), 1 / (1 + math.exp(0.4))],
        ),
        (
            "nonlinear_gaussian",
            {},
            [2.0, math.log(0.5), 0.4, math.log(0.3)],
            [(0.0,), (1.0,)],
            None,
            [2.4, 2 * math.exp(-0.5) + 0.4],
        ),
        (
            "poisson_exposure",
            {"design_columns": 1},
            [math.log(2)],
            [(1.0, 0.5), (1.0, 3.0)],
            None,
            [1.0, 6.0],
        ),
        (
            "gaussian_random_intercept",
            {},
            [0.7, math.log(0.8), math.log(0.5)],
            [(), ()],
            "new_group_mean",
            [0.7, 0.7],
        ),
    ]
    for name, config, theta, features, target, expected in cases:
        result = predict_batch(resolve_model(name, config), theta, features, target)
        error = max(abs(a - b) for a, b in zip(result, expected, strict=True))
        assert error < 1e-12
        errors.append(error)
    register_model_factory("quadratic_mean", quadratic_model, replace_existing=True)
    custom = resolve_model("quadratic_mean", {"sigma": 0.5})
    custom_rows = [(0.0, 1.2, 1.0), (1.0, 2.8, 1.0), (2.0, 9.3, 1.0)]
    custom_result = evaluate_partition(0, custom_rows, (1.0, 2.0), custom.loss, batch_size=2)
    custom_expected = 3 * (math.log(0.5) + 0.5 * math.log(2 * math.pi)) + 0.17 / 0.5
    custom_error = max(
        abs(custom_result.value - custom_expected),
        abs(custom_result.gradient[0] + 1.2),
        abs(custom_result.gradient[1] + 4.0),
    )
    assert custom_error < 1e-12
    assert predict_batch(custom, (1.0, 2.0), [(3.0,), (4.0,)]) == [19.0, 33.0]
    assert custom.fingerprint != resolve_model("quadratic_mean", {"sigma": 2.0}).fingerprint
    unpredicted = RegisteredModel(normal_mean(), ("mu", "log_sigma"), ())
    try:
        predict_batch(unpredicted, [0.0, 0.0], [()])
    except ObjectiveError:
        pass
    else:
        raise AssertionError("a generic prediction was invented")
    try:
        predict_batch(resolve_model("normal_mean"), [0.0, 0.0], [(1.0,)])
    except ObjectiveError:
        pass
    else:
        raise AssertionError("response/undeclared features were accepted")
    data = (1.0, 2.0, 4.0, 7.0)

    def objective(theta):
        mu, log_sigma = theta
        variance = math.exp(2 * log_sigma)
        rss = math.fsum((y - mu) ** 2 for y in data)
        value = 4 * (log_sigma + 0.5 * math.log(2 * math.pi)) + rss / (2 * variance)
        gradient = (math.fsum(mu - y for y in data) / variance, 4 - rss / variance)
        summary = PartitionSummary(
            0, parameter_digest(theta), "normal_mean", 4, 4.0, value, gradient
        )
        return combine_summaries(
            [summary],
            parameters=theta,
            model_id="normal_mean",
            expected_partitions=1,
            expected_rows=4,
        )

    fitted = minimize_lbfgsb(objective, [0.0, 0.0], bounds=[(-20, 20), (-4, 4)])
    assert fitted.converged and fitted.gradient_inf_norm < 1e-6
    assert (
        max(
            abs(a - b)
            for a, b in zip(fitted.parameters, [3.5, math.log(math.sqrt(5.25))], strict=True)
        )
        < 2e-7
    )
    print(
        json.dumps(
            {
                "kind": "package-prediction-optimizer",
                "passed": True,
                "prediction_models": len(cases),
                "custom_model_value_gradient_error": custom_error,
                "custom_configuration_identity_checked": True,
                "max_prediction_error": max(errors),
                "undeclared_prediction_rejected": True,
                "response_input_rejected": True,
                "fitted_parameters": fitted.parameters,
                "gradient_inf_norm": fitted.gradient_inf_norm,
                "r_required": False,
            },
            sort_keys=True,
        )
    )
