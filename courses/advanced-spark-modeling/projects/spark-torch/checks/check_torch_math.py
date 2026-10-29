"""Real Torch CPU proof, independent analytic likelihood/gradient oracles.

Run only in the prepared runtime. This checks streaming partition math, not a
Spark cluster or distributed training. The Spark integration has its own gate.
"""

from __future__ import annotations

import json
import math

import torch
from ds60_spark_likelihood import ObjectiveError, combine_summaries
from ds60_spark_likelihood.models import (
    logistic,
    nonlinear_gaussian,
    normal_mean,
    poisson_exposure,
)
from ds60_spark_likelihood.torch_backend import TorchLoss, evaluate_partition


def close(actual: float, expected: float, *, tolerance: float = 1e-10) -> None:
    assert math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (actual, expected)


def partitions(rows, count):
    return [rows[index::count] for index in range(count)]


def run():
    theta = (0.2, -0.3)
    rows = [
        (1.0, x, y, w)
        for x, y, w in [
            (-2.0, 0.0, 1.0),
            (-0.2, 1.0, 3.0),
            (0.5, 0.0, 0.0),
            (2.0, 1.0, 2.0),
            (3.0, 1.0, 0.5),
        ]
    ]
    expected_value = 0.0
    expected_gradient = [0.0, 0.0]
    for intercept, x, y, weight in rows:
        eta = theta[0] * intercept + theta[1] * x
        expected_value += weight * (max(eta, 0.0) + math.log1p(math.exp(-abs(eta))) - y * eta)
        residual = weight * (1 / (1 + math.exp(-eta)) - y)
        expected_gradient[0] += residual
        expected_gradient[1] += residual * x
    errors = []
    for count in (1, 2, 3, 7):
        for batch_size in (1, 2, 8):
            summaries = [
                evaluate_partition(i, part, theta, logistic(2), batch_size=batch_size)
                for i, part in enumerate(partitions(rows, count))
            ]
            result = combine_summaries(
                summaries,
                parameters=theta,
                model_id="logistic",
                expected_partitions=count,
                expected_rows=len(rows),
            )
            close(result.value, expected_value)
            for actual, expected in zip(result.gradient, expected_gradient, strict=True):
                close(actual, expected)
            errors.append(
                max(
                    abs(result.value - expected_value),
                    *(abs(a - b) for a, b in zip(result.gradient, expected_gradient, strict=True)),
                )
            )
    normal_theta = (2.0, math.log(1.5))
    normal_rows = [(value, weight) for value, weight in [(1.0, 1.0), (2.0, 2.0), (4.0, 0.5)]]
    normal = evaluate_partition(0, normal_rows, normal_theta, normal_mean(), batch_size=2)
    expected = sum(
        w * (math.log(1.5) + 0.5 * ((y - 2) / 1.5) ** 2 + 0.5 * math.log(2 * math.pi))
        for y, w in normal_rows
    )
    close(normal.value, expected)
    close(normal.gradient[0], sum(w * (2 - y) / 1.5**2 for y, w in normal_rows))
    close(normal.gradient[1], sum(w * (1 - ((y - 2) / 1.5) ** 2) for y, w in normal_rows))
    poisson_rows = [(1.0, exposure, y, 1.0) for exposure, y in [(0.5, 0.0), (2.0, 3.0), (1.5, 2.0)]]
    poisson = evaluate_partition(0, poisson_rows, (0.3,), poisson_exposure(1))
    expected = sum(
        math.exp(0.3) * e - y * (0.3 + math.log(e)) + math.lgamma(y + 1)
        for _, e, y, _ in poisson_rows
    )
    close(poisson.value, expected)
    close(poisson.gradient[0], sum(math.exp(0.3) * e - y for _, e, y, _ in poisson_rows))
    nonlinear_theta = (2.0, -0.3, 0.5, -0.2)
    nonlinear_rows = [(t, y, 1.0) for t, y in [(0.0, 2.7), (0.5, 1.8), (1.5, 1.3), (3.0, 0.6)]]
    actual = evaluate_partition(0, nonlinear_rows, nonlinear_theta, nonlinear_gaussian())

    def oracle(values):
        a, log_rate, baseline, log_scale = values
        return sum(
            log_scale
            + 0.5
            * ((y - (a * math.exp(-math.exp(log_rate) * t) + baseline)) / math.exp(log_scale)) ** 2
            + 0.5 * math.log(2 * math.pi)
            for t, y, _ in nonlinear_rows
        )

    close(actual.value, oracle(nonlinear_theta))
    finite_errors = []
    for i in range(4):
        plus, minus = list(nonlinear_theta), list(nonlinear_theta)
        plus[i] += 1e-6
        minus[i] -= 1e-6
        numeric = (oracle(plus) - oracle(minus)) / 2e-6
        close(actual.gradient[i], numeric, tolerance=1e-7)
        finite_errors.append(abs(actual.gradient[i] - numeric))
    bad_cases = [
        ([(1.0, 0.0, 2.0, 1.0)], theta, logistic(2)),
        ([(1.0, -0.1, 2.0, 1.0)], (0.1,), poisson_exposure(1)),
        ([(1.0, 0.0, 1.0, -1.0)], theta, logistic(2)),
        (rows, theta, TorchLoss("detached", 2, 2, lambda t, x, y: (x @ t).detach())),
        (rows, theta, TorchLoss("scalar", 2, 2, lambda t, x, y: (x @ t).sum())),
    ]
    for data, values, model in bad_cases:
        try:
            evaluate_partition(0, data, values, model)
        except ObjectiveError:
            pass
        else:
            raise AssertionError("invalid model/input was accepted")
    print(
        json.dumps(
            {
                "kind": "torch-cpu-partition-math",
                "passed": True,
                "torch": torch.__version__,
                "partition_batch_cases": len(errors),
                "max_analytic_error": max(errors),
                "max_nonlinear_gradient_error": max(finite_errors),
                "invalid_cases_rejected": len(bad_cases),
                "spark_executed": False,
                "distributed_training_executed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    run()
