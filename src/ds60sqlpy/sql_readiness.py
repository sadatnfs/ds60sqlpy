"""Inspect and non-destructively prepare the course database a lesson needs.

A learner may open any SQL or Python-to-PostgreSQL bridge lesson first. The seed
``training`` schema and the schemas that stateful lesson groups commit for their
later lessons are created on demand when they are absent. Existing data is never
dropped here; restoring changed seed data remains the separate, explicitly
confirmed reset.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from ds60sqlpy.catalog import Catalog, Lesson
from ds60sqlpy.sql_runner import SqlRunner, SqlRunnerError

# Course-owned schemas that a stateful lesson group commits for its later lessons.
PROJECT_SCHEMAS = {"dwh-project": "dwh"}
_IDENTIFIER = re.compile(r"[a-z_][a-z0-9_]{0,62}")
_TRANSCRIPT_LIMIT = 24_000


@dataclass(frozen=True, slots=True)
class Readiness:
    """What the course database offers one lesson right now."""

    state: str
    detail: str = ""
    project_schema: str | None = None
    project_state: str | None = None
    creator: str | None = None
    creator_title: str | None = None
    actions: tuple[str, ...] = field(default_factory=tuple)

    def as_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["actions"] = list(self.actions)
        return payload


def uses_course_database(lesson: Lesson) -> bool:
    """Whether the lesson's own code reads the course tables.

    SQL lessons and the bridge track, which drives PostgreSQL from Python, do.
    SQL snippets reach the database from any lesson, so runs check those too.
    """

    return lesson.runner == "sql" or lesson.track == "bridge"


def _project(catalog: Catalog, lesson: Lesson) -> tuple[str, Lesson] | None:
    """Return the schema and creating lesson that a later group lesson depends on."""

    group = lesson.stateful_group
    if group is None or group not in PROJECT_SCHEMAS:
        return None
    members = [item for item in catalog if item.stateful_group == group]
    if not members or members[0].id == lesson.id:
        return None
    schema = PROJECT_SCHEMAS[group]
    if _IDENTIFIER.fullmatch(schema) is None:
        raise ValueError(f"Invalid project schema name: {schema}")
    return schema, members[0]


def _reason(text: str) -> str:
    """Return psql's error message, or the last output line when there is none."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if "ERROR:" in line:
            return line.split("ERROR:", 1)[1].strip()[:400]
    return lines[-1][:400] if lines else ""


def _schemas(runner: SqlRunner, names: tuple[str, ...]) -> dict[str, bool] | str:
    """Return schema presence, or a short reason the database could not be asked."""

    checks = ", ".join(f"'{name}', to_regnamespace('{name}') IS NOT NULL" for name in names)
    run = runner.query(f"SELECT json_build_object({checks})::text")
    if run.returncode != 0:
        return _reason(run.stderr) or "The course database did not accept the status check."
    try:
        values = json.loads(run.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return "The course database returned an unexpected status response."
    return {name: values.get(name) is True for name in names}


def inspect(catalog: Catalog, lesson_id: str, runner: SqlRunner) -> Readiness:
    """Report readiness without changing anything."""

    lesson = catalog.get(lesson_id)
    project = _project(catalog, lesson)
    names = ("training",) + ((project[0],) if project else ())
    present = _schemas(runner, names)
    if isinstance(present, str):
        return Readiness(state="unavailable", detail=present)
    project_fields: dict[str, Any] = {}
    if project:
        schema, creator = project
        project_fields = {
            "project_schema": schema,
            "project_state": "ready" if present[schema] else "missing",
            "creator": creator.id,
            "creator_title": creator.title,
        }
    if not present["training"]:
        return Readiness(state="missing", **project_fields)
    verify = runner.verify()
    if verify.returncode != 0:
        return Readiness(
            state="changed",
            detail=_reason(verify.stderr) or "The seed data checks did not pass.",
            **project_fields,
        )
    return Readiness(state="ready", **project_fields)


def prepare(catalog: Catalog, lesson_id: str, runner: SqlRunner) -> tuple[Readiness, str]:
    """Create only what is absent: the seed schema, then a group's project schema."""

    lesson = catalog.get(lesson_id)
    project = _project(catalog, lesson)
    names = ("training",) + ((project[0],) if project else ())
    present = _schemas(runner, names)
    if isinstance(present, str):
        return Readiness(state="unavailable", detail=present), ""
    transcript = ""
    actions: list[str] = []
    if not present["training"]:
        setup = runner.setup()
        transcript += setup.stdout + setup.stderr
        if setup.returncode != 0:
            return (
                Readiness(state="missing", detail=_reason(setup.stderr) or "Setup failed."),
                transcript[-_TRANSCRIPT_LIMIT:],
            )
        verify = runner.verify()
        transcript += verify.stdout + verify.stderr
        actions.append("training")
    if project and not present[project[0]]:
        built = runner.lesson_id(project[1].id)
        transcript += built.stdout + built.stderr
        if built.returncode != 0:
            current = inspect(catalog, lesson_id, runner)
            return (
                Readiness(
                    **{
                        **asdict(current),
                        "detail": _reason(built.stderr) or "The project schema build failed.",
                        "actions": tuple(actions),
                    }
                ),
                transcript[-_TRANSCRIPT_LIMIT:],
            )
        actions.append(project[0])
    current = inspect(catalog, lesson_id, runner)
    return (
        Readiness(**{**asdict(current), "actions": tuple(actions)}),
        transcript[-_TRANSCRIPT_LIMIT:],
    )


def ensure_before_run(catalog: Catalog, lesson_id: str) -> dict[str, Any] | None:
    """Prepare absent course objects before a database run; never fail the run itself.

    The usual case costs one read-only query: when every schema the lesson needs
    exists, nothing else runs before the learner's code.
    """

    try:
        runner = SqlRunner(catalog, capture_output=True)
        project = _project(catalog, catalog.get(lesson_id))
        present = _schemas(runner, ("training",) + ((project[0],) if project else ()))
        if isinstance(present, str) or all(present.values()):
            return None
        readiness, _ = prepare(catalog, lesson_id, runner)
    except (SqlRunnerError, OSError, ValueError):
        return None
    if not readiness.actions:
        return None
    built = {
        "training": "the course training tables",
        **{schema: f"the {schema} project schema" for schema in PROJECT_SCHEMAS.values()},
    }
    loaded = " and ".join(built.get(action, action) for action in readiness.actions)
    return {
        "actions": list(readiness.actions),
        "message": f"Prepared {loaded} before this run. They stay loaded for later lessons.",
        "readiness": readiness.as_payload(),
    }
