"""Exercise actual coding-pad backends and optional isolated PostgreSQL checks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import pytest

from ds60sqlpy import step_through as stepping
from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import RUNNERS
from ds60sqlpy.execution import MAX_OUTPUT_BYTES, PadResult, PadRunner, lesson_search_path
from ds60sqlpy.sql_notebook import validate_course_database_target


@pytest.fixture
def course(tmp_path: Path) -> Catalog:
    lesson = replace(Catalog.load().get("python-01"), prerequisites=())
    return Catalog(tmp_path, (lesson,))


def test_backend_uses_real_python_and_restores_course_source_imports(course: Catalog) -> None:
    (course.repo_root / "src").mkdir()
    (course.repo_root / "src" / "learner_module.py").write_text("answer = 42\n", encoding="utf-8")
    runner = PadRunner(course)
    result = runner.run(
        "python-01", "python", "import learner_module; print(learner_module.answer)"
    )
    assert result["returncode"] == 0
    assert result["output"].strip() == "42"


def test_output_limit_bounds_unicode_bytes_and_stops_an_infinite_writer(course: Catalog) -> None:
    result = PadRunner(course, timeout=2).run(
        "python-01", "python", "while True: print('\\u20ac' * 10000)"
    )
    assert result["stopped"] == "output limit"
    assert "\u20ac" in result["output"]
    assert len(result["output"].encode("utf-8")) <= MAX_OUTPUT_BYTES
    assert result["elapsed_seconds"] < 4


def test_descendants_are_stopped_on_timeout(course: Catalog) -> None:
    sentinel = course.repo_root / "child-continued.txt"
    child = f"import time; from pathlib import Path; time.sleep(1); Path({str(sentinel)!r}).touch()"
    code = (
        "import subprocess, sys, time\n"
        f"subprocess.Popen([sys.executable, '-c', {child!r}])\n"
        "time.sleep(30)\n"
    )
    result = PadRunner(course, timeout=0.3).run("python-01", "python", code)
    assert result["elapsed_seconds"] < 3
    assert result["stopped"] == "time limit"
    time.sleep(1.1)
    assert not sentinel.exists(), "A descendant survived the timed-out coding-pad run."


def test_descendants_are_stopped_after_normal_parent_exit(course: Catalog) -> None:
    ready = course.repo_root / "child-ready.txt"
    sentinel = course.repo_root / "child-continued.txt"
    child = (
        "import os, time\n"
        "from pathlib import Path\n"
        f"ready = Path({str(ready)!r})\n"
        "pending = ready.with_suffix('.pending')\n"
        "pending.write_text(str(os.getpid()), encoding='utf-8')\n"
        "pending.replace(ready)\n"
        "time.sleep(1)\n"
        f"Path({str(sentinel)!r}).touch()\n"
    )
    code = (
        "import subprocess, sys, time\n"
        "from pathlib import Path\n"
        f"child = subprocess.Popen([sys.executable, '-c', {child!r}])\n"
        f"ready = Path({str(ready)!r})\n"
        "deadline = time.monotonic() + 10\n"
        "while not ready.exists():\n"
        "    if child.poll() is not None or time.monotonic() >= deadline:\n"
        "        raise RuntimeError('The owned child did not become ready.')\n"
        "    time.sleep(0.01)\n"
        # A Windows virtual-environment redirector can have a different PID
        # from the executing child. The owned readiness file identifies the
        # program whose continued execution the sentinel detects below.
        "print('parent finished with child', ready.read_text(encoding='utf-8').strip())\n"
    )
    # A normal exit needs its ordinary run budget. The separate timeout test
    # retains the short deadline; startup contention cannot turn this proof
    # into a timeout proof before the child has actually begun executing.
    result = PadRunner(course).run("python-01", "python", code)
    assert result["returncode"] == 0
    assert result["stopped"] is None
    child_pid = int(ready.read_text(encoding="utf-8"))
    assert child_pid > 0
    assert result["output"].strip() == f"parent finished with child {child_pid}"
    time.sleep(1.1)
    assert not sentinel.exists(), "A descendant survived the normally completed coding-pad run."


def test_explicit_backend_preserves_workspace_venv_python_symlink(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    prefix = course.repo_root / ".venv"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(prefix)], check=True)
    monkeypatch.delenv("DS60_PYTHON", raising=False)
    discovered = PadRunner._discover_python(course.repo_root, configured=str(prefix / "bin/python"))
    assert discovered is not None
    assert str(prefix) in discovered
    assert discovered != str(Path(discovered).resolve())


def test_explicit_backend_rejects_a_missing_or_unsupported_program(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError, match="Python 3.11-3.12"):
        PadRunner(course, python=str(course.repo_root / "missing-python"))
    monkeypatch.setenv("DS60_PYTHON", str(course.repo_root / "missing-python"))
    runner = PadRunner(course)
    assert runner.python is None
    with pytest.raises(ValueError, match="DS60_PYTHON"):
        runner.run("python-01", "python", "print(1)")
    assert not (course.repo_root / ".learning").exists()


def test_backend_transcripts_redact_known_database_credentials(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    # secret-scan: allow-fixture
    target = "postgresql://student:fake%40padpassword@localhost/advanced_sql_training"
    monkeypatch.setenv("DS60_DATABASE_URL", target)
    monkeypatch.setenv("PGPASSWORD", "another-fake-pad-password")
    result = PadRunner(course).run(
        "python-01",
        "python",
        (
            "import os\nprint(os.environ['DS60_DATABASE_URL'])\n"
            "print(os.environ['PGPASSWORD'])\nprint('fake@padpassword fake%40padpassword')"
        ),
    )
    assert result["returncode"] == 0
    assert "fake" not in result["output"]
    assert "[redacted" in result["output"]


def test_python_backend_does_not_inherit_implicit_notebook_state(course: Catalog) -> None:
    runner = PadRunner(course)
    assert runner.run("python-01", "python", "answer = 42")["returncode"] == 0
    result = runner.run("python-01", "python", "print(answer)")
    assert result["returncode"] != 0
    assert "NameError" in result["output"]


def test_notebook_cells_share_only_this_run_and_report_original_error_lines(
    course: Catalog,
) -> None:
    pytest.importorskip("IPython")
    runner = PadRunner(course)
    source = "# %%\nanswer = 42\n# %%\n%timeit -n1 -r1 answer + 1\nprint(answer)\n"
    result = runner.run("python-01", "python", source)
    assert result["returncode"] == 0 and "42" in result["output"]
    failed = runner.run(
        "python-01", "python", "# %%\ndef broken():\n    return 1 / 0\n# %%\nbroken()\n"
    )
    assert failed["returncode"] != 0 and failed["error_line"] == 3
    assert "ZeroDivisionError" in failed["output"]
    fresh = runner.run("python-01", "python", "# %%\nprint(answer)\n")
    assert fresh["returncode"] != 0 and "NameError" in fresh["output"]


@pytest.mark.parametrize("inline", [False, True])
def test_agg_and_inline_notebook_plots_survive_show_and_cell_close(
    course: Catalog, inline: bool
) -> None:
    pytest.importorskip("matplotlib")
    if inline:
        pytest.importorskip("IPython")
        pytest.importorskip("matplotlib_inline")
    source = (
        ("# %%\n%matplotlib inline\n" if inline else "")
        + "import matplotlib.pyplot as plt\n"
        + ("# %%\n" if inline else "")
        + "plt.plot([1, 2], [1, 4])\nplt.show()\n"
        + "import warnings\nwarnings.warn('keep learner warning')\n"
    )
    result = PadRunner(course).run("python-01", "python", source, timeout_seconds=60)
    assert result["returncode"] == 0, result["output"]
    assert result["figures"] and result["figures"][0].startswith("data:image/png;base64,")
    assert "keep learner warning" in result["output"]
    assert "FigureCanvasAgg is non-interactive" not in result["output"]


@pytest.mark.parametrize("value", [{"error_line": 999}, {"error_line": True}, [1], {}])
def test_python_source_diagnostics_reject_invalid_worker_metadata(
    course: Catalog, monkeypatch: pytest.MonkeyPatch, value: object
) -> None:
    runner = PadRunner(course)

    def capture(command: list[str], environment: dict[str, str], language: str) -> PadResult:
        (Path(command[-1]) / "execution.json").write_text(json.dumps(value), encoding="utf-8")
        return PadResult(
            language="python", returncode=1, output="", elapsed_seconds=0, stopped=None
        )

    monkeypatch.setattr(runner, "_execute", capture)
    assert "error_line" not in runner.run("python-01", "python", "raise ValueError()\n")


def test_public_course_default_does_not_corrupt_username_or_column_observations(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy.sql_runner import DEFAULT_DATABASE_URL

    monkeypatch.setenv("DS60_DATABASE_URL", DEFAULT_DATABASE_URL)
    monkeypatch.setenv("PGUSER", "admin")
    monkeypatch.setenv("PGPASSWORD", "admin")
    monkeypatch.setenv("PGDATABASE", "advanced_sql_training")
    monkeypatch.setenv("PGHOST", "127.0.0.1")
    result = PadRunner(course).run("python-01", "python", "print('admin admin_total')")
    assert result["returncode"] == 0
    assert result["output"].strip() == "admin admin_total"


def test_public_password_exception_requires_an_explicit_local_course_target() -> None:
    authority = "postgresql://admin:" + "admin@"
    for environment in (
        {"PGPASSWORD": "admin", "PGUSER": "admin", "PGDATABASE": "advanced_sql_training"},
        {"DS60_DATABASE_URL": authority + "remote.invalid/advanced_sql_training"},
        {"DS60_DATABASE_URL": authority + "localhost/private"},
    ):
        assert PadRunner._redact("admin", environment) == "[redacted]"


def test_plot_cache_is_shared_across_lessons_and_preserves_existing_files(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    second = replace(course.get("python-01"), id="python-02", day=2)
    catalog = Catalog(course.repo_root, (course.get("python-01"), second))
    runner = PadRunner(catalog)
    environments: list[dict[str, str]] = []

    def capture(command: list[str], environment: dict[str, str], language: str) -> PadResult:
        environments.append(environment)
        return PadResult(
            language=language, returncode=0, output="", elapsed_seconds=0.01, stopped=None
        )

    monkeypatch.setattr(runner, "_execute", capture)
    runner.run("python-01", "python", "print(1)")
    cache = Path(environments[0]["MPLCONFIGDIR"])
    sentinel = cache / "existing-font-cache.json"
    sentinel.write_text("preserved", encoding="utf-8")
    runner.run("python-02", "python", "print(2)")
    assert environments[0]["MPLBACKEND"] == "Agg"
    assert environments[1]["MPLCONFIGDIR"] == str(cache)
    assert cache == course.repo_root / ".learning/cache/matplotlib" / sys.platform
    assert sentinel.read_text(encoding="utf-8") == "preserved"


def test_sql_snippets_use_the_lesson_scripts_own_search_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = Catalog.load()
    lesson = replace(real.get("sql-29"), prerequisites=())
    script = tmp_path / lesson.lesson_path
    script.parent.mkdir(parents=True)
    script.write_text(real.resolve(lesson.lesson_path).read_text(encoding="utf-8"))
    catalog = Catalog(tmp_path, (lesson,))
    assert lesson_search_path(catalog, "sql-29") == "training,public"
    runner = PadRunner(catalog)
    environments: list[dict[str, str]] = []

    def capture(command: list[str], environment: dict[str, str], language: str) -> PadResult:
        environments.append(environment)
        return PadResult(
            language=language, returncode=0, output="", elapsed_seconds=0, stopped=None
        )

    monkeypatch.setattr(runner, "_execute", capture)
    runner.run("sql-29", "sql", "SELECT customer_id FROM customers;\n")
    assert environments[-1]["DS60_PAD_SEARCH_PATH"] == "training,public"
    # Only a plain top-level statement counts; anything else keeps the server default.
    script.write_text("-- SET search_path TO training;\nSET search_path TO x; DROP TABLE y;\n")
    assert lesson_search_path(catalog, "sql-29") is None
    runner.run("sql-29", "sql", "SELECT 1;\n")
    assert "DS60_PAD_SEARCH_PATH" not in environments[-1]
    assert {
        lesson_search_path(real, item.id)
        for item in real
        if item.lesson_path.startswith("sql/postgres-60day/day")
    } == {"training,public", "dwh,training,public"}


def test_empty_saved_pad_and_changed_versions_remain_recoverable(course: Catalog) -> None:
    runner = PadRunner(course)
    assert runner.saved("python-01", "python") is False
    runner.save("python-01", "python", "")
    assert runner.saved("python-01", "python") is True
    assert runner.read("python-01", "python") == ""
    assert runner.history("python-01", "python") == []
    runner.save("python-01", "python", "print(1)")
    first = runner.history("python-01", "python")
    assert len(first) == 1
    assert runner.read_history("python-01", "python", first[0]["id"]) == ""
    runner.save("python-01", "python", "print(1)")
    assert len(runner.history("python-01", "python")) == 1
    runner.save("python-01", "python", "print(2)")
    versions = runner.history("python-01", "python")
    assert len(versions) == 2
    assert runner.read_history("python-01", "python", versions[0]["id"]) == "print(1)"
    assert runner.read("python-01", "python") == "print(2)"


def test_lf_submissions_preserve_exact_bytes_and_do_not_create_false_history(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hashlib

    runner = PadRunner(course)
    code = "first = 1\nprint(first)\n"
    path = runner.save("python-01", "python", code)
    assert path.read_bytes() == code.encode("utf-8")
    runner.save("python-01", "python", code)
    assert runner.history("python-01", "python") == []
    snapshots: list[bytes] = []

    def execute(source: Path, language: str) -> dict[str, object]:
        snapshots.append(source.read_bytes())
        return {"returncode": 0}

    monkeypatch.setattr(runner, "_run_snapshot", execute)
    result = runner.run("python-01", "python", code)
    assert snapshots == [code.encode("utf-8")]
    assert result["source_sha256"] == hashlib.sha256(snapshots[0]).hexdigest()
    assert runner.history("python-01", "python") == []
    path.write_bytes(code.replace("\n", "\r\n").encode("utf-8"))
    runner.save("python-01", "python", code)
    assert len(runner.history("python-01", "python")) == 1
    runner.save("python-01", "python", code)
    assert len(runner.history("python-01", "python")) == 1


def test_history_is_bounded_in_listings_without_deleting_old_work(course: Catalog) -> None:
    runner = PadRunner(course)
    for number in range(15):
        runner.save("python-01", "sql", f"SELECT {number};")
    assert len(runner.history("python-01", "sql")) == 10
    assert len(runner.history("python-01", "sql", limit=50)) == 14
    with pytest.raises(ValueError, match="history ID"):
        runner.read_history("python-01", "sql", "../../private.txt")
    history = runner.history("python-01", "sql")
    digest = history[0]["id"]
    backup = course.repo_root / ".learning/pads/python-01/history" / f"practice-{digest}.sql"
    backup.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        runner.read_history("python-01", "sql", digest)


def test_run_executes_the_submission_even_if_another_save_changes_the_pad(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = PadRunner(course)
    execute = runner._execute

    def competing_save(command: list[str], environment: dict[str, str], language: str) -> PadResult:
        runner.save("python-01", "python", "print('later saved version')")
        return execute(command, environment, language)

    monkeypatch.setattr(runner, "_execute", competing_save)
    result = runner.run("python-01", "python", "print('submitted version')")
    assert result["returncode"] == 0
    assert result["output"].strip() == "submitted version"
    assert runner.read("python-01", "python") == "print('later saved version')"
    assert not list((course.repo_root / ".learning/pads/python-01").glob(".submission-*"))


def test_separate_process_saves_preserve_every_changed_version(course: Catalog) -> None:
    runner = PadRunner(course)
    runner.save("python-01", "python", "initial")
    root = Catalog.load().repo_root
    program = (
        "import sys; from pathlib import Path; "
        "from ds60sqlpy.catalog import Catalog; from ds60sqlpy.execution import PadRunner; "
        "base=Catalog.load(Path(sys.argv[1])).get('python-01'); "
        "PadRunner(Catalog(Path(sys.argv[2]),(base,))).save('python-01','python',sys.argv[3])"
    )
    processes: list[subprocess.Popen[bytes]] = []
    try:
        for n in range(4):
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        program,
                        str(root),
                        str(course.repo_root),
                        f"version {n}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            )
        for process in processes:
            _, error = process.communicate(timeout=15)
            assert process.returncode == 0, error.decode()
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=10)
    versions = {runner.read("python-01", "python")}
    versions.update(
        runner.read_history("python-01", "python", item["id"])
        for item in runner.history("python-01", "python", limit=50)
    )
    assert versions == {"initial", "version 0", "version 1", "version 2", "version 3"}


@dataclass
class LiveDatabase:
    driver: Any
    target: str
    schema: str
    admin_target: str


@pytest.fixture
def live_database(monkeypatch: pytest.MonkeyPatch) -> Any:
    target = os.environ.get("DS60_TEST_DATABASE_URL")
    if not target:
        pytest.skip("Set DS60_TEST_DATABASE_URL for the explicitly disposable local database")
    validate_course_database_target(target)
    psycopg = pytest.importorskip("psycopg")
    role = "testpad_" + uuid.uuid4().hex
    schema = role
    password = uuid.uuid4().hex
    parts = urlsplit(target)
    host = parts.hostname or "localhost"
    if ":" in host:
        host = f"[{host}]"
    authority = f"{quote(role)}:{quote(password)}@{host}:{parts.port or 5432}"
    limited_target = urlunsplit(parts._replace(netloc=authority))
    with psycopg.connect(target, autocommit=True) as admin:
        admin.execute(
            psycopg.sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                psycopg.sql.Identifier(role), psycopg.sql.Literal(password)
            )
        )
        admin.execute(
            psycopg.sql.SQL(
                "GRANT CONNECT, CREATE, TEMPORARY ON DATABASE advanced_sql_training TO {}"
            ).format(psycopg.sql.Identifier(role))
        )
    try:
        with psycopg.connect(limited_target, autocommit=True) as connection:
            connection.execute(
                psycopg.sql.SQL("CREATE SCHEMA {}").format(psycopg.sql.Identifier(schema))
            )
        monkeypatch.setenv("DS60_DATABASE_URL", limited_target)
        yield LiveDatabase(psycopg, limited_target, schema, target)
    finally:
        with psycopg.connect(target, autocommit=True) as admin:
            admin.execute(psycopg.sql.SQL("DROP OWNED BY {}").format(psycopg.sql.Identifier(role)))
            admin.execute(psycopg.sql.SQL("DROP ROLE {}").format(psycopg.sql.Identifier(role)))


def test_live_sql_pad_returns_bounded_result_sets_and_commits_success(
    course: Catalog, live_database: LiveDatabase
) -> None:
    result = PadRunner(course).run(
        "python-01",
        "sql",
        "CREATE TEMP TABLE pad_local (n int); "
        "INSERT INTO pad_local VALUES (5); SELECT * FROM pad_local; "
        "SELECT generate_series(1, 102) AS n;",
    )
    assert result["returncode"] == 0, result["output"]
    payload = json.loads(result["output"])
    assert payload["results"][2]["rows"] == [[5]]
    assert len(payload["results"][3]["rows"]) == 100
    assert payload["results"][3]["truncated"] is True
    assert "Committed success" in payload["transaction"]


@pytest.mark.parametrize("explicit_commit", [False, True])
def test_live_sql_error_rolls_back_current_transaction_and_preserves_explicit_commits(
    course: Catalog, live_database: LiveDatabase, explicit_commit: bool
) -> None:
    psycopg, target = live_database.driver, live_database.target
    table = live_database.schema + ".pad_test_" + uuid.uuid4().hex
    try:
        code = f"CREATE TABLE {table} (n int); INSERT INTO {table} VALUES (5); "
        if explicit_commit:
            code += "COMMIT; "
        result = PadRunner(course).run("python-01", "sql", code + "SELECT 1 / 0;")
        assert result["returncode"] != 0
        payload = json.loads(result["output"])
        assert payload["sqlstate"] == "22012"
        assert "earlier explicit commits are preserved" in payload["transaction"]
        with psycopg.connect(target, autocommit=True) as connection:
            exists = connection.execute("SELECT to_regclass(%s)", (f"{table}",)).fetchone()[0]
            assert bool(exists) is explicit_commit
            if explicit_commit:
                assert connection.execute(f"SELECT n FROM {table}").fetchall() == [(5,)]
    finally:
        with psycopg.connect(target, autocommit=True) as connection:
            connection.execute(f"DROP TABLE IF EXISTS {table}")


def test_live_sql_error_does_not_echo_the_database_target(
    course: Catalog, live_database: LiveDatabase
) -> None:
    target = live_database.target
    escaped = target.replace("'", "''")
    result = PadRunner(course).run(
        "python-01", "sql", f"DO $$ BEGIN RAISE EXCEPTION '{escaped}'; END $$;"
    )
    assert result["returncode"] != 0
    assert target not in result["output"]
    payload = json.loads(result["output"])
    assert "[redacted database URL]" in payload["message"]


def test_live_sql_timeout_closes_the_backend_connection(
    course: Catalog, live_database: LiveDatabase
) -> None:
    result = PadRunner(course, timeout=0.3).run("python-01", "sql", "SELECT pg_sleep(30);")
    assert result["stopped"] == "time limit"
    role = urlsplit(live_database.target).username
    with live_database.driver.connect(live_database.admin_target, autocommit=True) as admin:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            count = admin.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE usename = %s "
                "AND application_name = 'ds60-coding-pad'",
                (role,),
            ).fetchone()[0]
            if count == 0:
                break
            time.sleep(0.05)
    assert count == 0


def test_live_sql_pad_rejects_superuser_before_running_learner_statements(
    course: Catalog, live_database: LiveDatabase, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DS60_DATABASE_URL", live_database.admin_target)
    result = PadRunner(course).run("python-01", "sql", "SELECT 1;")
    assert result["returncode"] != 0
    payload = json.loads(result["output"])
    assert payload["error_type"] == "CourseRoleError"
    assert "limited course login" in payload["message"]
    assert "docs/setup/postgresql.md" in payload["message"]


@pytest.mark.parametrize(
    "privilege",
    [
        "CREATEROLE",
        "CREATEDB",
        "pg_execute_server_program",
        "pg_read_server_files",
        "pg_write_server_files",
        "admin-membership",
    ],
)
def test_live_sql_pad_rejects_elevated_flags_and_server_file_role_membership(
    course: Catalog, live_database: LiveDatabase, privilege: str
) -> None:
    driver = live_database.driver
    role = urlsplit(live_database.target).username
    with driver.connect(live_database.admin_target, autocommit=True) as admin:
        if privilege in {"CREATEROLE", "CREATEDB"}:
            admin.execute(
                driver.sql.SQL("ALTER ROLE {} " + privilege).format(driver.sql.Identifier(role))
            )
        else:
            granted_role = privilege
            if privilege == "admin-membership":
                granted_role = admin.execute("SELECT current_user").fetchone()[0]
            admin.execute(
                driver.sql.SQL("GRANT {} TO {}").format(
                    driver.sql.Identifier(granted_role), driver.sql.Identifier(role)
                )
            )
    result = PadRunner(course).run("python-01", "sql", "SELECT 1;")
    assert result["returncode"] != 0
    assert json.loads(result["output"])["error_type"] == "CourseRoleError"


@pytest.mark.parametrize("language", ["none", "cpp", "scala", "kubernetes"])
def test_registered_future_runner_saves_history_but_never_executes(
    course: Catalog, language: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = PadRunner(course)
    path = runner.save("python-01", language, "first\n")
    assert path.suffix == RUNNERS[language].file_suffix
    runner.save("python-01", language, "second\n")
    assert runner.read("python-01", language) == "second\n"
    history = runner.history("python-01", language)
    assert runner.read_history("python-01", language, history[0]["id"]) == "first\n"

    def unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("An unimplemented adapter started a process.")

    monkeypatch.setattr(runner, "_execute", unexpected)
    with pytest.raises(ValueError, match="not implemented"):
        runner.run("python-01", language, "new submission")
    assert runner.read("python-01", language) == "second\n"


def test_longer_run_limit_does_not_leak_into_the_next_request(course: Catalog) -> None:
    runner = PadRunner(course, timeout=0.05)
    code = "import time; time.sleep(0.15); print('finished')"
    extended = runner.run("python-01", "python", code, timeout_seconds=15)
    assert extended["returncode"] == 0 and extended["output"].strip() == "finished"
    ordinary = runner.run("python-01", "python", code)
    assert ordinary["stopped"] == "time limit"
    assert ordinary["elapsed_seconds"] < 1


@pytest.mark.parametrize("timeout", [True, 0, 121, 15.0, "15"])
def test_run_limit_override_rejects_unbounded_or_ambiguous_values(
    course: Catalog, timeout: Any
) -> None:
    with pytest.raises(ValueError, match="15, 60 or 120"):
        PadRunner(course).run("python-01", "python", "print(1)", timeout_seconds=timeout)
    assert not (course.repo_root / ".learning").exists()


def test_live_capabilities_distinguish_limited_login_from_bootstrap_administrator(
    course: Catalog, live_database: LiveDatabase, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy.capabilities import CapabilityService

    service = CapabilityService(course, sys.executable)
    limited = service.runner("python-01", "sql")
    assert limited["available"] and limited["can_run"], limited
    monkeypatch.setenv("DS60_DATABASE_URL", live_database.admin_target)
    privileged = service.runner("python-01", "sql")
    assert not privileged["available"] and "limited course login" in privileged["reason"]
    assert live_database.admin_target not in json.dumps(privileged)


def sql_lesson_catalog(course: Catalog, source: str) -> Catalog:
    root = course.repo_root / "sql"
    root.mkdir(exist_ok=True)
    (root / "includes").mkdir(exist_ok=True)
    (root / "local.sql").write_text(source, encoding="utf-8", newline="\n")
    (root / "includes/fixed.sql").write_text(
        "\\echo fixed include ran\nSELECT 8 AS fixed_value;\n", encoding="utf-8", newline="\n"
    )
    (root / "guide.md").write_text("# Whole SQL lesson\n", encoding="utf-8")
    lesson = replace(
        course.get("python-01"),
        id="sql-local",
        track="sql",
        runner="sql",
        day=1,
        dependency_group="postgres",
        lesson_path="sql/local.sql",
        guide_path="sql/guide.md",
        solution_paths=(),
        prerequisites=(),
    )
    return Catalog(course.repo_root, (lesson,))


def test_live_whole_sql_runs_the_edited_copy_with_fixed_conditionals_and_includes(
    course: Catalog, live_database: LiveDatabase
) -> None:
    from ds60sqlpy.sql_lesson import SqlLessonRunner

    source = (
        "\\set ON_ERROR_STOP on\nSELECT true AS gate \\gset\n\\if :gate\n"
        "SELECT 7 AS source_value;\n\\else\nSELECT 1/0;\n\\endif\n"
        "\\ir includes/fixed.sql\n"
    )
    catalog = sql_lesson_catalog(course, source)
    lessons = SqlLessonRunner(catalog, PadRunner(catalog))
    assert lessons.read("sql-local")["code"] == source
    edited = source.replace("SELECT 7 AS", "SELECT 9 AS")
    result = lessons.run("sql-local", edited, timeout_seconds=15)
    assert result["returncode"] == 0, result["output"]
    assert "source_value" in result["output"] and "fixed include ran" in result["output"]
    assert "9" in result["output"] and "__DS60_SESSION__" not in result["output"]
    assert (catalog.repo_root / "sql/local.sql").read_text() == source
    assert lessons.read("sql-local")["code"] == edited
    assert lessons.history("sql-local")
    failed = lessons.run("sql-local", source.replace("SELECT 7 AS", "SELECT 1/0 AS"))
    assert failed["returncode"] != 0 and failed["error_line"] == 4
    corrupt = edited + "\\! this_must_never_start\n"
    with pytest.raises(ValueError, match="meta-command"):
        lessons.run("sql-local", corrupt)
    assert lessons.read("sql-local")["code"] == corrupt
    assert not list((catalog.repo_root / ".learning/sql").rglob(".submission-*"))


@pytest.mark.parametrize(
    "directive", ["\\! echo forbidden", "\\connect private", "\\o unsafe", "\\echo `uname`"]
)
def test_whole_sql_client_directives_are_viewable_but_never_executed(
    course: Catalog, directive: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy.sql_lesson import SqlLessonRunner

    catalog = sql_lesson_catalog(course, directive + "\nSELECT 1;\n")
    pads = PadRunner(catalog)
    lessons = SqlLessonRunner(catalog, pads)
    assert directive in lessons.read("sql-local")["code"]

    def unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("Unsafe psql source started a process.")

    monkeypatch.setattr(pads, "_execute", unexpected)
    with pytest.raises(ValueError, match="directive"):
        lessons.run("sql-local", directive + "\nSELECT 1;\n")


def test_live_sql_timeout_cancels_the_exact_session_after_application_name_changes(
    course: Catalog, live_database: LiveDatabase
) -> None:
    changed = "ds60-changed-" + uuid.uuid4().hex
    result = PadRunner(course, timeout=0.5).run(
        "python-01",
        "sql",
        f"SET statement_timeout=0; SET application_name='{changed}'; SELECT pg_sleep(30);",
    )
    assert result["stopped"] == "time limit"
    assert result["elapsed_seconds"] < 4
    with live_database.driver.connect(live_database.target) as connection:
        active = connection.execute(
            "SELECT count(*) FROM pg_stat_activity WHERE application_name=%s AND state='active'",
            (changed,),
        ).fetchone()[0]
    assert active == 0


@pytest.mark.parametrize("line_ending", [b"\n", b"\r\n"])
@pytest.mark.parametrize("symbol", ["€", "😀"])
def test_whole_script_capture_drains_bounded_output_and_retains_final_errors(
    course: Catalog,
    line_ending: bytes,
    symbol: str,
) -> None:
    code = (
        "import os\n"
        "def emit(fd, data):\n"
        "    while data:\n"
        "        data = data[os.write(fd, data):]\n"
        f"emit(1, b'FIRST SENTINEL' + {line_ending!r})\n"
        f"emit(1, {symbol.encode('utf-8')!r} * 100000 + {line_ending!r})\n"
        f"emit(2, b'FINAL ERROR SENTINEL' + {line_ending!r})\n"
        "raise SystemExit(7)"
    )
    result = PadRunner(course)._execute(
        [sys.executable, "-u", "-c", code],
        dict(os.environ),
        "python",
        truncate_output=True,
    )
    assert result.returncode == 7 and result.stopped is None
    assert result.output_truncated
    assert "FIRST SENTINEL" in result.output and "FINAL ERROR SENTINEL" in result.output
    assert result.output.endswith("FINAL ERROR SENTINEL" + line_ending.decode("ascii"))
    assert len(result.output.encode()) <= MAX_OUTPUT_BYTES


def test_whole_script_output_drain_still_obeys_the_process_time_limit(course: Catalog) -> None:
    result = PadRunner(course, timeout=0.2)._execute(
        [sys.executable, "-u", "-c", "while True: print('x' * 8192)"],
        dict(os.environ),
        "python",
        truncate_output=True,
    )
    assert result.stopped == "time limit" and result.elapsed_seconds < 3
    assert len(result.output.encode()) <= MAX_OUTPUT_BYTES


TRACE_BACKENDS = pytest.mark.parametrize("backend", ["auto", "settrace"])


def _variables(frame: dict[str, Any]) -> dict[str, str]:
    return {item["name"]: item["value"] for item in frame["variables"]}


@TRACE_BACKENDS
def test_step_through_python_has_source_linked_events_and_locals(
    course: Catalog, monkeypatch: pytest.MonkeyPatch, backend: str
) -> None:
    monkeypatch.setattr(stepping, "PYTHON_TRACE_BACKEND", backend)
    code = (
        "def double(n):\n"
        "    result = n * 2\n"
        "    return result\n"
        "\n"
        "total = double(21)\n"
        "print('total', total)\n"
    )
    source = code.splitlines()
    response = PadRunner(course).step_through("python-01", "python", code)

    assert response["kind"] == "python" and response["code"] == code
    assert response["error"] is None and response["stopped"] is None
    assert response["step_limit_reached"] is False
    assert response["output"] == "total 42\n"
    assert isinstance(response["elapsed_seconds"], float)
    steps = response["steps"]
    assert steps and len(steps) < stepping.MAX_STEPS
    assert {step["event"] for step in steps} <= {"line", "call", "return", "exception"}
    for step in steps:
        assert 1 <= step["line"] <= len(source)
        assert step["stack"][-1]["function"] == step["function"]
        assert step["stack"][-1]["line"] == step["line"]
    assert (steps[0]["function"], steps[0]["line"]) == ("<module>", 1)
    assert [step["output_length"] for step in steps] == sorted(s["output_length"] for s in steps)
    assert steps[-1]["output_length"] == len(response["output"])

    def first(event: str, line: int) -> dict[str, Any]:
        return next(s for s in steps if s["event"] == event and s["line"] == line)

    call = first("call", 1)
    assert call["function"] == "double"
    assert [frame["function"] for frame in call["stack"]] == ["<module>", "double"]
    assert [frame["depth"] for frame in call["stack"]] == [0, 1]
    assert _variables(call["stack"][-1]) == {"n": "21"}
    # Line events report state before that statement runs.
    assert source[1].strip() == "result = n * 2"
    assert "result" not in _variables(first("line", 2)["stack"][-1])
    assert source[2].strip() == "return result"
    assert _variables(first("line", 3)["stack"][-1]) == {"n": "21", "result": "42"}
    assert first("return", 3)["return_value"] == "42"
    printing = first("line", 6)
    assert printing["function"] == "<module>" and printing["output_length"] == 0
    assert _variables(printing["stack"][0])["total"] == "42"
    module_return = steps[-1]
    assert (module_return["event"], module_return["function"]) == ("return", "<module>")
    assert module_return["return_value"] is None


@TRACE_BACKENDS
def test_step_through_python_reports_output_step_limits_and_errors(
    course: Catalog, monkeypatch: pytest.MonkeyPatch, backend: str
) -> None:
    monkeypatch.setattr(stepping, "PYTHON_TRACE_BACKEND", backend)
    runner = PadRunner(course)

    failed = runner.step_through("python-01", "python", "x = 1\nprint('a')\ny = x / 0\n")
    assert failed["error"] == {
        "type": "ZeroDivisionError",
        "message": "division by zero",
        "line": 3,
    }
    assert failed["output"] == "a\n"
    assert failed["step_limit_reached"] is False and failed["stopped"] is None
    raised = [step for step in failed["steps"] if step["event"] == "exception"]
    assert [(step["line"], step["exception"]) for step in raised] == [
        (3, "ZeroDivisionError: division by zero")
    ]

    nested = runner.step_through(
        "python-01", "python", "def inner():\n    return {}['missing']\n\ninner()\n"
    )
    assert nested["error"] is not None
    assert (nested["error"]["type"], nested["error"]["line"]) == ("KeyError", 2)

    looping = runner.step_through("python-01", "python", "for i in range(1000):\n    pass\n")
    assert looping["step_limit_reached"] is True
    assert len(looping["steps"]) == stepping.MAX_STEPS
    assert looping["error"] is None and looping["stopped"] is None

    noisy = runner.step_through("python-01", "python", "print('x' * 100000)\nprint('after')\n")
    assert noisy["output"].endswith(stepping.OUTPUT_NOTICE)
    assert len(noisy["output"]) == stepping.OUTPUT_CAP + len(stepping.OUTPUT_NOTICE)
    assert "after" not in noisy["output"]
    assert noisy["error"] is None and noisy["step_limit_reached"] is False
    assert all(step["output_length"] <= len(noisy["output"]) for step in noisy["steps"])


def test_plan_sql_fallback_is_explicitly_unsupported(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = "-- Clauses out of order\nSELECT 1 ORDER BY 1 WHERE true"
    statement = "SELECT 1 ORDER BY 1 WHERE true"
    plan = stepping.plan_sql(source)
    assert (plan.steps, plan.unsupported) == ((), stepping.UNSUPPORTED_SQL)
    assert plan.statement == statement
    assert source[plan.statement_offset :] == statement
    for code, message in {
        "UPDATE scores SET n = 0": stepping.NOT_A_QUERY,
        "WITH gone AS (DELETE FROM scores RETURNING n) SELECT * FROM gone": (stepping.NOT_A_QUERY),
        "SELECT * FROM scores FOR UPDATE": stepping.LOCKING_QUERY,
        "SELECT (1": stepping.UNBALANCED,
        "-- nothing to run": stepping.NO_QUERY,
    }.items():
        rejected = stepping.plan_sql(code)
        assert (rejected.steps, rejected.unsupported) == ((), message)

    runner = PadRunner(course)

    def unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("An unsupported walkthrough launched the SQL worker.")

    monkeypatch.setattr(runner, "_execute", unexpected)
    assert runner.step_through("python-01", "sql", source) == {
        "kind": "sql",
        "statement": statement,
        "statement_offset": source.index(statement),
        "steps": [],
        "unsupported": stepping.UNSUPPORTED_SQL,
        "elapsed_seconds": 0.0,
        "error": None,
    }
    assert not list(course.repo_root.rglob(".step-*"))


SQUARES_SOURCE = (
    "SELECT 0 AS warmup;\n\n"
    "-- Squares above two, largest first\n"
    "SELECT n, n * n AS square\n"
    "FROM generate_series(1, 5) AS g(n)\n"
    "WHERE n > 2\n"
    "ORDER BY n DESC\n"
    "LIMIT 2;\n"
)
SQUARES_CLAUSES = [
    ("from", "FROM generate_series(1, 5) AS g(n)"),
    ("where", "WHERE n > 2"),
    ("select", "SELECT n, n * n AS square"),
    ("order", "ORDER BY n DESC"),
    ("limit", "LIMIT 2"),
]


def _source_clauses(source: str, offset: int, steps: Any) -> list[tuple[str, str]]:
    clauses = []
    for step in steps:
        clause = step["clause"] if isinstance(step, dict) else step.clause
        start, end = step["highlight"] if isinstance(step, dict) else step.highlight
        clauses.append((clause, source[offset + start : offset + end]))
    return clauses


def test_step_through_sql_offsets_match_original_source() -> None:
    source = SQUARES_SOURCE
    start = source.index("SELECT n,")
    for cursor in (None, source.index("WHERE"), source.index("LIMIT 2") + 3):
        plan = stepping.plan_sql(source, cursor)
        assert plan.unsupported is None
        assert plan.statement_offset == start
        assert source[start : start + len(plan.statement)] == plan.statement
        assert plan.statement.endswith("LIMIT 2")
        assert _source_clauses(source, start, plan.steps) == SQUARES_CLAUSES
        assert plan.steps[-1].sql == plan.statement
    warmup = stepping.plan_sql(source, 3)
    assert (warmup.statement, warmup.statement_offset) == ("SELECT 0 AS warmup", 0)

    wide = (
        "-- \U0001f600 smile\nSELECT '\U0001f600' AS face\nFROM (VALUES (1)) AS v(n)\nWHERE n = 1"
    )
    plan = stepping.plan_sql(wide)
    where = next(step for step in plan.steps if step.clause == "where")
    begin, end = where.highlight
    assert wide[plan.statement_offset + begin : plan.statement_offset + end] == "WHERE n = 1"


def test_live_step_through_sql_results_and_rejection_preserve_database_state(
    course: Catalog, live_database: LiveDatabase
) -> None:
    driver, target = live_database.driver, live_database.target
    table = f"{live_database.schema}.step_sentinel_{uuid.uuid4().hex}"
    sequence = f"{live_database.schema}.step_sequence_{uuid.uuid4().hex}"
    with driver.connect(target, autocommit=True) as connection:
        connection.execute(f"CREATE TABLE {table} (n int PRIMARY KEY)")
        connection.execute(f"INSERT INTO {table} SELECT generate_series(1, 5)")
        connection.execute(f"CREATE SEQUENCE {sequence}")

    def snapshot() -> tuple[list[int], int, bool]:
        with driver.connect(target, autocommit=True) as connection:
            rows = [row[0] for row in connection.execute(f"SELECT n FROM {table} ORDER BY n")]
            last, called = connection.execute(
                f"SELECT last_value, is_called FROM {sequence}"
            ).fetchone()
        return rows, last, called

    before = snapshot()
    assert before == ([1, 2, 3, 4, 5], 1, False)
    runner = PadRunner(course)

    source = SQUARES_SOURCE.replace("generate_series(1, 5) AS g(n)", f"{table} AS g")
    walk = runner.step_through("python-01", "sql", source, timeout_seconds=60)
    assert walk["unsupported"] is None and walk["error"] is None, walk
    start = walk["statement_offset"]
    assert source[start : start + len(walk["statement"])] == walk["statement"]
    expected_clauses = [
        (clause, text.replace("generate_series(1, 5) AS g(n)", f"{table} AS g"))
        for clause, text in SQUARES_CLAUSES
    ]
    assert _source_clauses(source, start, walk["steps"]) == expected_clauses
    assert [
        (step["columns"], step["rows"], step["row_count"], step["error"]) for step in walk["steps"]
    ] == [
        (["n"], [[1], [2], [3], [4], [5]], 5, None),
        (["n"], [[3], [4], [5]], 3, None),
        (["n", "square"], [[3, 9], [4, 16], [5, 25]], 3, None),
        (["n", "square"], [[5, 25], [4, 16], [3, 9]], 3, None),
        (["n", "square"], [[5, 25], [4, 16]], 2, None),
    ]

    for code, message in {
        f"SELECT n FROM {table} ORDER BY n WHERE true": stepping.UNSUPPORTED_SQL,
        f"DELETE FROM {table}": stepping.NOT_A_QUERY,
        f"WITH gone AS (DELETE FROM {table} RETURNING n) SELECT * FROM gone": (
            stepping.NOT_A_QUERY
        ),
        f"SELECT n FROM {table} FOR UPDATE": stepping.LOCKING_QUERY,
    }.items():
        rejected = runner.step_through("python-01", "sql", code, timeout_seconds=15)
        assert (rejected["steps"], rejected["unsupported"]) == ([], message)
        assert snapshot() == before

    writer = runner.step_through(
        "python-01", "sql", f"SELECT nextval('{sequence}') AS n", timeout_seconds=15
    )
    assert writer["steps"] and all(step["error"] for step in writer["steps"]), writer
    assert all(step["rows"] == [] for step in writer["steps"])
    assert "read-only" in writer["steps"][-1]["error"]
    assert snapshot() == before
