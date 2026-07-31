from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import call, patch
from urllib.parse import quote

import nbformat
import pytest

from ds60sqlpy.catalog import Catalog, Lesson
from ds60sqlpy.sql_notebook import (
    COURSE_DATABASE_NAME,
    DATABASE_RESET_CONFIRMATION,
    SqlNotebookError,
    _psql_meta_segments,
    course_psql_environment,
    generate_sql_notebook,
    prepare_sql_workspace,
    run_sql_workspace,
    sql_notebook_readiness,
    validate_course_database_target,
)


def _password_url(database_name: str, password: str) -> str:
    """Build a fake runtime URL without placing credential syntax in source."""

    authority = f"course-user:{password}@localhost/{database_name}"
    return "://".join(("postgresql", authority))


def _lesson(
    lesson_id: str,
    day: int,
    *,
    stateful_group: str | None = None,
) -> Lesson:
    return Lesson(
        id=lesson_id,
        track="sql",
        day=day,
        title=f"Lesson {day}",
        level="foundation",
        phase="Tests",
        estimated_minutes=30,
        prerequisites=(),
        lesson_path=f"sql/lessons/{lesson_id}.sql",
        guide_path=f"sql/guides/{lesson_id}.md",
        solution_paths=(
            f"sql/solutions/{lesson_id}.md",
            f"sql/solutions/{lesson_id}.sql",
        ),
        dependency_group="postgres",
        network="offline",
        stateful_group=stateful_group,
    )


@pytest.fixture
def catalog(tmp_path: Path) -> Catalog:
    """Build a minimal catalog with real source and support files."""

    lessons = (
        _lesson("sql-01", 1),
        _lesson("sql-52", 52, stateful_group="dwh-project"),
        _lesson("sql-53", 53, stateful_group="dwh-project"),
        _lesson("sql-54", 54, stateful_group="dwh-project"),
        Lesson(
            id="python-01",
            track="python",
            day=1,
            title="Python",
            level="foundation",
            phase="Tests",
            estimated_minutes=30,
            prerequisites=(),
            lesson_path="python/lesson.py",
            guide_path="python/guide.md",
            solution_paths=("python/solution.py",),
            dependency_group="core",
            network="offline",
        ),
    )
    for lesson in lessons:
        lesson_path = tmp_path / lesson.lesson_path
        lesson_path.parent.mkdir(parents=True, exist_ok=True)
        lesson_path.write_text(
            f"\\echo '{lesson.id}'\nSELECT {lesson.day};\n",
            encoding="utf-8",
        )
        guide_path = tmp_path / lesson.guide_path
        guide_path.parent.mkdir(parents=True, exist_ok=True)
        guide_path.write_text(f"# {lesson.title}\n", encoding="utf-8")
        for raw_solution in lesson.solution_paths:
            solution_path = tmp_path / raw_solution
            solution_path.parent.mkdir(parents=True, exist_ok=True)
            solution_path.write_text(
                (
                    f"# {lesson.title} solution\n"
                    if solution_path.suffix == ".md"
                    else f"\\echo '{lesson.id} solution'\nSELECT {lesson.day};\n"
                ),
                encoding="utf-8",
            )

    support = tmp_path / "sql" / "postgres-60day"
    support.mkdir(parents=True)
    (support / "00_setup.sql").write_text("SELECT 'setup';\n", encoding="utf-8")
    (support / "00_verify.sql").write_text("SELECT 'verify';\n", encoding="utf-8")
    return Catalog(tmp_path, lessons)


def test_generate_notebook_is_valid_guided_and_credential_free(
    catalog: Catalog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DS60_DATABASE_URL",
        _password_url(COURSE_DATABASE_NAME, "do-not-save-me"),
    )

    workspace = generate_sql_notebook(catalog, "sql-01")
    notebook = nbformat.read(  # type: ignore[no-untyped-call]
        workspace.notebook_path,
        as_version=4,
    )
    nbformat.validate(notebook)
    source = "\n".join(str(cell.source) for cell in notebook.cells)

    assert workspace.sql_path.read_text(encoding="utf-8") == (
        catalog.repo_root / "sql/lessons/sql-01.sql"
    ).read_text(encoding="utf-8")
    assert workspace.notebook_path.is_relative_to(catalog.repo_root / ".learning")
    assert workspace.sql_path.is_relative_to(catalog.repo_root / ".learning")
    assert "## Goal" in source
    assert "## Setup" in source
    assert "## Steps" in source
    assert "## Checks" in source
    assert "## Next Steps" in source
    assert "psql -X -v ON_ERROR_STOP=1 -f" in source
    assert "\\echo 'sql-01'" in source
    assert "do-not-save-me" not in workspace.notebook_path.read_text(encoding="utf-8")
    assert notebook.metadata.course.lesson_id == "sql-01"
    assert notebook.metadata.course.source_path == "sql/lessons/sql-01.sql"
    assert notebook.metadata.kernelspec.name == "ds60sqlpy"
    assert all(
        cell.execution_count is None and cell.outputs == []
        for cell in notebook.cells
        if cell.cell_type == "code"
    )


def test_generate_solution_selects_only_cataloged_executable_sql(catalog: Catalog) -> None:
    workspace = generate_sql_notebook(
        catalog,
        "sql-01",
        "solution",
        1,
    )

    assert workspace.source_path == catalog.repo_root / "sql/solutions/sql-01.sql"
    assert workspace.notebook_path.name == "guided.ipynb"
    assert "solution-1" in workspace.sql_path.parts
    assert workspace.sql_path.name == "sql-01.sql"
    assert "sql-01 solution" in workspace.sql_path.read_text(encoding="utf-8")

    with pytest.raises(SqlNotebookError, match="solution 2 does not exist"):
        generate_sql_notebook(catalog, "sql-01", "solution", 2)
    with pytest.raises(SqlNotebookError, match="not in the SQL track"):
        generate_sql_notebook(catalog, "python-01")
    with pytest.raises(SqlNotebookError, match="Unknown lesson ID"):
        generate_sql_notebook(catalog, "sql-does-not-exist")


def test_generation_does_not_overwrite_learner_files(catalog: Catalog) -> None:
    workspace = generate_sql_notebook(catalog, "sql-01")
    workspace.sql_path.write_text("-- my attempt\nSELECT 42;\n", encoding="utf-8")
    workspace.notebook_path.write_text('{"my": "notes"}\n', encoding="utf-8")

    regenerated = generate_sql_notebook(catalog, "sql-01")

    assert regenerated == workspace
    assert workspace.sql_path.read_text(encoding="utf-8") == "-- my attempt\nSELECT 42;\n"
    assert workspace.notebook_path.read_text(encoding="utf-8") == '{"my": "notes"}\n'


@pytest.mark.parametrize(
    "target",
    (
        COURSE_DATABASE_NAME,
        "postgresql:///advanced_sql_training",
        "postgres://user@localhost:5432/advanced_sql_training?sslmode=disable",
        "postgresql://[::1]:5432/advanced_sql_training",
    ),
)
def test_course_database_target_accepts_only_course_database(target: str) -> None:
    assert validate_course_database_target(target) == target


@pytest.mark.parametrize(
    "target",
    (
        "",
        "postgresql:///postgres",
        "postgresql+psycopg://localhost/advanced_sql_training",
        "mysql://localhost/advanced_sql_training",
        "dbname=advanced_sql_training",
        "postgresql:///advanced_sql_training?dbname=postgres",
        "postgresql:///advanced_sql_training?service=production",
        "postgresql://db.example/advanced_sql_training",
        "postgresql://localhost:5432,db.example:5432/advanced_sql_training",
        "postgresql://localhost/advanced_sql_training?host=127.0.0.2",
        "postgresql://localhost/advanced_sql_training?hostaddr=127.0.0.2",
        "postgresql://localhost/advanced_sql_training?passfile=secrets.txt",
        "postgresql://localhost/advanced_sql_training?connect_timeout=30",
        "postgresql:///advanced_sql_training#fragment",
        "postgresql:advanced_sql_training",
    ),
)
def test_course_database_target_rejects_ambiguous_or_other_targets(target: str) -> None:
    with pytest.raises(SqlNotebookError):
        validate_course_database_target(target)


def test_course_psql_environment_removes_inherited_routing_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "PGHOST",
        "PGHOSTADDR",
        "PGPORT",
        "PGSERVICE",
        "PGSERVICEFILE",
        "PGOPTIONS",
    ):
        monkeypatch.setenv(name, "untrusted-routing-value")
    monkeypatch.setenv("DS60_DATABASE_URL", "do-not-copy")

    environment = course_psql_environment(
        COURSE_DATABASE_NAME,
        application_name="ds60sqlpy-test",
        connect_timeout=7,
    )

    assert environment["PGDATABASE"] == COURSE_DATABASE_NAME
    assert environment["PGAPPNAME"] == "ds60sqlpy-test"
    assert environment["PGCONNECT_TIMEOUT"] == "7"
    assert not set(environment) & {
        "DS60_DATABASE_URL",
        "PGHOST",
        "PGHOSTADDR",
        "PGPORT",
        "PGSERVICE",
        "PGSERVICEFILE",
        "PGOPTIONS",
    }


def test_course_psql_environment_decomposes_url_without_exposing_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    password = "temporary password"
    authority = (
        f"course-user:{quote(password)}@127.0.0.1:55432/{COURSE_DATABASE_NAME}?sslmode=disable"
    )
    target = "://".join(("postgresql", authority))
    monkeypatch.setenv("PGHOST", "untrusted.example")
    monkeypatch.setenv("PGPORT", "6543")

    environment = course_psql_environment(
        target,
        application_name="ds60sqlpy-test",
        connect_timeout=7,
    )

    assert environment["PGDATABASE"] == COURSE_DATABASE_NAME
    assert environment["PGHOST"] == "127.0.0.1"
    assert environment["PGPORT"] == "55432"
    assert environment["PGUSER"] == "course-user"
    assert environment["PGPASSWORD"] == password
    assert environment["PGSSLMODE"] == "disable"
    assert target not in environment.values()


def test_workspace_run_uses_fixed_psql_flags_without_a_shell(
    catalog: Catalog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = generate_sql_notebook(catalog, "sql-01")
    monkeypatch.delenv("DS60_DATABASE_URL", raising=False)
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="answer\n",
        stderr="",
    )
    with (
        patch("ds60sqlpy.sql_notebook.shutil.which", return_value="/tools/psql"),
        patch("ds60sqlpy.sql_notebook.subprocess.run", return_value=completed) as run,
    ):
        result = run_sql_workspace(catalog, "sql-01")

    command = run.call_args.args[0]
    assert command == [
        "/tools/psql",
        "-X",
        "--no-password",
        "-v",
        "ON_ERROR_STOP=1",
        "--pset",
        "pager=off",
        "-f",
        str(workspace.sql_path),
    ]
    assert "shell" not in run.call_args.kwargs
    assert run.call_args.kwargs["cwd"] == catalog.repo_root
    assert run.call_args.kwargs["env"]["PGDATABASE"] == COURSE_DATABASE_NAME
    assert result.succeeded
    assert result.transcript() == "[PASS] Run sql-01 lesson\n\nanswer"


def test_generation_mirrors_relative_includes_and_preserves_psql_semantics(
    catalog: Catalog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = catalog.repo_root / "sql/lessons/sql-52.sql"
    source.write_text(
        "\\echo 'sql-52'\n\\ir ../fixtures/prepare.sql\nSELECT 52;\n",
        encoding="utf-8",
    )
    dependency = catalog.repo_root / "sql/fixtures/prepare.sql"
    dependency.parent.mkdir(parents=True)
    dependency.write_bytes(b"\\echo 'prepare'\r\nSELECT 1;\r\n")

    workspace = generate_sql_notebook(catalog, "sql-52")
    mirrored = workspace.notebook_path.parent / "workspace" / "sql" / "fixtures" / "prepare.sql"

    assert mirrored.read_bytes() == dependency.read_bytes()
    assert workspace.sql_path.relative_to(workspace.notebook_path.parent).as_posix() == (
        "workspace/sql/lessons/sql-52.sql"
    )

    monkeypatch.delenv("DS60_DATABASE_URL", raising=False)
    completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    with (
        patch("ds60sqlpy.sql_notebook.shutil.which", return_value="/tools/psql"),
        patch("ds60sqlpy.sql_notebook.subprocess.run", return_value=completed) as run,
    ):
        run_sql_workspace(catalog, "sql-52")
    assert run.call_args.args[0][-1] == str(workspace.sql_path)


def test_run_rejects_changed_meta_commands_or_include_dependencies(
    catalog: Catalog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = catalog.repo_root / "sql/lessons/sql-52.sql"
    source.write_text(
        "\\echo 'sql-52'\n\\ir ../fixtures/prepare.sql\nSELECT 52;\n",
        encoding="utf-8",
    )
    dependency = catalog.repo_root / "sql/fixtures/prepare.sql"
    dependency.parent.mkdir(parents=True)
    dependency.write_text("SELECT 1;\n", encoding="utf-8")
    monkeypatch.delenv("DS60_DATABASE_URL", raising=False)

    workspace = generate_sql_notebook(catalog, "sql-52")
    workspace.sql_path.write_text(
        workspace.sql_path.read_text(encoding="utf-8") + "\\! arbitrary-command\n",
        encoding="utf-8",
    )
    with pytest.raises(SqlNotebookError, match="changed a psql meta-command"):
        run_sql_workspace(catalog, "sql-52")

    workspace.sql_path.write_text(
        source.read_text(encoding="utf-8") + "SELECT 52; \\! arbitrary-command\n",
        encoding="utf-8",
    )
    with pytest.raises(SqlNotebookError, match="changed a psql meta-command"):
        run_sql_workspace(catalog, "sql-52")

    workspace.sql_path.write_text(
        source.read_text(encoding="utf-8") + "SELECT 52; \\ir ../../outside.sql\n",
        encoding="utf-8",
    )
    with pytest.raises(SqlNotebookError, match="changed a psql meta-command"):
        run_sql_workspace(catalog, "sql-52")

    workspace.sql_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    mirrored = workspace.notebook_path.parent / "workspace" / "sql" / "fixtures" / "prepare.sql"
    mirrored.write_text("\\! arbitrary-command\n", encoding="utf-8")
    with pytest.raises(SqlNotebookError, match="include dependency changed"):
        run_sql_workspace(catalog, "sql-52")


def test_meta_command_lexer_ignores_sql_literals_identifiers_and_comments() -> None:
    source = r"""
SELECT '\! literal', E'escaped \\' quote';
SELECT "\ir identifier";
SELECT $$\! dollar quoted$$, $tag$\ir also dollar quoted$tag$;
-- \! line comment
/* outer \ir ignored
   /* nested \! ignored */
*/
SELECT 1;
"""

    assert _psql_meta_segments(source) == ()
    assert _psql_meta_segments("SELECT 1; \\! danger\n") == ("\\! danger",)
    assert _psql_meta_segments("SELECT 1; \\ir ../../outside.sql\n") == ("\\ir ../../outside.sql",)
    assert _psql_meta_segments("SELECT x$tag$\\! danger$tag$;\n") == ("\\! danger$tag$;",)
    assert _psql_meta_segments("SELECT x\u0301$tag$\\! danger$tag$;\n") == ("\\! danger$tag$;",)
    assert _psql_meta_segments("SELECT x\u0301E'\\' \\! danger\n") == ("\\! danger",)


def test_notebook_generation_rejects_cwd_relative_psql_include(catalog: Catalog) -> None:
    source = catalog.repo_root / "sql/lessons/sql-01.sql"
    source.write_text("\\i ../fixtures/prepare.sql\nSELECT 1;\n", encoding="utf-8")

    with pytest.raises(SqlNotebookError, match=r"repository-relative \\ir, not \\i"):
        generate_sql_notebook(catalog, "sql-01")


def test_readiness_and_run_reject_unsafe_workspace_symlink(
    catalog: Catalog,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = generate_sql_notebook(catalog, "sql-01")
    outside = tmp_path / "outside.sql"
    outside.write_text("SELECT current_database();\n", encoding="utf-8")
    workspace.sql_path.unlink()
    try:
        workspace.sql_path.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"Symbolic links are unavailable: {exc}")

    monkeypatch.delenv("DS60_DATABASE_URL", raising=False)
    readiness = sql_notebook_readiness(catalog, "sql-01")
    assert not readiness.workspace_present
    assert not readiness.ready
    with pytest.raises(SqlNotebookError, match="missing or unsafe"):
        run_sql_workspace(catalog, "sql-01")


def test_readiness_does_not_echo_unsafe_connection_value(
    catalog: Catalog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generate_sql_notebook(catalog, "sql-01")
    secret = "do-not-echo-this"
    monkeypatch.setenv(
        "DS60_DATABASE_URL",
        _password_url("production", secret),
    )
    with patch("ds60sqlpy.sql_notebook.shutil.which", return_value="/tools/psql"):
        readiness = sql_notebook_readiness(catalog, "sql-01")

    assert not readiness.database_safe
    assert not readiness.ready
    assert secret not in "\n".join(readiness.messages)


def test_prepare_resets_verifies_and_runs_only_stateful_predecessors(
    catalog: Catalog,
) -> None:
    successful = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="ok\n",
        stderr="",
    )
    with (
        patch("ds60sqlpy.sql_notebook.shutil.which", return_value="/tools/psql"),
        patch("ds60sqlpy.sql_notebook.subprocess.run", return_value=successful) as run,
    ):
        results = prepare_sql_workspace(
            catalog,
            "sql-54",
            confirmation=DATABASE_RESET_CONFIRMATION,
        )

    assert len(results) == 4
    invoked_files = [Path(item.args[0][-1]).name for item in run.call_args_list]
    assert invoked_files == [
        "00_setup.sql",
        "00_verify.sql",
        "sql-52.sql",
        "sql-53.sql",
    ]
    assert all(result.succeeded for result in results)

    with pytest.raises(SqlNotebookError, match="not confirmed"):
        prepare_sql_workspace(catalog, "sql-54", confirmation="yes")


def test_preparation_stops_at_first_failure(catalog: Catalog) -> None:
    succeeded = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    failed = subprocess.CompletedProcess(args=[], returncode=3, stdout="", stderr="bad")
    with (
        patch("ds60sqlpy.sql_notebook.shutil.which", return_value="/tools/psql"),
        patch(
            "ds60sqlpy.sql_notebook.subprocess.run",
            side_effect=(succeeded, succeeded, failed, succeeded),
        ) as run,
    ):
        results = prepare_sql_workspace(
            catalog,
            "sql-54",
            confirmation=DATABASE_RESET_CONFIRMATION,
        )

    assert [result.returncode for result in results] == [0, 0, 3]
    assert run.call_count == 3
    assert run.call_args_list[0] != call()


def test_generated_notebook_json_has_no_absolute_repository_path(catalog: Catalog) -> None:
    workspace = generate_sql_notebook(catalog, "sql-01")
    payload = json.loads(workspace.notebook_path.read_text(encoding="utf-8"))

    assert str(catalog.repo_root) not in json.dumps(payload)
