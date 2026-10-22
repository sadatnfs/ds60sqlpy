"""Run PostgreSQL course scripts through ``psql`` without shell-specific pipes."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urlunsplit

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.runtime_environment import external_dll_directory, external_program_environment
from ds60sqlpy.sql_notebook import (
    SqlNotebookError,
    course_psql_environment,
    validate_course_database_target,
)

# Public disposable-course defaults, never production credentials.
# secret-scan: allow-fixture
DEFAULT_DATABASE_URL = "postgresql://admin:admin@localhost:55432/advanced_sql_training"


def default_course_database_url(environment: Mapping[str, str] | None = None) -> str:
    """Choose a host target or safely encoded private-container course target."""

    settings = os.environ if environment is None else environment
    if settings.get("DS60_CONTAINER") != "1":
        return DEFAULT_DATABASE_URL
    user = quote(settings.get("DS60_COURSE_USER", "admin"), safe="")
    password = quote(settings.get("DS60_COURSE_PASSWORD", "admin"), safe="")
    return urlunsplit(
        ("postgresql", f"{user}:{password}@127.0.0.1:5432", "/advanced_sql_training", "", "")
    )


class SqlRunnerError(RuntimeError):
    """Raised when PostgreSQL course execution cannot proceed."""


@dataclass(frozen=True, slots=True)
class SqlRun:
    """The result of one psql invocation."""

    path: Path
    returncode: int
    stdout: str = ""
    stderr: str = ""


class SqlRunner:
    """Execute setup, lessons, and solutions using a portable subprocess call."""

    def __init__(
        self,
        catalog: Catalog,
        database_url: str | None = None,
        *,
        quiet: bool = False,
        capture_output: bool = False,
    ) -> None:
        executable = shutil.which("psql", path=external_program_environment().get("PATH"))
        if executable is None:
            raise SqlRunnerError(
                "psql is not on PATH. Install PostgreSQL client tools or use the "
                "cross-platform Docker Compose commands in docs."
            )
        self.executable = executable
        self.catalog = catalog
        database_target = (
            database_url or os.environ.get("DS60_DATABASE_URL") or default_course_database_url()
        )
        try:
            self.database_url = validate_course_database_target(database_target)
        except SqlNotebookError as exc:
            raise SqlRunnerError(
                "Refusing to run SQL: the connection target is not the disposable "
                "advanced_sql_training course database."
            ) from exc
        self.quiet = quiet
        self.capture_output = capture_output

    def run_file(self, path: Path) -> SqlRun:
        """Run one SQL file with safe psql startup and stop-on-error behavior."""

        command = [
            self.executable,
            "-X",
            "--no-password",
            "-v",
            "ON_ERROR_STOP=1",
            "-f",
            str(path),
        ]
        environment = course_psql_environment(
            self.database_url,
            application_name="ds60sqlpy-course-runner",
            connect_timeout=10,
        )
        environment = external_program_environment(environment)
        stdout = (
            subprocess.PIPE if self.capture_output else subprocess.DEVNULL if self.quiet else None
        )
        if self.capture_output:
            environment["PGOPTIONS"] = "-c statement_timeout=30000 -c lock_timeout=2000"
        try:
            with external_dll_directory():
                result = subprocess.run(
                    command,
                    check=False,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout,
                    stderr=subprocess.PIPE if self.capture_output else None,
                    text=True,
                    timeout=60 if self.capture_output else None,
                )
        except subprocess.TimeoutExpired as exc:
            raise SqlRunnerError(
                "Course SQL preparation timed out. The training schema may be incomplete. "
                "Inspect database availability, then explicitly reset and verify it again."
            ) from exc
        return SqlRun(
            path=path,
            returncode=result.returncode,
            stdout=(result.stdout or "") if self.capture_output else "",
            stderr=(result.stderr or "") if self.capture_output else "",
        )

    def setup(self) -> SqlRun:
        """Reset and seed the course-owned ``training`` schema."""

        return self.run_file(self.catalog.repo_root / "sql" / "postgres-60day" / "00_setup.sql")

    def verify(self) -> SqlRun:
        """Run fail-fast invariants against the course seed data."""

        return self.run_file(self.catalog.repo_root / "sql" / "postgres-60day" / "00_verify.sql")

    def lesson(self, day: int) -> SqlRun:
        """Run one lesson by its track ordering number."""

        lesson = self.catalog.by_day("sql", day)
        return self.run_file(self.catalog.resolve(lesson.lesson_path))

    def lesson_id(self, lesson_id: str) -> SqlRun:
        """Run one SQL lesson by stable catalog ID."""

        lesson = self.catalog.get(lesson_id)
        if lesson.runner != "sql":
            raise SqlRunnerError(f"Lesson does not use the SQL runner: {lesson_id}")
        return self.run_file(self.catalog.resolve(lesson.lesson_path))

    def all_lessons(self) -> tuple[SqlRun, ...]:
        """Run every SQL lesson sequentially, preserving explicit project state."""

        runs: list[SqlRun] = []
        for lesson in self.catalog:
            if lesson.runner != "sql":
                continue
            run = self.run_file(self.catalog.resolve(lesson.lesson_path))
            runs.append(run)
            if run.returncode != 0:
                break
        return tuple(runs)

    def solution_files(self) -> tuple[Path, ...]:
        """Return cataloged executable SQL solutions in lesson order."""

        return tuple(
            self.catalog.resolve(path)
            for lesson in self.catalog
            if lesson.runner == "sql"
            for path in lesson.solution_paths
            if Path(path).suffix == ".sql"
        )

    def all_solutions(self) -> tuple[SqlRun, ...]:
        """Run every executable SQL solution sequentially."""

        runs: list[SqlRun] = []
        for path in self.solution_files():
            run = self.run_file(path)
            runs.append(run)
            if run.returncode != 0:
                break
        return tuple(runs)
