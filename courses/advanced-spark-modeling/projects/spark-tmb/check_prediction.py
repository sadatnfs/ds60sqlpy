"""Native typed-model value, gradient, fit and response-free report oracles."""

from __future__ import annotations

import json
import math

from spark_tmb import (
    ModelContractError,
    describe_prepared,
    evaluate_prepared,
    fit_prepared,
    predict_prepared,
)
from spark_tmb.cli import handle


def close(actual, expected, tolerance=1e-6):
    error = max(abs(a - b) for a, b in zip(actual, expected, strict=True))
    if error > tolerance:
        raise AssertionError((actual, expected, error))
    return error


def gaussian_oracle(x, y, beta, log_sigma):
    variance = math.exp(2 * log_sigma)
    residual = [
        outcome - beta[0] - beta[1] * feature for feature, outcome in zip(x, y, strict=True)
    ]
    rss = math.fsum(r * r for r in residual)
    value = len(y) * (log_sigma + 0.5 * math.log(2 * math.pi)) + rss / (2 * variance)
    gradient = [
        -math.fsum(residual) / variance,
        -math.fsum(r * v for r, v in zip(residual, x, strict=True)) / variance,
        len(y) - rss / variance,
    ]
    return value, gradient


def run_checks():
    normal = evaluate_prepared("normal_location", {"y": [1, 2, 4, 7]}, [2.2, 0.3])
    reference, gradient = gaussian_oracle([0] * 4, [1, 2, 4, 7], [2.2, 0], 0.3)
    normal_error = close(
        [normal["value"], *normal["gradient"]], [reference, gradient[0], gradient[2]]
    )
    constant = predict_prepared("normal_location", {}, [2.2, 0.3], n_rows=3)
    close(constant["prediction"], [2.2] * 3)
    x = [-2, -1, 0, 1, 2, 3]
    y = [-2.9, -0.8, 0.9, 3.1, 4.8, 7.2]
    theta = [0.4, 1.7, math.log(0.5)]
    regression = evaluate_prepared("linear_regression", {"x": x, "y": y}, theta)
    reference, gradient = gaussian_oracle(x, y, theta[:2], theta[2])
    regression_error = close([regression["value"], *regression["gradient"]], [reference, *gradient])
    if regression["parameter_names"] != ["beta_0", "beta_1", "log_sigma"]:
        raise AssertionError("Canonical parameter block layout changed")
    fitted = fit_prepared("linear_regression", {"x": x, "y": y}, [1, 2, -1])
    xmean, ymean = math.fsum(x) / len(x), math.fsum(y) / len(y)
    slope = math.fsum((a - xmean) * (b - ymean) for a, b in zip(x, y, strict=True)) / math.fsum(
        (a - xmean) ** 2 for a in x
    )
    intercept = ymean - slope * xmean
    sigma = math.sqrt(
        math.fsum((b - intercept - slope * a) ** 2 for a, b in zip(x, y, strict=True)) / len(y)
    )
    fit_error = close(fitted["fitted_parameters"], [intercept, slope, math.log(sigma)], 2e-5)
    alternate = fit_prepared("linear_regression", {"x": x, "y": y}, [0, 0, 0])
    fit_error = max(
        fit_error, close(alternate["fitted_parameters"], [intercept, slope, math.log(sigma)], 2e-5)
    )
    future = [-3, 0, 2]
    predicted = predict_prepared(
        "linear_regression", {"x_prediction": future}, fitted["fitted_parameters"], n_rows=3
    )
    prediction_error = close(predicted["prediction"], [intercept + slope * a for a in future], 2e-5)
    cli = handle(
        {
            "schema_version": 1,
            "operation": "predict",
            "model_id": "normal_location",
            "data": {},
            "parameters": [2.2, 0.3],
            "n_rows": 3,
            "target": "conditional_mean",
        }
    )
    close(cli["result"]["prediction"], [2.2] * 3)
    failures = []
    for name, model, data, parameters, count, target in [
        ("undeclared-normal", "normal_mean", {}, [0, 0], 2, None),
        ("undeclared-random", "random_intercept", {}, [0, 0, 0], 2, None),
        (
            "response-leak",
            "linear_regression",
            {"x_prediction": [1, 2], "y": [9, 9]},
            theta,
            2,
            None,
        ),
        ("row-count", "linear_regression", {"x_prediction": [1]}, theta, 2, None),
        ("wrong-target", "normal_location", {}, [0, 0], 2, "prediction_interval"),
    ]:
        try:
            predict_prepared(model, data, parameters, n_rows=count, target=target)
        except ModelContractError:
            failures.append(name)
        else:
            raise AssertionError("Invalid prediction was accepted: " + name)
    descriptor = describe_prepared("linear_regression")
    return {
        "case": "prediction-models",
        "normal_value_gradient_error": normal_error,
        "regression_value_gradient_error": regression_error,
        "fit_parameter_error": fit_error,
        "fit_diagnostics": [
            {
                key: record[key]
                for key in ("convergence", "gradient_max", "optimizer_message", "fit_controls")
            }
            for record in (fitted, alternate)
        ],
        "prediction_error": prediction_error,
        "predictor_free_rows": len(constant["prediction"]),
        "response_free": True,
        "rejected": failures,
        "target": predicted["target"],
        "prepared": descriptor["prepared"],
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), sort_keys=True, allow_nan=False))
