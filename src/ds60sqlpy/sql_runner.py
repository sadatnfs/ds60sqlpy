"""Run PostgreSQL course scripts through ``psql`` without shell-specific pipes."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ds60sqlpy.catalog import Catalog

DEFAULT_DATABASE_URL = "postgresql://ds60:ds60@localhost:5432/advanced_sql_training"


class SqlRunnerError(RuntimeError):
    """Raised when PostgreSQL course execution cannot proceed."""


@dataclass(frozen=True, slots=True)
class SqlRun:
    """The result of one psql invocation."""

    path: Path
    returncode: int


class SqlRunner:
    """Execute setup, lessons, and solutions using a portable subprocess call."""

    def __init__(
        self,
        catalog: Catalog,
        database_url: str | None = None,
        *,
        quiet: bool = False,
    ) -> None:
        executable = shutil.which("psql")
        if executable is None:
            raise SqlRunnerError(
                "psql is not on PATH. Install PostgreSQL client tools or use the "
                "cross-platform Docker Compose commands in docs."
            )
        self.executable = executable
        self.catalog = catalog
        self.database_url = (
            database_url or os.environ.get("DS60_DATABASE_URL") or DEFAULT_DATABASE_URL
        )
        self.quiet = quiet

    def run_file(self, path: Path) -> SqlRun:
        """Run one SQL file with safe psql startup and stop-on-error behavior."""

        command = [
            self.executable,
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "--dbname",
            self.database_url,
            "-f",
            str(path),
        ]
        stdout = subprocess.DEVNULL if self.quiet else None
        result = subprocess.run(command, check=False, stdout=stdout)
        return SqlRun(path=path, returncode=result.returncode)

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
        if lesson.track != "sql":
            raise SqlRunnerError(f"Lesson is not in the SQL track: {lesson_id}")
        return self.run_file(self.catalog.resolve(lesson.lesson_path))

    def all_lessons(self) -> tuple[SqlRun, ...]:
        """Run every SQL lesson sequentially, preserving explicit project state."""

        runs: list[SqlRun] = []
        for lesson in self.catalog.lessons("sql"):
            run = self.run_file(self.catalog.resolve(lesson.lesson_path))
            runs.append(run)
            if run.returncode != 0:
                break
        return tuple(runs)

    def solution_files(self) -> tuple[Path, ...]:
        """Return cataloged executable SQL solutions in lesson order."""

        return tuple(
            self.catalog.resolve(path)
            for lesson in self.catalog.lessons("sql")
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
