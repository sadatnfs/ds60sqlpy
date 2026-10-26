"""Independent numerical and offline-source contracts for additive tutorials."""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import runpy
import socket
from pathlib import Path
from typing import Any

import numpy as np
import pytest

stats = pytest.importorskip("scipy.stats")

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "courses" / "statistics-ml"
TUTORIALS = BOOK / "tutorials"
INDEX = json.loads((TUTORIALS / "index.json").read_text())
UNITS = INDEX["units"]


def namespace(name: str) -> dict[str, Any]:
    return runpy.run_path(str(TUTORIALS / "authoring" / f"{name}_casebook.py"))


def test_ratio_uncertainty_matches_joint_covariance_and_rejects_undefined_target() -> None:
    ratio_summary = namespace("experiment")["ratio_summary"]
    numerator = np.array([1.0, 9.0, 4.0, 8.0])
    denominator = np.array([1.0, 3.0, 2.0, 4.0])
    ratio, se = ratio_summary(numerator, denominator)
    gradient = np.array([1 / denominator.mean(), -numerator.mean() / denominator.mean() ** 2])
    covariance_of_means = np.cov(np.stack([numerator, denominator]), ddof=1) / len(numerator)
    assert ratio == pytest.approx(2.2)
    assert se**2 == pytest.approx(gradient @ covariance_of_means @ gradient)
    independent_wrong = np.sum(gradient**2 * np.diag(covariance_of_means))
    assert not np.isclose(se**2, independent_wrong)
    with pytest.raises(ValueError, match="positive total"):
        ratio_summary(numerator, np.zeros(4))
    with pytest.raises(ValueError, match="at least two"):
        ratio_summary([1], [1])


def test_interval_coverage_matches_independent_binomial_event_calculation() -> None:
    result = namespace("learning")["case_01"]()
    # At p=.05,n=12 the Wald interval covers only counts 1,2,3;
    # Wilson covers counts 0,1,2. Sum those events independently.
    assert result["exact_wald_coverage_at_005"] == pytest.approx(
        stats.binom.cdf(3, 12, 0.05) - stats.binom.pmf(0, 12, 0.05)
    )
    assert result["exact_wilson_coverage_at_005"] == pytest.approx(stats.binom.cdf(2, 12, 0.05))


def test_aipw_expectation_under_each_single_correct_nuisance() -> None:
    score = namespace("science")["aipw_score"]
    e = np.array([0.2, 0.8])
    true_m0, true_m1 = np.array([1.0, 3.0]), np.array([4.0, 5.0])
    for ehat, m0hat, m1hat in (
        (e, np.zeros(2), np.ones(2)),
        (np.array([0.5, 0.5]), true_m0, true_m1),
    ):
        expected = e * score(1, true_m1, ehat, m0hat, m1hat)
        expected += (1 - e) * score(0, true_m0, ehat, m0hat, m1hat)
        assert np.allclose(expected, true_m1 - true_m0)
    wrong = e * score(1, true_m1, np.full(2, 0.5), np.zeros(2), np.ones(2))
    wrong += (1 - e) * score(0, true_m0, np.full(2, 0.5), np.zeros(2), np.ones(2))
    assert not np.allclose(wrong, true_m1 - true_m0)


def test_stable_logistic_objective_preserves_extreme_correct_and_wrong_predictions() -> None:
    objective = namespace("learning")["logistic_objective"]
    design = np.array([[-1000.0], [1000.0]])
    assert objective(np.array([1.0]), design, np.array([0, 1])) == pytest.approx(0)
    assert objective(np.array([1.0]), design, np.array([1, 0])) == pytest.approx(2000)


def test_competing_event_incidence_matches_observed_complete_followup_fraction() -> None:
    incidence = namespace("science")["cumulative_incidence"]
    for cause in (np.array([2, 1, 2, 1]), np.array([1, 2, 1, 2])):
        assert incidence(np.arange(1, 5), cause) == pytest.approx(np.mean(cause == 1))


def test_additive_route_preserves_real_content_and_local_links() -> None:
    assert INDEX["mode"] == "tutorial" and INDEX["schema_version"] == 1
    identifiers = {unit["id"] for unit in UNITS}
    assert len(identifiers) == len(UNITS)
    for unit in UNITS:
        guide = ROOT / unit["chapter_path"]
        assert guide.is_relative_to(BOOK) and guide.exists()
        text = guide.read_text()
        assert unit["mode"] == "tutorial" and unit["network"] == "offline"
        assert unit["concepts"] and unit["outcome"] and unit["expected_outputs"]
        assert "\u2014" not in text and "**Answered discussion:" in text
        assert not re.search(r"^#{1,4} (?:Exercises|Exam|Problem sets)\b", text, re.M | re.I)
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if target.startswith(("http:", "https:", "#")):
                continue
            resolved = (guide.parent / target.split("#", 1)[0]).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.exists(), (unit["id"], target)
        for relative in unit["example_paths"]:
            path = ROOT / relative
            assert path.is_relative_to(BOOK) and path.exists()
            source = path.read_text()
            tree = ast.parse(source)
            assert any(
                isinstance(node, ast.If) and "__name__" in ast.unparse(node.test)
                for node in tree.body
            )
            assert sum(isinstance(node, ast.Assert) for node in ast.walk(tree)) >= 2, unit["id"]
            assert "\u2014" not in source


@pytest.mark.parametrize("unit", UNITS, ids=lambda unit: unit["id"])
def test_standalone_program_works_without_sibling_files(
    unit: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    if unit["profile"] == "bayesian-cpu" and (
        importlib.util.find_spec("pymc") is None or importlib.util.find_spec("arviz") is None
    ):
        pytest.skip("Separate bayesian-cpu package/runtime qualification")

    def no_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("An offline scientific example attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.chdir(tmp_path)
    for relative in unit["example_paths"]:
        runpy.run_path(str(ROOT / relative), run_name="__main__")
    output = capsys.readouterr().out
    for label in unit["expected_outputs"]:
        assert label in output
