"""Independent identities and publication contracts for the advanced Spark tutorial."""

from __future__ import annotations

import ast
import json
import math
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/advanced-spark-modeling"


def source(number: int) -> dict[str, Any]:
    return runpy.run_path(str(BASE / f"authoring/programs/asm-{number:03}.py"))


def test_all_chapters_have_complete_sources_and_fresh_outputs() -> None:
    track = json.loads((BASE / "track.json").read_text())
    manifest = json.loads((BASE / "lessons.json").read_text())
    assert track["learning_mode"] == "tutorial"
    assert [row["id"] for row in track["lessons"]] == [f"asm-{i:03}" for i in range(1, 39)]
    assert len(manifest["lessons"]) == 38
    for lesson in manifest["lessons"]:
        key = lesson["id"]
        prose = (BASE / "authoring/chapters" / f"{key}.md").read_text()
        guide = (ROOT / lesson["guide_path"]).read_text()
        program = (ROOT / lesson["source_path"]).read_text()
        assert len(prose.split()) >= 500 and prose.count("## Worked case") == 2
        assert "## Interview discussion" in prose and "## Failure diagnosis" in prose
        assert "\u2014" not in guide
        assert lesson["solution_paths"] == [] and lesson["verification_id"] is None
        if lesson["runtime_profile"] == "reading":
            assert lesson["language"] == "markdown"
            assert "no ordinary pad Run action" in guide
            assert program.strip() in guide
        else:
            assert "```" + lesson["language"] + "\n" + program.rstrip() + "\n```" in guide
        if lesson["language"] == "python":
            ast.parse(program)
    checked = subprocess.run(
        [sys.executable, str(BASE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr


def test_reading_projects_are_not_falsely_admitted_to_single_file_workers() -> None:
    manifest = json.loads((BASE / "lessons.json").read_text())
    reading = {row["id"] for row in manifest["lessons"] if row["runtime_profile"] == "reading"}
    assert reading == {"asm-018", "asm-021", "asm-022", "asm-023"} | {
        f"asm-{i:03}" for i in range(26, 39)
    }
    coverage = json.loads((BASE / "coverage.json").read_text())
    assert {key for area in coverage["areas"] for key in area["units"]} == {
        f"asm-{i:03}" for i in range(1, 39)
    }


@pytest.mark.parametrize("number", range(1, 13))
def test_public_python_sources_import_without_spark_or_execution(number: int) -> None:
    namespace = source(number)
    assert callable(namespace["run"]) and callable(namespace["session"])
    assert "spark" not in namespace


def test_shared_random_intercept_covariance_is_not_independent_marginals() -> None:
    ns = source(2)
    independent = ns["normal_nll"]([1.0, 1.0], 0.0, math.sqrt(2.0))
    coupled = ns["shared_intercept_nll"](1.0, 1.0, 1.0, 1.0)
    expected = math.log(2 * math.pi) + 0.5 * math.log(3) + 1 / 3
    assert coupled == pytest.approx(expected)
    assert coupled != pytest.approx(independent)
    assert ns["shared_intercept_nll"](1.0, 2.0, 1.0, 0.0) == pytest.approx(
        ns["normal_nll"]([1.0, 2.0], 0.0, 1.0)
    )
    with pytest.raises(ValueError):
        ns["normal_nll"]([1.0], 0.0, 0.0)
    with pytest.raises(ValueError):
        ns["shared_intercept_nll"](1.0, 2.0, 0.0, 1.0)


def test_group_numeric_lower_bound_rejects_invalid_dimensions() -> None:
    bound = source(4)["dense_numeric_lower_bound"]
    assert bound(2_000_000, 50) == 800_000_000
    assert bound(0, 50) == 0
    for rows, columns in [(-1, 1), (1, 0), (1.5, 2), (1, -1)]:
        with pytest.raises(ValueError):
            bound(rows, columns)


@pytest.mark.parametrize("z", [-1000.0, -20.0, -1.0, 0.0, 1.0, 20.0, 1000.0])
def test_stable_logit_primitives_match_independent_symmetry(z: float) -> None:
    ns = source(5)
    positive, negative = ns["softplus"](z), ns["softplus"](-z)
    assert math.isfinite(positive) and positive >= 0
    assert positive - negative == pytest.approx(z)
    assert ns["sigmoid"](z) + ns["sigmoid"](-z) == pytest.approx(1.0)


def test_logistic_gradient_has_correct_coordinates_and_normalization() -> None:
    oracle = source(6)["oracle"]
    rows = [(-1.0, 0.0), (2.0, 1.0), (3.0, 0.0)]
    loss, gradient = oracle(rows, [0.0, 0.0])
    assert loss == pytest.approx(3 * math.log(2))
    assert gradient == pytest.approx((0.5, 0.0))
    double_loss, double_gradient = oracle(rows + rows, [0.0, 0.0])
    assert double_loss == pytest.approx(2 * loss)
    assert double_gradient == pytest.approx(tuple(2 * g for g in gradient))
    beta = [0.3, -0.7]
    _, grad = oracle(rows, beta)
    for index in range(2):
        step = 1e-5
        plus, minus = list(beta), list(beta)
        plus[index] += step
        minus[index] -= step
        numerical = (oracle(rows, plus)[0] - oracle(rows, minus)[0]) / (2 * step)
        assert grad[index] == pytest.approx(numerical, abs=1e-9)


def test_retry_summary_reconciliation_rejects_conflicting_identity() -> None:
    ns = source(9)
    identity = ("dataset-v1", "theta-v1", "logical-chunk-a")
    value = ns["summary"]([1.0, 3.0])
    assert ns["reconcile"]([(identity, value), (identity, value)]) == {identity: value}
    with pytest.raises(ValueError, match="disagrees"):
        ns["reconcile"]([(identity, value), (identity, {"count": 1, "sum": 4.0})])
    assert (
        len(
            ns["reconcile"](
                [(identity, value), (("dataset-v1", "theta-v2", "logical-chunk-a"), value)]
            )
        )
        == 2
    )


def test_profile_fit_matches_independent_residual_calculation() -> None:
    fit = source(10)["profile_fit"]
    u, y = [1.0, 0.5, 0.25, 0.125], [2.6, 1.4, 1.1, 0.7]
    a, c, variance, loss = fit(
        len(u),
        sum(u),
        sum(x * x for x in u),
        sum(y),
        sum(x * z for x, z in zip(u, y, strict=True)),
        sum(z * z for z in y),
    )
    residuals = [z - a * x - c for x, z in zip(u, y, strict=True)]
    expected = sum(r * r for r in residuals) / len(u)
    assert variance == pytest.approx(expected, abs=1e-14)
    assert sum(residuals) == pytest.approx(0.0, abs=1e-12)
    assert sum(r * x for r, x in zip(residuals, u, strict=True)) == pytest.approx(0.0, abs=1e-12)
    assert loss == pytest.approx(len(u) * (math.log(2 * math.pi * expected) + 1) / 2)
    with pytest.raises(ValueError, match="identifiable"):
        fit(3, 3, 3, 6, 6, 14)
    with pytest.raises(ValueError, match="positive residual"):
        fit(2, 1, 1, 1, 1, 1)


def test_joint_pair_covariance_retains_cross_terms() -> None:
    nll = source(11)["pair_nll"]
    assert nll(1.0, 2.0, 0.0) == pytest.approx(math.log(2 * math.pi) + 2.5)
    assert nll(1.0, 1.0, 0.8) < nll(1.0, -1.0, 0.8)
    for rho in [-1.0, 1.0, 1.1]:
        with pytest.raises(ValueError):
            nll(1.0, 1.0, rho)


def test_ar1_initial_state_and_transition_boundary() -> None:
    nll = source(12)["series_nll"]
    values = [1.0, 0.9, 0.6, 0.5]
    phi, sigma = 0.7, 0.5
    stationary_variance = sigma**2 / (1 - phi**2)
    expected = 0.5 * (
        math.log(2 * math.pi * stationary_variance) + values[0] ** 2 / stationary_variance
    )
    expected += sum(
        0.5 * (math.log(2 * math.pi * sigma**2) + (b - phi * a) ** 2 / sigma**2)
        for a, b in zip(values, values[1:], strict=False)
    )
    assert nll(values, phi, sigma) == pytest.approx(expected)
    assert nll(values[:2], phi, sigma) + nll(values[2:], phi, sigma) != pytest.approx(expected)
    for invalid_phi, invalid_sigma in [(1.0, 1.0), (0.0, 0.0)]:
        with pytest.raises(ValueError):
            nll(values, invalid_phi, invalid_sigma)


def test_coupled_laplace_and_posterior_reference_arithmetic() -> None:
    determinant = 2.0 * 2.0 - 1.0 * 1.0
    assert 0.5 * math.log(4.0 / determinant) == pytest.approx(0.14384103622589042)
    posterior_precision = 2.0 / 1.0 + 1.0 / 1.0
    posterior_mean = (4.0 / 1.0 + 0.0 / 1.0) / posterior_precision
    assert posterior_mean == pytest.approx(4.0 / 3.0)
    assert posterior_mean != pytest.approx(2.0)
