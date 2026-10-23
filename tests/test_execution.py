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

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.curriculum_framework import RUNNERS
from ds60sqlpy.execution import MAX_OUTPUT_BYTES, PadResult, PadRunner, external_program_environment
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
        "print('parent finished with child', child.pid)\n"
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


def test_frozen_discovery_prefers_workspace_venv_without_resolving_its_python_symlink(
    course: Catalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    prefix = course.repo_root / ".venv"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(prefix)], check=True)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.delenv("DS60_PYTHON", raising=False)
    discovered = PadRunner._discover_python(course.repo_root)
    assert discovered is not None
    assert str(prefix) in discovered
    assert discovered != str(Path(discovered).resolve()) or os.name == "nt"


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


def test_frozen_environment_restores_loader_values_without_changing_the_parent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", "/temporary/bundle", raising=False)
    monkeypatch.setenv("LD_LIBRARY_PATH", "/temporary/bundle")
    monkeypatch.setenv("LD_LIBRARY_PATH_ORIG", "/system/libraries")
    monkeypatch.setenv("DYLD_LIBRARY_PATH", "/temporary/bundle")
    monkeypatch.delenv("DYLD_LIBRARY_PATH_ORIG", raising=False)
    monkeypatch.setenv("_PYI_APPLICATION_HOME_DIR", "/temporary/bundle")
    monkeypatch.setenv("PATH", os.pathsep.join(("/temporary/bundle/bin", "/system/bin")))
    child = external_program_environment()
    assert child["LD_LIBRARY_PATH"] == "/system/libraries"
    assert "DYLD_LIBRARY_PATH" not in child
    assert "_PYI_APPLICATION_HOME_DIR" not in child
    assert "/temporary/bundle/bin" not in child["PATH"]
    assert os.environ["LD_LIBRARY_PATH"] == "/temporary/bundle"


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
    assert "docs/offline-app.md" in payload["message"]


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


def test_whole_script_capture_drains_bounded_output_and_retains_final_errors(
    course: Catalog,
) -> None:
    from ds60sqlpy.execution import WORKER_GATE

    code = (
        WORKER_GATE + "import sys\nprint('FIRST SENTINEL')\n"
        "print('\\u20ac' * 100000)\n"
        "print('FINAL ERROR SENTINEL', file=sys.stderr)\nraise SystemExit(7)"
    )
    result = PadRunner(course)._execute(
        [sys.executable, "-u", "-c", code],
        external_program_environment(),
        "python",
        truncate_output=True,
    )
    assert result.returncode == 7 and result.stopped is None
    assert result.output_truncated
    assert "FIRST SENTINEL" in result.output and "FINAL ERROR SENTINEL" in result.output
    assert len(result.output.encode()) <= MAX_OUTPUT_BYTES


def test_whole_script_output_drain_still_obeys_the_process_time_limit(course: Catalog) -> None:
    from ds60sqlpy.execution import WORKER_GATE

    result = PadRunner(course, timeout=0.2)._execute(
        [sys.executable, "-u", "-c", WORKER_GATE + "while True: print('x' * 8192)"],
        external_program_environment(),
        "python",
        truncate_output=True,
    )
    assert result.stopped == "time limit" and result.elapsed_seconds < 3
    assert len(result.output.encode()) <= MAX_OUTPUT_BYTES
