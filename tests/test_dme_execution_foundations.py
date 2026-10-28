"""Independent engine, layout, retry, backfill and state-recovery contracts."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from itertools import permutations
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROGRAMS = ROOT / "courses/data-ml-engineering/authoring/foundations/examples"


def reference(number: int) -> ModuleType:
    dependencies = {17: ("duckdb", "polars"), 18: ("pyarrow",), 22: ("duckdb",)}.get(number, ())
    for dependency in dependencies:
        pytest.importorskip(dependency, reason="Prepared data-engineering runtime required")
    name = f"dme_execution_{number}"
    spec = importlib.util.spec_from_file_location(name, PROGRAMS / f"dme-{number:03}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("number", [17, 18, 20, 21, 22, 23, 24])
def test_complete_execution_examples(number: int) -> None:
    module = reference(number)
    assert isinstance(module.example_one(), dict)
    assert isinstance(module.example_two(), dict)


def test_real_engines_preserve_known_zero_and_reject_duplicate_grain() -> None:
    module = reference(17)
    values = [(7, "day-a", None), (8, "day-a", 0), (8, "day-b", 4)]
    expected = [(7, None, 1, 0), (8, 4, 2, 2)]
    assert module.sql_result(lambda: sqlite3.connect(":memory:"), values) == expected
    assert module.sql_result(lambda: module.duckdb.connect(":memory:"), values) == expected
    assert module.polars_result(values, explicit_empty_policy=True) == expected
    duplicated = [values[0], values[0]]
    with pytest.raises(sqlite3.IntegrityError):
        module.sql_result(lambda: sqlite3.connect(":memory:"), duplicated)
    with pytest.raises(ValueError, match="grain"):
        module.polars_result(duplicated)


def test_real_layout_preserves_keys_across_all_supported_fixture_file_sizes(tmp_path: Path) -> None:
    module = reference(18)
    for size in (1, 2, 4):
        dataset = module.write_layout(tmp_path / str(size), size)
        result = module.selected(dataset, "2024-01-02")
        assert result["rows"] == [
            {"delivery_id": 3, "packages": 4},
            {"delivery_id": 4, "packages": 1},
        ]
        assert result["selected_fragments"] <= result["all_fragments"]
        assert module.selected(dataset, "2024-02-01")["selected_fragments"] == 0


def test_completed_workflow_cannot_hide_corrupted_publication(tmp_path: Path) -> None:
    module = reference(20)
    baseline = module.run_pipeline(tmp_path, [2, 3, 1])
    path = tmp_path / (baseline["identity"] + ".product.json")
    path.write_text(json.dumps({**baseline["product"], "packages": 999}))
    with pytest.raises(ValueError, match="Published content"):
        module.run_pipeline(tmp_path, [2, 3, 1])


def test_outbox_inbox_replay_and_conflicting_identity_are_atomic(tmp_path: Path) -> None:
    module = reference(21)
    source = module.producer(tmp_path / "producer.db")
    destination = module.consumer(tmp_path / "consumer.db")
    try:
        module.create_event(source, "one", 2)
        module.create_event(source, "two", 3)
        with pytest.raises(RuntimeError):
            module.dispatch(source, destination, fail_after_effect=True)
        assert module.dispatch(source, destination) == [("one", "replayed"), ("two", "applied")]
        assert destination.execute("select units from projection").fetchone() == (5,)
        with pytest.raises(ValueError, match="conflicting"):
            module.create_event(source, "one", 100)
        with pytest.raises(ValueError, match="differs"):
            module.consume(destination, "one", 100)
        assert source.execute("select units from state").fetchone() == (5,)
        assert destination.execute("select units from projection").fetchone() == (5,)
        assert source.execute("select sum(sent) from outbox").fetchone() == (2,)
    finally:
        source.close()
        destination.close()


def test_backfill_rolls_back_earlier_partition_on_later_conflict() -> None:
    module = reference(22)
    with module.database() as connection:
        events = module.fixture()
        module.backfill(connection, events, "2024-01-01", "2024-01-02", 1)
        module.backfill(connection, events, "2024-01-02", "2024-01-03", 2)
        before = module.rows(connection)
        changed = [{**row, "packages": 99} if row["id"] == "B" else row for row in events]
        with pytest.raises(ValueError, match="conflicting"):
            module.backfill(connection, changed, "2024-01-01", "2024-01-03", 2)
        assert module.rows(connection) == before


def test_backfill_empty_complete_partition_and_order_independence() -> None:
    module = reference(22)
    with module.database() as connection:
        module.backfill(connection, [], "2024-01-01", "2024-01-02", 1)
        assert module.rows(connection) == [("2024-01-01", 0, 1)]
        events = module.fixture()
        module.backfill(connection, events, "2024-01-01", "2024-01-04", 2)
        assert all(
            decision == "replayed"
            for _, decision in module.backfill(
                connection, list(reversed(events)), "2024-01-01", "2024-01-04", 2
            )
        )


def test_window_boundaries_watermark_monotonicity_and_sink_revision() -> None:
    module = reference(23)
    windows = module.Windows(grace=0)
    windows.event(4, 2)
    windows.event(5, 3)
    windows.advance(5)
    assert module.materialize(windows.changes) == {0: 2}
    assert set(windows.states) == {5}
    assert windows.event(4, 100) == "late-side-output"
    with pytest.raises(ValueError, match="monotone"):
        windows.advance(4)
    changes = [(0, 1, 5), (0, 2, 9), (0, 1, 5), (5, 1, 2)]
    for order in permutations(changes):
        assert module.materialize(order) == {0: 9, 5: 2}
    with pytest.raises(ValueError, match="two values"):
        module.materialize([(0, 2, 9), (0, 2, 10)])


@pytest.mark.parametrize("corruption", ["offset", "effect", "missing-effect"])
def test_checkpoint_rejects_corrupt_committed_prefix(tmp_path: Path, corruption: str) -> None:
    module = reference(24)
    path = tmp_path / "state.db"
    connection = module.connect(path, module.fixture(), "a" * 64)
    module.resume(connection, module.fixture())
    with connection:
        if corruption == "offset":
            connection.execute("update cursor set next_offset=99")
        elif corruption == "effect":
            connection.execute("update effects set value=999 where event_id='A'")
        else:
            connection.execute("delete from effects where event_id='A'")
    connection.close()
    with pytest.raises(ValueError, match="offset|prefix"):
        module.connect(path, module.fixture(), "a" * 64)


def test_resume_rejects_changed_tape_after_connection_and_conflicting_replay(
    tmp_path: Path,
) -> None:
    module = reference(24)
    tape = [["A", 2], ["A", 3]]
    connection = module.connect(tmp_path / "state.db", tape, "a" * 64)
    try:
        with pytest.raises(ValueError, match="differs"):
            module.resume(connection, [["B", 100]])
        with pytest.raises(ValueError, match="conflicting"):
            module.resume(connection, tape)
        assert module.snapshot(connection) == {"next_offset": 1, "effects": {"A": 2}}
    finally:
        connection.close()
