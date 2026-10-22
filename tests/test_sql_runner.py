from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.sql_runner import SqlRunner, SqlRunnerError


def _password_url(password: str) -> str:
    """Build a test URL without checking credential-shaped text into source."""

    return "://".join(("postgresql", f"course-user:{password}@localhost/advanced_sql_training"))


@pytest.fixture
def runner() -> SqlRunner:
    """Create a runner without depending on a locally installed psql binary."""

    with patch("ds60sqlpy.sql_runner.shutil.which", return_value="/usr/bin/psql"):
        return SqlRunner(Catalog.load(), database_url="postgresql:///advanced_sql_training")


def test_named_foundation_resolves_cataloged_sql(runner: SqlRunner) -> None:
    with patch.object(runner, "run_file") as run_file:
        runner.lesson_id("sql-found-01")

    path = run_file.call_args.args[0]
    assert path.name == "sql_found_01_relational_design.sql"
    assert path.is_relative_to(runner.catalog.repo_root)


def test_named_lesson_rejects_non_sql_track(runner: SqlRunner) -> None:
    with pytest.raises(SqlRunnerError, match="not in the SQL track"):
        runner.lesson_id("python-pro-01")


def test_solution_files_follow_catalog_and_are_sql(runner: SqlRunner) -> None:
    paths = runner.solution_files()

    assert len(paths) == len(runner.catalog.lessons("sql"))
    assert all(path.suffix == ".sql" for path in paths)
    assert paths[0].name == "sql_start_01_tables_and_grain_solutions.sql"
    assert paths[-1].name == "sql_concurrency_01_isolation_and_versions_solutions.sql"
    assert all(isinstance(path, Path) for path in paths)


@pytest.mark.parametrize(
    "target",
    [
        "postgresql:///valuable_database",
        "postgresql:///advanced_sql_training?dbname=postgres",
        "postgresql:///advanced_sql_training?service=valuable",
    ],
)
def test_runner_refuses_targets_outside_disposable_course_database(target: str) -> None:
    with (
        patch("ds60sqlpy.sql_runner.shutil.which", return_value="/usr/bin/psql"),
        pytest.raises(SqlRunnerError, match="disposable"),
    ):
        SqlRunner(Catalog.load(), database_url=target)


def test_runner_keeps_password_bearing_target_out_of_process_arguments(
    tmp_path: Path,
) -> None:
    connection = _password_url("temporary-password")
    sql_file = tmp_path / "lesson.sql"
    sql_file.write_text("SELECT 1;\n", encoding="utf-8")
    completed: subprocess.CompletedProcess[bytes] = subprocess.CompletedProcess(
        args=[],
        returncode=0,
    )

    with (
        patch("ds60sqlpy.sql_runner.shutil.which", return_value="/usr/bin/psql"),
        patch("ds60sqlpy.sql_runner.subprocess.run", return_value=completed) as run,
    ):
        runner = SqlRunner(Catalog.load(), database_url=connection)
        result = runner.run_file(sql_file)

    command = run.call_args.args[0]
    environment = run.call_args.kwargs["env"]
    assert result.returncode == 0
    assert connection not in command
    assert environment["PGDATABASE"] == "advanced_sql_training"
    assert environment["PGHOST"] == "localhost"
    assert environment["PGUSER"] == "course-user"
    assert environment["PGPASSWORD"] == "temporary-password"
    assert connection not in environment.values()
    assert "DS60_DATABASE_URL" not in environment


def test_captured_preparation_timeout_is_actionable(runner: SqlRunner) -> None:
    runner.capture_output = True
    with (
        patch("ds60sqlpy.sql_runner.subprocess.run", side_effect=subprocess.TimeoutExpired([], 60)),
        pytest.raises(SqlRunnerError, match="training schema may be incomplete"),
    ):
        runner.setup()


def test_frozen_runner_cleans_loader_state_without_reintroducing_pg_routing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os
    import sys
    from collections.abc import Iterator
    from contextlib import contextmanager

    sql_file = tmp_path / "lesson.sql"
    sql_file.write_text("SELECT 1;\n", encoding="utf-8")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", "/temporary/frozen-course", raising=False)
    monkeypatch.setenv("LD_LIBRARY_PATH", "/temporary/frozen-course")
    monkeypatch.setenv("LD_LIBRARY_PATH_ORIG", "/system/libraries")
    monkeypatch.setenv("_PYI_APPLICATION_HOME_DIR", "/temporary/frozen-course")
    monkeypatch.setenv("PATH", os.pathsep.join(("/temporary/frozen-course/bin", "/usr/bin")))
    monkeypatch.setenv("PGSERVICE", "must-not-route")
    monkeypatch.setenv("PGOPTIONS", "must-not-inherit")
    monkeypatch.setenv("PGHOST", "remote.invalid")
    monkeypatch.setenv("PGDATABASE", "valuable")
    monkeypatch.setenv("DS60_DATABASE_URL", "must-not-leak")
    entered: list[str] = []

    @contextmanager
    def dll_boundary() -> Iterator[None]:
        entered.append("entered")
        yield
        entered.append("restored")

    def invoke(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert entered == ["entered"]
        environment = kwargs["env"]
        assert isinstance(environment, dict)
        assert environment["LD_LIBRARY_PATH"] == "/system/libraries"
        assert "/temporary/frozen-course/bin" not in environment["PATH"]
        assert "_PYI_APPLICATION_HOME_DIR" not in environment
        assert "PGSERVICE" not in environment
        assert "DS60_DATABASE_URL" not in environment
        assert environment["PGDATABASE"] == "advanced_sql_training"
        assert environment["PGHOST"] == "127.0.0.1"
        assert environment["PGPORT"] == "58432"
        assert environment["PGUSER"] == "course-user"
        assert environment["PGOPTIONS"] == "-c statement_timeout=30000 -c lock_timeout=2000"
        return subprocess.CompletedProcess(command, 0, "verified", "")

    with (
        patch("ds60sqlpy.sql_runner.shutil.which", return_value="/usr/bin/psql") as which,
        patch("ds60sqlpy.sql_runner.external_dll_directory", side_effect=dll_boundary),
        patch("ds60sqlpy.sql_runner.subprocess.run", side_effect=invoke),
    ):
        course_runner = SqlRunner(
            Catalog.load(),
            database_url="postgresql://course-user@127.0.0.1:58432/advanced_sql_training",
            capture_output=True,
        )
        result = course_runner.run_file(sql_file)
    assert result.stdout == "verified"
    assert entered == ["entered", "restored"]
    assert "/temporary/frozen-course/bin" not in which.call_args.kwargs["path"]
    assert os.environ["LD_LIBRARY_PATH"] == "/temporary/frozen-course"
    assert os.environ["PGHOST"] == "remote.invalid"
