"""Opt-in PostgreSQL proofs for the new SQL curriculum.

Set DS60_SQL_EXPANSION_TEST_URL to an isolated local advanced_sql_training
URL. No test connects using ambient DS60_DATABASE_URL or a default server.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from ds60sqlpy.sql_notebook import course_psql_environment, validate_course_database_target

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "professional"
STEMS = (
    "sql_start_01_tables_and_grain",
    "sql_start_02_values_null_order",
    "sql_start_03_query_debugging",
    "sql_quality_01_bags_and_fanout",
    "sql_scale_01_cursors_and_batches",
    "sql_concurrency_01_isolation_and_versions",
)


@pytest.fixture
def live_psql() -> tuple[str, dict[str, str]]:
    target = os.environ.get("DS60_SQL_EXPANSION_TEST_URL")
    if not target:
        pytest.skip("set DS60_SQL_EXPANSION_TEST_URL for the isolated PostgreSQL proof")
    validated = validate_course_database_target(target)
    psql = shutil.which("psql")
    if psql is None:
        pytest.fail("psql must be installed for an explicitly requested live SQL check")
    environment = course_psql_environment(
        validated, application_name="ds60-sql-expansion-test", connect_timeout=5
    )
    return psql, environment


def _run(
    live_psql: tuple[str, dict[str, str]],
    *,
    script: Path | None = None,
    command: str | None = None,
) -> subprocess.CompletedProcess[str]:
    psql, environment = live_psql
    arguments = [psql, "-X", "-qAt", "-v", "ON_ERROR_STOP=1"]
    if script is not None:
        arguments.extend(["-f", str(script)])
    elif command is not None:
        arguments.extend(["-c", command])
    else:
        raise ValueError("a script or command is required")
    result = subprocess.run(
        arguments, cwd=ROOT, env=environment, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.mark.parametrize("stem", STEMS)
@pytest.mark.parametrize("kind", ("lesson", "solution"))
def test_sql_expansion_executes_twice_without_persistent_fixture(
    live_psql: tuple[str, dict[str, str]], stem: str, kind: str
) -> None:
    """Actual PostgreSQL evaluates answers, negative controls, and rollback."""
    path = SQL / "lessons" / f"{stem}.sql"
    if kind == "solution":
        path = SQL / "solutions" / f"{stem}_solutions.sql"
    _run(live_psql, script=path)
    _run(live_psql, script=path)
    # A different connection must see no accidentally permanent fixture tables.
    remaining = _run(
        live_psql,
        command="""
        SELECT count(*) FROM pg_catalog.pg_class AS c
        JOIN pg_catalog.pg_namespace AS n ON n.oid=c.relnamespace
        WHERE n.nspname NOT LIKE 'pg_temp_%'
          AND c.relname IN ('start_readings','start_shipments','start_tasks',
            'quality_source','quality_target','quality_sent','quality_received',
            'quality_orders','quality_lines','quality_attempts','scale_events',
            'concurrency_stock','model_trace');
        """,
    )
    assert remaining.stdout.strip() == "0"


def test_sql_expansion_observes_two_session_snapshots(
    live_psql: tuple[str, dict[str, str]],
) -> None:
    """Prove the optional lab's two visibility observations and own cleanup."""
    fixture = SQL / "fixtures" / "concurrency"
    # Refuse an existing schema before taking ownership of any state.
    _run(live_psql, script=fixture / "verify_cleanup.sql")
    prepared = False
    psql, environment = live_psql
    try:
        _run(live_psql, script=fixture / "prepare.sql")
        prepared = True
        for isolation, expected_second in (
            ("READ COMMITTED", "A|4|2"),
            ("REPEATABLE READ", "A|5|1"),
        ):
            _run(
                live_psql,
                command="UPDATE sql_concurrency_live.stock SET available=5,version=1 WHERE sku='A'",
            )
            session = subprocess.Popen(
                [psql, "-X", "-qAt", "-v", "ON_ERROR_STOP=1"],
                cwd=ROOT,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                assert session.stdin is not None
                assert session.stdout is not None
                session.stdin.write(
                    f"BEGIN ISOLATION LEVEL {isolation};\n"
                    "SET LOCAL statement_timeout='10s';\n"
                    "SELECT sku,available,version FROM sql_concurrency_live.stock WHERE sku='A';\n"
                    "\\echo first_snapshot_ready\n"
                )
                session.stdin.flush()
                observed: list[str] = []
                while True:
                    line = session.stdout.readline()
                    assert line, "session A ended before establishing its snapshot"
                    if line.strip() == "first_snapshot_ready":
                        break
                    observed.append(line.strip())
                assert "A|5|1" in observed
                committed = _run(
                    live_psql,
                    command="""
                    BEGIN;
                    SET LOCAL lock_timeout='2s';
                    SET LOCAL statement_timeout='10s';
                    UPDATE sql_concurrency_live.stock
                    SET available=available-1,version=version+1
                    WHERE sku='A' AND version=1 AND available>=1
                    RETURNING sku,available,version;
                    COMMIT;
                    """,
                )
                assert committed.stdout.strip() == "A|4|2"
                session.stdin.write(
                    "SELECT sku,available,version FROM sql_concurrency_live.stock WHERE sku='A';\n"
                    "ROLLBACK;\n\\q\n"
                )
                session.stdin.flush()
                rest, _ = session.communicate(timeout=15)
                assert session.returncode == 0, rest
                assert expected_second in rest.splitlines()
                fresh = _run(
                    live_psql,
                    command=(
                        "SELECT sku,available,version FROM sql_concurrency_live.stock WHERE sku='A'"
                    ),
                )
                assert fresh.stdout.strip() == "A|4|2"
            finally:
                if session.poll() is None:
                    session.terminate()
                    session.communicate(timeout=10)
    finally:
        if prepared:
            _run(live_psql, script=fixture / "cleanup.sql")
    _run(live_psql, script=fixture / "verify_cleanup.sql")
