"""Offline teaching/reference contracts for the two authored ML course slices."""

from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

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


def test_complete_ml_plans_have_no_missing_or_extra_authored_ids() -> None:
    for track in TRACKS:
        planned = json.loads((ROOT / "docs/expansion/plans" / f"{track}.json").read_text())
        authored = [entry for name, entry in _entries() if name == track]
        assert {entry["id"] for entry in authored} == {item["id"] for item in planned["lessons"]}
        assert len(authored) == (36 if track == "deep-learning-tensorflow" else 48)
        specifications = {item["id"]: item for item in planned["lessons"]}
        for entry in authored:
            assert entry["runtime_profile"] == specifications[entry["id"]]["runtime"]


def _completed_reference_cases(profile: str) -> list[tuple[str, str]]:
    return [
        (track, entry["id"])
        for track, entry in _entries()
        if entry["runtime_profile"] == profile
        and int(entry["id"].rsplit("-", 1)[1]) > (8 if track == TRACKS[0] else 9)
    ]


@pytest.mark.parametrize(("track", "lesson_id"), _completed_reference_cases("python-core"))
def test_new_core_reference_exercises_execute(track: str, lesson_id: str) -> None:
    assert _module(track, lesson_id).verify() == {"checks": 6, "status": "passed"}


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TENSORFLOW") != "1",
    reason="TensorFlow reference execution requires an explicitly prepared CPU runtime",
)
@pytest.mark.parametrize(("track", "lesson_id"), _completed_reference_cases("tensorflow-cpu"))
def test_completed_tensorflow_reference_exercises(track: str, lesson_id: str) -> None:
    assert _module(track, lesson_id).verify() == {"checks": 6, "status": "passed"}


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1",
    reason="PyTorch reference execution requires an explicitly prepared CPU runtime",
)
@pytest.mark.parametrize(("track", "lesson_id"), _completed_reference_cases("llm-torch-cpu"))
def test_completed_torch_reference_exercises(track: str, lesson_id: str) -> None:
    assert _module(track, lesson_id).verify() == {"checks": 6, "status": "passed"}


def test_tool_proposal_validation_copies_only_an_allowed_shape() -> None:
    module = _module("llm-theory", "llm-038")
    original = {"tool": "read_fixture", "document_id": "d2"}
    accepted = module.validate(original)
    accepted["document_id"] = "d1"
    assert original["document_id"] == "d2"
    for invalid_shape in [None, ["read_fixture", "d1"], 1]:
        with pytest.raises(TypeError):
            module.validate(invalid_shape)
    for value in [
        {"tool": "read_fixture", "document_id": "/etc/passwd"},
        {"tool": "read_fixture", "document_id": "d1", "args": {}},
        {"tool": "write_fixture", "document_id": "d1"},
    ]:
        with pytest.raises(ValueError):
            module.validate(value)


def test_local_retrieval_ranking_uses_content_and_deterministic_ties() -> None:
    module = _module("llm-theory", "llm-036")
    documents = {"z": "red square", "a": "blue square", "b": "red circle"}
    assert module.rank("red square", documents, 1) == ["z"]
    assert module.rank("square", documents, 2) == ["a", "z"]
    assert module.rank("absent", documents, 2) == ["a", "b"]
    assert module.rank("red", documents, 0) == []


def test_tokenwise_normalization_preserves_prefix_but_time_centering_does_not() -> None:
    module = _module("llm-theory", "llm-010")
    values = np.array([[2.0, 6.0, 10.0], [1.0, 3.0, 5.0], [30.0, 40.0, 50.0]])
    full = module.layer_norm(values)
    np.testing.assert_allclose(module.layer_norm(values[:1]), full[:1], atol=1e-12, rtol=0)
    assert not np.allclose((values - values.mean(axis=0))[:1], values[:1] - values[:1].mean(axis=0))


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1", reason="Requires prepared PyTorch CPU runtime"
)
def test_decoder_cache_has_nonuniform_prefix_and_context_limit_controls() -> None:
    torch = importlib.import_module("torch")

    module = _module("llm-theory", "llm-024")
    torch.manual_seed(19)
    model = module.TinyDecoder(vocab=12, width=8, heads=2, context=5).eval()
    ids = torch.tensor([[1, 4, 2, 7, 3]])
    with torch.no_grad():
        full, _ = model(ids)
        first, cache = model(ids[:, :2])
        rest, cache = model(ids[:, 2:], cache)
        torch.testing.assert_close(torch.cat([first, rest], 1), full, atol=1e-6, rtol=0)
        with pytest.raises(ValueError, match="context"):
            model(torch.tensor([[1]]), cache)
        foreign_batch = {"k": cache["k"].repeat(2, 1, 1, 1), "v": cache["v"].repeat(2, 1, 1, 1)}
        # Shorten the foreign cache so the batch check runs before the context limit.
        foreign_batch = {name: value[:, :, :1] for name, value in foreign_batch.items()}
        with pytest.raises(ValueError, match="batch"):
            model(torch.tensor([[1]]), foreign_batch)


@pytest.mark.parametrize(
    ("track", "lesson_id"),
    [
        ("deep-learning-tensorflow", "tf-028"),
        ("deep-learning-tensorflow", "tf-032"),
        ("llm-theory", "llm-022"),
    ],
)
def test_fresh_process_reference_programs_compile_without_heavy_imports(
    track: str, lesson_id: str
) -> None:
    import textwrap

    path = ROOT / "courses" / track / "solutions" / f"{lesson_id}_solution.py"
    tree = ast.parse(path.read_text())
    programs = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not any(
            isinstance(target, ast.Name) and target.id == "program" for target in node.targets
        ):
            continue
        assert isinstance(node.value, ast.Call)
        assert isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "dedent"
        assert len(node.value.args) == 1 and isinstance(node.value.args[0], ast.Constant)
        assert isinstance(node.value.args[0].value, str)
        program = textwrap.dedent(node.value.args[0].value)
        compile(program, f"{lesson_id}-child", "exec")
        programs.append(program)
    assert len(programs) == 1
    source = path.read_text()
    assert "result.stderr" in source and "check=False" in source


def test_expert_rotary_positions_preserve_relative_dot_products_and_norms() -> None:
    module = _module("llm-theory", "llm-044")
    query = np.array([[1.0, 2.0, 3.0, 4.0]])
    key = np.array([[-1.0, 0.0, 2.0, 1.0]])
    first = float(module.rope(query, np.array([3]))[0] @ module.rope(key, np.array([8]))[0])
    shifted = float(module.rope(query, np.array([103]))[0] @ module.rope(key, np.array([108]))[0])
    relative = float(query[0] @ module.rope(key, np.array([5]))[0])
    np.testing.assert_allclose([first, shifted], [relative, relative], atol=1e-12, rtol=0)
    with pytest.raises(ValueError):
        module.rope(np.ones((2, 3)), np.array([0, 1]))
    with pytest.raises(ValueError):
        module.rope(np.ones((2, 4)), np.array([0]))


def test_online_softmax_rescales_both_numerator_and_denominator() -> None:
    module = _module("llm-theory", "llm-046")
    scores = np.array([0.0, 1000.0])
    values = np.array([[1.0], [10.0]])
    actual, peak = module.online_row(scores, values, 1)
    np.testing.assert_allclose(actual, [10.0], atol=1e-12, rtol=0)
    assert peak == 1
    # A concrete mutant rescales the denominator but keeps the old numerator.
    old_numerator = 1.0
    new_mass = 1.0
    wrong = (old_numerator + new_mass * 10) / (0.0 + new_mass)
    assert wrong == 11 and not np.allclose(actual, wrong)
    shifted, _ = module.online_row(scores + 5000, values, 1)
    np.testing.assert_allclose(shifted, actual, atol=1e-12, rtol=0)
    with pytest.raises(ValueError):
        module.online_row([], np.empty((0, 1)), 1)


def test_grouped_attention_uses_contiguous_query_groups_and_rejects_nan() -> None:
    module = _module("llm-theory", "llm-046")
    query = np.zeros((4, 2, 2))
    keys = np.zeros((2, 2, 2))
    values = np.array([[[1.0, 0.0], [3.0, 0.0]], [[0.0, 2.0], [0.0, 4.0]]])
    actual = module.gqa(query, keys, values)
    np.testing.assert_array_equal(actual[0], actual[1])
    np.testing.assert_array_equal(actual[2], actual[3])
    assert not np.array_equal(actual[1], actual[2])
    bad = query.copy()
    bad[0, 0, 0] = np.nan
    with pytest.raises(ValueError):
        module.gqa(bad, keys, values)


def test_sparse_expert_capacity_keeps_overflow_tokens_on_residual_path() -> None:
    module = _module("llm-theory", "llm-047")
    values = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    logits = np.array([[4.0, 0.0], [3.0, 0.0], [2.0, 0.0]])
    experts = np.stack([np.eye(2), 2 * np.eye(2)])
    output, dropped, assigned, accepted = module.capacity_route(values, logits, experts, 1)
    assert assigned.tolist() == [3, 0] and accepted.tolist() == [1, 0]
    assert dropped.tolist() == [False, True, True]
    np.testing.assert_array_equal(output[1:], values[1:])
    np.testing.assert_array_equal(output[0], 2 * values[0])


def test_sparse_router_auxiliary_gradient_has_the_expected_direction() -> None:
    module = _module("llm-theory", "llm-047")
    probabilities = np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.9], [0.9, 0.1]])
    logits = np.log(probabilities)
    fractions = np.array([0.75, 0.25])
    coefficient = 0.01

    def loss(value: NDArray[np.float64]) -> float:
        return float(coefficient * 2 * np.dot(fractions, module.softmax_rows(value).mean(0)))

    plus = logits.copy()
    minus = logits.copy()
    plus[0, 0] += 1e-6
    minus[0, 0] -= 1e-6
    numeric = (loss(plus) - loss(minus)) / (2e-6)
    expected = coefficient * 2 / 4 * 0.9 * (0.75 - (0.9 * 0.75 + 0.1 * 0.25))
    np.testing.assert_allclose(numeric, expected, atol=1e-10, rtol=0)
    assert numeric > 0  # Gradient descent reduces this overused expert logit locally.


def test_speculative_correction_preserves_many_exact_target_distributions() -> None:
    module = _module("llm-theory", "llm-048")
    cases = [
        (np.array([0.5, 0.3, 0.2]), np.array([0.2, 0.5, 0.3])),
        (np.array([0.0, 1.0]), np.array([1.0, 0.0])),
        (np.array([0.2, 0.8]), np.array([0.2, 0.8])),
    ]
    rng = np.random.default_rng(19)
    for _ in range(20):
        p = rng.random(5)
        q = rng.random(5)
        cases.append((p / p.sum(), q / q.sum()))
    for p, q in cases:
        acceptance, residual, rejection = module.correction(p, q)
        emitted = q * acceptance
        if residual is not None:
            emitted = emitted + rejection * residual
        np.testing.assert_allclose(emitted, p, atol=1e-12, rtol=0)
    p, q = cases[0]
    acceptance, residual, rejection = module.correction(p, q)
    wrong = q * acceptance + rejection * p
    assert not np.allclose(wrong, p)


def test_speculative_round_uses_the_correct_conditional_prefix_and_stops() -> None:
    module = _module("llm-theory", "llm-048")
    calls: list[tuple[int, ...]] = []

    def target(prefix: list[int]) -> NDArray[np.float64]:
        calls.append(tuple(prefix))
        return np.array([0.5, 0.3, 0.2]) if not prefix else np.array([0.8, 0.1, 0.1])

    def draft(prefix: list[int]) -> NDArray[np.float64]:
        return np.array([0.2, 0.5, 0.3])

    result = module.speculative_round([], target, draft, [0.1, 0.3], [0.2, 0.9], 0.4, budget=3)
    assert calls == [(), (0,)] and result["tokens"] == [0, 0] and result["accepted_count"] == 1
    with pytest.raises(ValueError):
        module.one_step([0.5, 0.5], [1.0, 0.0], 1, 0.2, 0.3)
    with pytest.raises(ValueError):
        module.draw([0.5, 0.5], 1.0)
    with pytest.raises(ValueError):
        module.probabilities([0.8, 0.8])


def test_speculative_cache_rollback_recomputes_the_same_positions() -> None:
    module = _module("llm-theory", "llm-048")
    cache = module.TinyCache([2, 0, 1])
    result = {"tokens": [0, 0], "accepted_count": 1, "rejected": True, "proposals": [0, 1]}
    module.apply_round(cache, 1, result)
    fresh = module.TinyCache([2, 0, 0])
    assert cache.tokens == fresh.tokens
    np.testing.assert_array_equal(cache.keys, fresh.keys)
    np.testing.assert_array_equal(cache.values, fresh.values)
    np.testing.assert_allclose(cache.output(), fresh.output(), atol=1e-12, rtol=0)
    with pytest.raises(ValueError):
        cache.truncate(99)


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1", reason="Requires prepared PyTorch CPU runtime"
)
def test_rmsnorm_gradcheck_and_noncentering_contract() -> None:
    torch = importlib.import_module("torch")

    module = _module("llm-theory", "llm-045")
    value = torch.tensor([0.3, -0.7, 1.2], dtype=torch.float64, requires_grad=True)
    assert torch.autograd.gradcheck(module.rms_norm, (value,))
    assert not torch.allclose(module.rms_norm(value + 5), module.rms_norm(value))
    torch.testing.assert_close(
        module.layer_norm(value + 5), module.layer_norm(value), atol=1e-12, rtol=0
    )


def test_position_lesson_relabels_queries_and_key_value_pairs_independently() -> None:
    module = _module("llm-theory", "llm-010")
    query = np.array([[2.0, -1.0, 0.5], [-0.5, 1.0, 2.0]])
    key = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, -1.0], [2.0, 1.0, 0.0], [-1.0, 0.5, 1.0]])
    value = np.array([[1.0, 2.0], [4.0, -1.0], [0.0, 3.0], [2.0, 5.0]])
    query_order = [1, 0]
    key_order = [2, 0, 3, 1]
    original = module.attention(query, key, value)
    changed = module.attention(query[query_order], key[key_order], value[key_order])
    np.testing.assert_allclose(changed, original[query_order], atol=1e-12, rtol=0)
    assert original.shape == (2, 2)


def test_position_lesson_mask_relabelling_and_upstream_leakage_are_distinct() -> None:
    module = _module("llm-theory", "llm-010")
    values = np.array([[2.0, 5.0, -1.0], [7.0, -2.0, 4.0], [0.0, 3.0, 9.0]])
    mask = np.tri(3, dtype=bool)
    order = [2, 0, 1]
    query = values / 10
    output = module.attention(query, query, values, mask)
    permuted_mask = mask[np.ix_(order, order)]
    relabelled = module.attention(query[order], query[order], values[order], permuted_mask)
    np.testing.assert_allclose(relabelled, output[order], atol=1e-12, rtol=0)
    assert not np.allclose(
        module.attention(query[order], query[order], values[order], mask), output[order]
    )
    centered = values - values.mean(axis=0, keepdims=True)
    leaking = module.attention(centered, centered, centered, mask)
    np.testing.assert_allclose(leaking[0], centered[0], atol=1e-12, rtol=0)
    prefix_centered = values[:1] - values[:1].mean(axis=0, keepdims=True)
    prefix = module.attention(prefix_centered, prefix_centered, prefix_centered)
    assert not np.allclose(prefix, leaking[:1])


def test_position_lesson_epsilon_variance_and_invalid_axes_are_explicit() -> None:
    module = _module("llm-theory", "llm-010")
    values = np.array([[1.0, 3.0]])
    normalized = module.layer_norm(values, epsilon=0.25)
    np.testing.assert_allclose(normalized.var(axis=-1), [1.0 / 1.25], atol=1e-12, rtol=0)
    for bad in [np.empty((2, 0)), np.array([[np.nan, 1.0]])]:
        with pytest.raises(ValueError):
            module.layer_norm(bad)
    with pytest.raises(ValueError):
        module.layer_norm(values, epsilon=0)
    with pytest.raises(ValueError):
        module.attention(values, np.ones((1, 3)), values)
    with pytest.raises(ValueError):
        module.attention(values, values, values, np.ones((1, 1), dtype=int))
    with pytest.raises(ValueError):
        module.attention(values, values, values, np.zeros((1, 1), dtype=bool))


def _standalone_worked_cases() -> list[tuple[str, str, int, str]]:
    cases: list[tuple[str, str, int, str]] = []
    for track, entry in _entries():
        number = int(entry["id"].rsplit("-", 1)[1])
        if not (
            (track == "deep-learning-tensorflow" and number >= 9)
            or (track == "llm-theory" and 10 <= number <= 42)
        ):
            continue
        guide = (ROOT / entry["guide_path"]).read_text()
        for index, source in enumerate(re.findall(r"```python\n(.*?)\n```", guide, re.DOTALL), 1):
            cases.append((entry["id"], entry["runtime_profile"], index, source))
    return cases


@pytest.mark.parametrize(
    ("lesson_id", "profile", "example", "source"),
    _standalone_worked_cases(),
    ids=[f"{lesson}-example-{index}" for lesson, _, index, _ in _standalone_worked_cases()],
)
def test_original_completion_worked_examples_are_fresh_process_programs(
    lesson_id: str, profile: str, example: int, source: str, tmp_path: Path
) -> None:
    ast.parse(source, filename=f"{lesson_id}-example-{example}")
    flag = {"tensorflow-cpu": "DS60_TEST_TENSORFLOW", "llm-torch-cpu": "DS60_TEST_TORCH"}.get(
        profile
    )
    if flag and os.environ.get(flag) != "1":
        pytest.skip(f"Fresh-process worked example requires prepared {profile}")
    path = tmp_path / "example.py"
    path.write_text(source)
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
    )
    assert result.returncode == 0, f"{lesson_id} example {example}: {result.stdout}{result.stderr}"


def test_multiple_heads_keep_head_identity_and_causal_visibility() -> None:
    module = _module("llm-theory", "llm-011")
    values = np.array([[0.2, -0.4, 1.0, 0.0], [0.7, 0.1, -0.2, 0.3], [0.4, 0.8, -0.5, 0.2]])
    output, weights = module.multihead(values, heads=2, causal=True)
    columns = [2, 3, 0, 1]
    swapped, swapped_weights = module.multihead(values[:, columns], heads=2, causal=True)
    np.testing.assert_allclose(swapped, output[:, columns], atol=1e-12, rtol=0)
    np.testing.assert_allclose(swapped_weights, weights[[1, 0]], atol=1e-12, rtol=0)
    changed = values.copy()
    changed[-1] = [9.0, -3.0, 4.0, 8.0]
    causal_changed, _ = module.multihead(changed, heads=2, causal=True)
    np.testing.assert_allclose(causal_changed[:2], output[:2], atol=1e-12, rtol=0)
    unmasked, _ = module.multihead(values, heads=2, causal=False)
    unmasked_changed, _ = module.multihead(changed, heads=2, causal=False)
    assert not np.allclose(unmasked_changed[:2], unmasked[:2])
