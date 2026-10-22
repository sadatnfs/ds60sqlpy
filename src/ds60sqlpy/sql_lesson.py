"""Execute guarded learner SQL scripts with their fixed psql include graph."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import validate_content_path
from ds60sqlpy.execution import (
    ALLOWED_TIMEOUT_SECONDS,
    COURSE_ROLE_QUERY,
    MAX_CODE_BYTES,
    WORKER_GATE,
    PadRunner,
)
from ds60sqlpy.runtime_environment import external_program_environment
from ds60sqlpy.sql_notebook import (
    SqlNotebookError,
    _psql_meta_segments,
    _relative_include_sources,
    course_psql_environment,
    generate_sql_notebook,
    validate_course_database_target,
    validate_sql_workspace,
)
from ds60sqlpy.sql_runner import default_course_database_url

SAFE_PSQL_COMMANDS = {"echo", "set", "ir", "gset", "if", "elif", "else", "endif", "gexec"}
PSQL_WORKER = (
    WORKER_GATE
    + "COURSE_ROLE_QUERY = "
    + repr(COURSE_ROLE_QUERY)
    + "\n"
    + r"""
import json, os, subprocess, sys
from pathlib import Path
try:
    import psycopg
    with psycopg.connect('', options='-c statement_timeout=2000 -c lock_timeout=1000') as conn:
        role = conn.execute(COURSE_ROLE_QUERY).fetchone()
        if conn.info.dbname != 'advanced_sql_training' or not role or role[0]:
            raise ValueError('Whole SQL lessons require the limited course login.')
except Exception:
    print(json.dumps({'error_type':'CourseRoleError',
        'message':'Whole SQL lessons require the local course database and a limited login.'}))
    sys.exit(1)
process = subprocess.Popen(
    [os.environ['DS60_PSQL'], '-X', '--no-password', '--quiet',
     '-v', 'ON_ERROR_STOP=1', '-f', sys.argv[1]],
    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stream = process.stdout
first = stream.readline(512)
if first.startswith(b'__DS60_SESSION__:'):
    pid, started = first.decode('utf-8').strip().split(':',2)[1:]
    Path(os.environ['DS60_PAD_BACKEND_START']).write_text(started)
    Path(os.environ['DS60_PAD_BACKEND_PID']).write_text(pid)
else:
    sys.stdout.buffer.write(first)
while chunk := stream.read(8192):
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
stream.close()
sys.exit(process.wait())
"""
)


def _lesson_sources(catalog: Catalog, lesson_id: str) -> tuple[Path, ...]:
    lesson = catalog.get(lesson_id)
    if lesson.runner != "sql" or Path(lesson.lesson_path).suffix.casefold() != ".sql":
        raise ValueError("Whole SQL mode requires a cataloged SQL source file.")
    source = catalog.resolve(lesson.lesson_path)
    sources = (source, *_relative_include_sources(catalog, source))
    for path in sources:
        validate_content_path(
            catalog.repo_root, path.relative_to(catalog.repo_root).as_posix(), "SQL source/include"
        )
    return sources


def lesson_source_policy(catalog: Catalog, lesson_id: str) -> None:
    """Permit reviewed directives when executing, never shell/reconnect/output commands."""

    try:
        sources = _lesson_sources(catalog, lesson_id)
    except SqlNotebookError as exc:
        raise ValueError(str(exc)) from exc
    for path in sources:
        for segment in _psql_meta_segments(path.read_text(encoding="utf-8")):
            command = re.match(r"\s*\\([a-z]+)\b", segment)
            if command is None or command.group(1) not in SAFE_PSQL_COMMANDS or "`" in segment:
                raise ValueError(
                    "This SQL artifact contains a client directive outside whole-lesson mode. "
                    "Use its external workflow. Shell/reconnect/output directives are disabled."
                )


class SqlLessonRunner:
    """Share a nonoverwriting working copy with Jupyter and bounded pad execution."""

    def __init__(self, catalog: Catalog, pads: PadRunner):
        self.catalog = catalog
        self.pads = pads

    def _workspace(self, lesson_id: str) -> Path:
        try:
            _lesson_sources(self.catalog, lesson_id)
            workspace = generate_sql_notebook(self.catalog, lesson_id)
        except SqlNotebookError as exc:
            raise ValueError(str(exc)) from exc
        return workspace.sql_path

    def read(self, lesson_id: str) -> dict[str, Any]:
        path = self._workspace(lesson_id)
        if path.stat().st_size > MAX_CODE_BYTES:
            raise ValueError(
                "This SQL script exceeds the browser input limit. Use its Jupyter/CLI workflow."
            )
        return {"code": path.read_text(encoding="utf-8"), "saved": True, "mode": "lesson"}

    def save(self, lesson_id: str, code: str) -> Path:
        return self.pads._save_path(self._workspace(lesson_id), code)

    def history(self, lesson_id: str) -> list[dict[str, Any]]:
        return self.pads._history_path(self._workspace(lesson_id))

    def read_history(self, lesson_id: str, history_id: str) -> str:
        return self.pads._read_history_path(self._workspace(lesson_id), history_id)

    def run(self, lesson_id: str, code: str, *, timeout_seconds: int = 60) -> dict[str, Any]:
        if type(timeout_seconds) is not int or timeout_seconds not in ALLOWED_TIMEOUT_SECONDS:
            raise ValueError("Choose a run limit of 15, 60 or 120 seconds.")
        lesson_source_policy(self.catalog, lesson_id)
        if self.pads.python is None:
            raise ValueError("Select a usable Python 3.11-3.12 backend with psycopg.")
        environment = external_program_environment()
        executable = shutil.which("psql", path=environment.get("PATH"))
        if executable is None:
            raise ValueError(
                "Whole SQL lessons need psql. Use Docker or install PostgreSQL client tools."
            )
        path = self.save(lesson_id, code)
        try:
            validate_sql_workspace(self.catalog, lesson_id, submitted_code=code)
            target = validate_course_database_target(
                os.environ.get("DS60_DATABASE_URL") or default_course_database_url()
            )
        except SqlNotebookError as exc:
            raise ValueError(str(exc)) from exc
        database = course_psql_environment(
            target, application_name="ds60-coding-pad", connect_timeout=3
        )
        for name in tuple(environment):
            if name.startswith("PG"):
                environment.pop(name)
        environment.update(
            {name: value for name, value in database.items() if name.startswith("PG")}
        )
        environment.update(
            DS60_PSQL=executable,
            PGOPTIONS="-c statement_timeout=5000 -c lock_timeout=2000",
            PYTHONIOENCODING="utf-8",
            PYTHONUTF8="1",
        )
        snapshot: Path | None = None
        wrapper: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=".submission-",
                suffix=".sql",
                delete=False,
            ) as source:
                snapshot = Path(source.name)
                source.write(code)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=".session-",
                suffix=".sql",
                delete=False,
            ) as source:
                wrapper = Path(source.name)
                source.write(
                    "\\pset format unaligned\n\\pset tuples_only on\n"
                    "SELECT '__DS60_SESSION__:' || pid || ':' || backend_start::text "
                    "FROM pg_stat_activity WHERE pid=pg_backend_pid();\n"
                    "\\pset format aligned\n\\pset tuples_only off\n"
                    f"\\ir {snapshot.name}\n"
                )
            result = self.pads._execute(
                [self.pads.python, "-I", "-u", "-c", PSQL_WORKER, str(wrapper)],
                environment,
                "sql",
                timeout_seconds=timeout_seconds,
                truncate_output=True,
            )
            error_line = None
            if result.returncode:
                matches = re.findall(
                    rf"(?m)^psql:.*{re.escape(snapshot.name)}:(\d+):", result.output
                )
                if matches and 1 <= int(matches[-1]) <= code.count("\n") + 1:
                    error_line = int(matches[-1])
            return {
                **asdict(result),
                "mode": "lesson",
                "error_line": error_line,
                "source_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
            }
        except SqlNotebookError as exc:
            raise ValueError(str(exc)) from exc
        finally:
            if snapshot is not None:
                snapshot.unlink(missing_ok=True)
            if wrapper is not None:
                wrapper.unlink(missing_ok=True)
