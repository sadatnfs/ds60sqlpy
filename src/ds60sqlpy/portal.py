"""Loopback-only learning portal with safe progress and launch actions."""

from __future__ import annotations

import json
import mimetypes
import os
import secrets
import shutil
import subprocess
import sys
import webbrowser
from dataclasses import asdict, dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Any, cast
from urllib.parse import unquote, urlsplit

from ds60sqlpy.catalog import Catalog, Lesson
from ds60sqlpy.doctor import diagnose
from ds60sqlpy.progress import ProgressStore
from ds60sqlpy.sql_notebook import (
    SqlArtifactKind,
    SqlNotebookError,
    generate_sql_notebook,
)

MAX_REQUEST_BYTES = 64 * 1024
BLOCKED_PARTS = {
    ".git",
    ".learning",
    ".mypy_cache",
    ".playwright-cli",
    ".pytest_cache",
    ".ruff_cache",
    ".serena",
    ".venv",
    "__pycache__",
    "artifacts",
    "htmlcov",
    "mlruns",
    "node_modules",
}
BLOCKED_NAMES = {
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "pgpass.conf",
}
BLOCKED_SUFFIXES = {".jks", ".key", ".p12", ".pem", ".pfx"}


class PortalError(RuntimeError):
    """A safe, learner-facing portal failure."""


@dataclass(frozen=True, slots=True)
class Launch:
    """One allowlisted process launched by the portal."""

    action: str
    command: tuple[str, ...]
    process_id: int


class PortalLauncher:
    """Resolve and launch only known VS Code and Jupyter actions."""

    def __init__(self, catalog: Catalog, *, enabled: bool = True) -> None:
        self.catalog = catalog
        self.enabled = enabled

    def command(
        self,
        action: str,
        *,
        lesson_id: str | None = None,
        artifact: str = "lesson",
        solution_index: int = 0,
    ) -> tuple[str, ...]:
        """Build an allowlisted command without executing it."""

        if action == "open-repo":
            return (self._code_executable(), str(self.catalog.repo_root))
        if action in {"open-lesson", "open-artifact"}:
            if lesson_id is None:
                raise PortalError("Choose a lesson before opening it in VS Code.")
            lesson = self.catalog.get(lesson_id)
            target = self._lesson_artifact(
                lesson,
                artifact,
                solution_index=solution_index,
            )
            return (
                self._code_executable(),
                "--reuse-window",
                str(self.catalog.repo_root),
                "--goto",
                str(target),
            )
        if action == "jupyter-lesson":
            if lesson_id is None:
                raise PortalError("Choose a notebook lesson before launching JupyterLab.")
            lesson = self.catalog.get(lesson_id)
            target = self._lesson_artifact(
                lesson,
                artifact,
                solution_index=solution_index,
            )
            if target.suffix.lower() != ".ipynb":
                raise PortalError(
                    f"{lesson.id} uses {target.suffix or 'a non-notebook artifact'}; "
                    "open it in VS Code instead."
                )
            return (*self._python_command(), "-m", "jupyterlab", str(target))
        if action == "jupyter-python":
            target = self.catalog.repo_root / "python" / "ds-60day" / "notebooks"
            return (*self._python_command(), "-m", "jupyterlab", str(target))
        if action == "jupyter-sql":
            if lesson_id is not None:
                if artifact not in {"lesson", "solution"}:
                    raise PortalError(
                        "Guided SQL notebooks support only lesson or solution artifacts."
                    )
                if solution_index < 1:
                    raise PortalError("Guided SQL notebooks use a one-based solution index.")
                try:
                    workspace = generate_sql_notebook(
                        self.catalog,
                        lesson_id,
                        cast(SqlArtifactKind, artifact),
                        solution_index,
                    )
                except SqlNotebookError as exc:
                    raise PortalError(str(exc)) from exc
                return (
                    *self._python_command(),
                    "-m",
                    "jupyterlab",
                    str(workspace.notebook_path),
                )
            target = self.catalog.repo_root / "bridge" / "professional" / "notebooks"
            return (*self._python_command(), "-m", "jupyterlab", str(target))
        raise PortalError(f"Unsupported portal action: {action}")

    def launch(
        self,
        action: str,
        *,
        lesson_id: str | None = None,
        artifact: str = "lesson",
        solution_index: int = 0,
    ) -> Launch:
        """Launch one allowlisted action and return its process metadata."""

        if not self.enabled:
            raise PortalError("Native launches are disabled for this portal session.")
        command = self.command(
            action,
            lesson_id=lesson_id,
            artifact=artifact,
            solution_index=solution_index,
        )
        kwargs: dict[str, Any] = {
            "cwd": self.catalog.repo_root,
            "stdin": subprocess.DEVNULL,
        }
        if os.name == "nt":
            kwargs["creationflags"] = int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        else:
            kwargs["start_new_session"] = True
        try:
            process = subprocess.Popen(command, **kwargs)
        except OSError as exc:
            raise PortalError(f"Could not launch {action}: {exc}") from exc
        return Launch(action=action, command=command, process_id=process.pid)

    def _lesson_artifact(
        self,
        lesson: Lesson,
        artifact: str,
        *,
        solution_index: int = 0,
    ) -> Path:
        paths = {
            "lesson": lesson.lesson_path,
            "guide": lesson.guide_path,
        }
        if artifact == "solution":
            if not lesson.solution_paths:
                raise PortalError(f"{lesson.id} has no cataloged solution artifact.")
            if not 0 <= solution_index < len(lesson.solution_paths):
                raise PortalError(
                    f"{lesson.id} has {len(lesson.solution_paths)} solution artifact(s); "
                    f"solution index {solution_index} is unavailable."
                )
            relative = lesson.solution_paths[solution_index]
        else:
            try:
                relative = paths[artifact]
            except KeyError as exc:
                raise PortalError(f"Unsupported lesson artifact: {artifact}") from exc
        target = self.catalog.resolve(relative)
        if not target.is_file():
            raise PortalError(f"Cataloged artifact is missing: {relative}")
        return target

    def _python_command(self) -> tuple[str, ...]:
        candidates = (
            self.catalog.repo_root / ".venv" / "Scripts" / "python.exe",
            self.catalog.repo_root / ".venv" / "python.exe",
            self.catalog.repo_root / ".venv" / "bin" / "python",
        )
        for candidate in candidates:
            if candidate.is_file():
                return (str(candidate),)
        raise PortalError(
            "The repository .venv is missing. Complete setup before launching Jupyter."
        )

    @staticmethod
    def _native_code_path(candidate: str | Path) -> str | None:
        """Resolve a VS Code command shim to a directly launchable executable."""

        path = Path(candidate)
        if path.suffix.lower() in {".bat", ".cmd"}:
            # A normal Windows VS Code installation puts bin\code.cmd beside
            # the parent Code.exe. The portal never invokes a command shell, so
            # return the native executable rather than the batch shim.
            for executable in (
                path.parent.parent / "Code.exe",
                path.parent / "Code.exe",
            ):
                if executable.is_file():
                    return str(executable)
            return None
        if path.is_file():
            return str(path)
        return None

    @staticmethod
    def _code_executable() -> str:
        discovered = shutil.which("code")
        if discovered:
            executable = PortalLauncher._native_code_path(discovered)
            if executable:
                return executable

        candidates: list[Path] = []
        if sys.platform == "darwin":
            candidates.append(
                Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code")
            )
        if os.name == "nt":
            for variable in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)"):
                root = os.environ.get(variable)
                if root:
                    candidates.extend(
                        (
                            Path(root) / "Programs" / "Microsoft VS Code" / "Code.exe",
                            Path(root) / "Microsoft VS Code" / "Code.exe",
                            Path(root) / "Microsoft VS Code" / "bin" / "code.cmd",
                        )
                    )
        for candidate in candidates:
            executable = PortalLauncher._native_code_path(candidate)
            if executable:
                return executable
        raise PortalError(
            "VS Code's 'code' launcher was not found. In VS Code, install the "
            "shell command or open this repository folder manually."
        )


class PortalServer(ThreadingHTTPServer):
    """HTTP server state shared with portal request handlers."""

    daemon_threads = True

    def __init__(
        self,
        catalog: Catalog,
        *,
        port: int = 0,
        progress_path: Path | None = None,
        allow_launches: bool = True,
        token: str | None = None,
    ) -> None:
        self.catalog = catalog
        self.repo_root = catalog.repo_root
        self.progress = ProgressStore(catalog, progress_path)
        self.launcher = PortalLauncher(catalog, enabled=allow_launches)
        self.token = token or secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", port), PortalRequestHandler)
        self.expected_host = f"127.0.0.1:{self.server_address[1]}"

    @property
    def url(self) -> str:
        """Return the private loopback URL for this session."""

        return f"http://{self.expected_host}/"


class PortalRequestHandler(BaseHTTPRequestHandler):
    """Serve the generated guide and a small authenticated local API."""

    server_version = "DS60Portal/1"

    @property
    def portal(self) -> PortalServer:
        return cast(PortalServer, self.server)

    def do_GET(self) -> None:  # noqa: N802
        """Serve the guide, status API, or a safe repository artifact."""

        if self.headers.get("Host") != self.portal.expected_host:
            self._send_error(HTTPStatus.BAD_REQUEST, "Unexpected Host header.")
            return
        path = urlsplit(self.path).path
        if path == "/api/status":
            if not self._authorized_api_request(require_origin=False):
                return
            diagnostics = [asdict(item) for item in diagnose(self.portal.catalog)]
            self._send_json(
                {
                    "mode": "launcher",
                    "completed": [
                        completion.lesson_id for completion in self.portal.progress.completions()
                    ],
                    "progress_path": ".learning/progress.json",
                    "launches_enabled": self.portal.launcher.enabled,
                    "diagnostics": diagnostics,
                }
            )
            return
        if path in {"/", "/START_HERE.html"}:
            self._serve_guide()
            return
        self._serve_repository_file(path)

    def do_POST(self) -> None:  # noqa: N802
        """Handle authenticated progress and native-launch actions."""

        if not self._authorized_api_request(require_origin=True):
            return
        try:
            payload = self._read_json()
            path = urlsplit(self.path).path
            if path == "/api/progress":
                self._update_progress(payload)
                return
            if path == "/api/progress/replace":
                self._replace_progress(payload)
                return
            if path == "/api/launch":
                self._launch(payload)
                return
            self._send_error(HTTPStatus.NOT_FOUND, "Unknown portal API route.")
        except (KeyError, OSError, PortalError, TypeError, ValueError) as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def log_message(self, format: str, *args: object) -> None:
        """Keep terminal logs concise and free of request tokens."""

        if self.path.startswith("/api/"):
            print(f"[portal] {self.command} {urlsplit(self.path).path} -> {args[1]}")

    def _authorized_api_request(self, *, require_origin: bool) -> bool:
        if self.headers.get("Host") != self.portal.expected_host:
            self._send_error(HTTPStatus.BAD_REQUEST, "Unexpected Host header.")
            return False
        if not secrets.compare_digest(
            self.headers.get("X-DS60-Token", ""),
            self.portal.token,
        ):
            self._send_error(HTTPStatus.FORBIDDEN, "Invalid portal session token.")
            return False
        if require_origin:
            origin = self.headers.get("Origin")
            expected_origin = f"http://{self.portal.expected_host}"
            if origin not in {None, expected_origin}:
                self._send_error(HTTPStatus.FORBIDDEN, "Unexpected request origin.")
                return False
        return True

    def _read_json(self) -> dict[str, Any]:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise PortalError("Portal API requests must use application/json.")
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise PortalError("Portal API request is missing Content-Length.")
        length = int(raw_length)
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise PortalError("Portal API request is too large.")
        decoded = json.loads(self.rfile.read(length))
        if not isinstance(decoded, dict):
            raise PortalError("Portal API payload must be a JSON object.")
        return cast(dict[str, Any], decoded)

    def _update_progress(self, payload: dict[str, Any]) -> None:
        lesson_id = payload.get("lesson_id")
        complete = payload.get("complete")
        if not isinstance(lesson_id, str) or not isinstance(complete, bool):
            raise PortalError("Progress update needs a lesson_id and boolean complete.")
        if complete:
            self.portal.progress.mark_complete(lesson_id)
        else:
            self.portal.progress.mark_incomplete(lesson_id)
        self._send_json({"ok": True, "lesson_id": lesson_id, "complete": complete})

    def _replace_progress(self, payload: dict[str, Any]) -> None:
        completed = payload.get("completed")
        if not isinstance(completed, list) or not all(isinstance(item, str) for item in completed):
            raise PortalError("Progress replacement needs a completed lesson list.")
        records = self.portal.progress.replace_completions(completed)
        self._send_json({"ok": True, "completed": [record.lesson_id for record in records]})

    def _launch(self, payload: dict[str, Any]) -> None:
        action = payload.get("action")
        lesson_id = payload.get("lesson_id")
        artifact = payload.get("artifact", "lesson")
        solution_index = payload.get("solution_index", 0)
        if not isinstance(action, str):
            raise PortalError("Launch request needs an action.")
        if lesson_id is not None and not isinstance(lesson_id, str):
            raise PortalError("lesson_id must be a string.")
        if not isinstance(artifact, str):
            raise PortalError("artifact must be a string.")
        if (
            not isinstance(solution_index, int)
            or isinstance(solution_index, bool)
            or solution_index < 0
        ):
            raise PortalError("solution_index must be a non-negative integer.")
        launch = self.portal.launcher.launch(
            action,
            lesson_id=lesson_id,
            artifact=artifact,
            solution_index=solution_index,
        )
        self._send_json(
            {
                "ok": True,
                "action": launch.action,
                "process_id": launch.process_id,
            },
            status=HTTPStatus.ACCEPTED,
        )

    def _serve_guide(self) -> None:
        path = self.portal.repo_root / "START_HERE.html"
        try:
            document = path.read_text(encoding="utf-8")
        except OSError as exc:
            self._send_error(HTTPStatus.NOT_FOUND, f"START_HERE.html is unavailable: {exc}")
            return
        marker = 'const SERVER_TOKEN = "";'
        if marker not in document:
            self._send_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "START_HERE.html is stale; rebuild it with scripts/build_course_guide.py.",
            )
            return
        document = document.replace(
            marker,
            f"const SERVER_TOKEN = {json.dumps(self.portal.token)};",
            1,
        )
        encoded = document.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self._security_headers("text/html; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _serve_repository_file(self, raw_path: str) -> None:
        decoded_path = unquote(raw_path)
        # URL paths use forward slashes. Reject backslashes before converting
        # to the host Path type so Windows cannot reinterpret an encoded
        # ``foo\..\.git\config`` path after the hidden-part check.
        if "\\" in decoded_path:
            self._send_error(HTTPStatus.NOT_FOUND, "Repository artifact not found.")
            return
        relative = PurePosixPath(decoded_path.lstrip("/"))
        if not relative.parts or any(
            part.startswith(".") or part.lower() in BLOCKED_PARTS for part in relative.parts
        ):
            self._send_error(HTTPStatus.NOT_FOUND, "Repository artifact not found.")
            return
        lesson_page = (
            len(relative.parts) == 2
            and relative.parts[0] == "lesson-pages"
            and relative.suffix.lower() == ".html"
        )
        reference_page = (
            len(relative.parts) >= 2
            and relative.parts[0] == "reference-pages"
            and relative.suffix.lower() == ".html"
        )
        if not lesson_page and not reference_page:
            self._send_error(HTTPStatus.NOT_FOUND, "Repository artifact not found.")
            return
        target = (self.portal.repo_root / Path(*relative.parts)).resolve()
        if (
            not target.is_relative_to(self.portal.repo_root)
            or not target.is_file()
            or target.name.lower() in BLOCKED_NAMES
            or target.suffix.lower() in BLOCKED_SUFFIXES
        ):
            self._send_error(HTTPStatus.NOT_FOUND, "Repository artifact not found.")
            return
        try:
            encoded = target.read_bytes()
        except OSError as exc:
            self._send_error(HTTPStatus.NOT_FOUND, str(exc))
            return
        if (
            target.suffix.lower() == ".html"
            and target.parent.name == "lesson-pages"
            and b'const SERVER_TOKEN = "";' in encoded
        ):
            document = encoded.decode("utf-8")
            document = document.replace(
                'const SERVER_TOKEN = "";',
                f"const SERVER_TOKEN = {json.dumps(self.portal.token)};",
                1,
            )
            encoded = document.encode("utf-8")
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self._security_headers(content_type, len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _security_headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def _send_json(
        self,
        payload: dict[str, Any],
        *,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        encoded = (json.dumps(payload, ensure_ascii=False) + "\n").encode()
        self.send_response(status)
        self._security_headers("application/json; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_error(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"ok": False, "error": message}, status=status)


def create_portal_server(
    catalog: Catalog,
    *,
    port: int = 0,
    progress_path: Path | None = None,
    allow_launches: bool = True,
    token: str | None = None,
) -> PortalServer:
    """Create a loopback portal server without starting its request loop."""

    if not 0 <= port <= 65535:
        raise ValueError("Port must be between 0 and 65535.")
    return PortalServer(
        catalog,
        port=port,
        progress_path=progress_path,
        allow_launches=allow_launches,
        token=token,
    )


def serve_portal(
    catalog: Catalog,
    *,
    port: int = 0,
    open_browser: bool = True,
    allow_launches: bool = True,
) -> None:
    """Run the portal until interrupted."""

    server = create_portal_server(
        catalog,
        port=port,
        allow_launches=allow_launches,
    )
    print(f"DS60 learning portal: {server.url}")
    print("Progress is private in .learning/progress.json. Press Ctrl+C to stop.")
    if open_browser and not webbrowser.open(server.url):
        print("The browser did not open automatically; copy the URL above.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping DS60 learning portal.")
    finally:
        server.server_close()
