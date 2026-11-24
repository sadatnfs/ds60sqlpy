"""Parsing and planning for recorded app-build CI evidence, from a fixture (no network)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from scripts import check_track_qualification as qualification
from scripts import record_track_runtime_evidence as evidence
from scripts.ci_profiles import groups

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/gh_run_view/app_build_run.json"
KNOWN = {row["id"] for row in groups(ROOT)}
COMMIT = "0123456789abcdef0123456789abcdef01234567"


def payload() -> dict[str, Any]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def pending_ledger() -> dict[str, Any]:
    """The committed ledger with recorded CI evidence removed, as before any run."""
    ledger = qualification.load_ledger(ROOT)
    for record in ledger["tracks"]:
        required = qualification.required_ci_groups(record)
        if not required or record["runtime"].pop("evidence", None) is None:
            continue
        record["runtime"]["walkthrough_outputs_checked"] = False
        record["criteria"]["R10"] = {
            "status": "gap",
            "justification": (
                "No recorded app-build run yet cites a successful qualify job for the "
                f"ordinary CI groups {', '.join(required)}."
            ),
        }
    return ledger


def test_parse_run_reads_each_group_qualify_outcome() -> None:
    commit, outcomes = evidence.parse_run(payload(), KNOWN)
    assert commit == COMMIT
    assert outcomes == {
        "c-go": "success",
        "python-core": "success",
        "pytorch": "success",
        "java": "job failure",
        "swift": "job skipped",
        "cpp": "qualify step not found",
        "r": "job failure",
    }


def test_parse_run_rejects_other_workflows_and_bad_commits() -> None:
    other = payload()
    other["workflowName"] = "CI"
    with pytest.raises(ValueError, match="app-build"):
        evidence.parse_run(other, KNOWN)
    short = payload()
    short["headSha"] = "abc123"
    with pytest.raises(ValueError, match="40 character"):
        evidence.parse_run(short, KNOWN)


def test_plan_records_only_tracks_whose_groups_all_succeeded() -> None:
    ledger = pending_ledger()
    before = copy.deepcopy(ledger)
    _commit, outcomes = evidence.parse_run(payload(), KNOWN)
    updated, lines = evidence.plan_updates(ledger, "123456", COMMIT, outcomes)
    assert ledger == before
    records = {record["track"]: record for record in updated["tracks"]}
    go = records["go"]
    assert go["runtime"]["walkthrough_outputs_checked"] is True
    assert go["runtime"]["evidence"] == {"ci_run": "123456", "commit": COMMIT, "groups": ["c-go"]}
    assert go["criteria"]["R10"] == {"status": "pass"}
    assert records["llm-theory"]["runtime"]["evidence"]["groups"] == ["python-core", "pytorch"]
    for track in ("java", "swift", "cpp", "r", "tmb-modeling", "data-ml-engineering"):
        assert "evidence" not in records[track]["runtime"], track
        assert records[track]["criteria"]["R10"]["status"] == "gap", track
    for track in ("python", "sql", "dax", "cuda"):
        assert records[track] == next(r for r in before["tracks"] if r["track"] == track)
    assert "RECORD go: run 123456" in "\n".join(lines)
    assert "SKIP java: java (job failure)" in lines
    matrix = qualification.load_matrix(ROOT)
    for track in ("go", "c", "llm-theory", "java"):
        assert qualification.evaluate_track(matrix, records[track], ROOT) == [], track
    assert qualification.meets_threshold(matrix, records["go"]) == []


def test_full_success_run_qualifies_every_track() -> None:
    outcomes = dict.fromkeys(KNOWN, "success")
    updated, lines = evidence.plan_updates(pending_ledger(), "123456", COMMIT, outcomes)
    assert not any(line.startswith("SKIP") for line in lines)
    matrix = qualification.load_matrix(ROOT)
    for record in updated["tracks"]:
        assert qualification.evaluate_track(matrix, record, ROOT) == [], record["track"]
        assert qualification.meets_threshold(matrix, record) == [], record["track"]
        assert not qualification.evidence_pending(matrix, record)


def test_dump_json_matches_the_committed_ledger_format() -> None:
    text = (ROOT / qualification.LEDGER).read_text(encoding="utf-8")
    assert evidence.dump_json(json.loads(text)) + "\n" == text
    nested = {"a": {"groups": ["c-go"], "long": ["x" * 30, "y" * 30, "z" * 30]}}
    dumped = evidence.dump_json(nested)
    assert '"groups": ["c-go"]' in dumped
    assert '"long": [\n' in dumped
    assert all(len(line) <= evidence.PRINT_WIDTH for line in dumped.splitlines())
    edge = ["x" * (evidence.PRINT_WIDTH - len('  "k": [""]'))]
    assert evidence.dump_json({"k": edge}).splitlines()[1] == f'  "k": ["{edge[0]}"]'
    assert '"k": [\n' in evidence.dump_json({"k": edge, "z": 1})


def test_main_rejects_non_numeric_run(capsys: pytest.CaptureFixture[str]) -> None:
    assert evidence.main(["--run", "abc", "--dry-run"]) == 2
    assert "numeric run ID" in capsys.readouterr().err
