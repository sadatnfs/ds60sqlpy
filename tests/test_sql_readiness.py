from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy import sql_readiness
from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lab import LabServer
from ds60sqlpy.sql_readiness import ensure_before_run, inspect, prepare
from ds60sqlpy.sql_runner import SqlRun

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Catalog.load(ROOT)


class FakeRunner:
    """A database whose schemas appear only when the course scripts create them."""

    def __init__(self, *, schemas: set[str], seed_valid: bool = True, online: bool = True):
        self.schemas = set(schemas)
        self.seed_valid = seed_valid
        self.online = online
        self.calls: list[str] = []

    def query(self, statement: str) -> SqlRun:
        self.calls.append("query")
        if not self.online:
            return SqlRun(ROOT, 2, "", "psql: error: connection refused\n")
        names = [name for name in ("training", "dwh") if f"'{name}'" in statement]
        return SqlRun(ROOT, 0, json.dumps({name: name in self.schemas for name in names}) + "\n")

    def verify(self) -> SqlRun:
        self.calls.append("verify")
        ok = "training" in self.schemas and self.seed_valid
        failure = (
            "psql:00_verify.sql:58: ERROR:  customer seed invariant failed\n"
            "CONTEXT:  PL/pgSQL function inline_code_block line 24 at RAISE\n"
        )
        return SqlRun(ROOT, 0 if ok else 3, "", "" if ok else failure)

    def setup(self) -> SqlRun:
        self.calls.append("setup")
        self.schemas.add("training")
        return SqlRun(ROOT, 0, "CREATE SCHEMA\n")

    def lesson_id(self, lesson_id: str) -> SqlRun:
        self.calls.append(f"lesson:{lesson_id}")
        if lesson_id == "sql-52":
            self.schemas.add("dwh")
        return SqlRun(ROOT, 0, "COMMIT\n")


def test_status_is_read_only_and_reports_a_missing_seed() -> None:
    runner = FakeRunner(schemas=set())
    readiness = inspect(CATALOG, "sql-25", runner)  # type: ignore[arg-type]
    assert readiness.state == "missing" and readiness.project_schema is None
    assert runner.calls == ["query"]


def test_prepare_loads_an_absent_seed_once_then_reports_ready() -> None:
    runner = FakeRunner(schemas=set())
    readiness, transcript = prepare(CATALOG, "sql-25", runner)  # type: ignore[arg-type]
    assert readiness.state == "ready" and readiness.actions == ("training",)
    assert runner.calls.count("setup") == 1 and "CREATE SCHEMA" in transcript
    again, _ = prepare(CATALOG, "sql-25", runner)  # type: ignore[arg-type]
    assert again.actions == () and runner.calls.count("setup") == 1


def test_changed_seed_data_is_reported_but_never_reset_automatically() -> None:
    runner = FakeRunner(schemas={"training"}, seed_valid=False)
    readiness, _ = prepare(CATALOG, "sql-25", runner)  # type: ignore[arg-type]
    assert readiness.state == "changed"
    assert readiness.detail == "customer seed invariant failed"
    assert "setup" not in runner.calls


def test_later_warehouse_lessons_build_the_project_schema_from_its_first_lesson() -> None:
    runner = FakeRunner(schemas=set())
    before = inspect(CATALOG, "sql-53", runner)  # type: ignore[arg-type]
    assert (before.project_schema, before.project_state, before.creator) == (
        "dwh",
        "missing",
        "sql-52",
    )
    readiness, _ = prepare(CATALOG, "sql-54", runner)  # type: ignore[arg-type]
    assert readiness.actions == ("training", "dwh") and readiness.project_state == "ready"
    assert runner.calls.index("setup") < runner.calls.index("lesson:sql-52")
    first = inspect(CATALOG, "sql-52", FakeRunner(schemas={"training"}))  # type: ignore[arg-type]
    assert first.project_schema is None


def test_unreachable_database_is_unavailable_without_changes() -> None:
    runner = FakeRunner(schemas=set(), online=False)
    readiness, _ = prepare(CATALOG, "sql-01", runner)  # type: ignore[arg-type]
    assert readiness.state == "unavailable" and "connection refused" in readiness.detail
    assert runner.calls == ["query"]


def test_runs_report_preparation_only_when_something_was_created(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = FakeRunner(schemas=set())
    monkeypatch.setattr(sql_readiness, "SqlRunner", lambda *args, **kwargs: database)
    note = ensure_before_run(CATALOG, "sql-01")
    assert note is not None and note["actions"] == ["training"]
    assert "training tables" in note["message"]
    already = len(database.calls)
    assert ensure_before_run(CATALOG, "sql-01") is None
    assert database.calls[already:] == ["query"]


def test_runs_that_reach_the_course_database_prepare_it_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lessons = tuple(
        replace(CATALOG.get(item), prerequisites=()) for item in ("python-01", "bridge-03")
    )
    for lesson in lessons:
        for relative in (lesson.guide_path, lesson.lesson_path, *lesson.solution_paths):
            target = tmp_path / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(CATALOG.resolve(relative).read_bytes())
    prepared: list[str] = []

    def ensure(catalog: Catalog, lesson_id: str) -> dict[str, Any]:
        prepared.append(lesson_id)
        return {"actions": ["training"], "message": "Prepared the course training tables."}

    monkeypatch.setattr("ds60sqlpy.lab.ensure_before_run", ensure)
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(
        Catalog(tmp_path, lessons), progress_path=tmp_path / "progress.json", python=sys.executable
    )
    try:

        def run(lesson_id: str, language: str) -> dict[str, Any]:
            return server.action(
                {"action": "run", "lesson_id": lesson_id, "language": language, "code": "print(1)"}
            )

        assert "database_preparation" not in run("python-01", "python")
        assert prepared == []
        bridge = run("bridge-03", "python")
        assert bridge["database_preparation"]["actions"] == ["training"]
        assert prepared == ["bridge-03"]
        finished = run("python-01", "python")
        monkeypatch.setattr(server.pads, "run", lambda *args, **kwargs: finished)
        assert "database_preparation" in run("python-01", "sql")
        assert prepared == ["bridge-03", "python-01"]
    finally:
        server.server_close()
