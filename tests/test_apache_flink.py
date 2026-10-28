"""Flink fixture, no-replay and native-lifecycle policy contracts, not runtime simulation."""

from __future__ import annotations

import hashlib
import importlib
import io
import json
import os
import runpy
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Any

import pytest

BASE = Path(__file__).resolve().parents[1] / "courses/apache-data-platforms/projects/flink"


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.syspath_prepend(str(BASE))
    module = importlib.import_module("project_state")
    root = tmp_path / "state"
    root.mkdir()
    monkeypatch.setattr(module, "ROOT", root)
    module.initialize()
    return module


def test_flink_initialized_source_is_immutable_and_corruption_is_not_repaired(state: Any) -> None:
    before = {p.name: p.read_bytes() for p in (state.ROOT / "input").iterdir()}
    state.initialize()
    assert before == {p.name: p.read_bytes() for p in (state.ROOT / "input").iterdir()}
    target = state.ROOT / "input/orders.csv"
    target.write_text("unexpected retained input")
    with pytest.raises(ValueError, match="no replacement"):
        state.initialize()
    assert target.read_text() == "unexpected retained input"


def test_flink_checkpoint_oracle_rejects_missing_duplicate_and_wrong_final_state(
    state: Any,
) -> None:
    rows = [[str(i), str((i + 1) * (i + 2) // 2)] for i in range(100)]
    assert state.verify_result("checkpointed", rows)["final_total"] == 5050
    for wrong in [rows[:-1], rows[:-1] + [rows[0]], rows[:-1] + [["99", "5000"]]]:
        with pytest.raises(ValueError, match="Recovered"):
            state.verify_result("checkpointed", wrong)


def test_flink_timer_oracle_separates_old_state_from_fresh_activity(state: Any) -> None:
    rows = [
        ["update", "east", "1", "4"],
        ["update", "east", "3", "11"],
        ["update", "west", "2", "9"],
        ["timer", "west", "1000", "9"],
        ["timer", "east", "2000", "11"],
        ["late", "east", "4", "1000", "5"],
        ["update", "east", "5", "3"],
        ["timer", "east", "3000", "3"],
    ]
    assert state.verify_result("state", rows)["inactive_state_cleared"] is True
    wrong = [row if row[:3] != ["update", "east", "5"] else row[:3] + ["14"] for row in rows]
    with pytest.raises(ValueError, match="timer replacement"):
        state.verify_result("state", wrong)


def test_flink_result_reader_ignores_inprogress_but_rejects_unsafe_identity(state: Any) -> None:
    identity = "a" * 32
    folder = state.ROOT / "results" / identity
    folder.mkdir()
    (folder / "part-complete").write_text("east,11\n")
    (folder / "part-pending.inprogress.token").write_text("not committed\n")
    rows, hashes = state.result_rows(identity)
    assert rows == [["east", "11"]] and set(hashes) == {"part-complete"}
    with pytest.raises(ValueError, match="identity"):
        state.result_rows("../other")


def test_flink_atomic_write_preserves_preexisting_final_state(state: Any) -> None:
    target = state.ROOT / "receipts/existing.json"
    target.write_text("retained")
    with pytest.raises(FileExistsError):
        state.atomic_json(target, {"passed": True})
    assert target.read_text() == "retained"


def test_unknown_flink_submission_is_not_silently_replayed(
    state: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = runpy.run_path(str(BASE / "workshop.py"))
    submit = scope["submit"]
    monkeypatch.setitem(submit.__globals__, "jobs_named", lambda name: [])
    monkeypatch.setitem(
        submit.__globals__,
        "job_artifact",
        lambda: pytest.fail("An unknown submission must not compile/resubmit"),
    )
    monkeypatch.setitem(
        submit.__globals__,
        "process",
        lambda *args, **kwargs: pytest.fail("No client may be replayed"),
    )
    record = {
        "schema_version": 1,
        "source_sha256": "b" * 64,
        "action": "check",
        "request_id": "a" * 32,
        "status": "unknown",
        "job_id": None,
        "output": "/state/results/" + "a" * 32,
    }
    with pytest.raises(RuntimeError, match="no job was replayed"):
        submit(record, "bounded")
    saved = json.loads((state.ROOT / "requests/check.json").read_text())
    assert saved["status"] == "unknown" and saved["job_id"] is None


def test_saved_flink_result_readback_never_submits(
    state: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = runpy.run_path(str(BASE / "workshop.py"))
    path = state.ROOT / "receipts" / ("a" * 32 + ".json")
    record = {
        "schema_version": 1,
        "request_id": "a" * 32,
        "action": "check",
        "source_sha256": "b" * 64,
        "job_id": "c" * 32,
        "receipt": str(path),
    }
    state.atomic_json(
        path,
        record
        | {
            "passed": True,
            "actual_flink": True,
            "status": "completed",
            "observation": {"source_records": 3},
        },
    )
    monkeypatch.setitem(
        scope["saved"].__globals__,
        "process",
        lambda *args, **kwargs: pytest.fail("Inspection cannot execute"),
    )
    assert scope["saved"](record)["saved_readback_no_execution"] is True
    with pytest.raises(ValueError, match="request identity"):
        scope["saved"](record | {"source_sha256": "d" * 64})
    with pytest.raises(ValueError, match="Invalid saved receipt"):
        scope["saved"](record | {"request_id": "e" * 32})


def test_flink_installer_rejects_unsafe_archive_after_hash_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = runpy.run_path(str(BASE / "binary-image/install.py"))
    install = scope["install"]
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w:gz") as archive:
        member = tarfile.TarInfo("flink-2.3.0/../../escaped")
        member.size = 1
        archive.addfile(member, io.BytesIO(b"x"))
    payload = data.getvalue()
    lock = install.__globals__["LOCK"]
    monkeypatch.setitem(lock, "archive_bytes", len(payload))
    monkeypatch.setitem(lock, "sha512", hashlib.sha512(payload).hexdigest())

    class Response(io.BytesIO):
        def geturl(self) -> str:
            return str(lock["url"])

    monkeypatch.setattr(
        install.__globals__["urllib"].request, "urlopen", lambda *args, **kwargs: Response(payload)
    )
    monkeypatch.setattr(
        install.__globals__["subprocess"],
        "check_output",
        lambda args, **kwargs: (
            'openjdk version "17.0.21"' if args[0] == "java" else "javac 17.0.21"
        ),
    )
    with pytest.raises(ValueError, match="Unsafe distribution path"):
        install(tmp_path / "runtime")
    assert not (tmp_path / "escaped").exists() and not (tmp_path / "runtime").exists()


def test_actual_result_stays_visible_when_flink_receipt_storage_fails(
    state: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = runpy.run_path(str(BASE / "workshop.py"))
    identity = "a" * 32
    folder = state.ROOT / "results" / identity
    folder.mkdir()
    (folder / "part-done").write_text("update,east,1,4\nupdate,west,2,9\nupdate,east,3,11\n")
    finish = scope["wait_finish"]
    monkeypatch.setitem(finish.__globals__, "job_state", lambda job: {"state": "FINISHED"})
    monkeypatch.setitem(finish.__globals__, "api", lambda path: {"counts": {}, "latest": {}})

    def unavailable(*args: Any, **kwargs: Any) -> None:
        raise OSError("fixture save failure")

    monkeypatch.setitem(finish.__globals__, "atomic_json", unavailable)
    record = {
        "schema_version": 1,
        "action": "check",
        "request_id": identity,
        "source_sha256": "b" * 64,
        "status": "running",
        "output": "/state/results/" + identity,
        "job_id": "c" * 32,
    }
    result = finish(record, "bounded")
    assert result["passed"] is True
    assert result["observation"]["final_key_totals"] == {"east": 11, "west": 9}
    assert "storage_warning" in result
    assert not (state.ROOT / "receipts" / (identity + ".json")).exists()


def test_batch_sql_observer_does_not_require_a_checkpoint_endpoint(
    state: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = runpy.run_path(str(BASE / "workshop.py"))
    identity = "a" * 32
    folder = state.ROOT / "results" / identity
    folder.mkdir()
    (folder / "sql-rows.csv").write_text("east,11\nwest,9\n")
    finish = scope["wait_finish"]
    monkeypatch.setitem(finish.__globals__, "job_state", lambda job: {"state": "FINISHED"})
    monkeypatch.setitem(
        finish.__globals__, "api", lambda path: pytest.fail("Batch SQL has no checkpoint gate")
    )
    record = {
        "schema_version": 1,
        "action": "check-sql",
        "request_id": identity,
        "source_sha256": "b" * 64,
        "status": "running",
        "output": "/state/results/" + identity,
        "job_id": "c" * 32,
    }
    result = finish(record, "sql")
    assert result["passed"] is True and result["checkpoint_summary"] == {}


def test_retained_flink_request_cannot_redirect_state_writes(
    state: Any,
) -> None:
    scope = runpy.run_path(str(BASE / "workshop.py"))
    identity_before = (state.ROOT / "identity.json").read_bytes()
    record = {
        "schema_version": 1,
        "action": "../identity",
        "request_id": "a" * 32,
        "source_sha256": "b" * 64,
        "status": "running",
        "output": "/state/results/" + "a" * 32,
        "job_id": None,
    }
    with pytest.raises(ValueError, match="identity/schema"):
        scope["save_request"](record)
    assert (state.ROOT / "identity.json").read_bytes() == identity_before


def test_flink_pressure_requires_an_observed_producer_metric(state: Any) -> None:
    scope = runpy.run_path(str(BASE / "workshop.py"))
    extract = scope["accumulated_pressure"]
    assert (
        extract(
            {
                "vertices": [
                    {"name": "slow-consumer", "metrics": {"accumulated-backpressured-time": 9000}}
                ]
            }
        )
        == []
    )
    assert (
        extract(
            {
                "vertices": [
                    {
                        "name": "pressure-payload-producer",
                        "metrics": {"accumulated-backpressured-time": "NaN"},
                    }
                ]
            }
        )
        == []
    )
    measured = extract(
        {
            "vertices": [
                {
                    "name": "pressure-payload-producer",
                    "metrics": {"accumulated-backpressured-time": 5137},
                }
            ]
        }
    )
    assert measured == [
        {
            "id": "accumulated-backpressured-time",
            "value": "5137",
            "units": "milliseconds",
            "vertex": "pressure-payload-producer",
            "source": "actual-task-rest-metrics",
        }
    ]


@pytest.mark.parametrize("workshop", ["ballista", "airflow", "streaming", "flink"])
def test_owned_workshop_compose_ignores_ambient_identity_overrides(
    tmp_path: Path, workshop: str
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    shutil.copy2(BASE.parent / workshop / "run.sh", project / "run.sh")
    owner = "0123456789abcdef0123456789abcdef"
    prefix = "stream" if workshop == "streaming" else workshop
    expected = {
        "DS60_WORKSHOP_OWNER": owner,
        "DS60_WORKSHOP_PROJECT": f"ds60-apache-{prefix}-{owner[:12]}",
    }
    expected.update(
        {
            "ballista": {"DS60_BALLISTA_IMAGE": "ds60-apache-ballista-swift:54.1.0"},
            "airflow": {
                "DS60_AIRFLOW_IMAGE": "ds60-apache-airflow-core:3.3.2",
                "DS60_AIRFLOW_PORT": "18880",
            },
            "streaming": {
                "DS60_KAFKA_CLUSTER_ID": "abcdefghijklmnopqrstuv",
                "DS60_KAFKA_ROUTE": "binary",
            },
            "flink": {"DS60_FLINK_IMAGE": "ds60-apache-flink-binary:2.3.0"},
        }[workshop]
    )
    (project / ".env").write_text("".join(f"{key}={value}\n" for key, value in expected.items()))
    tools = tmp_path / "tools"
    tools.mkdir()
    captured = tmp_path / "compose-environment.json"
    docker = tools / "docker"
    docker.write_text(
        "#!/usr/bin/env python3\n"
        + """
import json,os,sys
from pathlib import Path
args=sys.argv[1:]
if args[:2] == ['info','--format']:
    print('linux|aarch64')
elif args[0] == 'compose':
    keys=json.loads(os.environ['EXPECTED_KEYS'])
    observed={key: os.environ.get(key) for key in keys}
    Path(os.environ['CAPTURE_COMPOSE_ENV']).write_text(json.dumps(observed))
elif args[:2] not in [['ps','-aq'],['network','ls'],['volume','ls']]:
    raise SystemExit(99)
"""
    )
    docker.chmod(0o755)
    original = (project / ".env").read_bytes()
    result = subprocess.run(
        ["bash", "run.sh", "status"],
        cwd=project,
        env=os.environ
        | dict.fromkeys(expected, "unexpected-ambient-value")
        | {
            "PATH": str(tools) + os.pathsep + os.environ["PATH"],
            "DOCKER_CONTEXT": "",
            "DOCKER_HOST": "unix:///fixture/docker.sock",
            "DOCKER_DEFAULT_PLATFORM": "linux/amd64",
            "CAPTURE_COMPOSE_ENV": str(captured),
            "EXPECTED_KEYS": json.dumps([*expected, "DOCKER_DEFAULT_PLATFORM"]),
        },
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(captured.read_text()) == expected | {"DOCKER_DEFAULT_PLATFORM": None}
    assert (project / ".env").read_bytes() == original
    assert not (project / ".workshop-lock").exists()
