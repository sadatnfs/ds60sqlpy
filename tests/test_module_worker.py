"""Real loopback protocol checks without images, installation or privileged jobs."""

from __future__ import annotations

import contextlib
import http.client
import json
import os
import threading
import time
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ds60sqlpy.module_worker import (
    MAX_REQUEST_BYTES,
    MAX_TERMINAL_JOBS,
    WorkerHTTPServer,
    WorkerRequestError,
    WorkerState,
    probe_isolation,
    read_worker_token,
)
from ds60sqlpy.worker_operations import OperationResult

TOKEN = "a" * 64


def payload(**change: Any) -> dict[str, Any]:
    return {
        "job_id": uuid.uuid4().hex,
        "profile": "python-core",
        "operation": "execute",
        "source": "print(42)",
        "language": "python",
        "timeout_seconds": 15,
        "verification_id": None,
        **change,
    }


def successful(*args: Any, **kwargs: Any) -> OperationResult:
    return OperationResult(0, "42\n", False, "succeeded", "Execution only.")


@contextlib.contextmanager
def server(state: WorkerState) -> Iterator[str]:
    httpd = WorkerHTTPServer(("127.0.0.1", 0), state, TOKEN)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()


def request(
    url: str, data: dict[str, Any] | None = None, token: str = TOKEN, **headers: str
) -> tuple[int, dict[str, Any]]:
    body = json.dumps(data).encode() if data is not None else None
    req = Request(
        url,
        data=body,
        headers={"X-DS60-Worker-Token": token, "Content-Type": "application/json", **headers},
    )
    try:
        with urlopen(req, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        with exc:
            return exc.code, json.load(exc)


def wait_done(state: WorkerState, key: str) -> dict[str, Any]:
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        result = state.get(key)
        if result["status"] in {"succeeded", "failed", "cancelled", "timed_out"}:
            return result
        time.sleep(0.005)
    raise AssertionError("Fake worker did not finish.")


def test_real_http_submit_poll_and_private_health() -> None:
    state = WorkerState(
        "python-core",
        executor=successful,
        ready=True,
        detail="Fake backend for protocol tests.",
        isolate_jobs=False,
    )
    with server(state) as base:
        assert request(base + "/health", token="wrong")[0] == 401
        assert request(base + "/health", Origin="http://example.invalid")[0] == 401
        code, health = request(base + "/health")
        assert code == 200 and health["ready"] is True and health["profile"] == "python-core"
        assert len(health["instance_id"]) == 32
        assert request(base + "/health")[1]["instance_id"] == health["instance_id"]
        body = payload()
        code, accepted = request(base + "/jobs", body)
        assert code == 202 and accepted["job_id"] == body["job_id"]
        done = wait_done(state, body["job_id"])
        code, polled = request(base + f"/jobs/{body['job_id']}")
        assert code == 200 and polled["output"] == "42\n"
        assert done["status"] == "succeeded" and done["returncode"] == 0
        assert done["checks"] == []  # Execution is not fabricated verification.
        assert request(base + "/jobs", body)[0] == 409
        assert request(base + "/jobs/" + "f" * 32)[0] == 404
        assert request(base + "/health?token=anything")[0] == 404


@pytest.mark.parametrize(
    "change",
    [
        {"job_id": "../bad"},
        {"profile": "cpp20"},
        {"operation": "shell"},
        {"source": []},
        {"source": "x" * 262145},
        {"source": "\ud800"},
        {"language": "cpp"},
        {"timeout_seconds": True},
        {"timeout_seconds": 16},
        {"verification_id": "stdout-looks-good"},
        {"verification_id": []},
        {"extra": "bad"},
    ],
)
def test_payload_rejected_before_executor(change: dict[str, Any]) -> None:
    state = WorkerState("python-core", executor=successful, ready=True)
    with pytest.raises(WorkerRequestError):
        state.submit(payload(**change))
    assert not state.jobs


def test_busy_cancel_and_cleanup_on_server_close() -> None:
    entered = threading.Event()

    def blocking(*args: Any, **kwargs: Any) -> OperationResult:
        cancel = args[4]
        entered.set()
        assert cancel.wait(3)
        return OperationResult(-15, "", False, "cancelled", "Owned process stopped.")

    state = WorkerState("python-core", executor=blocking, ready=True)
    with server(state) as base:
        first = payload()
        assert request(base + "/jobs", first)[0] == 202
        assert entered.wait(1)
        assert request(base + "/jobs", payload())[0] == 409
        assert request(base + f"/jobs/{first['job_id']}/cancel", {"wrong": 1})[0] == 400
        assert request(base + f"/jobs/{first['job_id']}/cancel", {})[0] == 200
        assert wait_done(state, first["job_id"])["status"] == "cancelled"
        second = payload()
        assert request(base + "/jobs", second)[0] == 202
    assert wait_done(state, second["job_id"])["status"] == "cancelled"
    assert state.thread is not None and not state.thread.is_alive()


def test_not_ready_does_not_accept_jobs() -> None:
    state = WorkerState("python-core", executor=successful, ready=False, detail="Missing NumPy.")
    with pytest.raises(WorkerRequestError, match="NumPy") as error:
        state.submit(payload())
    assert error.value.status == 503


def test_terminal_memory_is_bounded_and_source_is_discarded() -> None:
    state = WorkerState("python-core", executor=successful, ready=True)
    keys = []
    try:
        for _ in range(MAX_TERMINAL_JOBS + 3):
            body = payload()
            keys.append(body["job_id"])
            state.submit(body)
            wait_done(state, body["job_id"])
        assert len(state.jobs) == MAX_TERMINAL_JOBS
        assert all(job.source == "" for job in state.jobs.values())
        with pytest.raises(WorkerRequestError):
            state.get(keys[0])
    finally:
        state.close()


def test_raw_http_body_limits_and_json_types() -> None:
    state = WorkerState("python-core", executor=successful, ready=True)
    with server(state) as base:
        port = int(base.rsplit(":", 1)[1])
        for length, body, expected in [
            (MAX_REQUEST_BYTES + 1, b"", 413),
            (2, b"[]", 400),
            (1, b"{", 400),
        ]:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
            try:
                connection.request(
                    "POST",
                    "/jobs",
                    body=body,
                    headers={
                        "X-DS60-Worker-Token": TOKEN,
                        "Content-Type": "application/json",
                        "Content-Length": str(length),
                    },
                )
                response = connection.getresponse()
                assert response.status == expected
                response.read()
            finally:
                connection.close()
        assert not state.jobs


@pytest.mark.skipif(
    os.name != "posix", reason="Worker credential modes are a Linux container contract."
)
def test_private_token_validation_and_no_learning_backups(tmp_path: Path) -> None:
    token = tmp_path / "worker-token"
    token.write_text(TOKEN)
    token.chmod(0o600)
    assert read_worker_token(token) == TOKEN
    token.chmod(0o644)
    with pytest.raises(ValueError, match="mode600"):
        read_worker_token(token)
    token.chmod(0o600)
    learning = tmp_path / ".learning"
    learning.mkdir()
    backup = learning / "token"
    backup.write_text(TOKEN)
    backup.chmod(0o600)
    with pytest.raises(ValueError, match="outside"):
        read_worker_token(backup)
    alias = tmp_path / "alias"
    alias.symlink_to(token)
    with pytest.raises(ValueError):
        read_worker_token(alias)


def test_unqualified_native_worker_never_claims_identity_isolation(tmp_path: Path) -> None:
    # These tests do not require a privileged supervisor on the developer host.
    if not Path("/.dockerenv").exists():
        ready, detail = probe_isolation(tmp_path / "missing")
        assert ready is False and "Linux supervisor" in detail


def test_real_http_runs_current_source_and_streams_partial_logs() -> None:
    from ds60sqlpy.worker_operations import execute_operation

    state = WorkerState("python-core", executor=execute_operation, ready=True, isolate_jobs=False)
    with server(state) as base:
        body = payload(
            source="import time\nprint('PARTIAL',flush=True)\ntime.sleep(.6)\nprint(42)\n"
        )
        assert request(base + "/jobs", body)[0] == 202
        observed = False
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            code, snapshot = request(base + "/jobs/" + body["job_id"])
            assert code == 200
            if "PARTIAL" in snapshot["output"] and snapshot["status"] not in {
                "succeeded",
                "failed",
            }:
                observed = True
            if snapshot["status"] == "succeeded":
                assert snapshot["output"].splitlines() == ["PARTIAL", "42"]
                break
            time.sleep(0.02)
        else:
            raise AssertionError("Real HTTP job did not finish")
        assert observed, "Small flushed output must be visible before process exit"


def test_control_routes_do_not_need_a_new_thread_under_job_pid_pressure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered = threading.Event()

    def busy(*args: Any, **kwargs: Any) -> OperationResult:
        entered.set()
        assert args[4].wait(3)
        return OperationResult(-15, "", False, "cancelled", "Stopped.")

    state = WorkerState("python-core", executor=busy, ready=True)
    with server(state) as base:
        body = payload()
        assert request(base + "/jobs", body)[0] == 202
        assert entered.wait(1)

        def exhausted(*args: Any, **kwargs: Any) -> None:
            raise RuntimeError("cannot start new thread")

        with monkeypatch.context() as patch:
            patch.setattr(threading.Thread, "start", exhausted)
            assert request(base + "/health")[0] == 200
            assert request(base + "/jobs/" + body["job_id"])[0] == 200
            assert request(base + "/jobs/" + body["job_id"] + "/cancel", {})[0] == 200
            assert wait_done(state, body["job_id"])["status"] == "cancelled"


def test_job_thread_admission_failure_is_terminal_and_not_falsely_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = WorkerState("python-core", executor=successful, ready=True)

    def unavailable(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("cannot start new thread")

    with server(state) as base, monkeypatch.context() as patch:
        patch.setattr(threading.Thread, "start", unavailable)
        body = payload()
        code, result = request(base + "/jobs", body)
        assert code == 202 and result["status"] == "failed"
        assert result["returncode"] is None and result["checks"] == []
        assert "No learner process started" in result["detail"]
        assert request(base + "/health")[1]["ready"] is False
