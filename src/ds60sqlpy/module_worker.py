"""Authenticated, private-network asynchronous learning worker.

Run this service only through an explicitly prepared optional worker profile.
It publishes no port itself and never starts an engine or downloads a model.
"""

from __future__ import annotations

import argparse
import contextlib
import hmac
import json
import os
import re
import secrets
import select
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from ds60sqlpy.http_server import LocalHTTPServer
from ds60sqlpy.worker_operations import (
    MAX_SOURCE_BYTES,
    PROFILES,
    TIMEOUTS,
    OperationResult,
    execute_operation,
    probe_profile,
    validate_operation,
)

MAX_REQUEST_BYTES = MAX_SOURCE_BYTES * 6 + 4096
MAX_TERMINAL_JOBS = 32
JOB_ID = re.compile(r"[0-9a-f]{32}\Z")
TERMINAL = frozenset({"succeeded", "failed", "cancelled", "timed_out"})


class WorkerRequestError(ValueError):
    def __init__(self, detail: str, status: int = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(detail)
        self.status = status


def read_worker_token(path: Path) -> str:
    resolved = path.resolve(strict=True)
    if ".learning" in resolved.parts or path.is_symlink():
        raise ValueError("Worker credentials must be a private file outside portable .learning.")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or not 32 <= info.st_size <= 512:
        raise ValueError("The worker token must be a regular 32-512 byte file.")
    parent = path.parent
    parent_info = parent.lstat()
    protected_parent = (
        parent == Path("/run/ds60")
        and stat.S_ISDIR(parent_info.st_mode)
        and not parent.is_symlink()
        and parent_info.st_uid == 0
        and stat.S_IMODE(parent_info.st_mode) == 0o700
    )
    # Windows engine file sharing can expand mode bits despite a private host
    # ACL. Only the image-owned exact root-private parent is an alternative;
    # the mandatory demoted-UID probe must still prove the token unreadable.
    if (stat.S_IMODE(info.st_mode) & 0o077 and not protected_parent) or info.st_uid == 65534:
        raise ValueError("The worker token must be private mode600 and unreadable by the job UID.")
    token = path.read_text(encoding="ascii").strip()
    if not 32 <= len(token) <= 512 or any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise ValueError(
            "The worker token must contain 32-512 printable non-space ASCII characters."
        )
    return token


def probe_isolation(token_path: Path) -> tuple[bool, str]:
    if (
        sys.platform != "linux"
        or os.geteuid() != 0
        or not (Path("/.dockerenv").exists() or Path("/run/.containerenv").exists())
    ):
        return False, "Prepared workers require a Linux supervisor able to drop job UID/GID."
    command = (
        "import os,sys,time; os.setgroups([]); os.setgid(65534); os.setuid(65534); "
        "\ntry:\n open(sys.argv[1], 'rb').close()\nexcept PermissionError:\n pass"
        "\nexcept OSError:\n sys.exit(2)\nelse:\n sys.exit(3)"
        "\nprint('ISOLATED',flush=True); time.sleep(4)"
    )
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", command, str(token_path)],
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        assert process.stdout is not None
        readable, _, _ = select.select([process.stdout], [], [], 2)
        if not readable or process.stdout.readline(16) != b"ISOLATED\n":
            return False, "The job UID can read the token or privilege-drop setup failed."
        # CAP_KILL is needed because the supervisor and job use different UIDs.
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=2)
        if process.returncode != -signal.SIGTERM:
            return False, "The supervisor could not terminate its demoted job identity."
        return True, "Fixed job UID/GID isolation, token privacy and cancellation probe passed."
    except (OSError, subprocess.TimeoutExpired):
        return False, "Identity isolation or different-UID process cleanup is unavailable."
    finally:
        if process is not None:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=5)
            if process.stdout is not None:
                process.stdout.close()


@dataclass
class WorkerJob:
    job_id: str
    profile: str
    source: str
    language: str
    timeout_seconds: int
    verification_id: str | None
    status: str = "queued"
    output: str = ""
    returncode: int | None = None
    checks: list[dict[str, Any]] = field(default_factory=list)
    truncated: bool = False
    detail: str = "Accepted; waiting for the owned execution thread."
    started: float = field(default_factory=time.monotonic)
    finished: float | None = None
    cancel: threading.Event = field(default_factory=threading.Event)

    def snapshot(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "profile": self.profile,
            "status": self.status,
            "output": self.output,
            "returncode": self.returncode,
            "checks": [dict(item) for item in self.checks],
            "truncated": self.truncated,
            "elapsed_seconds": round((self.finished or time.monotonic()) - self.started, 3),
            "detail": self.detail,
        }


Executor = Callable[..., OperationResult]


class WorkerState:
    """One active operation plus at most 32 terminal in-memory snapshots."""

    def __init__(
        self,
        profile: str,
        *,
        scratch_root: Path | None = None,
        executor: Executor = execute_operation,
        ready: bool = False,
        detail: str = "Readiness has not been probed.",
        isolate_jobs: bool = True,
    ) -> None:
        if profile not in PROFILES:
            raise ValueError("Unknown worker profile.")
        self.profile = profile
        self.instance_id = secrets.token_hex(16)
        self.scratch_root = scratch_root
        self.executor = executor
        self.ready = ready
        self.detail = detail
        self.isolate_jobs = isolate_jobs
        self.jobs: OrderedDict[str, WorkerJob] = OrderedDict()
        self.lock = threading.RLock()
        self.thread: threading.Thread | None = None
        self.closing = False

    def submit(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {
            "job_id",
            "profile",
            "operation",
            "source",
            "language",
            "timeout_seconds",
            "verification_id",
        }
        if set(payload) != required:
            raise WorkerRequestError("Submit exactly the version 1 job fields.")
        job_id = payload["job_id"]
        if not isinstance(job_id, str) or not JOB_ID.fullmatch(job_id):
            raise WorkerRequestError("job_id must be a lowercase UUID hex string.")
        if payload["profile"] != self.profile or payload["operation"] != "execute":
            raise WorkerRequestError("Profile or operation does not match this worker.")
        if (
            not isinstance(payload["source"], str)
            or len(payload["source"].encode("utf-8", errors="surrogatepass")) > MAX_SOURCE_BYTES
        ):
            raise WorkerRequestError("source must be a UTF-8 string of at most 256 KiB.")
        if any(0xD800 <= ord(char) <= 0xDFFF for char in payload["source"]):
            raise WorkerRequestError("Source must contain valid Unicode characters.")
        if not isinstance(payload["language"], str):
            raise WorkerRequestError("language must be a registered language string.")
        timeout = payload["timeout_seconds"]
        if type(timeout) is not int or timeout not in TIMEOUTS:
            raise WorkerRequestError("timeout_seconds must be 15, 60 or 120.")
        verification_id = payload["verification_id"]
        if verification_id is not None and not isinstance(verification_id, str):
            raise WorkerRequestError("verification_id must be a registered string or null.")
        try:
            validate_operation(self.profile, payload["language"], verification_id)
        except ValueError as exc:
            raise WorkerRequestError(str(exc)) from exc
        with self.lock:
            if self.closing or not self.ready:
                raise WorkerRequestError(self.detail, HTTPStatus.SERVICE_UNAVAILABLE)
            if job_id in self.jobs:
                raise WorkerRequestError(
                    "Duplicate job_id; poll the existing job.", HTTPStatus.CONFLICT
                )
            if any(job.status not in TERMINAL for job in self.jobs.values()):
                raise WorkerRequestError("Worker is busy with one active job.", HTTPStatus.CONFLICT)
            job = WorkerJob(
                job_id,
                self.profile,
                payload["source"],
                payload["language"],
                timeout,
                verification_id,
            )
            self.jobs[job_id] = job
            self.thread = threading.Thread(target=self._run, args=(job,), daemon=True)
            snapshot = job.snapshot()
            try:
                self.thread.start()
            except RuntimeError:
                self.ready = False
                self.detail = (
                    "Worker thread capacity is unavailable; inspect and restart this profile."
                )
                job.status = "failed"
                job.detail = (
                    "No learner process started because the job controller could not start."
                )
                job.source = ""
                job.finished = time.monotonic()
                return job.snapshot()
            return snapshot

    def _run(self, job: WorkerJob) -> None:
        def update(status: str) -> None:
            with self.lock:
                if job.status not in TERMINAL:
                    job.status = status

        def output_update(output: str, truncated: bool) -> None:
            with self.lock:
                job.output = output
                job.truncated = truncated

        try:
            update("preparing")
            with tempfile.TemporaryDirectory(prefix="job-", dir=self.scratch_root) as temporary:
                result = self.executor(
                    job.profile,
                    job.source,
                    Path(temporary),
                    job.timeout_seconds,
                    job.cancel,
                    update,
                    job.verification_id,
                    isolate_user=self.isolate_jobs,
                    on_output=output_update,
                )
            with self.lock:
                job.status = result.status
                job.output = result.output
                job.returncode = result.returncode
                job.checks = result.checks
                job.truncated = result.truncated
                job.detail = result.detail
                if self.profile in {"cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"}:
                    from ds60sqlpy.gpu_runtime import needs_device_review

                    if needs_device_review(
                        result.status, result.output, result.detail, result.returncode
                    ):
                        self.ready = False
                        self.detail = (
                            "GPU health needs owner review after an interrupted or "
                            "failed device operation. Child-process cleanup does not "
                            "prove device recovery. Inspect the GPU, then restart this "
                            "worker to repeat its real kernel probe. "
                            "No GPU reset was attempted."
                        )
                        job.detail += " " + self.detail
        except Exception:
            with self.lock:
                job.status = "failed"
                job.detail = (
                    "Worker infrastructure failed; cleanup is not confirmed. "
                    "Inspect and restart this prepared profile before retrying."
                )
                self.ready = False
                self.detail = job.detail
        finally:
            with self.lock:
                job.source = ""  # Retain bounded results, not submitted source copies.
                job.finished = time.monotonic()
                terminal_ids = [key for key, item in self.jobs.items() if item.status in TERMINAL]
                for key in terminal_ids[:-MAX_TERMINAL_JOBS]:
                    del self.jobs[key]

    def get(self, job_id: str) -> dict[str, Any]:
        with self.lock:
            if job_id not in self.jobs:
                raise WorkerRequestError("Unknown or expired worker job.", HTTPStatus.NOT_FOUND)
            return self.jobs[job_id].snapshot()

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        with self.lock:
            if job_id not in self.jobs:
                raise WorkerRequestError("Unknown or expired worker job.", HTTPStatus.NOT_FOUND)
            job = self.jobs[job_id]
            if job.status not in TERMINAL:
                job.cancel.set()
                job.detail = "Cancellation requested; waiting for process-tree cleanup."
            return job.snapshot()

    def close(self) -> None:
        with self.lock:
            self.closing = True
            for job in self.jobs.values():
                if job.status not in TERMINAL:
                    job.cancel.set()
            thread = self.thread
        if thread is not None and thread.ident is not None:
            thread.join(timeout=8)


class WorkerHTTPServer(LocalHTTPServer):
    """Keep the control loop on its existing thread under child PID pressure.

    Jobs run in one background thread. Health/poll/cancel never need to create
    a new thread, so a JVM reaching its container PID ceiling cannot starve the
    controller's ability to ask for cancellation or retrieve a failure.
    """

    request_queue_size = 16

    def __init__(self, address: tuple[str, int], state: WorkerState, token: str) -> None:
        self.state = state
        self.token = token
        super().__init__(address, WorkerHandler)

    def server_close(self) -> None:
        self.state.close()
        super().server_close()


class WorkerHandler(BaseHTTPRequestHandler):
    server: WorkerHTTPServer
    protocol_version = "HTTP/1.1"
    server_version = "DS60Worker/1"
    sys_version = ""

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, format: str, *args: Any) -> None:
        # No request headers, submitted code, tokens or learner paths in access logs.
        return

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        with contextlib.suppress(BrokenPipeError, ConnectionResetError):
            self.wfile.write(data)

    def _authenticated(self) -> bool:
        supplied = self.headers.get("X-DS60-Worker-Token", "")
        if self.headers.get("Origin") or not hmac.compare_digest(
            supplied.encode("utf-8"), self.server.token.encode("utf-8")
        ):
            self._send(HTTPStatus.UNAUTHORIZED, {"detail": "Worker authentication required."})
            return False
        return True

    def _body(self) -> dict[str, Any]:
        if self.headers.get("Transfer-Encoding"):
            raise WorkerRequestError("Transfer-Encoding is not supported.")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or len(lengths[0]) > 10 or not lengths[0].isdecimal():
            raise WorkerRequestError("One decimal Content-Length is required.")
        length = int(lengths[0])
        if length > MAX_REQUEST_BYTES:
            raise WorkerRequestError(
                "Job request is too large.", HTTPStatus.REQUEST_ENTITY_TOO_LARGE
            )
        if self.headers.get_content_type() != "application/json":
            raise WorkerRequestError("Use application/json.", HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise WorkerRequestError("The request body was incomplete.")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise WorkerRequestError("The body must contain valid UTF-8 JSON.") from exc
        if not isinstance(payload, dict):
            raise WorkerRequestError("The JSON body must be an object.")
        return payload

    def do_GET(self) -> None:
        if not self._authenticated():
            return
        try:
            parsed = urlsplit(self.path)
            if parsed.query or parsed.fragment:
                raise WorkerRequestError("Query strings are not supported.", HTTPStatus.NOT_FOUND)
            if parsed.path == "/health":
                state = self.server.state
                self._send(
                    HTTPStatus.OK,
                    {
                        "schema_version": 1,
                        "profile": state.profile,
                        "ready": state.ready,
                        "detail": state.detail,
                        "instance_id": state.instance_id,
                    },
                )
            elif re.fullmatch(r"/jobs/[0-9a-f]{32}", parsed.path):
                self._send(HTTPStatus.OK, self.server.state.get(parsed.path.rsplit("/", 1)[1]))
            else:
                raise WorkerRequestError("Unknown worker route.", HTTPStatus.NOT_FOUND)
        except WorkerRequestError as exc:
            self._send(exc.status, {"detail": str(exc)})

    def do_POST(self) -> None:
        if not self._authenticated():
            return
        try:
            parsed = urlsplit(self.path)
            if parsed.query or parsed.fragment:
                raise WorkerRequestError("Query strings are not supported.", HTTPStatus.NOT_FOUND)
            payload = self._body()
            if parsed.path == "/jobs":
                self._send(HTTPStatus.ACCEPTED, self.server.state.submit(payload))
            elif re.fullmatch(r"/jobs/[0-9a-f]{32}/cancel", parsed.path):
                if payload:
                    raise WorkerRequestError("Cancellation accepts an empty JSON object only.")
                self._send(HTTPStatus.OK, self.server.state.cancel_job(parsed.path.split("/")[2]))
            else:
                raise WorkerRequestError("Unknown worker route.", HTTPStatus.NOT_FOUND)
        except WorkerRequestError as exc:
            self._send(exc.status, {"detail": str(exc)})
        except (TimeoutError, OSError):
            self._send(
                HTTPStatus.REQUEST_TIMEOUT, {"detail": "The request body did not arrive in time."}
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8081)
    arguments = parser.parse_args(argv)
    profile = os.environ.get("DS60_WORKER_PROFILE", "")
    token_file = os.environ.get("DS60_WORKER_TOKEN_FILE", "")
    if not token_file:
        parser.error("DS60_WORKER_TOKEN_FILE must name a private external runtime-session file.")
    try:
        token = read_worker_token(Path(token_file))
        isolated, isolation_detail = probe_isolation(Path(token_file))
        ready, detail = (
            probe_profile(profile, isolate_user=True) if isolated else (False, isolation_detail)
        )
        state = WorkerState(profile, ready=ready, detail=detail)
        server = WorkerHTTPServer((arguments.host, arguments.port), state, token)
    except (OSError, ValueError) as exc:
        print(f"Worker startup refused: {exc}", file=sys.stderr)
        return 2
    print(f"DS60 optional worker {profile}: {detail}", flush=True)

    def stop(signum: int, frame: Any) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
