"""Exercise the real xdist scheduler using dummy database fixtures, never a DB."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CONFTEST = Path(__file__).with_name("conftest.py")


def mini_suite(tmp_path: Path, *, conflicting_group: bool = False) -> Path:
    pytest.importorskip("xdist")
    (tmp_path / "records").mkdir()
    (tmp_path / "pytest.ini").write_text("[pytest]\naddopts = --strict-markers\n", encoding="utf-8")
    (tmp_path / "conftest.py").write_text(
        CONFTEST.read_text(encoding="utf-8")
        + "\nfrom pathlib import Path\n"
        + "\n@pytest.fixture\ndef live_database():\n"
        + "    Path('database-fixture-ran').touch()\n    return 'dummy database'\n"
        + "\n@pytest.fixture\ndef live_psql():\n"
        + "    Path('psql-fixture-ran').touch()\n    return 'dummy psql'\n"
        + "\n@pytest.fixture\ndef indirect_database(live_database):\n    return live_database\n",
        encoding="utf-8",
    )
    (tmp_path / "record.py").write_text(
        """import hashlib, json, os, time
from pathlib import Path

def record(request, worker_id, kind):
    root = Path(__file__).parent
    lock = root / 'shared-database.lock'
    if kind == 'database':
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            time.sleep(0.04)
        finally:
            os.close(handle)
            lock.unlink()
    else:
        time.sleep(0.02)
    identity = hashlib.sha256(request.node.nodeid.encode()).hexdigest()
    groups = [m.kwargs.get('name', m.args[0] if m.args else 'default')
              for m in request.node.iter_markers('xdist_group')]
    (root / 'records' / (identity + '.json')).write_text(json.dumps({
        'worker': worker_id, 'kind': kind, 'groups': groups,
        'nodeid': request.node.nodeid}), encoding='utf-8')
""",
        encoding="utf-8",
    )
    conflict = "@pytest.mark.xdist_group('another-resource')\n" if conflicting_group else ""
    (tmp_path / "test_database.py").write_text(
        "import pytest\nfrom record import record\n"
        + conflict
        + "@pytest.mark.parametrize('case', range(3))\n"
        + "def test_direct(live_database, request, worker_id, case):\n"
        + "    record(request, worker_id, 'database')\n"
        + "def test_transitive(indirect_database, request, worker_id):\n"
        + "    record(request, worker_id, 'database')\n",
        encoding="utf-8",
    )
    (tmp_path / "test_expansion.py").write_text(
        "import pytest\nfrom record import record\n"
        "@pytest.mark.parametrize('case', range(3))\n"
        "def test_psql(live_psql, request, worker_id, case):\n"
        "    record(request, worker_id, 'database')\n",
        encoding="utf-8",
    )
    (tmp_path / "test_unit.py").write_text(
        "import pytest\nfrom record import record\n"
        "@pytest.mark.parametrize('case', range(6))\n"
        "def test_independent(request, worker_id, case):\n"
        "    record(request, worker_id, 'unit')\n",
        encoding="utf-8",
    )
    return tmp_path


def run_mini_suite(
    root: Path, *, distribution: str = "loadgroup"
) -> subprocess.CompletedProcess[str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTEST_ADDOPTS", "PYTEST_PLUGINS"} and not key.startswith(("DS60_", "PG"))
    }
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    # These values only enable the guard. The dummy fixtures never connect.
    environment["DS60_TEST_DATABASE_URL"] = "dummy-isolated-database-fixture"
    environment["DS60_SQL_EXPANSION_TEST_URL"] = "dummy-isolated-psql-fixture"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "xdist.plugin",
            "-c",
            "pytest.ini",
            "-q",
            "-n",
            "2",
            "--dist",
            distribution,
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=35,
        check=False,
    )


def test_shared_fixture_closure_uses_one_worker_without_serializing_units(tmp_path: Path) -> None:
    root = mini_suite(tmp_path)
    result = run_mini_suite(root)
    assert result.returncode == 0, result.stdout + result.stderr
    records = [
        json.loads(path.read_text(encoding="utf-8")) for path in (root / "records").glob("*")
    ]
    database = [record for record in records if record["kind"] == "database"]
    units = [record for record in records if record["kind"] == "unit"]
    assert len(database) == 7 and len(units) == 6
    workers = {record["worker"] for record in database}
    assert len(workers) == 1, database
    assert any(record["worker"] not in workers for record in units), records
    assert all(record["groups"] == ["shared-postgres"] for record in database)
    assert all(not record["groups"] for record in units)
    assert not (root / "shared-database.lock").exists()


@pytest.mark.parametrize("distribution", ["load", "loadfile", "worksteal"])
def test_wrong_parallel_strategy_is_rejected_before_shared_fixture_runs(
    tmp_path: Path, distribution: str
) -> None:
    root = mini_suite(tmp_path)
    result = run_mini_suite(root, distribution=distribution)
    assert result.returncode != 0
    assert "Shared PostgreSQL proofs require --dist loadgroup" in result.stdout + result.stderr
    records = [
        json.loads(path.read_text(encoding="utf-8")) for path in (root / "records").glob("*")
    ]
    assert not any(record["kind"] == "database" for record in records)
    assert not (root / "database-fixture-ran").exists()
    assert not (root / "psql-fixture-ran").exists()


def test_second_group_cannot_split_shared_postgres_across_workers(tmp_path: Path) -> None:
    root = mini_suite(tmp_path, conflicting_group=True)
    result = run_mini_suite(root)
    assert result.returncode != 0
    assert "cannot also use xdist_group" in result.stdout + result.stderr
    records = [
        json.loads(path.read_text(encoding="utf-8")) for path in (root / "records").glob("*")
    ]
    assert not any("test_direct" in record["nodeid"] for record in records)
