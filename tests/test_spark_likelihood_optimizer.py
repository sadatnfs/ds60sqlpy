"""Optimizer checks against closed-form normal likelihood and constrained optima."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import replace
from typing import Any, NoReturn

import pytest
from ds60_spark_likelihood import ObjectiveError, PartitionSummary, combine_summaries
from ds60_spark_likelihood.contracts import ObjectiveEvaluation, parameter_digest
from ds60_spark_likelihood.optimization import minimize_lbfgsb

pytest.importorskip("scipy.optimize", reason="explicit optional optimizer runtime")


def gaussian(values: Sequence[float]) -> ObjectiveEvaluation:
    mu, log_sigma = values
    data = (1.0, 2.0, 4.0, 7.0)
    variance = math.exp(2 * log_sigma)
    squared = sum((y - mu) ** 2 for y in data)
    value = len(data) * (log_sigma + 0.5 * math.log(2 * math.pi)) + squared / (2 * variance)
    gradient = (sum(mu - y for y in data) / variance, len(data) - squared / variance)
    return combine_summaries(
        [
            PartitionSummary(
                0, parameter_digest(values), "normal", len(data), len(data), value, gradient
            )
        ],
        parameters=values,
        model_id="normal",
        expected_rows=len(data),
        expected_partitions=1,
    )


def test_normal_mle_matches_closed_form_and_reports_stationarity() -> None:
    result = minimize_lbfgsb(gaussian, (0.0, 0.0), bounds=((-20, 20), (-4, 4)))
    assert result.converged
    assert result.parameters == pytest.approx((3.5, math.log(math.sqrt(5.25))), abs=2e-7)
    assert result.gradient_inf_norm < 1e-6
    assert result.projected_gradient_inf_norm == result.gradient_inf_norm
    assert result.active_bounds == ()
    assert result.objective_calls == len(result.trace)
    assert result.evaluation.row_count == 4


def test_bound_convergence_reports_raw_and_projected_gradients_separately() -> None:
    result = minimize_lbfgsb(gaussian, (0.0, 0.0), bounds=((-2, 2), (-4, 4)))
    assert result.converged
    assert result.parameters[0] == pytest.approx(2)
    assert result.parameters[1] == pytest.approx(math.log(math.sqrt(7.5)), abs=1e-6)
    assert result.active_bounds == (0,)
    assert result.gradient_inf_norm > 0.7
    assert result.projected_gradient_inf_norm < 1e-6


def test_iteration_exhaustion_returns_failed_fit_instead_of_claiming_convergence() -> None:
    result = minimize_lbfgsb(gaussian, (-12, 3), max_iterations=1)
    assert not result.converged and result.status != 0
    assert result.iterations == 1


@pytest.mark.parametrize(
    "options",
    [
        {"bounds": ((0, 1),)},
        {"bounds": ((2, 1), (None, None))},
        {"bounds": ((1, 2), (None, None))},
        {"max_iterations": True},
        {"max_iterations": 0},
        {"gradient_tolerance": 0},
        {"function_tolerance": float("nan")},
    ],
)
def test_invalid_optimizer_contract_fails_before_evaluation(options: dict[str, Any]) -> None:
    def never(values: Sequence[float]) -> NoReturn:
        raise AssertionError("should not evaluate")

    with pytest.raises(ObjectiveError):
        minimize_lbfgsb(never, (0, 0), **options)


def test_optimizer_refuses_stale_or_nonfinite_external_evaluations() -> None:
    for fault in ("stale", "nan", "dimension"):

        def corrupt(values: Sequence[float], fault: str = fault) -> ObjectiveEvaluation:
            result = gaussian(values)
            if fault == "stale":
                return replace(result, parameter_digest=parameter_digest((9, 9)))
            if fault == "nan":
                return replace(result, value=float("nan"))
            return replace(result, gradient=(1,))

        with pytest.raises(ObjectiveError):
            minimize_lbfgsb(corrupt, (0, 0))


def test_narrow_interval_interior_is_not_reported_as_active_at_both_bounds() -> None:
    def quadratic(theta: Sequence[float]) -> ObjectiveEvaluation:
        value = float(theta[0])
        return combine_summaries(
            [
                PartitionSummary(
                    0,
                    parameter_digest(theta),
                    "quadratic",
                    1,
                    1,
                    0.5 * (value - 1) ** 2,
                    (value - 1,),
                )
            ],
            parameters=theta,
            model_id="quadratic",
            expected_partitions=1,
            expected_rows=1,
        )

    result = minimize_lbfgsb(quadratic, (5e-13,), bounds=((0, 1e-12),))
    # SciPy can stop on its step-based tolerance in this tiny feasible interval.
    # Our exact-bound diagnostic must not claim an interior point satisfies KKT.
    assert result.parameters == (5e-13,)
    assert result.active_bounds == ()
    assert result.projected_gradient_inf_norm > 0.99
