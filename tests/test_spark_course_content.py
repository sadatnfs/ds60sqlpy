"""Authored Spark content evidence, separate from root-owned worker execution."""

from __future__ import annotations

import ast
import json
import re
from datetime import UTC
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/scala-spark"
PILOTS = {"spark-001", "spark-002", "spark-003", "spark-013"}
MANIFEST = json.loads((COURSE / "lessons.json").read_text())
RECORDS = MANIFEST["lessons"]
NEW = [record for record in RECORDS if record["id"] not in PILOTS]
PLAN = {
    lesson["id"]: lesson
    for lesson in json.loads((ROOT / "docs/expansion/plans/scala-spark.json").read_text())[
        "lessons"
    ]
}


def test_existing_pilots_and_variant_are_preserved_and_ids_are_planned() -> None:
    by_id = {record["id"]: record for record in RECORDS}
    assert by_id.keys() >= PILOTS
    assert len(by_id) == len(RECORDS)
    assert by_id.keys() <= PLAN.keys()
    assert by_id["spark-013"]["verification_id"] == "spark-rows-v1"
    assert by_id["spark-013"]["variants"][0]["id"] == "pyspark"
    assert all(record["verification_id"] is None for record in NEW)


@pytest.mark.parametrize("record", NEW, ids=lambda record: record["id"])
def test_new_guides_explain_mechanisms_and_all_six_cases(record: dict[str, Any]) -> None:
    text = (ROOT / record["guide_path"]).read_text()
    explanation = (
        ROOT / next(path for path in record["solution_paths"] if path.endswith("_solutions.md"))
    ).read_text()
    assert len(text.split()) >= 1050
    assert len(explanation.split()) >= 700
    assert len(re.findall(r"^### Exercise [1-6]:", text, re.M)) == 6
    assert text.count("**Verify:**") == 6
    assert text.count("**Progressive hint:") >= 6
    assert text.count("### Worked example") >= 2
    for prerequisite in PLAN[record["id"]]["prerequisites"]:
        assert f"`{prerequisite}`" in text
    cases = json.loads((COURSE / "fixtures" / f"{record['id']}-cases.json").read_text())
    assert cases["lesson_id"] == record["id"]
    assert [case["exercise"] for case in cases["cases"]] == list(range(1, 7))
    assert all(case["expected"] and case["verification"] for case in cases["cases"])


@pytest.mark.parametrize("record", NEW, ids=lambda record: record["id"])
def test_sources_are_separate_bounded_programs_with_truthful_execution_profiles(
    record: dict[str, Any],
) -> None:
    implementations = [record, *record.get("variants", [])]
    for implementation in implementations:
        paths = [implementation["source_path"], *implementation["solution_paths"]]
        for relative in paths:
            path = ROOT / relative
            assert path.resolve().is_relative_to(COURSE)
            text = path.read_text()
            assert "\u2014" not in text
            assert "/Users/" not in text
            if path.suffix == ".scala":
                assert "object Main" in text and "def main(args: Array[String])" in text
                assert {str(n) for n in range(1, 7)} <= set(re.findall(r"Exercise ([1-6]):", text))
            elif path.suffix == ".py":
                tree = ast.parse(text)
                assert any(
                    isinstance(node, ast.If) and "__name__" in ast.unparse(node.test)
                    for node in tree.body
                )
                assert {str(n) for n in range(1, 7)} <= set(re.findall(r"Exercise ([1-6]):", text))
            if implementation["runtime_profile"].startswith("spark-local") and path.suffix in {
                ".scala",
                ".py",
            }:
                assert "local[2]" in text
                assert "finally" in text and ".stop()" in text
                assert "spark.ui.enabled" in text


def test_collection_and_validation_ledgers_have_independent_tiny_oracles() -> None:
    collection = json.loads((COURSE / "fixtures/spark-004-cases.json").read_text())["golden"]
    accepted = [value for value in collection["input"] if value >= 0]
    rejected = [value for value in collection["input"] if value < 0]
    assert accepted == collection["accepted"] and rejected == collection["rejected"]
    assert len(accepted) == collection["count"] and sum(accepted) == collection["total_cents"]
    fixture = json.loads((COURSE / "fixtures/spark-007-cases.json").read_text())["golden"]
    accepted_rows = []
    rejected_rows = []
    for position, raw in enumerate(fixture["lines"]):
        fields = raw.split("|")
        reason = None
        if len(fields) != 3:
            reason = "malformed_record"
        elif not fields[0].strip():
            reason = "missing_id"
        elif fields[1].strip() not in {"paid", "void"}:
            reason = "unknown_status"
        elif (
            not re.fullmatch(r"[0-9]+", fields[2].strip())
            or not 0 <= int(fields[2].strip()) <= 1_000_000
        ):
            reason = "invalid_amount"
        if reason:
            rejected_rows.append([position, reason])
        else:
            accepted_rows.append((fields[0].strip(), fields[1].strip(), int(fields[2].strip())))
    assert [row[0] for row in accepted_rows] == fixture["accepted_ids"]
    assert rejected_rows == fixture["rejected"]
    assert sum(row[1] == "paid" for row in accepted_rows) == fixture["paid_count"]
    assert sum(row[2] for row in accepted_rows if row[1] == "paid") == fixture["paid_total"]


def test_revenue_capstone_has_an_independent_identity_and_missingness_oracle() -> None:
    fixture = json.loads((COURSE / "fixtures/spark-014-cases.json").read_text())["golden"]
    accepted = []
    rejected = []
    for source_row, event_id, team, amount, status in fixture["rows"]:
        reason = (
            "missing_id"
            if event_id is None
            else "invalid_id"
            if event_id <= 0
            else "unknown_status"
            if status not in {"paid", "void"}
            else "negative_amount"
            if amount is not None and amount < 0
            else None
        )
        if reason:
            rejected.append([source_row, event_id, reason])
        else:
            accepted.append((event_id, team, amount, status))
    assert [row[0] for row in accepted] == fixture["accepted_ids"]
    assert rejected == fixture["quarantine"]
    assert len(accepted) + len(rejected) == len(fixture["rows"]) == 12
    paid = [row for row in accepted if row[3] == "paid"]
    assert [row[0] for row in paid] == fixture["paid_ids"]
    known = [row[2] for row in paid if row[2] is not None]
    assert [len(paid), len(known), sum(known)] == fixture["paid_metrics"]
    groups = []
    for team in sorted({row[1] for row in paid}, key=lambda value: (value is None, value or "")):
        members = [row for row in paid if row[1] == team]
        known = [row[2] for row in members if row[2] is not None]
        groups.append([team, len(members), len(known), sum(known) if known else None])
    assert groups == fixture["groups"]
    wrong = {(row[1], row[2]) for row in paid}
    known = [amount for _, amount in wrong if amount is not None]
    assert [len(wrong), len(known), sum(known)] == fixture["wrong_distinct_metrics"]


def test_nested_collection_ledger_preserves_occurrences_and_placeholders() -> None:
    fixture = json.loads((COURSE / "fixtures/spark-017-cases.json").read_text())["golden"]
    lengths = fixture["array_lengths"]
    assert sum(length for length in lengths if length is not None) == 3
    assert sum(max(length or 0, 1) for length in lengths) == fixture["outer_count"] == 5
    assert len({(row[0], row[1]) for row in fixture["child_rows"]}) == 3
    assert sum(row[3] for row in fixture["child_rows"] if row[3] is not None) == 5
    assert len(fixture["accepted_sources"]) + len(fixture["quarantine"]) == 7


def test_timestamp_fixture_boundaries_have_an_independent_zone_oracle() -> None:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    fixture = json.loads((COURSE / "fixtures/spark-018-cases.json").read_text())["golden"]
    zone = ZoneInfo("America/Los_Angeles")
    start = datetime(2024, 11, 3, tzinfo=zone).astimezone(UTC)
    end = datetime(2024, 11, 4, tzinfo=zone).astimezone(UTC)
    assert (end - start).total_seconds() == fixture["local_day_hours"] * 3600
    first = datetime.fromisoformat("2024-11-03T01:30:00-07:00")
    second = datetime.fromisoformat("2024-11-03T01:30:00-08:00")
    assert (second - first).total_seconds() == fixture["fold_seconds"]
    assert first.astimezone(zone).strftime("%H:%M") == second.astimezone(zone).strftime("%H:%M")


def test_window_winner_policy_has_an_independent_collection_oracle() -> None:
    fixture = json.loads((COURSE / "fixtures/spark-019-cases.json").read_text())["golden"]
    winners = []
    peers: list[int] = []
    for entity in sorted({row[1] for row in fixture["rows"]}):
        candidates = [row for row in fixture["rows"] if row[1] == entity]
        best = max(candidates, key=lambda row: (row[2] is not None, row[2] or 0, row[0]))
        winners.append(best[0])
        peers.extend(row[0] for row in candidates if row[2] == best[2])
    assert sorted(winners) == fixture["winners"]
    assert sorted(peers) == fixture["top_time_candidates"]


def test_cache_golden_preserves_the_declared_duplicate_bag() -> None:
    from collections import Counter

    fixture = json.loads((COURSE / "fixtures/spark-027-cases.json").read_text())["golden"]
    actual = [
        (identity, segment, None if amount is None else amount * 2)
        for identity, segment, amount in fixture["source"]
        if amount is None or amount >= 0
    ]
    expected = [tuple(row) for row in fixture["golden"]]
    assert Counter(actual) == Counter(expected)
    assert len(actual) == 7 and len(set(actual)) == 5
    assert sum(row[2] for row in actual if row[2] is not None) == fixture["known_total"]


def test_batch_capstone_key_summary_has_an_independent_formula_oracle() -> None:
    fixture = json.loads((COURSE / "fixtures/spark-028-cases.json").read_text())["golden"]
    groups: dict[int, list[int | None]] = {}
    for identity in range(1, 2001):
        key = 0 if identity <= 1600 else (identity - 1601) % 4 + 1
        amount = None if identity % 10 == 0 else identity % 7 + 1
        groups.setdefault(key, []).append(amount)
    summary = []
    for key, amounts in sorted(groups.items()):
        known = [amount for amount in amounts if amount is not None]
        summary.append([key, len(amounts), len(known), sum(known), sum(known) * (key + 2)])
    assert summary == fixture["key_summary"]
    assert sum(row[3] for row in summary) == fixture["amount_total"]
    assert sum(row[4] for row in summary) == fixture["weighted_total"]


def test_publication_digest_matches_the_declared_independent_json_convention() -> None:
    import hashlib

    fixture = json.loads((COURSE / "fixtures/spark-029-cases.json").read_text())["golden"]
    canonical = "\n".join(
        json.dumps({"id": identity, "value": identity * 2}, separators=(",", ":"))
        for identity in range(30)
    )
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == fixture["sha256"]
    assert sum(identity * 2 for identity in range(30)) == fixture["value_total"]


def test_stream_join_has_an_independent_half_open_pair_and_outer_oracle() -> None:
    fixture = json.loads((COURSE / "fixtures/spark-034-cases.json").read_text())["golden"]
    pairs = [
        [left[0], right[0]]
        for left in fixture["impressions"]
        for right in fixture["clicks"]
        if left[1] == right[1]
        and left[2] <= right[2] < left[2] + fixture["upper_bound_exclusive_minutes"]
    ]
    assert pairs == fixture["matched"]
    matched_left = {pair[0] for pair in pairs}
    outer = pairs + [
        [left[0], None] for left in fixture["impressions"] if left[0] not in matched_left
    ]
    assert sorted(outer, key=lambda pair: pair[0]) == fixture["final_outer"]
    assert all(pair[1] != "c3" for pair in pairs)


@pytest.mark.parametrize("number", [31, 32, 33, 34])
def test_introductory_streams_have_explicit_bounded_query_lifecycle(number: int) -> None:
    for suffix in ["py", "scala"]:
        source = (COURSE / "solutions" / f"spark-{number:03}_solution.{suffix}").read_text()
        assert "awaitTermination(30" in source
        assert "query.stop()" in source and "finally" in source
        assert "AvailableNow" in source or "availableNow=True" in source
        assert '"10000"' in source and "spark.sql.streaming.stopTimeout" in source
        assert "preserve scratch" in source
        assert "time.sleep(" not in source and "Thread.sleep(" not in source
        assert '.format("socket")' not in source and '.format("kafka")' not in source
