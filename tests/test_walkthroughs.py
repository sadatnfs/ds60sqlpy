"""Authored walkthroughs are hash-bound, reveal-gated and never claim execution."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy.exercises import REVEAL_MESSAGE
from ds60sqlpy.modules import ModuleCatalog, ModuleLesson
from ds60sqlpy.walkthroughs import (
    WALKTHROUGH_LABEL,
    executable_reference_path,
    load_walkthroughs,
    validate_index,
    walkthrough_payload,
)
from scripts import check_walkthroughs as script

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "total = 2 + 3\nprint(total)\nname = 'go'\nprint(name)\nprint('done')\n"


def lesson(key: str, profile: str = "python-core", mode: str = "practice") -> ModuleLesson:
    return ModuleLesson(
        id=key,
        track_id="demo",
        language="markdown" if profile == "reading" else "python",
        runtime_profile=profile,
        guide_path=f"courses/demo/guides/{key}.md",
        source_path=f"courses/demo/lessons/{key}.py",
        solution_paths=(
            f"courses/demo/solutions/{key}_solution.py",
            f"courses/demo/solutions/{key}_solutions.md",
        ),
        verification_id=None,
        learning_mode=mode,
    )


def step(lines: list[int], number: int) -> dict[str, Any]:
    text = SOURCE.split("\n")
    return {
        "lines": lines,
        "excerpt": "\n".join(text[lines[0] - 1 : lines[1]]),
        "title": f"Step {number}",
        "explanation": "Plain explanation of these lines.",
        "observe": "What to notice.",
    }


def entry(key: str, path: str) -> dict[str, Any]:
    return {
        "lesson_id": key,
        "title": "A short walkthrough",
        "anchor": "reference",
        "source_path": path,
        "source_sha256": hashlib.sha256(SOURCE.encode()).hexdigest(),
        "expected_output": ["5", "done"],
        "steps": [step([1, 2], 1), step([3, 4], 2), step([5, 5], 3)],
    }


def fixture(root: Path) -> tuple[Any, Path, dict[str, Any]]:
    lessons = {
        "demo-001": lesson("demo-001"),
        "demo-002": lesson("demo-002", mode="tutorial"),
        "demo-003": lesson("demo-003", profile="reading"),
        "demo-004": lesson("demo-004", profile="javascript-browser"),
        "demo-005": lesson("demo-005", profile="dax-offline"),
    }
    for item in lessons.values():
        for path in (item.source_path, *item.solution_paths):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(SOURCE)
    catalog = SimpleNamespace(
        root=root,
        lessons=lessons,
        planned={
            "demo-001": {"level": "beginner"},
            "demo-002": {"level": "intermediate"},
            "demo-003": {"level": "advanced"},
            "demo-004": {"level": "advanced"},
            "demo-005": {"level": "advanced"},
        },
    )
    payload = {
        "schema_version": 1,
        "track_id": "demo",
        "evidence": "authored",
        "walkthroughs": [
            entry("demo-001", "courses/demo/solutions/demo-001_solution.py"),
            entry("demo-002", "courses/demo/lessons/demo-002.py"),
        ],
    }
    index = root / "courses/demo/walkthroughs.json"
    index.write_text(json.dumps(payload, indent=2))
    return catalog, index, payload


def test_fixture_is_valid_and_reference_rule_matches(tmp_path: Path) -> None:
    catalog, _, _ = fixture(tmp_path)
    found = load_walkthroughs(tmp_path, catalog, "demo")
    assert sorted(found) == ["demo-001", "demo-002"]
    assert found["demo-001"]["solution_anchor"] is True
    assert found["demo-002"]["solution_anchor"] is False
    assert executable_reference_path(catalog.lessons["demo-002"]).endswith("demo-002.py")
    assert load_walkthroughs(tmp_path, catalog, "other") == {}


def test_payload_is_authored_and_not_executed(tmp_path: Path) -> None:
    catalog, _, _ = fixture(tmp_path)
    payload = walkthrough_payload(tmp_path, catalog, "demo-001", reveal=True)
    assert payload["kind"] == "authored"
    assert payload["label"] == WALKTHROUGH_LABEL == "Authored steps, not a live trace"
    assert payload["evidence"] == "authored" and payload["executed"] is False
    assert payload["source"] == SOURCE
    assert payload["steps"][0] == {
        "lines": [1, 2],
        "title": "Step 1",
        "explanation": "Plain explanation of these lines.",
        "observe": "What to notice.",
    }
    assert "CI reference corpus" in payload["verified_by"]
    tutorial = walkthrough_payload(tmp_path, catalog, "demo-002", reveal=False)
    assert tutorial["solution_anchor"] is False


def test_solution_anchor_requires_reveal(tmp_path: Path) -> None:
    catalog, _, _ = fixture(tmp_path)
    for reveal in (False, "true", 1):
        with pytest.raises(ValueError, match=REVEAL_MESSAGE):
            walkthrough_payload(tmp_path, catalog, "demo-001", reveal=reveal)  # type: ignore[arg-type]


def test_missing_walkthrough_is_named(tmp_path: Path) -> None:
    catalog, _, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="no authored walkthrough"):
        walkthrough_payload(tmp_path, catalog, "demo-003", reveal=True)


def test_stale_source_is_refused(tmp_path: Path) -> None:
    catalog, _, _ = fixture(tmp_path)
    (tmp_path / "courses/demo/solutions/demo-001_solution.py").write_text(SOURCE + "# edit\n")
    with pytest.raises(ValueError, match="Walkthrough for demo-001 is stale"):
        load_walkthroughs(tmp_path, catalog, "demo")
    with pytest.raises(ValueError, match="stale"):
        walkthrough_payload(tmp_path, catalog, "demo-002", reveal=True)


def mutate(payload: dict[str, Any], change: str) -> None:
    item = payload["walkthroughs"][0]
    steps = item["steps"]
    if change == "evidence":
        payload["evidence"] = "executed"
    elif change == "track":
        payload["track_id"] = "other"
    elif change == "schema":
        payload["schema_version"] = 2
    elif change == "unknown_lesson":
        item["lesson_id"] = "demo-999"
    elif change == "duplicate":
        payload["walkthroughs"].append(copy.deepcopy(item))
    elif change == "reading":
        item["lesson_id"] = "demo-003"
        item["source_path"] = "courses/demo/solutions/demo-003_solution.py"
    elif change == "browser":
        item["lesson_id"] = "demo-004"
        item["source_path"] = "courses/demo/solutions/demo-004_solution.py"
    elif change == "dax":
        item["lesson_id"] = "demo-005"
        item["source_path"] = "courses/demo/solutions/demo-005_solution.py"
    elif change == "wrong_path":
        item["source_path"] = "courses/demo/lessons/demo-001.py"
    elif change == "traversal":
        item["source_path"] = "courses/demo/../demo/solutions/demo-001_solution.py"
    elif change == "anchor":
        item["anchor"] = "live"
    elif change == "excerpt":
        steps[1]["excerpt"] = "name = 'python'\nprint(name)"
    elif change == "range":
        steps[2]["lines"] = [5, 9]
    elif change == "zero":
        steps[0]["lines"] = [0, 1]
    elif change == "reversed":
        steps[0]["lines"] = [2, 1]
    elif change == "decreasing":
        steps[1], steps[2] = steps[2], steps[1]
    elif change == "two_steps":
        del steps[2]
    elif change == "many_steps":
        item["steps"] = [copy.deepcopy(steps[0]) for _ in range(21)]
    elif change == "long_title":
        steps[0]["title"] = "x" * 201
    elif change == "long_explanation":
        steps[0]["explanation"] = "x" * 1201
    elif change == "long_observe":
        steps[0]["observe"] = "x" * 601
    elif change == "empty_text":
        steps[0]["observe"] = "  "
    elif change == "em_dash":
        steps[0]["explanation"] = "a \u2014 b"
    elif change == "en_dash":
        item["title"] = "1\u20132"
    elif change == "no_expected":
        del item["expected_output"]
    elif change == "empty_expected":
        item["expected_output"] = []
    elif change == "blank_expected":
        item["expected_output"] = [""]
    elif change == "too_many_expected":
        item["expected_output"] = ["a"] * 6
    elif change == "extra_key":
        item["executed"] = True
    elif change == "bad_digest":
        item["source_sha256"] = "XYZ"
    else:
        raise AssertionError(change)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("evidence", "must not claim runtime evidence"),
        ("track", "track_id"),
        ("schema", "schema_version"),
        ("unknown_lesson", "demo-999: not an authored lesson"),
        ("duplicate", "demo-001: duplicate"),
        ("reading", "demo-003: runtime profile reading"),
        ("browser", "demo-004: runtime profile javascript-browser"),
        ("dax", "demo-005: runtime profile dax-offline"),
        ("wrong_path", "demo-001: source_path must be the executable reference"),
        ("traversal", "inside the repository"),
        ("anchor", "demo-001: anchor"),
        ("excerpt", "demo-001 step 2: excerpt no longer matches"),
        ("range", "demo-001 step 3: lines 5-9"),
        ("zero", "demo-001 step 1: lines 0-1"),
        ("reversed", "demo-001 step 1: lines 2-1"),
        ("decreasing", "demo-001 step 3: steps must not move backward"),
        ("two_steps", "demo-001: needs 3 to 20 steps"),
        ("many_steps", "demo-001: needs 3 to 20 steps"),
        ("long_title", "demo-001 step 1: title exceeds 200"),
        ("long_explanation", "demo-001 step 1: explanation exceeds 1200"),
        ("long_observe", "demo-001 step 1: observe exceeds 600"),
        ("empty_text", "demo-001 step 1: observe must be non-empty"),
        ("em_dash", "demo-001 step 1: explanation must not contain an em or en dash"),
        ("en_dash", "demo-001: title must not contain an em or en dash"),
        ("no_expected", "demo-001: expected_output needs 1 to 5"),
        ("empty_expected", "demo-001: expected_output needs 1 to 5"),
        ("blank_expected", "demo-001: expected_output must be non-empty"),
        ("too_many_expected", "demo-001: expected_output needs 1 to 5"),
        ("extra_key", "demo-001: unknown keys"),
        ("bad_digest", "demo-001: source_sha256 must be 64"),
    ],
)
def test_refuse_malformed_or_misleading_walkthrough(
    tmp_path: Path, change: str, message: str
) -> None:
    catalog, index, payload = fixture(tmp_path)
    mutate(payload, change)
    index.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match=message.replace("(", r"\(")):
        load_walkthroughs(tmp_path, catalog, "demo")
    _, errors = validate_index(tmp_path, catalog, "demo")
    assert any(message in error for error in errors)


def test_validate_index_reports_every_error(tmp_path: Path) -> None:
    catalog, index, payload = fixture(tmp_path)
    payload["walkthroughs"][0]["steps"][0]["title"] = ""
    payload["walkthroughs"][1]["expected_output"] = []
    index.write_text(json.dumps(payload))
    clean, errors = validate_index(tmp_path, catalog, "demo")
    assert clean == {}
    assert len(errors) == 2


def test_check_script_passes_and_fails_with_step_messages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    catalog, index, payload = fixture(tmp_path)
    monkeypatch.setattr(script, "load_catalog", lambda root: catalog)
    assert script.main(["--root", str(tmp_path), "--check"]) == 0
    assert "OK: 2 authored walkthroughs across 1 tracks" in capsys.readouterr().out
    mutate(payload, "excerpt")
    index.write_text(json.dumps(payload))
    assert script.main(["--root", str(tmp_path), "--check"]) == 1
    assert "demo-001 step 2: excerpt no longer matches" in capsys.readouterr().out


def test_track_report_lists_stage_steps_and_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    catalog, _, _ = fixture(tmp_path)
    monkeypatch.setattr(script, "load_catalog", lambda root: catalog)
    assert script.main(["--root", str(tmp_path), "--track", "demo"]) == 0
    out = capsys.readouterr().out
    assert "demo-001  stage=beginner  steps=3  expected_output=2" in out
    assert "demo-002  stage=intermediate  steps=3  expected_output=2" in out
    assert "stages without one ['advanced']" in out


def test_rebind_updates_only_hashes_when_excerpts_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalog, index, _ = fixture(tmp_path)
    monkeypatch.setattr(script, "load_catalog", lambda root: catalog)
    reference = tmp_path / "courses/demo/solutions/demo-001_solution.py"
    reference.write_text(SOURCE + "# trailing comment\n")
    before = index.read_text()
    assert script.main(["--root", str(tmp_path), "--track", "demo", "--rebind"]) == 0
    after = index.read_text()
    new_digest = hashlib.sha256(reference.read_bytes()).hexdigest()
    old_digest = hashlib.sha256(SOURCE.encode()).hexdigest()
    assert after == before.replace(old_digest, new_digest, 1)
    assert load_walkthroughs(tmp_path, catalog, "demo")["demo-001"]["source_sha256"] == new_digest
    assert script.main(["--root", str(tmp_path), "--track", "demo", "--rebind"]) == 0
    assert index.read_text() == after


def test_rebind_refuses_when_an_excerpt_drifted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalog, index, _ = fixture(tmp_path)
    monkeypatch.setattr(script, "load_catalog", lambda root: catalog)
    reference = tmp_path / "courses/demo/solutions/demo-001_solution.py"
    reference.write_text(SOURCE.replace("name = 'go'", "name = 'gopher'"))
    before = index.read_text()
    assert script.main(["--root", str(tmp_path), "--track", "demo", "--rebind"]) == 1
    assert index.read_text() == before


def test_rebind_requires_track() -> None:
    with pytest.raises(SystemExit):
        script.main(["--check", "--rebind"])


def test_go_walkthroughs_are_valid() -> None:
    catalog = ModuleCatalog(ROOT)
    found = load_walkthroughs(ROOT, catalog, "go")
    assert "go-001" in found
    payload = walkthrough_payload(ROOT, catalog, "go-001", reveal=True)
    assert payload["executed"] is False and payload["evidence"] == "authored"
    stages = {catalog.planned[key]["level"] for key in found}
    assert stages >= {"beginner", "intermediate", "advanced"}


def test_repository_walkthroughs_all_validate() -> None:
    catalog = ModuleCatalog(ROOT)
    for track in script.tracks_with_walkthroughs(ROOT):
        _, errors = validate_index(ROOT, catalog, track)
        assert errors == [], track
