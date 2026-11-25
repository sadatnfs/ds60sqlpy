"""The track qualification ledger agrees with the matrix, the runtime registry and CI groups."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from scripts import check_module_references as references
from scripts import check_track_qualification as qualification

ROOT = Path(__file__).resolve().parents[1]
MATRIX = qualification.load_matrix(ROOT)
LEDGER = qualification.load_ledger(ROOT)
RECORDS = {record["track"]: record for record in LEDGER["tracks"]}


def go_record() -> dict[str, Any]:
    return copy.deepcopy(RECORDS["go"])


def test_go_record_is_consistent_with_matrix() -> None:
    record = RECORDS["go"]
    assert set(record["criteria"]) == set(qualification.CRITERIA)
    assert qualification.evaluate_track(MATRIX, record, ROOT) == []
    for criterion, codes in qualification.MEASURED.items():
        measured = qualification.measured_rows(MATRIX, "go", codes)
        entry = record["criteria"][criterion]
        if entry["status"] == "pass":
            assert measured == []
        if entry["status"] == "accepted-gap":
            assert entry["lessons"] == measured


def test_pass_with_measured_rows_is_rejected() -> None:
    matrix = copy.deepcopy(MATRIX)
    row = next(row for row in matrix["lessons"] if row["track"] == "go")
    row["gaps"] = [*row["gaps"], "few-terms"]
    record = go_record()
    assert record["criteria"]["R3"]["status"] == "pass"
    errors = qualification.evaluate_track(matrix, record, ROOT)
    assert any(error.startswith("go R3: pass") and row["id"] in error for error in errors)


def test_one_record_per_matrix_track() -> None:
    tracks = [record["track"] for record in LEDGER["tracks"]]
    matrix_tracks = {row["track"] for row in MATRIX["lessons"]}
    assert len(tracks) == len(set(tracks)) == len(matrix_tracks) == 40
    assert set(tracks) == matrix_tracks
    for track, record in RECORDS.items():
        assert record["rows"] == len(qualification.track_rows(MATRIX, track))
    assert qualification.check(ROOT) == []


@pytest.mark.parametrize("track", sorted(RECORDS))
def test_record_is_consistent(track: str) -> None:
    assert qualification.evaluate_track(MATRIX, RECORDS[track], ROOT) == []


def test_runtime_profiles_match_matrix() -> None:
    for track, record in RECORDS.items():
        used = {row["runtime"] for row in qualification.track_rows(MATRIX, track)}
        assert set(record["runtime"]["profiles"]) == used, track


def test_routes_and_reasons_are_derived() -> None:
    for track, record in RECORDS.items():
        family = record["family"]
        runtime = record["runtime"]
        expected_unavailable = []
        for profile, entry in sorted(runtime["profiles"].items()):
            assert entry["route"] == qualification.expected_route(family, profile), track
            assert entry["label"] in qualification.RESULT_LABELS
            assert entry["label"] == qualification.ROUTE_LABELS[entry["route"]]
            if family != "core" and profile not in references.ORDINARY_PROFILES:
                expected_unavailable.append(
                    {"profile": profile, "reason": references.EXTERNAL_REASONS[profile]}
                )
        assert runtime["unavailable"] == expected_unavailable, track
        assert all(item["reason"].strip() for item in runtime["unavailable"])
        assert qualification.GUIDE_RUNNER in runtime["guide_examples"]
        assert "not executed" not in runtime["guide_examples"]
    with pytest.raises(ValueError):
        qualification.expected_route("module", "not-a-profile")
    record = copy.deepcopy(RECORDS["kubernetes"])
    record["runtime"]["unavailable"][0]["reason"] = "Runs everywhere."
    assert any("unavailable" in e for e in qualification.evaluate_track(MATRIX, record, ROOT))


def test_ordinary_profiles_name_their_ci_group() -> None:
    from scripts import ci_profiles

    group_of = {p: row["id"] for row in ci_profiles.groups(ROOT) for p in row["profiles"]}
    for track, record in RECORDS.items():
        for profile, entry in record["runtime"]["profiles"].items():
            if entry["route"] == "reference-corpus":
                assert entry["ci_group"] == group_of[profile], (track, profile)
            else:
                assert "ci_group" not in entry, (track, profile)
    record = go_record()
    record["runtime"]["profiles"]["go"]["ci_group"] = "java"
    assert any("runtime go" in e for e in qualification.evaluate_track(MATRIX, record, ROOT))


def test_walkthrough_routes_and_counts() -> None:
    routes = {track: record["walkthrough"]["route"] for track, record in RECORDS.items()}
    assert routes.pop("python") == "live-python"
    assert routes.pop("sql") == "live-sql"
    assert routes.pop("bridge") == "live-python"
    assert routes.pop("dax") == "hand-derived"
    for track in ("cuda", "docker", "kubernetes", "spark-deployment"):
        assert routes.pop(track) == "na"
        assert RECORDS[track]["criteria"]["R9"]["status"] == "na"
    assert len(routes) == 32 and set(routes.values()) == {"authored"}
    for track in routes:
        assert RECORDS[track]["walkthrough"]["floor"] == 3, track
        assert "count" not in RECORDS[track]["walkthrough"]


def test_r9_counts_only_validated_walkthroughs(monkeypatch: pytest.MonkeyPatch) -> None:
    beginner = next(
        row["id"]
        for row in MATRIX["lessons"]
        if row["track"] == "go" and row["stage"] == "beginner"
    )
    assert qualification.walkthrough_stages(ROOT, MATRIX, "go") == {
        "beginner",
        "intermediate",
        "advanced",
    }
    record = go_record()
    assert record["criteria"]["R9"] == {"status": "pass"}

    def only_beginner(root: Path, catalog: object, track: str) -> dict[str, dict[str, Any]]:
        return {beginner: {"lesson_id": beginner}}

    monkeypatch.setattr(qualification, "load_walkthroughs", only_beginner)
    assert qualification.walkthrough_stages(ROOT, MATRIX, "go") == {"beginner"}
    errors = qualification.evaluate_track(MATRIX, record, ROOT)
    assert any(e.startswith("go R9: pass needs walkthroughs") for e in errors)
    record["criteria"]["R9"] = {"status": "gap", "justification": "x" * 40}
    assert qualification.evaluate_track(MATRIX, record, ROOT) == []

    def invalid(root: Path, catalog: object, track: str) -> dict[str, dict[str, Any]]:
        raise ValueError("go-001: excerpt does not match the source lines.")

    monkeypatch.setattr(qualification, "load_walkthroughs", invalid)
    assert qualification.walkthrough_stages(ROOT, MATRIX, "go") == set()
    record["criteria"]["R9"] = {"status": "pass"}
    errors = qualification.evaluate_track(MATRIX, record, ROOT)
    assert any("pass needs a valid walkthrough file" in e for e in errors)


def test_r8_baseline_rule() -> None:
    record = go_record()
    entry = record["criteria"]["R8"]
    assert entry["status"] == "pass"
    total = qualification.templated_total(MATRIX, "go")
    assert total is not None and total <= entry["templated_baseline"]
    assert qualification.COMMIT.search(entry["templated_baseline_source"])
    for track, other in RECORDS.items():
        r8 = other["criteria"]["R8"]
        assert r8["status"] == "pass", track
        assert qualification.templated_total(MATRIX, track) == r8["templated_baseline"], track
    del record["criteria"]["R8"]["templated_baseline_source"]
    assert any("templated_baseline_source" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R8"]["templated_baseline"] = True
    assert any("integer templated_baseline" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R3"]["templated_baseline"] = 1
    assert any("only R8 records" in e for e in _errors(record))


def _with_evidence(record: dict[str, Any], **changes: Any) -> dict[str, Any]:
    runtime = record["runtime"]
    runtime["walkthrough_outputs_checked"] = True
    runtime["evidence"] = {"ci_run": "45313712049", "commit": "a" * 40, "groups": ["c-go"]}
    runtime["evidence"].update(changes)
    record["criteria"]["R10"] = {"status": "pass"}
    return record


def test_walkthrough_outputs_checked_requires_ci_evidence() -> None:
    assert _errors(_with_evidence(go_record())) == []
    assert qualification.meets_threshold(MATRIX, _with_evidence(go_record())) == []
    for changes, message in (
        ({"ci_run": "run-1"}, "ci_run must be a string of digits"),
        ({"ci_run": 45313712049}, "ci_run must be a string of digits"),
        ({"commit": "A" * 40}, "commit must be 40 lowercase hex"),
        ({"commit": "a" * 39}, "commit must be 40 lowercase hex"),
        ({"groups": []}, "lacks the ordinary CI groups ['c-go']"),
        ({"groups": ["java"]}, "lacks the ordinary CI groups ['c-go']"),
        ({"groups": ["c-go", "not-a-group"]}, "unknown groups"),
        ({"groups": ["c-go", "c-go"]}, "sorted list of unique names"),
    ):
        errors = _errors(_with_evidence(go_record(), **changes))
        assert any(message in e for e in errors), (changes, errors)
        assert any("R10: pass requires" in e for e in errors), changes
    record = _with_evidence(go_record())
    del record["runtime"]["evidence"]["groups"]
    assert any("needs evidence" in e for e in _errors(record))
    record = _with_evidence(go_record())
    del record["runtime"]["evidence"]
    assert any("needs evidence" in e for e in _errors(record))
    record = _with_evidence(go_record())
    record["runtime"]["walkthrough_outputs_checked"] = False
    assert any("recorded only with walkthrough_outputs_checked" in e for e in _errors(record))
    multi = copy.deepcopy(RECORDS["llm-theory"])
    _with_evidence(multi, groups=["python-core"])
    assert any("lacks the ordinary CI groups ['pytorch']" in e for e in _errors(multi))
    _with_evidence(multi, groups=["python-core", "pytorch"])
    assert _errors(multi) == []
    core = copy.deepcopy(RECORDS["python"])
    core["runtime"]["walkthrough_outputs_checked"] = True
    core["runtime"]["evidence"] = {"ci_run": "1", "commit": "a" * 40, "groups": []}
    assert any("no ordinary CI group" in e for e in _errors(core))


def test_r10_pass_requires_ci_evidence_for_ordinary_profiles() -> None:
    record = go_record()
    record["runtime"]["walkthrough_outputs_checked"] = False
    record["runtime"].pop("evidence", None)
    record["criteria"]["R10"] = {"status": "pass"}
    assert any("R10: pass requires recorded CI evidence" in e for e in _errors(record))
    for track, other in RECORDS.items():
        if qualification.required_ci_groups(other):
            checked = other["runtime"]["walkthrough_outputs_checked"]
            assert (other["criteria"]["R10"]["status"] == "pass") == checked, track
        else:
            assert other["criteria"]["R10"]["status"] == "pass", track
            assert other["runtime"]["walkthrough_outputs_checked"] is False, track


def test_gap_and_status_rules() -> None:
    record = go_record()
    record["criteria"]["R7"]["lessons"] = ["go-043"]
    assert any("only accepted-gap lists lessons" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R7"] = {
        "status": "accepted-gap",
        "lessons": ["go-043"],
        "justification": "x" * 40,
    }
    assert any("accepted lessons must equal" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R3"] = {"status": "not-assessed", "justification": "x" * 40}
    assert any("only on R11" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R11"] = {"status": "pass"}
    assert any("named reviewer" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R8"]["templated_baseline"] = 10**9
    assert not any("R8" in e for e in _errors(record))
    unmeasured = copy.deepcopy(MATRIX)
    for row in unmeasured["lessons"]:
        row.get("metrics", {}).pop("templated_words", None)
    errors = qualification.evaluate_track(unmeasured, record, ROOT)
    assert any("templated_words metric" in e for e in errors)
    record["criteria"]["R8"]["templated_baseline"] = 0
    assert any("exceeds the recorded baseline" in e for e in _errors(record))
    record = go_record()
    record["criteria"]["R5"] = {"status": "gap", "justification": "too short"}
    assert any("at least 40" in e for e in _errors(record))


def _errors(record: dict[str, Any]) -> list[str]:
    return qualification.evaluate_track(MATRIX, record, ROOT)


def test_no_dashes_in_ledger() -> None:
    text = (ROOT / qualification.LEDGER).read_text(encoding="utf-8")
    assert "\u2014" not in text and "\u2013" not in text
    record = go_record()
    record["criteria"]["R11"]["justification"] += " \u2014"
    assert any("dashes" in e for e in _errors(record))


def test_meets_threshold_rules() -> None:
    passing = go_record()
    passing["criteria"] = {rid: {"status": "pass"} for rid in qualification.CRITERIA}
    assert qualification.meets_threshold(MATRIX, passing) == []
    reviewed = copy.deepcopy(passing)
    reviewed["criteria"]["R11"] = {"status": "not-assessed", "justification": "x" * 40}
    assert qualification.meets_threshold(MATRIX, reviewed) == []
    capped = copy.deepcopy(passing)
    ids = [row["id"] for row in qualification.track_rows(MATRIX, "go")]
    capped["criteria"]["R7"] = {
        "status": "accepted-gap",
        "lessons": ids[:4],
        "justification": "x" * 40,
    }
    assert qualification.meets_threshold(MATRIX, capped) == []
    capped["criteria"]["R7"]["lessons"] = ids[:5]
    assert any("exceed 10 percent" in r for r in qualification.meets_threshold(MATRIX, capped))
    must = copy.deepcopy(passing)
    must["criteria"]["R1"] = {
        "status": "accepted-gap",
        "lessons": ids[:1],
        "justification": "x" * 40,
    }
    assert any("R1: must be pass" in r for r in qualification.meets_threshold(MATRIX, must))
    open_gap = copy.deepcopy(passing)
    open_gap["criteria"]["R5"] = {"status": "gap", "justification": "x" * 40}
    assert qualification.meets_threshold(MATRIX, open_gap) == ["go R5: open gap."]


@pytest.mark.parametrize("track", sorted(RECORDS))
def test_every_track_meets_threshold(track: str) -> None:
    assert qualification.meets_threshold(MATRIX, RECORDS[track]) == []


def test_ordinary_profile_tracks_cite_ci_evidence() -> None:
    for track, record in RECORDS.items():
        groups = qualification.required_ci_groups(record)
        runtime = record["runtime"]
        assert runtime["walkthrough_outputs_checked"] is bool(groups), track
        if groups:
            assert set(groups) <= set(runtime["evidence"]["groups"]), track


def test_go_report_writes_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    before = (ROOT / qualification.LEDGER).read_bytes()
    assert qualification.main(["--track", "go"]) == 0
    output = capsys.readouterr().out
    assert "R7" in output and "runtime:" in output and "CI group c-go" in output
    assert (ROOT / qualification.LEDGER).read_bytes() == before
