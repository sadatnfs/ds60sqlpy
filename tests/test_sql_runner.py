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
    assert paths[0].name == "sql_found_01_relational_design_solutions.sql"
    assert paths[-1].name == "sql_temporal_01_domain_modelling_solutions.sql"
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
