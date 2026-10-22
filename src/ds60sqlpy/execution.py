"""Bounded, explicit local backend execution for the coding-pad application.

This is a trusted local programming environment, not a security sandbox.
The ordinary portal and the MCP adapter do not expose these operations.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import unquote, urlsplit

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.runtime_environment import (
    external_dll_directory as external_dll_directory,
)
from ds60sqlpy.runtime_environment import (
    external_program_environment as external_program_environment,
)
from ds60sqlpy.sql_notebook import (
    SqlNotebookError,
    course_psql_environment,
    validate_course_database_target,
)
from ds60sqlpy.sql_runner import default_course_database_url
from ds60sqlpy.state_files import locked_update

MAX_CODE_BYTES = 60_000
MAX_OUTPUT_BYTES = 128_000


def matplotlib_cache_environment(repo_root: Path) -> dict[str, str]:
    """Share the platform-specific font cache across lessons and app restarts."""

    learning = repo_root / ".learning"
    cache = learning / "cache" / "matplotlib" / sys.platform
    if not cache.resolve().is_relative_to(learning.resolve()):
        raise ValueError("The Matplotlib cache must remain inside .learning/cache/.")
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    return {"MPLBACKEND": "Agg", "MPLCONFIGDIR": str(cache)}


# On Windows the parent assigns a Job Object before releasing this gate. A
# short-lived learner program cannot exit before its descendants are tracked.
WORKER_GATE = r"""
import os, time
while not os.path.isfile(os.environ["DS60_PAD_READY"]):
    time.sleep(0.01)
"""

PYTHON_WORKER = (
    WORKER_GATE
    + r"""
import runpy, sys
from pathlib import Path
try:
    runpy.run_path(sys.argv[1], run_name="__main__")
finally:
    pyplot = sys.modules.get("matplotlib.pyplot")
    if pyplot is not None:
        for index, number in enumerate(pyplot.get_fignums()[:4], 1):
            pyplot.figure(number).savefig(Path(sys.argv[2]) / f"figure-{index}.png")
        pyplot.close("all")
"""
)

SQL_WORKER = (
    WORKER_GATE
    + r"""
import json, sys
from pathlib import Path
try:
    import psycopg
except ImportError:
    print(json.dumps({"error_type": "ImportError", "sqlstate": None,
        "message": "Install the Core/bridge profile in the selected Python backend."}))
    sys.exit(1)

query = Path(sys.argv[1]).read_text(encoding="utf-8")
class CourseRoleError(ValueError):
    pass

try:
    with psycopg.connect("",
            options="-c statement_timeout=5000 -c lock_timeout=2000") as conn:
        if conn.info.dbname != "advanced_sql_training":
            raise ValueError("The SQL pad requires the disposable course database.")
        privileged = conn.execute('''
            SELECT rolsuper OR rolcreaterole OR rolcreatedb
                OR pg_catalog.pg_has_role(current_user, 'pg_execute_server_program', 'MEMBER')
                OR pg_catalog.pg_has_role(current_user, 'pg_read_server_files', 'MEMBER')
                OR pg_catalog.pg_has_role(current_user, 'pg_write_server_files', 'MEMBER')
                OR EXISTS (
                    SELECT 1 FROM pg_catalog.pg_roles elevated
                    WHERE (elevated.rolsuper OR elevated.rolcreaterole OR elevated.rolcreatedb)
                        AND pg_catalog.pg_has_role(current_user, elevated.oid, 'MEMBER')
                )
            FROM pg_catalog.pg_roles WHERE rolname = current_user
        ''').fetchone()
        if not privileged or privileged[0]:
            raise CourseRoleError(
                "SQL pads require a limited course login. See docs/offline-app.md for role setup."
            )
        Path(os.environ["DS60_PAD_BACKEND_PID"]).write_text(str(conn.info.backend_pid))
        with conn.cursor() as cur:
            cur.execute(query, prepare=False)
            results = []
            while True:
                if cur.description:
                    rows = cur.fetchmany(101)
                    results.append({"columns": [d.name for d in cur.description],
                        "rows": rows[:100], "truncated": len(rows) > 100})
                else:
                    results.append({"status": cur.statusmessage})
                if not cur.nextset():
                    break
    print(json.dumps({"results": results,
        "transaction": "Committed success; explicit COMMIT/ROLLBACK change boundaries."},
        default=str))
except Exception as exc:
    print(json.dumps({"error_type": type(exc).__name__,
        "sqlstate": getattr(exc, "sqlstate", None),
        "message": str(exc).splitlines()[0] if isinstance(exc, CourseRoleError)
            or isinstance(exc, psycopg.Error) and getattr(exc, "sqlstate", None)
            else "SQL backend unavailable or input rejected.",
        "transaction": "Current transaction rolled back; earlier explicit commits are preserved."}))
    sys.exit(1)
"""
)

SQL_CANCEL = r"""
import sys
import psycopg

with psycopg.connect("", connect_timeout=1,
        options="-c statement_timeout=1000 -c lock_timeout=1000") as connection:
    connection.execute('''
        SELECT pg_catalog.pg_cancel_backend(pid)
        FROM pg_catalog.pg_stat_activity
        WHERE pid = %s AND usename = current_user
            AND datname = 'advanced_sql_training'
            AND application_name = 'ds60-coding-pad'
    ''', (int(sys.argv[1]),))
"""


class _WindowsJob:
    """Own a Windows process tree, including descendants after the parent exits."""

    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_longlong),
                ("job_time", ctypes.c_longlong),
                ("flags", wintypes.DWORD),
                ("min_working_set", ctypes.c_size_t),
                ("max_working_set", ctypes.c_size_t),
                ("active_processes", wintypes.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", wintypes.DWORD),
                ("scheduling", wintypes.DWORD),
            ]

        class IoCounters(ctypes.Structure):
            _fields_ = [
                (name, ctypes.c_ulonglong)
                for name in (
                    "read_ops",
                    "write_ops",
                    "other_ops",
                    "read_bytes",
                    "write_bytes",
                    "other_bytes",
                )
            ]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [
                ("basic", BasicLimits),
                ("io", IoCounters),
                ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t),
                ("peak_process_memory", ctypes.c_size_t),
                ("peak_job_memory", ctypes.c_size_t),
            ]

        windows_library = getattr(ctypes, "WinDLL")  # noqa: B009
        self.kernel = windows_library("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError("Could not create a Windows backend process job.")
        limits = ExtendedLimits()
        limits.basic.flags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(
            self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            self.close()
            raise OSError("Could not set backend process-tree cleanup limits.")

    def assign(self, process: subprocess.Popen[bytes]) -> None:
        if not self.kernel.AssignProcessToJobObject(self.handle, int(getattr(process, "_handle"))):  # noqa: B009
            raise OSError("Could not contain the Windows backend process tree.")

    def close(self) -> None:
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


@dataclass(frozen=True, slots=True)
class PadResult:
    """An execution transcript with bounded output and an explicit stop reason."""

    language: str
    returncode: int
    output: str
    elapsed_seconds: float
    stopped: str | None


class PadRunner:
    """Run only explicit pad submissions using a supported local interpreter."""

    def __init__(self, catalog: Catalog, *, python: str | None = None, timeout: float = 15) -> None:
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("The backend time limit must be positive and finite.")
        self.catalog = catalog
        self.python = self._discover_python(catalog.repo_root, configured=python)
        if python is not None and self.python is None:
            raise ValueError("The selected backend must be a usable Python 3.11-3.12 interpreter.")
        self.timeout = timeout
        self._lock = threading.RLock()

    @staticmethod
    def _discover_python(
        repo_root: Path | None = None, *, configured: str | None = None
    ) -> str | None:
        explicit = configured or os.environ.get("DS60_PYTHON")
        candidates: list[list[str]] = []
        if explicit:
            candidates.append([shutil.which(explicit) or explicit])
        else:
            if not getattr(sys, "frozen", False):
                candidates.append([sys.executable])
            if repo_root is not None:
                candidates.extend(
                    [
                        [str(repo_root / relative)]
                        for relative in (
                            ".venv/Scripts/python.exe",
                            ".venv/python.exe",
                            ".venv/bin/python",
                        )
                    ]
                )
            candidates.extend(
                [
                    [path]
                    for name in ("python3.12", "python3.11", "python3", "python")
                    if (path := shutil.which(name))
                ]
            )
            if os.name == "nt" and (launcher := shutil.which("py")):
                candidates.extend([[launcher, version] for version in ("-3.12", "-3.11")])
        probe = (
            "import json,sys; print(json.dumps({'version':list(sys.version_info[:2]),"
            "'executable':sys.executable}))"
        )
        for candidate in candidates:
            try:
                with external_dll_directory():
                    result = subprocess.run(
                        [*candidate, "-I", "-c", probe],
                        stdin=subprocess.DEVNULL,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=4,
                        env=external_program_environment(),
                    )
                payload = json.loads(result.stdout)
                if result.returncode == 0 and payload["version"] in ([3, 11], [3, 12]):
                    executable = payload["executable"]
                    if isinstance(executable, str) and Path(executable).is_file():
                        # Preserve .venv symlinks: resolving them selects the base
                        # interpreter and discards the environment's packages.
                        return os.path.abspath(executable)  # noqa: PTH100
            except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired):
                continue
        return None

    def read(self, lesson_id: str, language: Literal["python", "sql"]) -> str:
        """Read only the named lesson's saved pad, never an arbitrary file."""

        with self._lock:
            path = self._path(lesson_id, language)
            if path.exists() and path.stat().st_size > MAX_CODE_BYTES:
                raise ValueError("Saved pad exceeds the size limit. Preserve it before repairing.")
            return path.read_text(encoding="utf-8") if path.exists() else ""

    def saved(self, lesson_id: str, language: Literal["python", "sql"]) -> bool:
        """Distinguish an intentionally empty saved pad from an unsaved pad."""

        with self._lock:
            return self._path(lesson_id, language).is_file()

    def history(
        self, lesson_id: str, language: Literal["python", "sql"], *, limit: int = 10
    ) -> list[dict[str, Any]]:
        """List recent content-addressed backups without deleting older learner work."""

        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError("History page size must be between 1 and 50.")
        with self._lock:
            path = self._path(lesson_id, language)
            directory = self._history_directory(path)
            pattern = re.compile(rf"practice-([a-f0-9]{{64}}){re.escape(path.suffix)}")
            backups = [
                item
                for item in directory.glob(f"practice-*{path.suffix}")
                if not item.is_symlink() and item.is_file() and pattern.fullmatch(item.name)
            ]
            backups.sort(key=lambda item: item.stat().st_mtime_ns, reverse=True)
            return [
                {
                    "id": item.stem.removeprefix("practice-"),
                    "saved_at": datetime.fromtimestamp(item.stat().st_mtime, UTC).isoformat(),
                    "bytes": item.stat().st_size,
                }
                for item in backups[:limit]
            ]

    def read_history(
        self, lesson_id: str, language: Literal["python", "sql"], history_id: str
    ) -> str:
        """Read one verified backup by digest, never a caller-supplied path."""

        if not isinstance(history_id, str) or re.fullmatch(r"[a-f0-9]{64}", history_id) is None:
            raise ValueError("Choose a saved history ID.")
        with self._lock:
            path = self._path(lesson_id, language)
            backup = self._history_directory(path) / f"practice-{history_id}{path.suffix}"
            if backup.is_symlink() or not backup.is_file():
                raise ValueError("That pad backup is unavailable.")
            if backup.stat().st_size > MAX_CODE_BYTES:
                raise ValueError(
                    "The pad backup exceeds the size limit; preserve it before repair."
                )
            content = backup.read_bytes()
            if hashlib.sha256(content).hexdigest() != history_id:
                raise ValueError("The pad backup has changed; preserve it before repair.")
            return content.decode("utf-8")

    @staticmethod
    def _history_directory(path: Path) -> Path:
        directory = path.parent / "history"
        if not directory.resolve().is_relative_to(path.parent.resolve()):
            raise ValueError("Pad history must remain inside the lesson's saved-work directory.")
        return directory

    def save(self, lesson_id: str, language: Literal["python", "sql"], code: str) -> Path:
        """Save a learner's explicit submission beneath ignored .learning/pads/."""

        if not isinstance(code, str) or len(code.encode("utf-8")) > MAX_CODE_BYTES:
            raise ValueError(f"Pad input must be text of at most {MAX_CODE_BYTES} UTF-8 bytes.")
        path = self._path(lesson_id, language)
        with self._lock, locked_update(path):
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                if path.stat().st_size > MAX_CODE_BYTES:
                    raise ValueError("Saved pad exceeds the size limit. Preserve it before repair.")
                previous = path.read_bytes()
                if previous != code.encode("utf-8"):
                    directory = self._history_directory(path)
                    directory.mkdir(parents=True, exist_ok=True)
                    digest = hashlib.sha256(previous).hexdigest()
                    backup = directory / f"practice-{digest}{path.suffix}"
                    if backup.is_symlink():
                        raise ValueError("Pad history cannot replace a symbolic link.")
                    if not backup.exists():
                        backup.write_bytes(previous)
                    elif backup.stat().st_size > MAX_CODE_BYTES or backup.read_bytes() != previous:
                        raise ValueError("The pad backup has changed; preserve it before repair.")
                    backup.touch()
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    newline="\n",
                    dir=path.parent,
                    prefix=f".{path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as output:
                    temporary = Path(output.name)
                    output.write(code)
                    output.flush()
                    os.fsync(output.fileno())
                temporary.replace(path)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            return path

    def run(self, lesson_id: str, language: Literal["python", "sql"], code: str) -> dict[str, Any]:
        """Save, execute, and bound one trusted local code submission."""

        if self.python is None:
            raise ValueError("Install Python 3.12, then set DS60_PYTHON to its executable path.")
        path = self.save(lesson_id, language, code)
        snapshot = None
        try:
            # A concurrent explicit save may change practice.py after this Run
            # was requested. Execute the submitted bytes, not that mutable file.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=".submission-",
                suffix=path.suffix,
                delete=False,
            ) as source:
                snapshot = Path(source.name)
                source.write(code)
            result = self._run_snapshot(snapshot, language)
            return {**result, "source_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest()}
        finally:
            if snapshot is not None:
                snapshot.unlink(missing_ok=True)

    def _run_snapshot(self, path: Path, language: Literal["python", "sql"]) -> dict[str, Any]:
        assert self.python is not None
        environment = external_program_environment()
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["PYTHONUTF8"] = "1"
        if language == "python":
            environment["PYTHONPATH"] = os.pathsep.join(
                (str(self.catalog.repo_root), str(self.catalog.repo_root / "src"))
            )
            environment.update(matplotlib_cache_environment(self.catalog.repo_root))
            with tempfile.TemporaryDirectory(prefix="figures-", dir=path.parent) as figures:
                command = [self.python, "-u", "-c", PYTHON_WORKER, str(path), figures]
                result = self._execute(command, environment, language)
                images = []
                for figure in sorted(Path(figures).glob("figure-*.png"))[:4]:
                    if figure.is_symlink() or figure.stat().st_size > 2_000_000:
                        continue
                    data = figure.read_bytes()
                    if data.startswith(b"\x89PNG\r\n\x1a\n"):
                        images.append("data:image/png;base64," + base64.b64encode(data).decode())
            return {**asdict(result), "figures": images}
        try:
            target = validate_course_database_target(
                os.environ.get("DS60_DATABASE_URL") or default_course_database_url()
            )
        except SqlNotebookError as exc:
            raise ValueError(str(exc)) from exc
        database_environment = course_psql_environment(
            target, application_name="ds60-coding-pad", connect_timeout=5
        )
        # Keep sanitized loader settings while retaining only the validated
        # libpq routing/authentication variables selected by the shared helper.
        for name in tuple(environment):
            if name.startswith("PG") and name not in database_environment:
                environment.pop(name, None)
        environment.update(
            {name: value for name, value in database_environment.items() if name.startswith("PG")}
        )
        command = [self.python, "-I", "-u", "-c", SQL_WORKER, str(path)]
        return asdict(self._execute(command, environment, language))

    def _path(self, lesson_id: str, language: str) -> Path:
        self.catalog.get(lesson_id)
        if language not in {"python", "sql"}:
            raise ValueError("Choose the Python or SQL pad.")
        suffix = "py" if language == "python" else "sql"
        root = self.catalog.repo_root / ".learning" / "pads"
        path = root / lesson_id / f"practice.{suffix}"
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("The saved pad must remain inside .learning/pads/.")
        return path

    @staticmethod
    def _redact(transcript: str, environment: dict[str, str]) -> str:
        secrets = {environment.get("PGPASSWORD", "")}
        public_passwords: set[str] = set()
        if (
            environment.get("PGDATABASE") == "advanced_sql_training"
            and environment.get("PGHOST") in {"localhost", "127.0.0.1", "::1"}
            and environment.get("PGUSER") in {"admin", "ds60"}
            and environment.get("PGPASSWORD") == environment.get("PGUSER")
        ):
            public_passwords.add(environment["PGPASSWORD"])
        target = environment.get("DS60_DATABASE_URL", "")
        if target:
            # Replace the complete URL even when it carries no password, keeping
            # connection settings out of execution transcripts.
            transcript = transcript.replace(target, "[redacted database URL]")
            with contextlib.suppress(ValueError, SqlNotebookError):
                parsed = urlsplit(target)
                password = parsed.password
                if password:
                    secrets.update((password, unquote(password)))
                    validate_course_database_target(target)
                    if (
                        parsed.scheme in {"postgresql", "postgres"}
                        and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
                        and parsed.path == "/advanced_sql_training"
                        and parsed.username in {"admin", "ds60"}
                        and unquote(password) == parsed.username
                    ):
                        public_passwords.update((password, unquote(password)))
        # Public course defaults are documented fixtures. Redacting the word
        # "admin" would corrupt legitimate usernames, column names, and results.
        for secret in sorted(secrets - {""} - public_passwords, key=len, reverse=True):
            transcript = transcript.replace(secret, "[redacted]")
        return transcript

    def _execute(self, command: list[str], environment: dict[str, str], language: str) -> PadResult:
        started = time.monotonic()
        stopped = None
        captured = bytearray()
        output_limit = threading.Event()
        job = _WindowsJob() if os.name == "nt" else None
        assigned = False
        process: subprocess.Popen[bytes] | None = None
        reader: threading.Thread | None = None
        with tempfile.TemporaryDirectory(prefix="ds60-pad-gate-") as gate:
            environment = {
                **environment,
                "DS60_PAD_READY": str(Path(gate) / "ready"),
                "DS60_PAD_BACKEND_PID": str(Path(gate) / "backend-pid"),
            }
            try:
                with external_dll_directory():
                    process = subprocess.Popen(
                        command,
                        cwd=self.catalog.repo_root,
                        env=environment,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        start_new_session=os.name != "nt",
                        creationflags=0x00000200 if os.name == "nt" else 0,
                    )
                if job:
                    job.assign(process)
                    assigned = True
                Path(environment["DS60_PAD_READY"]).touch()
                pipe = process.stdout
                assert pipe is not None

                def capture() -> None:
                    while chunk := pipe.read(8192):
                        remaining = MAX_OUTPUT_BYTES - len(captured)
                        captured.extend(chunk[:remaining])
                        if len(chunk) > remaining:
                            output_limit.set()
                            return

                reader = threading.Thread(target=capture, daemon=True)
                reader.start()
                while process.poll() is None:
                    if output_limit.is_set():
                        stopped = "output limit"
                        break
                    if time.monotonic() - started > self.timeout:
                        stopped = "time limit"
                        break
                    time.sleep(0.01)
            finally:
                if stopped and language == "sql":
                    self._cancel_sql(environment)
                if job:
                    job.close()
                if process is not None:
                    if os.name != "nt" or (process.poll() is None and not assigned):
                        self._stop(process)
                    elif process.poll() is None:
                        process.kill()
                    process.wait(timeout=5)
                    if reader:
                        reader.join(timeout=2)
                    if process.stdout is not None and (reader is None or not reader.is_alive()):
                        process.stdout.close()
        assert process is not None
        if output_limit.is_set():
            stopped = stopped or "output limit"
        transcript = self._redact(captured.decode("utf-8", errors="replace"), environment)
        encoded = transcript.encode("utf-8")
        if len(encoded) > MAX_OUTPUT_BYTES:
            stopped = stopped or "output limit"
            transcript = encoded[:MAX_OUTPUT_BYTES].decode("utf-8", errors="ignore")
        return PadResult(
            language, process.returncode, transcript, round(time.monotonic() - started, 3), stopped
        )

    def _cancel_sql(self, environment: dict[str, str]) -> None:
        """Cancel only this pad's registered local PostgreSQL session, boundedly."""

        if self.python is None:
            return
        try:
            pid = Path(environment["DS60_PAD_BACKEND_PID"]).read_text(encoding="utf-8")
            if not pid.isdecimal() or len(pid) > 10:
                return
            cancel_environment = {**environment, "PGAPPNAME": "ds60-coding-pad-cancel"}
            with external_dll_directory():
                subprocess.run(
                    [self.python, "-I", "-c", SQL_CANCEL, pid],
                    env=cancel_environment,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                    check=False,
                )
        except (OSError, ValueError, subprocess.TimeoutExpired):
            # Worker/tree cleanup still runs. PostgreSQL's independent 5-second
            # statement timeout bounds a query if the cancel connection fails.
            return

    @staticmethod
    def _stop(process: subprocess.Popen[bytes]) -> None:
        if os.name == "nt":
            # The Job Object normally performs tree cleanup. This fallback is
            # used only if setup failed before assignment.
            with contextlib.suppress(OSError, subprocess.TimeoutExpired):
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True,
                    check=False,
                    timeout=5,
                )
        else:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
        if process.poll() is None:
            process.kill()
