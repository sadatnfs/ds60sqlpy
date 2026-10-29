"""Actual Torch joint-unit derivatives compared with an independent rank-one oracle."""

from __future__ import annotations

import json
import math

from .contracts import ObjectiveError, combine_summaries
from .registry import resolve_model
from .unit_backend import CompleteUnit, evaluate_units


def rank_one_oracle(values, theta):
    beta, log_sigma, log_tau = theta
    s, t = math.exp(2 * log_sigma), math.exp(2 * log_tau)
    n = len(values)
    mean = math.fsum(values) / n
    centered = math.fsum((value - mean) ** 2 for value in values)
    delta = mean - beta
    denominator = s + n * t
    value = 0.5 * (
        n * math.log(2 * math.pi)
        + (n - 1) * math.log(s)
        + math.log(denominator)
        + centered / s
        + n * delta**2 / denominator
    )
    gradient = (
        n * (beta - mean) / denominator,
        n - 1 + s / denominator - centered / s - n * s * delta**2 / denominator**2,
        n * t / denominator - n * n * t * delta**2 / denominator**2,
    )
    return value, gradient


def run():
    model = resolve_model("gaussian_random_intercept").loss
    theta = (0.7, math.log(0.8), math.log(0.5))
    observations = [[-0.1, 0.2], [1.1, 1.3, 0.8], [2.2, 2.7, 1.9, 2.3]]
    weights = [1.0, 2.0, 0.5]
    units = [
        CompleteUnit(f"g{i}", [(y,) for y in values], weight)
        for i, (values, weight) in enumerate(zip(observations, weights, strict=True))
    ]
    references = [rank_one_oracle(values, theta) for values in observations]
    value = math.fsum(
        weight * result[0] for weight, result in zip(weights, references, strict=True)
    )
    gradient = [
        math.fsum(weight * result[1][j] for weight, result in zip(weights, references, strict=True))
        for j in range(3)
    ]
    errors = []
    for partitions in (1, 2, 5):
        records = [evaluate_units(i, units[i::partitions], theta, model) for i in range(partitions)]
        total = combine_summaries(
            [record.summary for record in records],
            parameters=theta,
            model_id=model.model_id,
            expected_partitions=partitions,
            expected_rows=9,
        )
        mean = combine_summaries(
            [record.summary for record in records],
            parameters=theta,
            model_id=model.model_id,
            expected_partitions=partitions,
            expected_rows=9,
            reduction="weighted_mean",
        )
        error = max(
            abs(total.value - value),
            *(abs(a - b) for a, b in zip(total.gradient, gradient, strict=True)),
        )
        assert error < 1e-9
        assert abs(mean.value - value / 3.5) < 1e-9 and abs(mean.value - value / 9) > 0.1
        assert sum(record.unit_count for record in records) == 3
        errors.append(error)
    finite_errors = []
    actual = evaluate_units(0, [units[0]], theta, model)
    for j in range(3):
        plus, minus = list(theta), list(theta)
        plus[j] += 1e-5
        minus[j] -= 1e-5
        numeric = (
            rank_one_oracle(observations[0], plus)[0] - rank_one_oracle(observations[0], minus)[0]
        ) / 2e-5
        finite_errors.append(abs(actual.summary.gradient[j] - numeric))
    assert max(finite_errors) < 1e-7
    import torch

    features = torch.empty((len(observations[0]), 0), dtype=torch.float64)
    targets = torch.tensor(observations[0], dtype=torch.float64)
    hessian = torch.autograd.functional.hessian(
        lambda values: model.per_unit(values, features, targets),
        torch.tensor(theta, dtype=torch.float64),
    ).tolist()
    hessian_errors = []
    for j in range(3):
        plus, minus = list(theta), list(theta)
        plus[j] += 1e-5
        minus[j] -= 1e-5
        gplus = rank_one_oracle(observations[0], plus)[1]
        gminus = rank_one_oracle(observations[0], minus)[1]
        for i in range(3):
            hessian_errors.append(abs(hessian[i][j] - (gplus[i] - gminus[i]) / 2e-5))
    assert max(hessian_errors) < 1e-7
    rejected = []
    try:
        evaluate_units(0, [CompleteUnit("oversized", [(1.0,)] * 257)], theta, model)
    except ObjectiveError:
        rejected.append("unit-bound-no-splitting")
    else:
        raise AssertionError("oversized joint unit was accepted")
    print(
        json.dumps(
            {
                "kind": "package-unit-numerical",
                "passed": True,
                "partition_cases": len(errors),
                "units": 3,
                "rows": 9,
                "unit_weight_sum": 3.5,
                "max_rank_one_value_gradient_error": max(errors),
                "max_finite_difference_error": max(finite_errors),
                "max_hessian_oracle_error": max(hessian_errors),
                "rejected": rejected,
                "integration": "exact Gaussian marginal; no generic Laplace",
                "spark_executed": False,
                "r_required": False,
            },
            sort_keys=True,
        )
    )
