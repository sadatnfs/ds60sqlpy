"""Shared classroom HTTP authentication, progress and rendered-document serving."""

from __future__ import annotations

import json
import mimetypes
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path, PurePosixPath
from typing import Any, cast
from urllib.parse import unquote, urlsplit

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.http_server import LocalThreadingHTTPServer
from ds60sqlpy.progress import ProgressStore

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


class RequestError(RuntimeError):
    """A safe, learner-facing classroom request failure."""


class CourseHTTPServer(LocalThreadingHTTPServer):
    """State shared by classroom HTTP request handlers."""

    daemon_threads = True

    def __init__(
        self,
        catalog: Catalog,
        *,
        port: int = 0,
        progress_path: Path | None = None,
        token: str | None = None,
        bind_host: str = "127.0.0.1",
    ) -> None:
        self.catalog = catalog
        self.repo_root = catalog.repo_root
        self.progress = ProgressStore(catalog, progress_path)
        self.token = token or secrets.token_urlsafe(32)
        super().__init__((bind_host, port), CourseRequestHandler)
        self.expected_host = (
            "127.0.0.1" if self.server_address[1] == 80 else f"127.0.0.1:{self.server_address[1]}"
        )

    @property
    def url(self) -> str:
        """Return the private loopback URL for this session."""

        return f"http://{self.expected_host}/"


class CourseRequestHandler(BaseHTTPRequestHandler):
    """Serve the generated guide and a small authenticated local API."""

    server_version = "DS60Classroom/1"

    @property
    def course(self) -> CourseHTTPServer:
        return cast(CourseHTTPServer, self.server)

    def do_GET(self) -> None:  # noqa: N802
        """Serve the guide, status API, or a safe repository artifact."""

        if self.headers.get("Host") != self.course.expected_host:
            self._send_error(HTTPStatus.BAD_REQUEST, "Unexpected Host header.")
            return
        path = urlsplit(self.path).path
        from ds60sqlpy.reader_tex import ASSET_ROUTE, public_font_names

        if path.startswith(ASSET_ROUTE) and path[len(ASSET_ROUTE) :] in public_font_names() | {
            "fonts.css"
        }:
            from importlib.resources import files

            data = (
                files("ds60sqlpy")
                .joinpath("assets/vendor/textbook/" + path[len(ASSET_ROUTE) :])
                .read_bytes()
            )
            self.send_response(HTTPStatus.OK)
            self._security_headers(
                "text/css; charset=utf-8" if path.endswith(".css") else "font/woff2", len(data)
            )
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/status":
            if not self._authorized_api_request(require_origin=False):
                return
            self._send_json(
                {
                    "mode": "classroom",
                    "completed": [
                        completion.lesson_id for completion in self.course.progress.completions()
                    ],
                    "progress_path": ".learning/progress.json",
                }
            )
            return
        if path in {"/", "/START_HERE.html"}:
            self._serve_guide()
            return
        self._serve_repository_file(path)

    def do_POST(self) -> None:  # noqa: N802
        """Handle authenticated progress mutations."""

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
            self._send_error(HTTPStatus.NOT_FOUND, "Unknown classroom API route.")
        except (KeyError, OSError, RequestError, TypeError, ValueError) as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def log_message(self, format: str, *args: object) -> None:
        """Keep terminal logs concise and free of request tokens."""

        path = getattr(self, "path", "")
        if path.startswith("/api/") and len(args) >= 2:
            print(f"[classroom] {getattr(self, 'command', '')} {urlsplit(path).path} -> {args[1]}")

    def _authorized_api_request(self, *, require_origin: bool) -> bool:
        if self.headers.get("Host") != self.course.expected_host:
            self._send_error(HTTPStatus.BAD_REQUEST, "Unexpected Host header.")
            return False
        if not secrets.compare_digest(
            self.headers.get("X-DS60-Token", ""),
            self.course.token,
        ):
            self._send_error(HTTPStatus.FORBIDDEN, "Invalid classroom session token.")
            return False
        if require_origin:
            origin = self.headers.get("Origin")
            expected_origin = f"http://{self.course.expected_host}"
            if origin != expected_origin:
                self._send_error(HTTPStatus.FORBIDDEN, "Unexpected request origin.")
                return False
        return True

    def _read_json(self, *, max_bytes: int = MAX_REQUEST_BYTES) -> dict[str, Any]:
        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            raise RequestError("Classroom API requests must use application/json.")
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise RequestError("Classroom API request is missing Content-Length.")
        length = int(raw_length)
        if length < 0 or length > max_bytes:
            raise RequestError("Classroom API request is too large.")
        decoded = json.loads(self.rfile.read(length))
        if not isinstance(decoded, dict):
            raise RequestError("Classroom API payload must be a JSON object.")
        return cast(dict[str, Any], decoded)

    def _update_progress(self, payload: dict[str, Any]) -> None:
        lesson_id = payload.get("lesson_id")
        complete = payload.get("complete")
        if not isinstance(lesson_id, str) or not isinstance(complete, bool):
            raise RequestError("Progress update needs a lesson_id and boolean complete.")
        if complete:
            self.course.progress.mark_complete(lesson_id)
        else:
            self.course.progress.mark_incomplete(lesson_id)
        self._send_json({"ok": True, "lesson_id": lesson_id, "complete": complete})

    def _replace_progress(self, payload: dict[str, Any]) -> None:
        completed = payload.get("completed")
        if not isinstance(completed, list) or not all(isinstance(item, str) for item in completed):
            raise RequestError("Progress replacement needs a completed lesson list.")
        records = self.course.progress.replace_completions(completed)
        self._send_json({"ok": True, "completed": [record.lesson_id for record in records]})

    def _serve_guide(self) -> None:
        path = self.course.repo_root / "START_HERE.html"
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
            f"const SERVER_TOKEN = {json.dumps(self.course.token)};",
            1,
        )
        document = document.replace("const LAB_MODE = false;", "const LAB_MODE = true;", 1)
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
        target = (self.course.repo_root / Path(*relative.parts)).resolve()
        if (
            not target.is_relative_to(self.course.repo_root)
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
                f"const SERVER_TOKEN = {json.dumps(self.course.token)};",
                1,
            )
            document = document.replace("const LAB_MODE = false;", "const LAB_MODE = true;", 1)
            encoded = document.encode("utf-8")
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self._security_headers(content_type, len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def _security_headers(
        self, content_type: str, length: int, *, allow_same_origin_frame: bool = False
    ) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN" if allow_same_origin_frame else "DENY")

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
