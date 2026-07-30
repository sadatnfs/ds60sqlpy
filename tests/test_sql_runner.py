from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.sql_runner import SqlRunner, SqlRunnerError


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
