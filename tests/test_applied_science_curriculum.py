"""Independent scientific identities and complete tutorial contracts."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/applied-science"


def source(number: int) -> dict[str, Any]:
    return runpy.run_path(str(BASE / f"authoring/programs/science-{number:03}.py"))


def test_published_tutorial_contract_and_generated_bytes() -> None:
    plan = json.loads((BASE / "track.json").read_text())
    manifest = json.loads((BASE / "lessons.json").read_text())
    assert plan["learning_mode"] == "tutorial"
    assert len(plan["lessons"]) == len(manifest["lessons"]) == 24
    assert {r["level"] for r in plan["lessons"]} == {"beginner", "intermediate", "advanced"}
    assert [r["id"] for r in plan["lessons"]] == [f"science-{i:03}" for i in range(1, 25)]
    for row in manifest["lessons"]:
        assert row["runtime_profile"] == "python-core" and row["language"] == "python"
        assert row["verification_id"] is None and row["solution_paths"] == []
        guide = (ROOT / row["guide_path"]).read_text()
        program = (ROOT / row["source_path"]).read_text()
        assert guide.count("## Worked case") == 2
        assert len(guide.split()) > 650 and "\u2014" not in guide
        assert "```python\n" + program.rstrip() + "\n```" in guide
        assert "## Answered scientific discussion" in guide
    completed = subprocess.run(
        [sys.executable, str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize("number", range(1, 25))
def test_every_case_runs_and_serializes_finite_evidence(number: int) -> None:
    result = source(number)["run_cases"]()
    assert isinstance(result, dict) and len(result) >= 3
    assert json.loads(json.dumps(result, allow_nan=False))


def test_transport_is_effect_weighting_not_arm_composition() -> None:
    f = source(1)["standardize"]
    assert f([2, 1], [0.2, 0.8]) == pytest.approx(1.2)
    with pytest.raises(ValueError):
        f([2, 1], [1, 1])
    with pytest.raises(ValueError):
        f([2, np.nan], [0.2, 0.8])
    assert source(1)["run_cases"]()["crude_difference"] < 0


def test_weight_concentration_and_invalid_assignments() -> None:
    ns = source(2)
    assert ns["effective_n"]([2, 2, 2]) == pytest.approx(3)
    assert ns["effective_n"]([1, 1, 1, 50]) == pytest.approx(2809 / 2503)
    for e in ([0, 0.5], [0.5, 1], [np.nan, 0.5]):
        with pytest.raises(ValueError):
            ns["weighted_effect"]([1, 2], [0, 1], e)
    with pytest.raises(ValueError):
        ns["weighted_effect"]([1, 2], [0, 2], [0.5, 0.5])


def test_bias_tipping_surface_is_exact() -> None:
    f = source(3)["bias_adjusted"]
    assert f(3, 0.5, 6) == 0
    assert f(3, 0.75, 6) == -1.5
    assert f(3, 0, 1000) == 3


def test_staggered_contrasts_exclude_already_treated_groups() -> None:
    result = source(4)["run_cases"]()
    assert result == {
        "early_cohort_at_t4": 6.0,
        "late_cohort_at_t4": 2.0,
        "already_treated_comparison": 0.0,
    }
    with pytest.raises(ValueError):
        source(4)["group_time_effect"](np.ones((2, 3)), [1, 99], 0, 1)


def test_longitudinal_g_formula_includes_the_mediated_path() -> None:
    f = source(5)["sequential_value"]
    assert f(lambda t, l0, l1: 0) == pytest.approx(2.2)
    assert f(lambda t, l0, l1: 1) == pytest.approx(7.6)
    assert f(lambda t, l0, l1: 1) - f(lambda t, l0, l1: 0) == pytest.approx(5.4)
    assert source(6)["run_cases"]()["always_treat_value"] == pytest.approx(7.2)


def test_vintage_leakage_changes_the_actual_forecast() -> None:
    result = source(7)["run_cases"]()
    assert result["vintage_forecast"] == pytest.approx(18)
    assert result["revised_backtest"] == pytest.approx(36)
    assert result["unique_targets"] == 3


def test_reconciliation_matches_an_independent_projection() -> None:
    ns = source(8)
    s = np.array([[1, 1], [1, 0], [0, 1.0]])
    expected = s @ np.linalg.lstsq(s, [12, 4, 5], rcond=None)[0]
    actual = ns["reconcile"]([12, 4, 5], s, np.eye(3))
    assert np.allclose(actual, expected) and np.allclose(actual, [11, 5, 6])
    assert actual[0] == pytest.approx(actual[1] + actual[2])


def test_partial_likelihood_and_delayed_entry_oracles() -> None:
    f = source(10)["cox_loglik"]
    t = [1, 2, 3, 4]
    d = [1, 1, 0, 1]
    x = [1, 0, 1, 0]
    assert f(0, t, d, x) == pytest.approx(-np.log(12))
    assert f(0, t, d, x, [0, 0, 2.5, 0]) == pytest.approx(-np.log(6))
    beta = 0.5 * np.log(2)
    h = 1e-5
    assert abs((f(beta + h, t, d, x) - f(beta - h, t, d, x)) / (2 * h)) < 1e-8


def test_censored_and_competing_event_likelihoods() -> None:
    assert source(11)["exponential_mle"]([1, 2, 4, 5, 8], [1, 1, 0, 1, 0]) == pytest.approx(0.15)
    incidence, survival = source(12)["competing_incidence"]([1, 2, 3, 4], [1, 2, 1, 2])
    assert np.allclose(incidence, [0.5, 0.5]) and survival == 0
    assert source(12)["run_cases"]()["naive_one_minus_km"] == pytest.approx(0.625)


def test_pairwise_gradient_is_checked_at_a_new_parameter_value() -> None:
    f = source(14)["bpr_loss_gradient"]
    d = np.array([[2.0, 1.0], [-1.0, 2.0], [0.5, -0.3]])
    w = np.array([0.4, -0.2])
    h = 1e-5
    _, analytic = f(w, d)
    numeric = np.array(
        [
            (f(w + np.eye(2)[j] * h, d)[0] - f(w - np.eye(2)[j] * h, d)[0]) / (2 * h)
            for j in range(2)
        ]
    )
    assert np.allclose(analytic, numeric, atol=1e-9)
    with pytest.raises(ValueError):
        source(13)["recall_at_k"](set(), ["a"], 1)


def test_off_policy_support_is_not_silently_repaired() -> None:
    ns = source(15)
    r = ns["run_cases"]()
    assert r["ips"] == pytest.approx(0.5) and r["doubly_robust"] == pytest.approx(0.5)
    assert r["logging_average"] == pytest.approx(0.32) and r["clipped_estimate"] < r["ips"]
    with pytest.raises(ValueError):
        ns["ips_value"]([1], [0], [0.5])


def test_integer_solution_matches_enumeration_and_rounding_fails() -> None:
    r = source(17)["run_cases"]()
    values = np.array([10, 8, 6])
    costs = np.array([6, 5, 4])
    feasible = [
        sum(values[list(choice)])
        for n in range(4)
        for choice in combinations(range(3), n)
        if sum(costs[list(choice)]) <= 9
    ]
    assert r["integer_value"] == max(feasible) == 14
    assert r["relaxation_bound"] > r["integer_value"] and r["rounded_cost"] > 9
    decision = source(18)["run_cases"]()
    assert (
        decision["expected_cost_choice"] == 4
        and decision["minimax_choice"] == 10
        and decision["evpi"] >= 0
    )


def test_heterogeneity_and_dependent_effect_variance() -> None:
    ns = source(19)
    result = ns["dl_meta"]([0.1, 0.2, 0.7, 0.9], [0.04] * 4)
    assert result["tau2"] == pytest.approx((11.1875 - 3) / 75)
    assert result["mean"] == pytest.approx(0.475)
    f = source(20)["gls_mean"]
    mean, var = f([0.4, 0.6], [[0.04, 0.03], [0.03, 0.04]])
    assert mean == pytest.approx(0.5) and var == pytest.approx(0.035)
    with pytest.raises(ValueError):
        f([0.4, 0.6], [[1, 2], [2, 1]])


def test_spatial_and_survey_covariance_oracles() -> None:
    result = source(21)["run_cases"]()
    assert result["clustered_I"] == pytest.approx(0.6) and result["alternating_I"] == pytest.approx(
        -1
    )
    assert result["random_boundary_edges"] == 5 and result["blocked_boundary_edges"] == 1
    survey = source(22)["run_cases"]()
    assert survey["expected_ht"] == 16 and survey["sample_ht"] == 15
    assert survey["design_effect"] == pytest.approx(2.2)


def test_capstone_estimates_uncertainty_before_deciding() -> None:
    r = source(24)["run_cases"]()
    assert r["estimated_effects"] == [3.0, 1.0, -1.0]
    assert np.allclose(r["standard_errors"], np.sqrt([1 / 3, 4 / 3, 1 / 12]))
    assert r["ledger"]["selected"] == ["north"] and r["updated_selection_count"] == 0


def test_censored_weibull_gradient_matches_independent_finite_differences() -> None:
    f = source(11)["weibull_nll_gradient"]
    theta = np.log([1.7, 6.0])
    t = np.array([1.0, 2.0, 4.0, 5.0, 8.0])
    d = np.array([1, 1, 0, 1, 0])
    h = 1e-5
    _, gradient = f(theta, t, d)
    numeric = np.array(
        [
            (f(theta + np.eye(2)[j] * h, t, d)[0] - f(theta - np.eye(2)[j] * h, t, d)[0]) / (2 * h)
            for j in range(2)
        ]
    )
    assert np.allclose(gradient, numeric, atol=1e-8)
    result = source(11)["run_cases"]()
    assert result["optimizer_success"] and result["gradient_norm"] < 1e-5


def test_negative_sampling_waits_for_attribution_and_reporting_completion() -> None:
    sample = source(14)["negative_candidates"]
    exposures = [("a", 0), ("b", 4), ("c", 0), ("d", 1)]
    events = [("a", 1, 2), ("b", 6, 8)]
    assert sample(exposures, events, 5, 3, 2) == ["c"]
    assert sample(exposures, events, 9, 3, 2) == ["c", "d"]
    with pytest.raises(ValueError):
        sample(exposures, events, 5, -1, 2)
