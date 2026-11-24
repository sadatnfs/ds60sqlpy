"""The track qualification ledger agrees with the matrix, the runtime registry and CI groups."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

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
            if family != "core" and profile not in qualification.ORDINARY_PROFILES:
                expected_unavailable.append(
                    {"profile": profile, "reason": qualification.EXTERNAL_REASONS[profile]}
                )
        assert runtime["unavailable"] == expected_unavailable, track
        assert all(item["reason"].strip() for item in runtime["unavailable"])
        assert qualification.NOT_EXECUTED in runtime["guide_examples"]
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


def test_r9_pass_requires_every_ordinary_stage(tmp_path: Path) -> None:
    (tmp_path / "courses/go").mkdir(parents=True)
    (tmp_path / "docker").mkdir()
    for name in ("ci-profile-groups.json", "classroom-images.tsv"):
        (tmp_path / "docker" / name).write_bytes((ROOT / "docker" / name).read_bytes())
    beginner = next(
        row["id"]
        for row in MATRIX["lessons"]
        if row["track"] == "go" and row["stage"] == "beginner"
    )
    (tmp_path / "courses/go/walkthroughs.json").write_text(
        json.dumps({"walkthroughs": [{"lesson_id": beginner}]}), encoding="utf-8"
    )
    record = go_record()
    record["criteria"]["R9"] = {"status": "pass"}
    errors = qualification.evaluate_track(MATRIX, record, tmp_path)
    assert any(e.startswith("go R9: pass needs walkthroughs") for e in errors)
    record["criteria"]["R9"] = copy.deepcopy(RECORDS["go"]["criteria"]["R9"])
    assert record["criteria"]["R9"]["status"] == "gap"
    assert qualification.evaluate_track(MATRIX, record, tmp_path) == []
    assert qualification.walkthrough_stages(tmp_path, MATRIX, "go") == {"beginner"}


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
    record["criteria"]["R8"] = {"status": "pass", "templated_baseline": 10**9}
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


@pytest.mark.xfail(strict=True, reason="Phase 5 closure (05-05) records final rubric results")
@pytest.mark.parametrize("track", sorted(RECORDS))
def test_every_track_meets_threshold(track: str) -> None:
    assert qualification.meets_threshold(MATRIX, RECORDS[track]) == []


def test_go_report_writes_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    before = (ROOT / qualification.LEDGER).read_bytes()
    assert qualification.main(["--track", "go"]) == 0
    output = capsys.readouterr().out
    assert "R7" in output and "runtime:" in output and "CI group c-go" in output
    assert (ROOT / qualification.LEDGER).read_bytes() == before
