"""Persist bounded jobs and talk only to explicit private runtime workers."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from ds60sqlpy.modules import MAX_SOURCE_BYTES, ModuleCatalog, ModuleState
from ds60sqlpy.plot_artifacts import read_saved_artifacts, validate_artifacts
from ds60sqlpy.state_files import atomic_json_write, locked_update

SERVICES = {
    "dbt-duckdb": "dbt-worker",
    "data-engineering": "data-engineering-worker",
    "data-platforms-python": "data-platforms-worker",
    "stan-cpu": "stan-worker",
    "julia": "julia-worker",
    "jax-cpu": "jax-worker",
    "bayesian-cpu": "bayesian-worker",
    "r-statistics": "r-worker",
    "php-cli": "php-worker",
    "cuda-cpp": "cuda-cpp-worker",
    "cuda-python": "cuda-python-worker",
    "pytorch-cuda": "pytorch-cuda-worker",
    "tensorflow-cuda": "tensorflow-cuda-worker",
    "python-core": "python-core-worker",
    "cpp20": "cpp-worker",
    "c17": "c-worker",
    "go": "go-worker",
    "csharp-dotnet": "csharp-worker",
    "rust-stable": "rust-worker",
    "swift-linux": "swift-worker",
    "java21": "java-worker",
    "javascript-node": "javascript-worker",
    "typescript-node": "typescript-worker",
    "tensorflow-cpu": "tensorflow-worker",
    "llm-torch-cpu": "llm-worker",
    "scala-jvm": "scala-worker",
    "spark-local-scala": "spark-scala-worker",
    "spark-local-python": "spark-python-worker",
    "k8s-kind": "kubernetes-worker",
}
TERMINAL = frozenset({"succeeded", "failed", "cancelled", "timed_out", "interrupted", "blocked"})
PHASES = TERMINAL | {"queued", "preparing", "compiling", "running", "verifying"}
IDENTIFIER = re.compile(r"[0-9a-f]{32}\Z")
# UTF-8 control characters can expand sixfold in JSON, alongside checks and plots.
MAX_RESPONSE = 2_000_000


class WorkerError(ValueError):
    def __init__(self, detail: str, status: int | None = None) -> None:
        super().__init__(detail)
        self.status = status


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: Any, msg: Any, headers: Any, newurl: Any
    ) -> None:
        return None


class WorkerClient:
    def __init__(self, environment: dict[str, str] | None = None) -> None:
        self.environment = dict(os.environ if environment is None else environment)
        raw = self.environment.get("DS60_MODULE_ENDPOINTS", "").strip() or "{}"
        endpoints = json.loads(raw)
        if not isinstance(endpoints, dict) or not set(endpoints) <= set(SERVICES):
            raise ValueError("Worker endpoints must map registered profiles only.")
        self.endpoints: dict[str, str] = {}
        for profile, value in endpoints.items():
            if not isinstance(value, str):
                raise ValueError("Invalid worker URL.")
            parsed = urlsplit(value)
            if (
                parsed.scheme != "http"
                or parsed.hostname not in {SERVICES[profile], "127.0.0.1", "localhost", "::1"}
                or parsed.username is not None
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
                or not parsed.port
            ):
                raise ValueError(
                    "Worker endpoints require a fixed private service or loopback URL."
                )
            self.endpoints[profile] = value.rstrip("/")
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def call(
        self, profile: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if profile not in SERVICES:
            raise ValueError("Unknown worker profile.")
        secret_path = self.environment.get("DS60_MODULE_TOKEN_FILE")
        if not secret_path or profile not in self.endpoints:
            raise ValueError("Prepare this optional runtime with the module launcher first.")
        token = Path(secret_path).read_text("utf-8").strip()
        if len(token) < 32 or len(token) > 256 or "\n" in token:
            raise ValueError("Invalid private worker session file.")
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            self.endpoints[profile] + path,
            data=data,
            headers={"Content-Type": "application/json", "X-DS60-Worker-Token": token},
        )
        try:
            with self.opener.open(request, timeout=4) as response:
                raw = response.read(MAX_RESPONSE + 1)
                if len(raw) > MAX_RESPONSE:
                    raise ValueError("Worker response exceeded its size limit.")
        except HTTPError as exc:
            raise WorkerError(
                f"Worker rejected the request (HTTP {exc.code}); inspect profile readiness.",
                exc.code,
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ValueError(
                "Worker is unreachable. Prepare/start its profile and retry readiness."
            ) from exc
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("Invalid worker response.")
        return result

    def readiness(self, profile: str) -> dict[str, Any]:
        if profile == "reading":
            return {
                "profile": profile,
                "ready": True,
                "detail": "Reading and written reasoning need no worker.",
            }
        try:
            result = self.call(profile, "/health")
            if (
                result.get("schema_version") != 1
                or result.get("profile") != profile
                or type(result.get("ready")) is not bool
            ):
                raise ValueError("Runtime handshake does not match the selected profile.")
            instance = result.get("instance_id")
            if instance is not None and (
                not isinstance(instance, str) or IDENTIFIER.fullmatch(instance) is None
            ):
                raise ValueError("Invalid worker instance identity.")
            return {
                "profile": profile,
                "ready": result["ready"],
                "detail": str(result.get("detail", ""))[:4000],
                "instance_id": instance,
            }
        except (OSError, ValueError) as exc:
            return {"profile": profile, "ready": False, "detail": str(exc)}


class ModuleJobs:
    def __init__(
        self, catalog: ModuleCatalog, state: ModuleState, client: WorkerClient | None = None
    ) -> None:
        self.catalog, self.state = catalog, state
        self.client = client or WorkerClient()
        self.directory = state.directory / "jobs"
        self.lock = threading.RLock()
        self.active: str | None = None
        self.pending: set[str] = set()
        self.threads: dict[str, threading.Thread] = {}
        self.closed = threading.Event()
        # Recovery only polls an existing worker job; it never re-submits source.
        for path in sorted(self.directory.glob("*.json")) if self.directory.is_dir() else []:
            value = self._read(path.stem)
            if value["status"] not in TERMINAL or value["status"] == "interrupted":
                self._reserve(path.stem)
                self._monitor(path.stem)

    def _reserve(self, key: str) -> None:
        with self.lock:
            self.pending.add(key)
            if self.active is None:
                self.active = key

    def _release(self, key: str) -> None:
        with self.lock:
            self.pending.discard(key)
            if self.active == key:
                self.active = next(iter(sorted(self.pending)), None)

    def _path(self, key: object) -> Path:
        if not isinstance(key, str) or IDENTIFIER.fullmatch(key) is None:
            raise ValueError("Choose a valid module job ID.")
        return self.state.safe_path(self.directory / f"{key}.json")

    def _read(self, key: str) -> dict[str, Any]:
        return self._read_document(key)

    def _read_document(self, key: str, *, for_storage: bool = False) -> dict[str, Any]:
        """Validate stored evidence, projecting only reads intended for display."""
        value = json.loads(self._path(key).read_text("utf-8"))
        if (
            not isinstance(value, dict)
            or value.get("job_id") != key
            or not isinstance(value.get("status"), str)
            or value["status"] not in PHASES
            or not isinstance(value.get("profile"), str)
            or value["profile"] not in SERVICES
        ):
            raise ValueError("Invalid module job receipt; preserve it for recovery.")
        self.catalog.get(value.get("lesson_id"))
        if "withheld_artifacts" in value:
            raise ValueError("Saved jobs cannot contain derived figure-readback metadata.")
        if "artifacts" in value:
            visible, withheld = read_saved_artifacts(value["artifacts"])
            if not for_storage:
                value["artifacts"] = visible
                if withheld:
                    value["withheld_artifacts"] = withheld
        return value

    def _update(self, key: str, change: dict[str, Any]) -> dict[str, Any]:
        path = self._path(key)
        if "withheld_artifacts" in change:
            raise ValueError("Figure-readback metadata cannot be written into a saved job.")
        if "artifacts" in change:
            validate_artifacts(change["artifacts"])
        with self.lock, locked_update(path):
            # Status recovery must retain historical raw artifacts rather than
            # writing a display projection over the original evidence.
            value = self._read_document(key, for_storage=True)
            # A late poll must never revive or replace a resolved attempt.
            if value["status"] in TERMINAL - {"interrupted"}:
                return self._read(key)
            value.update(change)
            value["updated_at"] = datetime.now(UTC).isoformat()
            atomic_json_write(path, value)
        return self._read(key)

    def _snapshot(self, value: dict[str, Any], key: str) -> dict[str, Any]:
        receipt = self._read(key)
        if (
            value.get("job_id") != key
            or value.get("profile") != receipt["profile"]
            or not isinstance(value.get("status"), str)
            or value["status"] not in PHASES
        ):
            raise ValueError("Worker returned an inconsistent job identity or state.")
        output = value.get("output", "")
        if not isinstance(output, str):
            raise ValueError("Invalid worker log.")
        code = value.get("returncode")
        if code is not None and type(code) is not int:
            raise ValueError("Invalid worker exit status.")
        checks = value.get("checks", [])
        if (
            not isinstance(checks, list)
            or len(checks) > 100
            or not all(
                isinstance(c, dict)
                and isinstance(c.get("name"), str)
                and type(c.get("passed")) is bool
                and isinstance(c.get("detail"), str)
                for c in checks
            )
        ):
            raise ValueError("Invalid structured verification results.")
        if value["status"] == "succeeded" and (
            code != 0
            or any(not c["passed"] for c in checks)
            or (receipt["verification_id"] is not None and not checks)
        ):
            raise ValueError("Worker reported success without a successful result.")
        elapsed = value.get("elapsed_seconds", 0)
        if (
            isinstance(elapsed, bool)
            or not isinstance(elapsed, (int, float))
            or not math.isfinite(elapsed)
            or elapsed < 0
        ):
            raise ValueError("Invalid worker duration.")
        return {
            "status": value["status"],
            "output": output.encode()[:128_000].decode("utf-8", errors="replace"),
            "returncode": code,
            "checks": checks,
            "truncated": bool(value.get("truncated")) or len(output.encode()) > 128_000,
            "elapsed_seconds": elapsed,
            "detail": str(value.get("detail", ""))[:4000],
            **(
                {"artifacts": validate_artifacts(value["artifacts"])}
                if "artifacts" in value
                else {}
            ),
        }

    def start(
        self, lesson_id: object, source: object, timeout: object, request_id: object
    ) -> dict[str, Any]:
        lesson = self.catalog.get(lesson_id)
        if lesson.runtime_profile == "dax-offline":
            raise ValueError("Offline DAX drafts cannot create execution jobs.")
        if lesson.runtime_profile == "reading":
            raise ValueError("This is a reading lesson. Save reasoning instead of running it.")
        if (
            not isinstance(source, str)
            or not source.strip()
            or len(source.encode()) > MAX_SOURCE_BYTES
        ):
            raise ValueError("Supply nonempty source of at most 48,000 UTF-8 bytes.")
        if type(timeout) is not int or timeout not in (15, 60, 120):
            raise ValueError("Choose a 15, 60, or 120 second total deadline.")
        self._path(request_id)
        source_hash = hashlib.sha256(source.encode()).hexdigest()
        with self.lock:
            if self.closed.is_set():
                raise ValueError("The module service is closing.")
            if self._path(request_id).exists():
                previous = self._read(str(request_id))
                if (
                    previous["lesson_id"] != lesson.id
                    or previous["source_sha256"] != source_hash
                    or previous["timeout_seconds"] != timeout
                ):
                    raise ValueError(
                        "This request ID already identifies different source or limits."
                    )
                return previous
            if self.pending:
                raise ValueError(
                    "A module job is active or unresolved. Wait, reconnect, or cancel it."
                )
            self.state.save(lesson.id, {"source": source})
            ready = self.client.readiness(lesson.runtime_profile)
            if not ready["ready"]:
                raise ValueError(ready["detail"])
            key = str(request_id)
            value: dict[str, Any] = {
                "schema_version": 1,
                "job_id": key,
                "lesson_id": lesson.id,
                "profile": lesson.runtime_profile,
                "source_sha256": source_hash,
                "source": source,
                "timeout_seconds": timeout,
                "verification_id": lesson.verification_id,
                "worker_instance_id": ready.get("instance_id"),
                "status": "queued",
                "output": "",
                "returncode": None,
                "checks": [],
                "truncated": False,
                "elapsed_seconds": 0,
                "detail": "Submitting to the prepared private worker.",
                "created_at": datetime.now(UTC).isoformat(),
            }
            with locked_update(self._path(key)):
                atomic_json_write(self._path(key), value)
            self._reserve(key)
            try:
                remote = self.client.call(
                    lesson.runtime_profile,
                    "/jobs",
                    {
                        "job_id": key,
                        "profile": lesson.runtime_profile,
                        "operation": "execute",
                        "source": source,
                        "language": lesson.language,
                        "timeout_seconds": timeout,
                        "verification_id": lesson.verification_id,
                    },
                )
                self._update(key, self._snapshot(remote, key))
            except (OSError, ValueError) as exc:
                self._update(
                    key,
                    {
                        "status": "interrupted",
                        "detail": (
                            f"Submission outcome is uncertain; source was saved. "
                            f"Inspect the worker before retrying. {exc}"
                        ),
                    },
                )
                self._monitor(key)
                return self._read(key)
            self._monitor(key)
            return self._read(key)

    def _monitor(self, key: str) -> None:
        def poll() -> None:
            try:
                receipt = self._read(key)
                deadline = time.monotonic() + receipt["timeout_seconds"] + 20
                cancel_deadline: float | None = None
                while receipt["status"] not in TERMINAL and not self.closed.is_set():
                    if time.monotonic() >= deadline and cancel_deadline is None:
                        remote = self.client.call(receipt["profile"], f"/jobs/{key}/cancel", {})
                        change = self._snapshot(remote, key)
                        if change["status"] == "cancelled":
                            change.update(
                                status="timed_out",
                                detail="Controller deadline exceeded; worker confirmed cleanup.",
                            )
                        receipt = self._update(key, change)
                        cancel_deadline = time.monotonic() + 8
                    if cancel_deadline is not None and time.monotonic() >= cancel_deadline:
                        raise ValueError("Worker did not confirm cleanup after cancellation.")
                    if receipt["status"] not in TERMINAL:
                        remote = self.client.call(receipt["profile"], f"/jobs/{key}")
                        change = self._snapshot(remote, key)
                        if cancel_deadline is not None and change["status"] == "cancelled":
                            change.update(
                                status="timed_out",
                                detail="Controller deadline exceeded; worker confirmed cleanup.",
                            )
                        receipt = self._update(key, change)
                    if receipt["status"] not in TERMINAL:
                        self.closed.wait(0.4)
            except (OSError, ValueError) as exc:
                self._update(
                    key,
                    {
                        "status": "interrupted",
                        "detail": f"Worker status unavailable; no source was replayed. {exc}",
                    },
                )
            finally:
                with self.lock:
                    receipt = self._read(key)
                    if receipt["status"] in TERMINAL - {"interrupted"}:
                        self._release(key)
                    self.threads.pop(key, None)

        with self.lock:
            if self.closed.is_set():
                return
            receipt = self._read(key)
            if receipt["status"] in TERMINAL - {"interrupted"}:
                self._release(key)
                return
            previous = self.threads.get(key)
            if previous is not None and previous.is_alive():
                return
            self.threads.pop(key, None)
            thread: threading.Thread | None = None
            try:
                thread = threading.Thread(target=poll, name=f"ds60-module-{key}", daemon=True)
                self.threads[key] = thread
                thread.start()
            except RuntimeError:
                if thread is not None and self.threads.get(key) is thread:
                    self.threads.pop(key, None)
                self._reserve(key)
                receipt = self._update(
                    key,
                    {
                        "status": "interrupted",
                        "detail": (
                            "Local status monitoring could not start; the worker outcome "
                            "remains unconfirmed. Source was saved and was not replayed. "
                            "Reconnect the saved job when local resources are available."
                        ),
                    },
                )
                if receipt["status"] in TERMINAL - {"interrupted"}:
                    self._release(key)

    def get(self, key: object) -> dict[str, Any]:
        self._path(key)
        identity = str(key)
        receipt = self._read(identity)
        if receipt["status"] == "interrupted":
            self._reserve(identity)
            try:
                remote = self.client.call(receipt["profile"], f"/jobs/{identity}")
                receipt = self._update(identity, self._snapshot(remote, identity))
            except (OSError, ValueError) as exc:
                if (
                    isinstance(exc, WorkerError)
                    and exc.status == 404
                    and receipt["profile"] != "k8s-kind"
                ):
                    ready = self.client.readiness(receipt["profile"])
                    previous = receipt.get("worker_instance_id")
                    replacement = ready.get("instance_id")
                    if (
                        ready.get("ready") is True
                        and isinstance(previous, str)
                        and isinstance(replacement, str)
                        and previous != replacement
                    ):
                        receipt = self._update(
                            identity,
                            {
                                "status": "failed",
                                "detail": (
                                    "The prepared worker was replaced; the previous result is "
                                    "unavailable. Source was retained and was not replayed."
                                ),
                                "recovery": {
                                    "type": "confirmed-new-worker-instance",
                                    "previous": previous,
                                    "replacement": replacement,
                                },
                            },
                        )
        with self.lock:
            # A monitor may have published a terminal receipt since the first
            # read. Monitoring can also synchronously record an admission failure.
            # Reconcile reservations against the same final snapshot we return.
            receipt = self._read(identity)
            if receipt["status"] not in TERMINAL and not self.closed.is_set():
                self._reserve(identity)
                if identity not in self.threads:
                    self._monitor(identity)
            receipt = self._read(identity)
            if receipt["status"] in TERMINAL - {"interrupted"}:
                self._release(identity)
            elif not self.closed.is_set():
                self._reserve(identity)
            return receipt

    def recover(self, key: object, confirmation: object) -> dict[str, Any]:
        receipt = self.get(key)
        if receipt["status"] != "interrupted":
            return receipt
        required = "CLUSTER RELEASED" if receipt["profile"] == "k8s-kind" else "WORKER RESTARTED"
        if confirmation != required:
            raise ValueError(f"After completing owned infrastructure recovery, type {required}.")
        identity = receipt["job_id"]
        result = self._update(
            identity,
            {
                "status": "failed",
                "detail": (
                    "The operator confirmed infrastructure recovery. The old result and cleanup "
                    "were not independently verified; source was preserved and no job was "
                    "replayed."
                ),
                "recovery": {
                    "type": "operator-confirmed",
                    "confirmation": required,
                    "at": datetime.now(UTC).isoformat(),
                },
            },
        )
        self._release(identity)
        return result

    def history(self, lesson_id: object) -> list[dict[str, Any]]:
        lesson = self.catalog.get(lesson_id)
        records = (
            [self._read(path.stem) for path in self.directory.glob("*.json")]
            if self.directory.is_dir()
            else []
        )
        return sorted(
            (r for r in records if r["lesson_id"] == lesson.id),
            key=lambda r: r["created_at"],
            reverse=True,
        )[:30]

    def cancel(self, key: object) -> dict[str, Any]:
        receipt = self.get(key)
        if receipt["status"] in TERMINAL - {"interrupted"}:
            return receipt
        result = self.client.call(receipt["profile"], f"/jobs/{receipt['job_id']}/cancel", {})
        return self._update(receipt["job_id"], self._snapshot(result, receipt["job_id"]))

    def close(self) -> None:
        self.closed.set()
        with self.lock:
            outstanding = list(self.pending)
        for identity in outstanding:
            try:
                self.cancel(identity)
            except (OSError, ValueError):
                self._update(
                    identity,
                    {
                        "status": "interrupted",
                        "detail": (
                            "App closed; cleanup was not confirmed. Inspect the owned worker."
                        ),
                    },
                )
        with self.lock:
            threads = list(self.threads.values())
        for thread in threads:
            if thread.ident is not None and thread is not threading.current_thread():
                thread.join(timeout=5)


def profile_readiness(client: WorkerClient, profiles: set[str]) -> list[dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(client.readiness, sorted(profiles)))
