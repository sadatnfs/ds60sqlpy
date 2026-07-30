from __future__ import annotations

import json
from pathlib import Path

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.progress import ProgressStore


def test_progress_round_trip(tmp_path: Path) -> None:
    catalog = Catalog.load()
    store = ProgressStore(catalog, tmp_path / "progress.json")

    assert store.next_lesson("python").id == "python-01"  # type: ignore[union-attr]
    completion = store.mark_complete("python-01", "First lesson")

    assert completion.lesson_id == "python-01"
    assert store.completions()[0].notes == "First lesson"
    assert store.next_lesson("python").id == "python-02"  # type: ignore[union-attr]
    assert store.next_lesson("bridge").id == "bridge-01"  # type: ignore[union-attr]


def test_progress_reset_removes_only_progress_file(tmp_path: Path) -> None:
    catalog = Catalog.load()
    path = tmp_path / "learning" / "progress.json"
    store = ProgressStore(catalog, path)
    store.mark_complete("sql-01")

    store.reset()

    assert not path.exists()


def test_progress_can_unmark_and_replace_completions(tmp_path: Path) -> None:
    catalog = Catalog.load()
    store = ProgressStore(catalog, tmp_path / "progress.json")
    first = store.mark_complete("python-01", "Keep this note")

    replaced = store.replace_completions(["python-01", "sql-01", "sql-01"])

    assert [item.lesson_id for item in replaced] == ["python-01", "sql-01"]
    assert replaced[0] == first
    assert store.mark_incomplete("sql-01")
    assert not store.mark_incomplete("sql-01")
    assert [item.lesson_id for item in store.completions()] == ["python-01"]
    assert store.replace_completions([]) == ()
    assert not store.path.exists()


def test_progress_rejects_unknown_lesson_in_saved_file(tmp_path: Path) -> None:
    catalog = Catalog.load()
    path = tmp_path / "progress.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "completed": {
                    "python-99": {
                        "completed_at": "2026-01-01T00:00:00+00:00",
                        "notes": "",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown lesson"):
        ProgressStore(catalog, path).completions()
