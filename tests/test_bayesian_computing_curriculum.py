"""Independent exact oracles and authored Bayesian tutorial contracts."""

from __future__ import annotations

import importlib.util
import json
import runpy
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pytest

stats = pytest.importorskip("scipy.stats")
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/bayesian-computing"


def source(number: int) -> dict[str, Any]:
    return runpy.run_path(str(BASE / f"authoring/programs/bayes-{number:03}.py"))


def test_complete_tutorial_admission_and_exact_fences() -> None:
    plan = json.loads((BASE / "track.json").read_text())
    manifest = json.loads((BASE / "lessons.json").read_text())
    assert plan["learning_mode"] == "tutorial"
    assert [r["id"] for r in plan["lessons"]] == [f"bayes-{n:03}" for n in range(1, 25)]
    assert len(manifest["lessons"]) == 24
    assert {r["level"] for r in plan["lessons"]} == {"beginner", "intermediate", "advanced"}
    for number, row in enumerate(manifest["lessons"], 1):
        expected = "python-core" if number <= 8 else "bayesian-cpu" if number <= 16 else "stan-cpu"
        assert row["runtime_profile"] == expected and row["verification_id"] is None
        assert row["solution_paths"] == []
        guide = (ROOT / row["guide_path"]).read_text()
        program = (ROOT / row["source_path"]).read_text()
        assert len(program.encode()) <= 48000 and guide.count("## Worked case") == 2
        assert len(guide.split("## Complete reproducible program")[0].split()) >= 600
        assert "```" + row["language"] + "\n" + program.rstrip() + "\n```" in guide
        assert "## Exercises" not in guide and "\u2014" not in guide
    p = subprocess.run(
        [sys.executable, str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert p.returncode == 0, p.stdout + p.stderr


@pytest.mark.parametrize("number", range(1, 9))
def test_exact_foundation_programs(number: int) -> None:
    result = source(number)["run_cases"]()
    assert isinstance(result, dict) and len(result) >= 3
    assert json.loads(json.dumps(result, allow_nan=False))


def test_bayes_odds_equal_fraction_oracle_and_repeated_signal_is_distinct() -> None:
    posterior = source(1)["posterior"]
    result = posterior([0.8, 0.2], [0.1, 0.9])
    exact = (
        Fraction(2, 10)
        * Fraction(9, 10)
        / (Fraction(8, 10) * Fraction(1, 10) + Fraction(2, 10) * Fraction(9, 10))
    )
    assert result[1] == pytest.approx(float(exact))
    independent = posterior([0.8, 0.2], [0.01, 0.81])
    assert independent[1] == pytest.approx(81 / 85) and independent[1] > result[1]
    with pytest.raises(ValueError):
        posterior([0.5, 0.5], [0, 0])


def test_log_normalization_rejects_impossible_and_infinite_targets() -> None:
    f = source(2)["normalized_log_weights"]
    assert np.allclose(f([-1000, -1001, -np.inf]), [1 / (1 + np.exp(-1)), 1 / (1 + np.exp(1)), 0])
    for values in ([-np.inf, -np.inf], [0, np.nan], [np.inf, 0]):
        with pytest.raises(ValueError):
            f(values)


def test_beta_binomial_matches_independent_moment_formula() -> None:
    ns = source(3)
    a, b, n = 10, 4, 5
    mass = ns["predictive_mass"](np.arange(n + 1), n, a, b)
    expected = stats.betabinom.pmf(np.arange(n + 1), n, a, b)
    assert np.allclose(mass, expected)
    var = n * a * b * (a + b + n) / ((a + b) ** 2 * (a + b + 1))
    assert ns["run_cases"]()["predictive_variance"] == pytest.approx(var)


def test_change_of_variable_recovers_the_intended_moment() -> None:
    r = source(4)["run_cases"]()
    assert r["correct_theta_second_moment"] == pytest.approx(2 * 3 / (4 * 5), abs=1e-6)
    assert r["omitted_jacobian_second_moment"] == pytest.approx(1 / 3, abs=3e-5)
    assert r["transformed_normalizer"] == pytest.approx(1, abs=1e-8)


def test_regret_difference_equals_expected_net_value() -> None:
    r = source(5)["run_cases"]()
    assert r["regret_wait"] - r["regret_treat"] == pytest.approx(5 / 7, abs=1e-6)
    assert 0.5 < r["probability_benefit_positive"] < 1


def test_perfect_acceptance_can_be_a_degenerate_chain() -> None:
    values, acceptance = source(6)["metropolis"](0.0)
    assert acceptance == 1 and values.var() == 0 and len(values) == 2500


def test_leapfrog_reversibility_at_an_independent_state() -> None:
    leap = source(7)["leapfrog"]
    q, p = leap(-0.3, 1.1, 0.1, 7)
    rq, rp = leap(q, -p, 0.1, 7)
    assert rq == pytest.approx(-0.3, abs=1e-12) and rp == pytest.approx(-1.1, abs=1e-12)
    assert abs((q * q + p * p) - (0.3**2 + 1.1**2)) < 0.02


def test_sbc_checks_include_the_ignored_data_counterexample() -> None:
    r = source(8)["run_cases"]()
    assert r["biased_rank_mean"] < r["correct_rank_mean"] - 10
    assert abs(r["prior_only_rank_mean"] - 32) < 4
    assert r["ignored_data_conditional_error"] > 5 * r["correct_conditional_error"]


def test_exact_loo_matches_scalar_posterior_predictive_refits() -> None:
    f = source(14)["exact_normal_loo"]
    y = np.array([-0.2, 0.1, 0.5])
    sd = 0.4
    precision = 2.0
    expected = 0.0
    for i, value in enumerate(y):
        others = np.delete(y, i)
        variance = 1 / (precision + len(others) / sd**2)
        mean = variance * others.sum() / sd**2
        expected += float(stats.norm.logpdf(value, mean, np.sqrt(sd**2 + variance)))
    assert f(np.ones((3, 1)), y, np.array([[precision]]), sd) == pytest.approx(expected)


def test_stan_reference_distribution_and_transform_oracles() -> None:
    # These formulas are independent scientific targets, not compiler acceptance.
    variance = 1 / (1 / 4 + 5)
    mean = variance * 10
    assert mean == pytest.approx(40 / 21) and variance == pytest.approx(4 / 21)
    z = np.array([-2.0, 0.0, 1.0])
    rate = np.exp(z)
    log_transformed = stats.gamma.logpdf(rate, a=8, scale=1 / 6) + z
    independent_log_gamma = stats.loggamma.logpdf(z + np.log(6), c=8)
    assert np.allclose(log_transformed, independent_log_gamma)
    phi, sigma = 0.5, 0.2
    assert sigma**2 * (1 + phi**2 + phi**4) == pytest.approx(0.0525)
    shape, beta = 1.5, 0.3
    assert np.exp(-shape * beta) == pytest.approx(np.exp(beta) ** (-shape))


def test_standard_stan_project_has_validated_separate_data() -> None:
    project = BASE / "projects/normal-mean"
    ns = runpy.run_path(str(project / "run.py"))
    data = json.loads((project / "data.json").read_text())
    ns["validate_data"](data)
    for delta in (
        {"N": True},
        {"N": 4},
        {"prior_sd": 0},
        {"observation_sd": float("nan")},
        {"extra": 1},
    ):
        with pytest.raises(ValueError):
            ns["validate_data"]({**data, **delta})
    assert "data {" in (project / "model.stan").read_text()
    for path in (BASE / "examples").glob("*.stan"):
        assert "\ndata {" not in path.read_text() and path.read_text().startswith(
            ("transformed data", "//")
        )


@pytest.mark.parametrize("number", range(9, 17))
@pytest.mark.skipif(
    importlib.util.find_spec("pymc") is None,
    reason="Requires prepared Bayesian CPU packages; real container qualification is separate",
)
def test_prepared_bayesian_runtime_programs(number: int) -> None:
    result = source(number)["run_cases"]()
    assert isinstance(result, dict) and json.loads(json.dumps(result, allow_nan=False))
