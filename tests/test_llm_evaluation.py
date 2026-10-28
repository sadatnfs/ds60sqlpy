"""Independent scientific and source contracts for the evaluation/alignment route."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import json
import math
import re
import runpy
import subprocess
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/llm-evaluation"


@cache
def reference(number: int, *, plot: bool = False) -> dict[str, Any]:
    suffix = "_plotly_reference.py" if plot else "_reference.py"
    return runpy.run_path(str(COURSE / "solutions" / f"eval-{number:03}{suffix}"))


def test_complete_route_and_independent_source_names() -> None:
    track = json.loads((COURSE / "track.json").read_text())
    authored = json.loads((COURSE / "lessons.json").read_text())
    assert [r["id"] for r in track["lessons"]] == [f"eval-{n:03}" for n in range(1, 25)]
    assert {r["level"] for r in track["lessons"]} == {"beginner", "intermediate", "advanced"}
    torch_ids = {r["id"] for r in authored["lessons"] if r["runtime_profile"] == "llm-torch-cpu"}
    assert torch_ids == {"eval-018", "eval-022"}
    plots: list[str] = []
    for row in authored["lessons"]:
        paths = [row["guide_path"], row["source_path"], *row["solution_paths"]]
        assert len(paths) == len(set(paths)) == 4
        assert all((ROOT / p).is_file() for p in paths)
        assert row["verification_id"] is None
        assert len((ROOT / row["source_path"]).read_bytes()) < 48_000
        plots.extend(row["id"] + "@" + v["id"] for v in row.get("variants", []))
    assert plots == ["eval-010@plotly", "eval-011@plotly", "eval-019@plotly"]


def test_full_authoring_round_trip() -> None:
    result = subprocess.run(
        [sys.executable, str(COURSE / "authoring/build.py"), "--check"],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_guide_depth_and_literal_math_contract() -> None:
    for number in range(1, 25):
        key = f"eval-{number:03}"
        source = (COURSE / "authoring/chapters" / f"{key}.md").read_text()
        guide = (COURSE / "guides" / f"{key}.md").read_text()
        unit = json.loads((COURSE / "authoring" / f"unit-{number:03}.json").read_text())
        assert len(re.findall(r"\b\w+\b", source)) >= 450
        assert guide.count("```python\n") == 2
        assert len(unit["exercises"]) == len({e["title"] for e in unit["exercises"]}) == 6
        assert len(unit["sources"]) >= 2
        assert "\u2014" not in guide
        assert "{{WORKED_" not in guide
        assert "## Primary references" in guide and "## Six investigations" in guide
        for title, link in unit["sources"]:
            assert title
            if not link.startswith("https://"):
                assert ((COURSE / "guides") / link).resolve().is_file(), link


def test_reference_contracts_bind_exact_programs() -> None:
    contracts = json.loads((COURSE / "fixtures/reference-contracts.json").read_text())["references"]
    assert len(contracts) == 27
    for row in contracts:
        source = (ROOT / row["reference"]).read_bytes()
        assert hashlib.sha256(source).hexdigest() == row["source_sha256"]
        assert row["expected_output"] in source.decode()
    plots = json.loads((COURSE / "figure-contracts.json").read_text())
    assert {r["id"] for r in plots["units"]} == {
        "eval-010@plotly",
        "eval-011@plotly",
        "eval-019@plotly",
    }
    assert all(
        r["kind"] == "plotly"
        and r["count"] == 1
        and r["description_required"]
        and r["table_required"]
        for r in plots["units"]
    )


@pytest.mark.parametrize("number", [n for n in range(1, 25) if n not in {18, 22}])
def test_complete_core_reference(number: int, capsys: pytest.CaptureFixture[str]) -> None:
    reference(number)["main"]()
    assert f"eval-{number:03}: all reference checks passed" in capsys.readouterr().out


@pytest.mark.parametrize("number", [18, 22])
def test_actual_torch_reference(number: int, capsys: pytest.CaptureFixture[str]) -> None:
    pytest.importorskip("torch", reason="Separate prepared PyTorch CPU worker qualification")
    reference(number)["main"]()
    assert f"eval-{number:03}: all reference checks passed" in capsys.readouterr().out


def test_estimands_do_not_confuse_requests_and_families() -> None:
    f = reference(1)["family_difference"]
    rows = [
        ("a", "x", 0, 1),
        ("b", "x", 0, 1),
        ("c", "x", 1, 1),
        ("d", "y", 1, 0),
        ("e", "z", 0, 1),
    ]
    assert f(rows) == pytest.approx(2 / 5)
    assert f(rows, "family") == pytest.approx(2 / 9)
    assert f(list(reversed(rows)), "family") == pytest.approx(2 / 9)
    with pytest.raises(ValueError):
        f(rows + [rows[0]])


def test_temporal_eligibility_and_group_leakage() -> None:
    n = reference(2)
    records = [
        {"id": "a", "event": 4, "label_available": 5},
        {"id": "b", "event": 5, "label_available": 9},
    ]
    assert n["training_ids"](records, 5) == ["a"]
    assert n["fingerprint"]("  SCORE\ncard ") == n["fingerprint"]("score card")
    with pytest.raises(ValueError):
        n["validate_split"](
            [
                {"id": "a", "family": "f", "split": "train"},
                {"id": "b", "family": "f", "split": "test"},
            ]
        )


def test_rubric_and_adjudication_keep_semantics() -> None:
    n = reference(3)
    assert n["rubric_score"]({"value": 2, "unit": 1, "unused": None}) == 0.75
    assert not n["admit"]({"value": 2}, None)
    labels = [
        {"item": "x", "annotator": "a", "label": 0, "rubric": "v1"},
        {"item": "x", "annotator": "b", "label": 2, "rubric": "v1"},
    ]
    original = copy.deepcopy(labels)
    resolved = n["adjudicate"](labels, "x", 1, "Boundary case")
    assert labels == original and resolved[-1]["parents"] == ["a", "b"]
    for bad in (True, 3, 0.5):
        with pytest.raises(ValueError):
            n["adjudicate"](labels, "x", bad, "Bad label")


def test_kappa_uses_both_empirical_marginals() -> None:
    observed, kappa, table = reference(4)["agreement"]([0, 0, 1, 1, 2], [0, 1, 1, 2, 2])
    assert observed == 0.6 and kappa == pytest.approx(7 / 17)
    assert table.sum() == 5
    assert reference(4)["ordinal_disagreement"]([0, 2], [2, 0]) == 1


def test_design_weights_keep_their_denominators() -> None:
    ht, normalized, ess = reference(5)["inclusion_estimates"]([2, 0, 1], [0.5, 1, 0.25], 10)
    assert ht == pytest.approx(0.8)
    assert normalized == pytest.approx(8 / 7)
    assert ess == pytest.approx(49 / 21)
    with pytest.raises(ValueError):
        reference(5)["target_mean"]({"a": float("nan")}, {"a": 1})


def test_exact_randomization_and_bootstrap_have_known_distributions() -> None:
    n = reference(6)
    assert n["sign_test"]([1, 1, 1, 1, -1])[0] == 0.375
    distribution = n["cluster_bootstrap"]([-2, 0, 5])
    assert len(distribution) == 27
    assert distribution.mean() == pytest.approx(1)
    assert distribution.var() == pytest.approx(26 / 9)
    with pytest.raises(ValueError):
        n["cluster_bootstrap"]([0, float("nan")])


def test_monitoring_budgets_do_not_turn_unknown_into_pass() -> None:
    n = reference(7)
    assert n["bonferroni"]([0.01, 0.02, 0.001, 0.5], alpha=0.04).tolist() == [
        True,
        False,
        True,
        False,
    ]
    with pytest.raises(ValueError):
        n["spent_decisions"]([0.01, 0.02], [0.03, 0.03])
    with pytest.raises(ValueError):
        n["spent_decisions"]([0.01], [0.01], alpha=float("nan"))


def test_ranking_convention_is_independent_of_library_default() -> None:
    result = reference(8)["retrieval_metrics"](["y", "x"], {"x": 2, "y": 1, "z": 0}, 2)
    expected = (1 + 3 / math.log2(3)) / (3 + 1 / math.log2(3))
    assert result == pytest.approx({"recall": 1, "mrr": 1, "ndcg": expected})
    with pytest.raises(ValueError):
        reference(8)["retrieval_metrics"](["x"], {"x": 1}, 1.5)


def test_citation_precision_is_distinct_from_claim_coverage() -> None:
    n = reference(9)
    assert n["citation_metrics"](["a", "b", "c", "d"], [("a", "doc")], {("a", "doc"): True}) == {
        "link_precision": 1,
        "claim_coverage": 0.25,
    }
    with pytest.raises(ValueError):
        n["citation_metrics"](["a"], [("a", "doc")], {("a", "doc"): None})
    assert not n["eligible_evidence"]({"id": "doc", "published": 11}, 10, {"doc"})


def test_selective_policy_rejects_fractional_binary_labels() -> None:
    n = reference(10)
    result = n["policy_metrics"]([0.1, 0.7, 0.9], [1, 0, 1], 0.5)
    assert result == pytest.approx({"coverage": 2 / 3, "accuracy": 0.5, "cost": 1.8})
    with pytest.raises(ValueError):
        n["policy_metrics"]([0.9], [0.5], 0.5)
    with pytest.raises(ValueError):
        n["policy_metrics"]([0.9], [1], 0.5, wrong_cost=-1)


def test_judge_orientation_and_calibration_boundaries() -> None:
    n = reference(11)
    assert n["identity_wins"]([1, 0, 0.5], [True, False, True]).tolist() == [1, 1, 0.5]
    brier, ece = n["calibration"]([0, 0.25, 0.5, 1], [0, 0, 1, 1])
    assert brier == 0.078125 and ece == 0.1875
    with pytest.raises(ValueError):
        n["calibration"]([0.5], [1], edges=(0, 0.5, 0.5, 1))
    with pytest.raises(ValueError):
        n["identity_wins"]([1], ["left"])


def test_crossed_decomposition_reconstructs_additive_data() -> None:
    model = np.array([1.0, 3.0])
    prompt = np.array([-0.5, 0, 0.5])
    noise = np.array([-0.1, 0.1])
    source = model[:, None, None] + prompt[None, :, None] + noise[None, None, :]
    cells, grand, m, p, interaction = reference(12)["decomposition"](source)
    np.testing.assert_allclose(interaction, 0, atol=1e-12)
    np.testing.assert_allclose(cells, grand + m[:, None] + p[None, :])


def test_selection_optimism_matches_closed_form() -> None:
    n = reference(13)
    for candidates in (1, 2, 3, 5):
        assert n["selection_optimism"](candidates) == pytest.approx(
            0.1 * (1 - 2 ** (1 - candidates))
        )
    selected, result = n["assess_procedure"]([[0.9, 0.8]], [[0.2, 0.99]])
    assert selected.tolist() == [0] and result.tolist() == [0.2]


def test_untrusted_text_cannot_grant_permission() -> None:
    n = reference(14)
    assert n["retrieve"]("public ignore rules restricted-note", {"public"}) == []
    with pytest.raises(ValueError):
        n["apply_proposal"](
            {"operation": "lookup", "record_id": "restricted-note"}, {"public-guide"}
        )
    with pytest.raises(ValueError):
        n["apply_proposal"](
            {"operation": "lookup", "record_id": "public-guide", "admin": True}, {"public-guide"}
        )


def test_drift_matches_squared_scipy_distance() -> None:
    distance = importlib.import_module("scipy.spatial.distance")
    p = [0.2, 0.3, 0.5]
    q = [0.6, 0.1, 0.3]
    assert reference(15)["js_divergence"](p, q) == pytest.approx(
        float(distance.jensenshannon(p, q)) ** 2
    )
    assert reference(15)["observed_cohort"]([], 0)["accuracy"] is None


def test_capstone_uses_only_the_actual_mature_holdout(monkeypatch: pytest.MonkeyPatch) -> None:
    n = reference(16)
    fixture = json.loads((COURSE / "fixtures/evaluation-corpus.json").read_text())
    assert n["RECORDS"] == fixture["records"]
    packet = n["fixture"]()
    assert packet["families"] == ["operations", "policy"]
    assert len(packet["eligible_ids"]) == 8
    assert packet["effect_estimate"] == 0
    assert [packet["effect_lower"], packet["effect_upper"]] == [-0.25, 0.25]
    assert packet["coverage"] == 0.75 and packet["critical_failures"] == 1
    assert n["decide"](packet)["failed"] == ["quality", "coverage", "critical_cases", "latency"]
    changed = copy.deepcopy(n["RECORDS"])
    for row in changed:
        if row["split"] != "test":
            row["candidate_correct"] = 1 - row["candidate_correct"]
    monkeypatch.setitem(n["fixture"].__globals__, "RECORDS", changed)
    assert n["fixture"]() == packet
    delayed = copy.deepcopy(changed)
    next(row for row in delayed if row["split"] == "test")["label_day"] = 7
    monkeypatch.setitem(n["fixture"].__globals__, "RECORDS", delayed)
    with pytest.raises(ValueError, match="mature labels"):
        n["fixture"]()
    edited = dict(packet, coverage=0.99)
    with pytest.raises(ValueError):
        n["verified_packet"](edited, n["digest"](packet))


def test_pairwise_likelihood_has_the_correct_gradient() -> None:
    n = reference(17)
    expected = 1 / (1 + math.exp(-1)) - 1
    np.testing.assert_allclose(n["pair_gradient"]([0.4, -0.6]), [expected, -expected])
    assert n["mle_difference"](9, 3) == pytest.approx(math.log(3))
    assert n["pair_loss"]([-500, 500]) == 1000


def test_kl_optimum_beats_a_grid_and_preserves_scale() -> None:
    n = reference(19)
    q = [0.3, 0.7]
    rewards = [2.0, -0.4]
    optimum = n["optimal_policy"](q, rewards, 0.8)
    maximum = n["objective"](optimum, q, rewards, 0.8)
    grid = [n["objective"]([p, 1 - p], q, rewards, 0.8) for p in np.linspace(0.001, 0.999, 100)]
    assert maximum >= max(grid) - 1e-12
    np.testing.assert_allclose(optimum, n["optimal_policy"](q, [20.0, -4.0], 8.0))
    with pytest.raises(ValueError):
        n["optimal_policy"](q, [float("nan"), 1], 0.8)


def test_dpo_beta_has_a_closed_form_finite_optimum() -> None:
    n = reference(20)
    delta = n["fitted_delta"](5, 2, 0.7, reference_delta=-0.3)
    assert delta == pytest.approx(-0.3 + math.log(2.5) / 0.7)
    assert n["dpo_gradient"](delta, -0.3, 0.7, 5 / 7) == pytest.approx(0, abs=1e-12)
    assert n["dpo_loss"](0, 0, 3) == pytest.approx(math.log(2))
    with pytest.raises(ValueError):
        n["dpo_loss"](0, 0, float("nan"))


def test_gae_termination_truncation_and_clipping_signs() -> None:
    n = reference(21)
    np.testing.assert_allclose(
        n["gae"]([0, 1], [0, 0, 2], [False, False], gamma=0.5, lam=1), [1, 2]
    )
    np.testing.assert_allclose(
        n["gae"]([0, 1], [0, 0, 2], [False, True], gamma=0.5, lam=1), [0.5, 1]
    )
    np.testing.assert_allclose(
        n["clipped_terms"]([2, 0.1, 0.1, 2], [2, 2, -2, -2]), [2.4, 0.2, -1.6, -4]
    )
    with pytest.raises(ValueError):
        n["gae"]([1], [0, 0], ["false"])


def test_group_relative_signal_and_kl_sampling_law() -> None:
    n = reference(23)
    np.testing.assert_allclose(n["group_advantages"]([1, 1, 3, 3]), [-1, -1, 1, 1])
    np.testing.assert_allclose(n["group_advantages"]([3, 3]), 0)
    p = np.array([0.7, 0.3])
    q = np.array([0.2, 0.8])
    k = n["kl_terms"](p, q)
    expected = 0.7 * math.log(0.7 / 0.2) + 0.3 * math.log(0.3 / 0.8)
    assert p @ k == pytest.approx(expected)
    assert not np.isclose(np.mean(k), expected)


def test_off_policy_estimators_recover_known_values_and_reject_missing_support() -> None:
    n = reference(24)
    behavior = [[0.5, 0.5]]
    target = [[0.25, 0.75]]
    log = [(0, 0, 2.0), (0, 1, 4.0)]
    result = n["estimate"](log, behavior, target, [[2.0, 4.0]])
    assert result["ips"] == result["snis"] == result["dr"] == 3.5
    assert result["weight_ess"] == pytest.approx(1.6)
    with pytest.raises(ValueError):
        n["policies"]([[1, 0]], target)
    with pytest.raises(ValueError):
        n["estimate"]([(-1, 0, 2.0)], behavior, target, [[2.0, 4.0]])


@pytest.mark.parametrize("number", [10, 11, 19])
def test_plotly_variants_have_real_data_and_accessible_tables(
    number: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    pio = pytest.importorskip("plotly.io")
    from ds60sqlpy.plot_artifacts import validate_artifacts

    captured: list[dict[str, Any]] = []

    def show(figure: Any, *_args: Any, **_kwargs: Any) -> None:
        captured.append(json.loads(pio.to_json(figure)))

    monkeypatch.setattr(pio, "show", show)
    reference(number, plot=True)["show_curve"]()
    checked = validate_artifacts([{"kind": "plotly", "figure": value} for value in captured])
    assert len(checked) == 1 and checked[0]["kind"] == "plotly"
    assert checked[0]["description"]
    assert checked[0]["table"]["rows"]
    if number == 10:
        assert checked[0]["table"]["rows"][-1][1:3] == [0.0, None]
    elif number == 11:
        assert [r[2] for r in checked[0]["table"]["rows"]] == [2, 2]
    else:
        y = [r[1] for r in checked[0]["table"]["rows"]]
        assert all(left > right for left, right in zip(y, y[1:], strict=False))


def test_all_worked_programs_are_complete_and_source_size_is_bounded() -> None:
    for path in (COURSE / "guides").glob("*.md"):
        programs = re.findall(r"```python\n(.*?)\n```", path.read_text(), re.DOTALL)
        assert len(programs) == 2
        for source in programs:
            ast.parse(source)
            assert "worked_a()" in source or "worked_b()" in source
    assert all(p.stat().st_size <= 48_000 for p in (COURSE / "lessons").glob("*.py"))
