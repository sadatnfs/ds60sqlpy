"""Independent checks for the new Python learning boundaries and project labs."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from python.professional.solutions import (
    py_data_02_exact_values_time_text_solution as exact,
)
from python.professional.solutions import (
    py_foundations_03_clean_records_solution as clean,
)
from python.professional.solutions import (
    py_foundations_04_first_investigation_solution as project,
)
from python.professional.solutions import (
    py_ml_02_group_time_evaluation_solution as evaluation,
)
from python.professional.solutions import (
    py_pro_03_restartable_file_pipeline_solution as pipeline,
)


@pytest.mark.parametrize("raw", [None, 0, True, "", " ", "many", "4.5", "-1"])
def test_quantity_rejects_missing_invalid_and_negative_values(raw: object) -> None:
    with pytest.raises(ValueError):
        clean.parse_quantity(raw)


def test_cleaner_preserves_raw_and_reserves_only_valid_ids() -> None:
    rows: list[dict[str, object]] = [
        {"id": "A", "quantity": "many"},
        {"id": " A ", "quantity": "2"},
        {"id": "A", "quantity": "3"},
        {"id": "a", "quantity": "0"},
    ]
    before = copy.deepcopy(rows)
    accepted, rejected = clean.clean_rows(rows)
    assert rows == before
    assert accepted == [{"id": "A", "quantity": 2}, {"id": "a", "quantity": 0}]
    assert [row["row_number"] for row in rejected] == [1, 3]
    assert [row["reason"] for row in rejected] == ["quantity is not an integer", "duplicate id"]
    assert len(rows) == len(accepted) + len(rejected)


def test_cleaner_distinguishes_empty_from_all_invalid() -> None:
    assert clean.clean_rows([]) == ([], [])
    accepted, rejected = clean.clean_rows([{"id": "A", "quantity": None}])
    assert not accepted and len(rejected) == 1
    assert clean.parse_quantity(" +4 ") == 4


def test_first_project_fixture_and_json_roundtrip(tmp_path: Path) -> None:
    rows = project.load_rows(project.FIXTURE)
    before = copy.deepcopy(rows)
    result = project.analyze_rows(rows)
    assert rows == before
    assert result["input_count"] == 7
    assert result["accepted_count"] == 4
    assert result["rejected_count"] == 3
    assert result["total_quantity"] == 11
    assert result["by_region"] == {"north": 7, "south": 0, "west": 4}
    target = tmp_path / "nested" / "report.json"
    project.write_report(result, target)
    assert json.loads(target.read_text(encoding="utf-8")) == result
    assert target.read_bytes().endswith(b"\n")


def test_first_project_empty_zero_and_invalid_are_different() -> None:
    empty = project.analyze_rows([])
    zero = project.analyze_rows([{"id": "Z", "region": "south", "quantity": "0"}])
    invalid = project.analyze_rows([{"id": "Z", "region": "south", "quantity": "bad"}])
    assert empty["total_quantity"] == zero["total_quantity"] == invalid["total_quantity"] == 0
    assert empty["by_region"] == invalid["by_region"] == {}
    assert zero["by_region"] == {"south": 0}
    assert empty["input_count"] == 0 and invalid["rejected_count"] == 1


@pytest.mark.parametrize(
    "header", ["id,quantity", "quantity,region,id", "id,region,quantity,other"]
)
def test_project_rejects_header_drift(tmp_path: Path, header: str) -> None:
    path = tmp_path / "rows.csv"
    path.write_text(header + "\nA,north,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="header"):
        project.load_rows(path)


@pytest.mark.parametrize("raw", ["1.005", "NaN", "Infinity", "1e2", "-1", "", 1.0, "1234567890123"])
def test_money_rejects_precision_notation_and_representation(raw: object) -> None:
    with pytest.raises(ValueError):
        exact.parse_money(raw)


def test_exact_money_is_independent_of_callers_decimal_precision() -> None:
    with localcontext() as context:
        context.prec = 2
        amount = exact.parse_money("123456789012.34")
        start = exact.parse_instant("2026-01-01T00:00:00+00:00")
        end = start + timedelta(days=1)
        count, total = exact.window_total(
            [{"amount": "123456789012.34", "occurred_at": start.isoformat()}] * 3,
            start,
            end,
        )
    assert amount == Decimal("123456789012.34")
    assert amount.as_tuple().exponent == -2
    assert count == 3 and total == Decimal("370370367037.02")


def test_unicode_collision_report_keeps_raw_spellings() -> None:
    assert exact.canonical_label("Café") == exact.canonical_label("Cafe\u0301")
    assert exact.collision_groups(["x", "x"]) == {}
    assert exact.collision_groups(["Straße", "STRASSE", "Straße"]) == {
        "strasse": ["Straße", "STRASSE"]
    }
    with pytest.raises(ValueError):
        exact.canonical_label(" ")


def test_instant_conversion_and_half_open_ownership() -> None:
    instant = exact.parse_instant("2026-01-02T00:30:00+02:00")
    start = exact.parse_instant("2026-01-01T22:00:00+00:00")
    end = start + timedelta(hours=1)
    assert instant == start + timedelta(minutes=30)
    assert exact.in_window(start, start, end)
    assert not exact.in_window(end, start, end)
    assert exact.in_window(end, end, end + timedelta(hours=1))
    with pytest.raises(ValueError):
        exact.parse_instant("2026-01-01T00:00:00")
    with pytest.raises(ValueError):
        exact.in_window(start, start, start)


def test_invalid_amount_is_not_hidden_by_window_filter() -> None:
    start = exact.parse_instant("2026-01-01T00:00:00+00:00")
    end = start + timedelta(days=1)
    rows = [{"amount": "bad", "occurred_at": (end + timedelta(days=1)).isoformat()}]
    with pytest.raises(ValueError):
        exact.window_total(rows, start, end)
    with pytest.raises(ValueError):
        exact.window_total([], end, start)


def observation(event: str, entity: str, day: int, target: float = 0.0) -> evaluation.Observation:
    instant = datetime(2026, 1, day, tzinfo=UTC)
    return evaluation.Observation(event, entity, instant, instant, instant, 2.0, target)


def test_observation_source_boundary_checks_availability_and_values() -> None:
    row = observation("A1", "A", 1)
    evaluation.validate_observations([row])
    invalid = [
        replace(row, feature_available_at=row.observed_at + timedelta(seconds=1)),
        replace(row, label_available_at=row.observed_at - timedelta(seconds=1)),
        replace(row, observed_at=row.observed_at.replace(tzinfo=None)),
        replace(row, feature=float("nan")),
        replace(row, target=float("inf")),
        replace(row, event_id=" A1 "),
    ]
    for probe in invalid:
        with pytest.raises(ValueError):
            evaluation.validate_observations([probe])
    with pytest.raises(ValueError, match="duplicate"):
        evaluation.validate_observations([row, row])


def test_group_holdout_owns_whole_entities_and_does_not_sort_source() -> None:
    rows = [observation("A2", "A", 2), observation("B1", "B", 1), observation("A1", "A", 1)]
    training, validation = evaluation.group_split(rows, {"A"})
    assert [row.event_id for row in training] == ["B1"]
    assert [row.event_id for row in validation] == ["A2", "A1"]
    assert not {row.entity_id for row in training} & {row.entity_id for row in validation}
    invalid_holdouts: tuple[set[str], ...] = ({"missing"}, {"A", "B"}, set())
    for held_out in invalid_holdouts:
        with pytest.raises(ValueError):
            evaluation.group_split(rows, held_out)


def test_time_split_excludes_exact_embargo_and_owns_end_once() -> None:
    cutoff = datetime(2026, 1, 5, tzinfo=UTC)
    gap = timedelta(days=1)
    eligible = replace(
        observation("eligible", "A", 1), label_available_at=cutoff - gap - timedelta(seconds=1)
    )
    excluded = replace(observation("late", "B", 1), label_available_at=cutoff - gap)
    at_start = observation("start", "A", 5)
    at_end = observation("end", "C", 6)
    rows = [eligible, excluded, at_start, at_end]
    training, validation, omitted = evaluation.time_split(
        rows, cutoff, gap, cutoff + timedelta(days=1)
    )
    assert [row.event_id for row in training] == ["eligible"]
    assert [row.event_id for row in validation] == ["start"]
    assert omitted == 2
    _, later, _ = evaluation.time_split(
        rows, cutoff + timedelta(days=1), gap, cutoff + timedelta(days=2)
    )
    assert [row.event_id for row in later] == ["end"]
    with pytest.raises(ValueError):
        evaluation.time_split(rows, cutoff, timedelta(seconds=-1))


def test_train_only_fitting_and_metric_preconditions() -> None:
    training = [observation("A1", "A", 1), observation("B1", "B", 1)]
    validation = [observation("C1", "C", 2, 100.0)]
    report = evaluation.evaluate_baseline(training, validation)
    assert report["train_target_mean"] == 0.0
    assert report["mae"] == 100.0
    assert evaluation.fit_mean([2.0, 4.0]) == 3.0
    leaked = evaluation.fit_mean([0.0, 0.0, 100.0])
    assert evaluation.mae([100.0], [leaked]) == pytest.approx(200 / 3)
    invalid_vectors: tuple[tuple[list[float], list[float]], ...] = (
        ([], []),
        ([1.0], []),
        ([float("inf")], [1.0]),
    )
    for actual, predicted in invalid_vectors:
        with pytest.raises(ValueError):
            evaluation.mae(actual, predicted)
    with pytest.raises(ValueError, match="duplicate"):
        evaluation.evaluate_baseline(training, training[:1])


def write_source(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def test_resume_after_injected_failure_matches_clean_run(tmp_path: Path) -> None:
    source, checkpoint = tmp_path / "source.jsonl", tmp_path / "state.json"
    write_source(source, [{"id": str(i), "quantity": i} for i in range(5)])
    with pytest.raises(RuntimeError, match="row 4"):
        pipeline.run_pipeline(source, checkpoint, fail_before_commit_at=4)
    assert json.loads(checkpoint.read_text(encoding="utf-8"))["next_row"] == 2
    assert not list(tmp_path.glob(".state.json.*.tmp"))
    resumed = pipeline.run_pipeline(source, checkpoint)
    clean_run = pipeline.run_pipeline(source, tmp_path / "clean.json", batch_size=1)
    assert resumed == clean_run
    assert resumed["total_quantity"] == 10 and resumed["complete"] is True
    committed = checkpoint.read_bytes()
    assert pipeline.run_pipeline(source, checkpoint, batch_size=10) == resumed
    assert checkpoint.read_bytes() == committed


def test_atomic_failure_preserves_old_bytes_and_unrelated_files(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    target.write_text('{"old":true}\n', encoding="utf-8")
    unrelated = tmp_path / ".other.tmp"
    unrelated.write_text("learner-owned", encoding="utf-8")
    previous = target.read_bytes()

    def fail() -> None:
        raise RuntimeError("candidate rejected")

    with pytest.raises(RuntimeError, match="candidate"):
        pipeline.atomic_write_state(target, {"new": True}, fail)
    assert target.read_bytes() == previous
    assert unrelated.read_text(encoding="utf-8") == "learner-owned"
    assert not list(tmp_path.glob(".state.json.*.tmp"))


def test_replayed_ids_do_not_double_count_and_conflicts_publish_nothing(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    write_source(
        source, [{"id": "A", "quantity": 2}, {"id": "A", "quantity": 2}, {"id": "B", "quantity": 5}]
    )
    state = pipeline.run_pipeline(source, tmp_path / "valid.json")
    assert state["next_row"] == 3
    assert state["quantities"] == {"A": 2, "B": 5}
    assert state["total_quantity"] == 7
    write_source(source, [{"id": "A", "quantity": 2}, {"id": "A", "quantity": 3}])
    with pytest.raises(ValueError, match="conflicting"):
        pipeline.run_pipeline(source, tmp_path / "conflict.json")
    assert not (tmp_path / "conflict.json").exists()


@pytest.mark.parametrize(
    "patch",
    [
        {"total_quantity": 99},
        {"next_row": -1},
        {"next_row": True},
        {"version": True},
        {"complete": 1},
    ],
)
def test_corrupt_checkpoint_is_retained_without_silent_reset(
    tmp_path: Path, patch: dict[str, object]
) -> None:
    source, checkpoint = tmp_path / "source.jsonl", tmp_path / "state.json"
    write_source(source, [{"id": "A", "quantity": 2}])
    state = pipeline.run_pipeline(source, checkpoint)
    state.update(patch)
    checkpoint.write_text(json.dumps(state), encoding="utf-8")
    previous = checkpoint.read_bytes()
    with pytest.raises(ValueError):
        pipeline.run_pipeline(source, checkpoint)
    assert checkpoint.read_bytes() == previous


def test_changed_source_requires_explicit_new_checkpoint(tmp_path: Path) -> None:
    source, checkpoint = tmp_path / "source.jsonl", tmp_path / "state.json"
    write_source(source, [{"id": "A", "quantity": 2}])
    pipeline.run_pipeline(source, checkpoint)
    previous = checkpoint.read_bytes()
    source.write_text('{"id":"A","quantity":2}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        pipeline.run_pipeline(source, checkpoint)
    assert checkpoint.read_bytes() == previous


def test_empty_source_and_invalid_batch_sizes(tmp_path: Path) -> None:
    source, checkpoint = tmp_path / "empty.jsonl", tmp_path / "state.json"
    source.write_bytes(b"")
    for size in (0, -1, True):
        with pytest.raises(ValueError, match="batch_size"):
            pipeline.run_pipeline(source, checkpoint, batch_size=size)
    state = pipeline.run_pipeline(source, checkpoint)
    assert state["next_row"] == state["total_quantity"] == 0
    assert state["complete"] is True
    with pytest.raises(ValueError, match="must differ"):
        pipeline.run_pipeline(source, source)


@pytest.mark.parametrize(
    "text",
    [
        '{"id":"A","quantity":true}\n',
        "\n",
        '{"id":"A","quantity":-1}\n',
        '{"id":"A","quantity":2,"extra":3}\n',
        '{"id":"A","quantity":2,"quantity":3}\n',
        '{"id":"A","quantity":2}\n\n',
    ],
)
def test_snapshot_schema_failure_prevents_publication(tmp_path: Path, text: str) -> None:
    source, checkpoint = tmp_path / "source.jsonl", tmp_path / "state.json"
    source.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        pipeline.run_pipeline(source, checkpoint)
    assert not checkpoint.exists()
