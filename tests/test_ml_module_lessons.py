"""Offline teaching/reference contracts for the two authored ML course slices."""

from __future__ import annotations

import ast
import importlib.util
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("deep-learning-tensorflow", "llm-theory")


def _module(track: str, lesson_id: str, *, learner: bool = False) -> Any:
    folder = "lessons" if learner else "solutions"
    name = lesson_id if learner else f"{lesson_id}_solution"
    path = ROOT / "courses" / track / folder / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _entries() -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    for track in TRACKS:
        payload = json.loads((ROOT / "courses" / track / "lessons.json").read_text())
        assert payload["schema_version"] == 1 and payload["track_id"] == track
        result.extend((track, entry) for entry in payload["lessons"])
    return result


def test_authored_inventory_has_real_paths_and_planned_identity() -> None:
    for track, entry in _entries():
        plan = json.loads((ROOT / "docs/expansion/plans" / f"{track}.json").read_text())
        assert entry["id"] in {lesson["id"] for lesson in plan["lessons"]}
        assert entry["status"] == "authored"
        assert entry["runtime_profile"] in plan["runtime_profiles"]
        assert entry["language"] in {"markdown", "python"}
        for relative in (entry["source_path"], entry["guide_path"], *entry["solution_paths"]):
            path = ROOT / relative
            assert path.is_file() and path.resolve().is_relative_to(ROOT / "courses" / track)
            source = path.read_text()
            assert "\u2014" not in source
            if path.suffix == ".py":
                ast.parse(source, filename=relative)
        if entry["runtime_profile"] == "reading":
            assert entry["language"] == "markdown" and entry["verification_id"] is None
        else:
            assert entry["language"] == "python"
        guide = (ROOT / entry["guide_path"]).read_text()
        assert len(re.findall(r"^\s*[1-6]\. \*\*", guide, re.MULTILINE)) == 6
        assert guide.count("**Expected:**") >= 8
        assert guide.count("**Verify:**") >= 6
        assert entry["guide_path"] in guide and entry["source_path"] in guide
        assert "## Ask Codex about this lesson" in guide
        for relative in entry["solution_paths"]:
            if relative.endswith(".md"):
                solution = (ROOT / relative).read_text()
                assert re.findall(r"^## Exercise ([1-6]):", solution, re.MULTILINE) == list(
                    "123456"
                )


@pytest.mark.parametrize(
    ("track", "lesson_id"),
    [
        ("deep-learning-tensorflow", "tf-001"),
        ("deep-learning-tensorflow", "tf-002"),
        ("deep-learning-tensorflow", "tf-003"),
        ("deep-learning-tensorflow", "tf-004"),
        ("deep-learning-tensorflow", "tf-005"),
        ("deep-learning-tensorflow", "tf-006"),
        ("llm-theory", "llm-001"),
        ("llm-theory", "llm-002"),
        ("llm-theory", "llm-003"),
        ("llm-theory", "llm-004"),
        ("llm-theory", "llm-005"),
        ("llm-theory", "llm-006"),
        ("llm-theory", "llm-007"),
        ("llm-theory", "llm-008"),
        ("llm-theory", "llm-009"),
    ],
)
def test_reference_exercise_checks(track: str, lesson_id: str) -> None:
    assert isinstance(_module(track, lesson_id).verify(), dict)


def test_split_validation_rejects_duplicate_groups_and_empty_evidence() -> None:
    module = _module("deep-learning-tensorflow", "tf-001")
    overlap = [dict(row) for row in module.HOLDOUT]
    overlap[0]["group"] = module.TRAIN[0]["group"]
    with pytest.raises(ValueError, match="group"):
        module.validate_split(module.TRAIN, overlap)
    with pytest.raises(ValueError, match="nonempty"):
        module.mse([], [])
    with pytest.raises(ValueError, match="equal-length"):
        module.mse([1], [1, 2])
    assert module.validate_split(module.TRAIN, module.HOLDOUT)


def test_pairing_guard_catches_broadcast_and_nonfinite_values() -> None:
    module = _module("deep-learning-tensorflow", "tf-002")
    with pytest.raises(ValueError, match="shape"):
        module.paired_difference([1, 2, 3], [[2], [4], [6]])
    with pytest.raises(ValueError, match="finite"):
        module.paired_difference([1, math.inf], [1, 2])
    result = module.paired_difference([100, 200], [1, 2])
    np.testing.assert_array_equal(result, [99, 198])


def test_affine_validates_output_axis_and_finite_inputs() -> None:
    module = _module("deep-learning-tensorflow", "tf-003")
    with pytest.raises(ValueError, match="bias"):
        module.affine([[1, 2]], [[1], [2]], [1, 2])
    with pytest.raises(ValueError, match="finite"):
        module.affine([[1, math.nan]], [[1], [2]], 0)
    np.testing.assert_array_equal(module.affine([[1, 2]], [[1], [2]], [3]), [[8]])


def test_family_evaluation_does_not_count_repeated_records() -> None:
    module = _module("llm-theory", "llm-001")
    row = {"id": "q1", "family": "A", "correct": True}
    with pytest.raises(ValueError, match="duplicate"):
        module.evaluate([row, dict(row)])
    with pytest.raises(TypeError, match="boolean"):
        module.evaluate([{**row, "correct": "yes"}])


def test_softmax_has_explicit_mask_and_shift_contracts() -> None:
    module = _module("llm-theory", "llm-002")
    expected = module.softmax([0, math.log(3)])
    np.testing.assert_allclose(
        module.softmax([1000, 1000 + math.log(3)]), expected, rtol=0, atol=1e-12
    )
    with pytest.raises(ValueError, match="allowed"):
        module.softmax([0, 0], [False, False])
    with pytest.raises(TypeError, match="boolean"):
        module.softmax([0, 0], [1, 0])


def test_likelihood_distinguishes_underflow_and_impossibility() -> None:
    module = _module("llm-theory", "llm-003")
    underflow = module.sequence_score([0.01] * 1000)
    impossible = module.sequence_score([0.01, 0])
    assert underflow["probability"] == impossible["probability"] == 0
    assert math.isfinite(underflow["nll"]) and math.isinf(impossible["nll"])
    with pytest.raises(ValueError, match="finite"):
        module.sequence_score([math.nan])
    with pytest.raises(TypeError, match="boolean"):
        module.sequence_score([True])


def test_causal_pilot_learner_matches_typed_fixture() -> None:
    module = _module("llm-theory", "llm-009", learner=True)
    fixture = json.loads(
        (ROOT / "courses/llm-theory/fixtures/llm-causal-attention-v1.json").read_text()
    )
    q, k, v = (np.asarray(fixture[key], dtype=np.float64) for key in ("q", "k", "v"))
    mask = np.asarray(fixture["allowed"], dtype=bool)
    output, weights = module.attention(q, k, v, mask)
    np.testing.assert_allclose(output, fixture["expected_output"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(weights, fixture["expected_weights"], rtol=0, atol=1e-12)
    for cut in range(1, len(q) + 1):
        prefix, _ = module.attention(q[:cut], k[:cut], v[:cut], np.tri(cut, dtype=bool))
        np.testing.assert_allclose(output[:cut], prefix, rtol=0, atol=1e-12)
    broken = mask.copy()
    broken[1] = False
    with pytest.raises(ValueError, match="each query needs at least one key"):
        module.attention(q, k, v, broken)
    with pytest.raises(TypeError, match="boolean"):
        module.attention(q, k, v, mask.astype(int))


def test_tensorflow_fixture_has_independent_fraction_oracle() -> None:
    fixture = json.loads(
        (ROOT / "courses/deep-learning-tensorflow/fixtures/tf-gradient-v1.json").read_text()
    )
    for case in fixture["cases"]:
        rate = Fraction(str(case["kwargs"]["rate"]))
        weight = Fraction(str(case["kwargs"]["initial_weight"]))
        before = Fraction(14, 3) * (weight - 2) ** 2
        gradient = Fraction(28, 3) * (weight - 2)
        updated = weight - rate * gradient
        expected = {
            "loss_before": before,
            "gradient": gradient,
            "weight_after": updated,
            "loss_after": Fraction(14, 3) * (updated - 2) ** 2,
        }
        for name, value in expected.items():
            assert math.isclose(float(value), case["expected"][name], rel_tol=0, abs_tol=1e-12)


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TENSORFLOW") != "1",
    reason="TensorFlow execution requires an explicitly qualified optional runtime",
)
def test_tensorflow_reference_and_public_callable_in_qualified_runtime() -> None:
    tape_reference = _module("deep-learning-tensorflow", "tf-007")
    assert tape_reference.verify()["gradient"] == -4
    reference = _module("deep-learning-tensorflow", "tf-008")
    learner = _module("deep-learning-tensorflow", "tf-008", learner=True)
    assert reference.verify()["checks"] == 6
    fixture = json.loads(
        (ROOT / "courses/deep-learning-tensorflow/fixtures/tf-gradient-v1.json").read_text()
    )
    for case in fixture["cases"]:
        result = learner.gradient_step(**case["kwargs"])
        for key, expected in case["expected"].items():
            assert math.isclose(result[key], expected, rel_tol=0, abs_tol=1e-12)
    with pytest.raises(ValueError):
        learner.gradient_step(rate=0)


def test_nonuniform_attention_fixture_detects_wrong_computations() -> None:
    module = _module("llm-theory", "llm-009", learner=True)
    fixture = json.loads(
        (ROOT / "courses/llm-theory/fixtures/llm-causal-attention-v1.json").read_text()
    )
    cases = fixture["cases"]
    assert len(cases) == 4

    def check(candidate: Any, case: dict[str, Any]) -> None:
        query, key, value = (np.asarray(case[name], dtype=np.float64) for name in ("q", "k", "v"))
        output, weights = candidate(query, key, value, np.asarray(case["allowed"], dtype=bool))
        np.testing.assert_allclose(weights, case["expected_weights"], rtol=0, atol=1e-12)
        np.testing.assert_allclose(output, case["expected_output"], rtol=0, atol=1e-12)

    for case in cases:
        check(module.attention, case)
    full = cases[0]
    e2 = math.exp(2)
    assert math.isclose(full["expected_weights"][1][1], e2 / (1 + e2), rel_tol=0, abs_tol=1e-12)
    np.testing.assert_allclose(
        cases[-1]["expected_output"][:2], full["expected_output"][:2], rtol=0, atol=1e-12
    )

    def ignores_scores(query: Any, key: Any, value: Any, allowed: Any) -> Any:
        return module.attention(np.zeros_like(query), np.zeros_like(key), value, allowed)

    def missing_scale(query: Any, key: Any, value: Any, allowed: Any) -> Any:
        masked = np.where(allowed, query @ key.T, -np.inf)
        mass = np.exp(masked - masked.max(axis=1, keepdims=True))
        weights = mass / mass.sum(axis=1, keepdims=True)
        return weights @ value, weights

    def wrong_axis(query: Any, key: Any, value: Any, allowed: Any) -> Any:
        masked = np.where(allowed, (query @ key.T) / np.sqrt(query.shape[1]), -np.inf)
        mass = np.exp(masked - masked.max(axis=0, keepdims=True))
        weights = mass / mass.sum(axis=0, keepdims=True)
        return weights @ value, weights

    def swapped_query_key(query: Any, key: Any, value: Any, allowed: Any) -> Any:
        return module.attention(key, query, value, allowed)

    for mutant in (ignores_scores, missing_scale, wrong_axis, swapped_query_key):
        with pytest.raises(AssertionError):
            check(mutant, full)


def test_authored_lessons_meet_shared_depth_and_practice_contracts() -> None:
    from ds60sqlpy.catalog import Catalog, Lesson
    from scripts.audit_lesson_depth import audit
    from scripts.audit_practice import count_practice

    lessons = []
    for track, entry in _entries():
        plan = json.loads((ROOT / "docs/expansion/plans" / f"{track}.json").read_text())
        spec = next(item for item in plan["lessons"] if item["id"] == entry["id"])
        lessons.append(
            Lesson(
                id=spec["id"],
                track=track,
                day=int(spec["id"].rsplit("-", 1)[1]),
                title=spec["title"],
                level=spec["level"],
                phase="Foundation",
                estimated_minutes=spec["minutes"],
                prerequisites=tuple(spec["prerequisites"]),
                lesson_path=entry["source_path"],
                guide_path=entry["guide_path"],
                solution_paths=tuple(entry["solution_paths"]),
                dependency_group="core",
                network="offline",
                runner="none" if entry["language"] == "markdown" else "python",
            )
        )
        assert count_practice(ROOT / entry["source_path"]) >= 6
        assert count_practice(ROOT / entry["guide_path"]) >= 6
        for relative in entry["solution_paths"]:
            assert count_practice(ROOT / relative, solution=True) >= 6
    tracks = {track: {"title": track, "plan": f"courses/{track}/README.md"} for track in TRACKS}
    measured = audit(Catalog(ROOT, lessons, tracks=tracks))
    assert len(measured) == len(_entries())
    assert not [(row.lesson_id, row.issues) for row in measured if not row.passes]


def test_loss_reduction_rejects_nonfinite_and_wrong_mask_shape() -> None:
    module = _module("deep-learning-tensorflow", "tf-004")
    with pytest.raises(ValueError, match="finite"):
        module.reduce_squared([math.inf])
    with pytest.raises(ValueError, match="mask"):
        module.reduce_squared([1, 2], mask=[True])
    assert module.reduce_squared([1, -1, 2], mask=[True, True, False]) == 1


def test_finite_difference_rejects_invalid_function_values() -> None:
    module = _module("deep-learning-tensorflow", "tf-005")
    with pytest.raises(ValueError, match="positive"):
        module.central_difference(lambda value: value * value, 0, -0.1)
    with pytest.raises(ValueError, match="probe"):
        module.central_difference(lambda value: math.inf, 0, 0.1)
    assert math.isclose(
        module.central_difference(lambda value: (value + 1) ** 2, 0, 0.01),
        2,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_chain_trace_has_distinct_state_and_dependency_values() -> None:
    module = _module("deep-learning-tensorflow", "tf-006")
    assert module.chain_trace(1)["loss"] == 9
    assert module.chain_trace(1)["gradient"] == 48
    assert module.chain_trace(1, 3)["gradient"] == 288
    with pytest.raises(ValueError, match="finite"):
        module.chain_trace(math.nan)


def test_bigram_fit_has_no_validation_or_document_boundary_update() -> None:
    module = _module("llm-theory", "llm-004")
    vocabulary = ["A", "B", "C"]
    counts = module.fit_bigram([["A"], ["B"]], vocabulary)
    assert counts.sum() == 0
    saved = counts.copy()
    np.testing.assert_allclose(
        module.next_probabilities(counts, "Z", vocabulary), [1 / 3] * 3, rtol=0, atol=1e-12
    )
    np.testing.assert_array_equal(counts, saved)
    with pytest.raises(ValueError, match="unknown"):
        module.fit_bigram([["Z"]], vocabulary)


def test_perplexity_counts_active_targets_and_preserves_infinity() -> None:
    module = _module("llm-theory", "llm-005")
    base = module.score_targets([0.5, 0.25])
    assert base == module.score_targets([0.5, 0.25, 0], [True, True, False])
    impossible = module.score_targets([0])
    assert math.isinf(impossible["mean_nll"]) and math.isinf(impossible["perplexity"])
    with pytest.raises(ValueError, match="finite"):
        module.score_targets([math.nan])


def test_unicode_raw_and_canonical_identity_are_separate() -> None:
    module = _module("llm-theory", "llm-006")
    composed, decomposed = "é", "e" + chr(0x0301)
    assert module.encode_record(composed)["payload"] != module.encode_record(decomposed)["payload"]
    assert (
        module.encode_record(composed, "NFC")["sha256"]
        == module.encode_record(decomposed, "NFC")["sha256"]
    )
    with pytest.raises(UnicodeDecodeError):
        module.decode_utf8(b"\xc3")
    with pytest.raises(TypeError, match="string"):
        module.encode_record(b"text")


def test_byte_pair_rules_are_ordered_frozen_and_reversible() -> None:
    module = _module("llm-theory", "llm-007")
    rules = module.fit_bpe(["ab", "ac"], 1)
    assert rules == module.fit_bpe(["ac", "ab"], 1)
    before = module.merge_hash(rules)
    assert module.decode_tokens(module.encode_word("🙂", rules)) == "🙂"
    assert module.merge_hash(rules) == before
    with pytest.raises(ValueError, match="marker"):
        module.decode_tokens([(256,), (97,)])
    with pytest.raises(ValueError, match="integer"):
        module.fit_bpe(["ab"], True)


def test_embedding_rejects_wrap_and_returns_owned_rows() -> None:
    module = _module("llm-theory", "llm-008")
    table = np.array([[1, 0], [0, 1], [2, 2], [-1, 1]], dtype=np.float64)
    saved = table.copy()
    with pytest.raises(ValueError, match="outside"):
        module.lookup(table, [-1])
    with pytest.raises(TypeError, match="integer"):
        module.lookup(table, [True])
    output = module.lookup(table, [2, 0, 2])
    output[0, 0] = 999
    np.testing.assert_array_equal(output[2], [2, 2])
    np.testing.assert_array_equal(table, saved)
