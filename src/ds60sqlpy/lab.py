"""Guided local application with opt-in coding-pad execution."""

from __future__ import annotations

import contextlib
import json
import math
import os
import signal
import threading
import webbrowser
from http import HTTPStatus
from importlib.resources import files
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from ds60sqlpy.capabilities import CapabilityService
from ds60sqlpy.catalog import Catalog, Lesson
from ds60sqlpy.classroom import ClassroomService
from ds60sqlpy.classroom_http import CourseHTTPServer, CourseRequestHandler, RequestError
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.curriculum_framework import RUNNERS
from ds60sqlpy.execution import ALLOWED_TIMEOUT_SECONDS, MAX_CODE_BYTES, PadRunner
from ds60sqlpy.lesson_reader import render_artifact, rendered_targets
from ds60sqlpy.module_service import ModuleService
from ds60sqlpy.run_explain import explain_pad_run
from ds60sqlpy.sql_lesson import SqlLessonRunner
from ds60sqlpy.sql_readiness import Readiness, ensure_before_run, uses_course_database
from ds60sqlpy.sql_readiness import inspect as inspect_sql
from ds60sqlpy.sql_readiness import prepare as prepare_sql
from ds60sqlpy.sql_runner import SqlRunner, SqlRunnerError


class LabServer(CourseHTTPServer):
    """The unified classroom server with explicit learner-controlled execution."""

    # Keep bounded execution controllers alive during shutdown so their finally
    # blocks reap workers and descendants before the application exits.
    daemon_threads = False

    def get_request(self) -> tuple[Any, Any]:
        connection, address = super().get_request()
        connection.settimeout(5)
        return connection, address

    def __init__(
        self,
        catalog: Catalog,
        *,
        port: int = 0,
        python: str | None = None,
        progress_path: Path | None = None,
        container: bool = False,
    ) -> None:
        if container and not (os.environ.get("DS60_CONTAINER") == "1"):
            raise ValueError(
                "Container binding requires the explicit DS60_CONTAINER=1 image setting."
            )
        public_port: int | None = None
        public_text = os.environ.get("DS60_PUBLIC_PORT", "") if container else ""
        if public_text:
            if not public_text.isascii() or not public_text.isdecimal():
                raise ValueError("DS60_PUBLIC_PORT must be an integer between 1 and 65535.")
            public_port = int(public_text)
            if not 1 <= public_port <= 65535:
                raise ValueError("DS60_PUBLIC_PORT must be an integer between 1 and 65535.")
        super().__init__(
            catalog,
            port=port,
            progress_path=progress_path,
            bind_host="0.0.0.0" if container else "127.0.0.1",
        )
        # A mapped Docker host port changes the one exact accepted Host/Origin,
        # never the listening interface or an allowlist of arbitrary hosts.
        if public_port is not None:
            self.expected_host = "127.0.0.1" if public_port == 80 else f"127.0.0.1:{public_port}"
        self.RequestHandlerClass = LabRequestHandler
        self.coaching = CoachingService(catalog, self.progress)
        self.pads = PadRunner(catalog, python=python)
        self.sql_lessons = SqlLessonRunner(catalog, self.pads)
        self.capabilities = CapabilityService(catalog, self.pads.python)
        self.execution_lock = threading.Lock()
        self.targets = rendered_targets(catalog)
        self._modules: ModuleService | None = None
        self._module_lock = threading.Lock()
        self._modules_closing = False
        self._module_state_directory = (
            progress_path.parent / "modules" if progress_path is not None else None
        )
        self._classroom = ClassroomService(
            catalog,
            self.action,
            self.targets,
            runs_directory=self.progress.path.parent / "classroom-runs",
        )

    def server_close(self) -> None:
        lock = getattr(self, "_module_lock", None)
        if lock is not None:
            with lock:
                self._modules_closing = True
                modules = self._modules
                if modules is not None:
                    modules.close()
        super().server_close()

    def _save_run_receipt(
        self,
        lesson_id: str,
        language: str,
        mode: str,
        source: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """Keep completed execution distinct from a failed attempt to retain its output."""
        try:
            receipt = self._classroom.runs.record(lesson_id, language, mode, source, result)
        except (OSError, TypeError, ValueError):
            return {
                **result,
                "receipt_saved": False,
                "receipt_error": (
                    "Execution finished, but its run receipt could not be saved. "
                    "Copy the output before leaving this page. Do not rerun only to save it."
                ),
            }
        return {**result, "receipt_saved": True, "receipt_id": receipt["id"]}

    @staticmethod
    def _explained(response: dict[str, Any], language: str, source: str) -> dict[str, Any]:
        """Add a beginner explanation to a failed response; the saved receipt is unchanged."""
        explanation = explain_pad_run(language, response, source)
        return response if explanation is None else {**response, "explanation": explanation}

    def action(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Dispatch only catalog-bound operations, with strict input types."""

        action = payload.get("action")
        if isinstance(action, str) and action.startswith("classroom-"):
            return self._classroom.action(payload)
        if isinstance(action, str) and action.startswith("module-"):
            with self._module_lock:
                if self._modules_closing:
                    raise ValueError("The module application is closing.")
                if self._modules is None:
                    self._modules = ModuleService(self.catalog, self._module_state_directory)
            return self._modules.action(payload)
        if action == "paths":
            return self.coaching.paths()
        if action == "plan":
            targets = payload.get("targets")
            hours = payload.get("weekly_hours", 5)
            if not isinstance(targets, list) or not all(isinstance(p, str) for p in targets):
                raise ValueError("Choose a list of stable goal lesson IDs.")
            if isinstance(hours, bool) or not isinstance(hours, (int, float)):
                raise ValueError("Weekly hours must be a positive number.")
            if not math.isfinite(hours) or not 0 < hours <= 168:
                raise ValueError("Weekly hours must be greater than zero and at most 168.")
            return self.coaching.plan(targets, hours)
        if action == "prepare-sql":
            if payload.get("confirmation") != "RESET TRAINING":
                raise ValueError(
                    "Type RESET TRAINING to reset only the disposable training schema."
                )
            if not self.execution_lock.acquire(blocking=False):
                raise ValueError(
                    "A pad is already running. Wait for its result before resetting SQL."
                )
            try:
                runner = SqlRunner(self.catalog, capture_output=True)
                setup = runner.setup()
                transcript = setup.stdout + setup.stderr
                status = setup.returncode
                if status == 0:
                    verify = runner.verify()
                    transcript += verify.stdout + verify.stderr
                    status = verify.returncode
                return {"returncode": status, "output": transcript[-128_000:]}
            except SqlRunnerError as exc:
                raise ValueError(str(exc)) from exc
            finally:
                self.execution_lock.release()
        lesson_id = payload.get("lesson_id")
        if not isinstance(lesson_id, str):
            raise ValueError("Choose a cataloged lesson ID.")
        lesson = self.catalog.get(lesson_id)
        if action == "capabilities":
            return self.capabilities.lesson(lesson_id)
        if action in {"sql-status", "sql-prepare"}:
            try:
                runner = SqlRunner(self.catalog, capture_output=True)
            except SqlRunnerError as exc:
                return {"readiness": Readiness(state="unavailable", detail=str(exc)).as_payload()}
            if action == "sql-status":
                try:
                    return {"readiness": inspect_sql(self.catalog, lesson_id, runner).as_payload()}
                except SqlRunnerError as exc:
                    state = Readiness(state="unavailable", detail=str(exc))
                    return {"readiness": state.as_payload()}
            if not self.execution_lock.acquire(blocking=False):
                raise ValueError(
                    "A run is in progress. Wait for its result before preparing the database."
                )
            try:
                readiness, transcript = prepare_sql(self.catalog, lesson_id, runner)
                return {"readiness": readiness.as_payload(), "output": transcript}
            except SqlRunnerError as exc:
                raise ValueError(str(exc)) from exc
            finally:
                self.execution_lock.release()
        if action == "lesson":
            return {
                **self.coaching.lesson(lesson_id),
                "capabilities": self.capabilities.lesson(lesson_id),
                "course_database": uses_course_database(lesson),
                "sql_snippet_starter": (
                    "SELECT current_database() AS database_name, current_user AS database_user;\n"
                    if lesson.runner == "sql"
                    else "SELECT 42 AS answer;\n"
                ),
                "guide_html": render_artifact(
                    self.catalog.resolve(lesson.guide_path),
                    repo_root=self.repo_root,
                    targets=self.targets,
                    id_prefix="lab-guide--",
                    output_path="classroom",
                ),
            }
        if action == "save":
            phase, note = payload.get("phase"), payload.get("note")
            if not isinstance(phase, str) or not isinstance(note, str):
                raise ValueError("Supply a phase and text evidence.")
            return self.coaching.save(lesson_id, phase, note)
        if action == "hint":
            number = payload.get("number", 1)
            if isinstance(number, bool) or not isinstance(number, int):
                raise ValueError("Hint number must be an integer.")
            return self.coaching.hint(lesson_id, number)
        if action == "solution":
            return self.coaching.solution(lesson_id, reveal=payload.get("reveal") is True)
        if action == "complete":
            return self.coaching.complete(lesson_id, confirmed=payload.get("confirmed") is True)
        if action == "run-lesson":
            code = payload.get("code")
            timeout = payload.get("timeout_seconds", 60)
            if not isinstance(code, str):
                raise ValueError("Supply the learner SQL working copy as text.")
            if type(timeout) is not int or timeout not in ALLOWED_TIMEOUT_SECONDS:
                raise ValueError("Choose a run limit of 15, 60 or 120 seconds.")
            if not self.execution_lock.acquire(blocking=False):
                raise ValueError(
                    "A pad is already running. Wait for its result before running again."
                )
            try:
                preparation = ensure_before_run(self.catalog, lesson_id)
                result = self.sql_lessons.run(lesson_id, code, timeout_seconds=timeout)
                response = self._explained(
                    self._save_run_receipt(lesson_id, "sql", "lesson", code, result), "sql", code
                )
                if preparation:
                    response["database_preparation"] = preparation
                return response
            finally:
                self.execution_lock.release()
        if action in {"save-pad", "read-pad", "pad-history", "read-history", "run"}:
            language = payload.get("language")
            if not isinstance(language, str) or language not in RUNNERS:
                raise ValueError("Choose a registered lesson runner.")
            mode = payload.get("mode", "snippet")
            if not isinstance(mode, str) or mode not in {"snippet", "lesson"}:
                raise ValueError("Choose SQL snippet or whole lesson mode.")
            if mode == "lesson":
                if language != "sql":
                    raise ValueError(
                        "Whole lesson mode is available only for cataloged SQL scripts."
                    )
                if action == "read-pad":
                    return self.sql_lessons.read(lesson_id)
                if action == "pad-history":
                    return {"history": self.sql_lessons.history(lesson_id)}
                if action == "read-history":
                    history_id = payload.get("history_id")
                    if not isinstance(history_id, str):
                        raise ValueError("Choose an existing pad history ID.")
                    return {"code": self.sql_lessons.read_history(lesson_id, history_id)}
                if action == "save-pad":
                    code = payload.get("code")
                    if not isinstance(code, str):
                        raise ValueError("Supply SQL as text.")
                    self.sql_lessons.save(lesson_id, code)
                    return {"ok": True}
                raise ValueError("Use the explicit run-lesson action for whole SQL mode.")
            if action == "read-pad":
                return {
                    "code": self.pads.read(lesson_id, language),
                    "saved": self.pads.saved(lesson_id, language),
                }
            if action == "pad-history":
                return {"history": self.pads.history(lesson_id, language)}
            if action == "read-history":
                history_id = payload.get("history_id")
                if not isinstance(history_id, str):
                    raise ValueError("Choose an existing pad history ID.")
                return {"code": self.pads.read_history(lesson_id, language, history_id)}
            code = payload.get("code")
            if not isinstance(code, str):
                raise ValueError("Supply code as text.")
            if action == "save-pad":
                self.pads.save(lesson_id, language, code)
                return {"ok": True}
            timeout = payload.get("timeout_seconds")
            if timeout is not None and (
                type(timeout) is not int or timeout not in ALLOWED_TIMEOUT_SECONDS
            ):
                raise ValueError("Choose a run limit of 15, 60 or 120 seconds.")
            purpose = payload.get("purpose", "practice")
            if not isinstance(purpose, str) or purpose not in {"practice", "solution"}:
                raise ValueError("Choose a practice run or a worked-solution run.")
            solution = purpose == "solution"
            if not self.execution_lock.acquire(blocking=False):
                raise ValueError(
                    "A pad is already running. Wait for its result before running again."
                )
            try:
                preparation = (
                    ensure_before_run(self.catalog, lesson_id)
                    if language == "sql" or uses_course_database(lesson)
                    else None
                )
                # Practice runs keep their original call; only a worked-solution run
                # asks the runner not to save the submitted code as the pad.
                options: dict[str, Any] = {}
                if timeout is not None:
                    options["timeout_seconds"] = timeout
                if solution:
                    options["save"] = False
                result = self.pads.run(lesson_id, language, code, **options)
                # A worked-solution run is shown once and kept out of the learner's
                # saved pad and run history.
                response = self._explained(
                    {**result, "purpose": "solution"}
                    if solution
                    else self._save_run_receipt(lesson_id, language, "snippet", code, result),
                    language,
                    code,
                )
                if preparation:
                    response["database_preparation"] = preparation
                return response
            finally:
                self.execution_lock.release()
        if action == "step-through":
            return self._step_through(payload, lesson_id, lesson)
        raise ValueError("Unknown learning-lab action.")

    def _step_through(
        self, payload: dict[str, Any], lesson_id: str, lesson: Lesson
    ) -> dict[str, Any]:
        """Trace a pad without saving it, writing a receipt or touching its history."""

        language = payload.get("language")
        definition = RUNNERS.get(language) if isinstance(language, str) else None
        if (
            not isinstance(language, str)
            or definition is None
            or definition.executor not in {"python", "sql"}
        ):
            raise ValueError("Step-through is available for Python and SQL lessons.")
        code = payload.get("code")
        if not isinstance(code, str):
            raise ValueError("Supply code as text.")
        try:
            oversized = len(code.encode("utf-8")) > MAX_CODE_BYTES
        except UnicodeEncodeError:
            oversized = True
        if oversized:
            raise ValueError(f"Pad input must be text of at most {MAX_CODE_BYTES} UTF-8 bytes.")
        timeout = payload.get("timeout_seconds")
        if timeout is not None and (
            type(timeout) is not int or timeout not in ALLOWED_TIMEOUT_SECONDS
        ):
            raise ValueError("Choose a run limit of 15, 60 or 120 seconds.")
        purpose = payload.get("purpose", "practice")
        if not isinstance(purpose, str) or purpose not in {"practice", "solution"}:
            raise ValueError("Choose a practice run or a worked-solution run.")
        cursor = payload.get("cursor_offset")
        if cursor is not None and (type(cursor) is not int or cursor < 0):
            raise ValueError("Choose a cursor position inside the code.")
        if not self.execution_lock.acquire(blocking=False):
            raise ValueError("A pad is already running. Wait for its result before running again.")
        try:
            preparation = (
                ensure_before_run(self.catalog, lesson_id)
                if language == "sql" or uses_course_database(lesson)
                else None
            )
            response = self.pads.step_through(
                lesson_id,
                language,
                code,
                cursor_offset=cursor if language == "sql" else None,
                timeout_seconds=timeout,
            )
            if preparation:
                response["database_preparation"] = preparation
            return response
        finally:
            self.execution_lock.release()


class LabRequestHandler(CourseRequestHandler):
    """Keep the original exact-Host, origin, token, and content limits."""

    @property
    def lab(self) -> LabServer:
        return cast(LabServer, self.server)

    def do_GET(self) -> None:  # noqa: N802
        route = urlsplit(self.path).path
        classroom_routes = {"/", "/classroom", "/learn", "/journeys", "/journey-preview"}
        script = "text/javascript; charset=utf-8"
        assets = {
            "/assets/classroom.css": ("classroom.css", "text/css; charset=utf-8"),
            "/assets/classroom.js": ("classroom.js", script),
            "/assets/browser-preview.js": ("browser-preview.js", script),
            "/assets/classroom-editor.js": ("classroom-editor.js", script),
            "/assets/classroom-shell.js": ("classroom-shell.js", script),
            "/assets/classroom-guide.js": ("classroom-guide.js", script),
            "/assets/codemirror.js": ("vendor/codemirror.v6.min.js", script),
        }
        if route not in classroom_routes | set(assets) | {
            "/assets/rich-content.css",
            "/browser-sandbox",
            "/plot-sandbox",
        }:
            super().do_GET()
            return
        if self.headers.get("Host") != self.lab.expected_host:
            self._send_error(HTTPStatus.BAD_REQUEST, "Unexpected Host header.")
            return
        content_type = "text/html; charset=utf-8"
        if route in {"/browser-sandbox", "/plot-sandbox"}:
            # No session token or learner data enters this document. The opaque
            # iframe receives source only through an explicitly connected port.
            assets_root = files("ds60sqlpy").joinpath("assets")
            document = assets_root.joinpath(
                "plot-sandbox.html" if route == "/plot-sandbox" else "browser-sandbox.html"
            ).read_text(encoding="utf-8")
            bundle = assets_root.joinpath("vendor/d3.v7.9.0.min.js").read_text(encoding="utf-8")
            plotly = assets_root.joinpath("vendor/plotly-cartesian.v4.1.2.min.js").read_text(
                encoding="utf-8"
            )
            if "</script" in plotly.lower():
                raise ValueError("The reviewed Plotly bundle cannot be embedded safely.")
            document = document.replace("__DS60_PLOTLY_BUNDLE__", plotly, 1)
            if "</script" in bundle.lower():
                raise ValueError("The reviewed D3 bundle cannot be embedded safely.")
            document = document.replace("__DS60_D3_BUNDLE__", bundle, 1).replace(
                "__DS60_BROWSER_ORIGIN__", json.dumps("http://" + self.lab.expected_host), 1
            )
            encoded = document.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self._security_headers(content_type, len(encoded), allow_same_origin_frame=True)
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; sandbox allow-scripts"
                + (" allow-downloads" if route == "/plot-sandbox" else "")
                + "; "
                "script-src 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'none'; "
                "frame-src 'none'; worker-src 'none'; base-uri 'none'; form-action 'none'; "
                "object-src 'none'; frame-ancestors 'self'",
            )
            self.end_headers()
            with contextlib.suppress(BrokenPipeError, ConnectionResetError):
                self.wfile.write(encoded)
            return
        if route == "/assets/rich-content.css":
            from ds60sqlpy.reader_content import rich_content_styles

            document = rich_content_styles()
            content_type = "text/css; charset=utf-8"
        elif route in assets:
            asset, content_type = assets[route]
            document = files("ds60sqlpy").joinpath(f"assets/{asset}").read_text(encoding="utf-8")
        else:
            document = (
                files("ds60sqlpy").joinpath("assets/classroom.html").read_text(encoding="utf-8")
            )
            if route in classroom_routes:
                document = document.replace(
                    'const SERVER_TOKEN = "";',
                    f"const SERVER_TOKEN = {json.dumps(self.lab.token)};",
                    1,
                )
        encoded = document.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self._security_headers(content_type, len(encoded))
        policy = (
            "default-src 'none'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self'; font-src 'self' data:; frame-src 'self'; base-uri 'none'; "
            "form-action 'none'; object-src 'none'; frame-ancestors 'none'"
        )
        self.send_header("Content-Security-Policy", policy)
        self.end_headers()
        with contextlib.suppress(BrokenPipeError, ConnectionResetError):
            self.wfile.write(encoded)

    def do_POST(self) -> None:  # noqa: N802
        route = urlsplit(self.path).path
        if route not in {"/api/lab", "/api/modules", "/api/classroom"}:
            super().do_POST()
            return
        if not self._authorized_api_request(require_origin=True):
            return
        try:
            payload = (
                self._read_json(max_bytes=512 * 1024)
                if route in {"/api/modules", "/api/classroom"}
                else self._read_json()
            )
            required_prefix = {
                "/api/modules": "module-",
                "/api/classroom": "classroom-",
            }.get(route)
            if required_prefix is not None and (
                not isinstance(payload.get("action"), str)
                or not payload["action"].startswith(required_prefix)
            ):
                raise ValueError("This endpoint accepts only its own application actions.")
            self._send_json(self.lab.action(payload))
        except (KeyError, OSError, RequestError, TypeError, ValueError) as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, str(exc))


def _stop_serving(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


def serve_lab(
    catalog: Catalog,
    *,
    port: int = 0,
    python: str | None = None,
    open_browser: bool = True,
    container: bool = False,
) -> None:
    """Start the trusted local coding environment until interrupted."""

    if not 0 <= port <= 65535:
        raise ValueError("Port must be between 0 and 65535.")
    server = LabServer(catalog, port=port, python=python, container=container)
    url = f"{server.url}classroom"
    print(f"DS60 Learning Lab: {url}")
    print("Coding pads run trusted local code. Saved work is in .learning/. Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    # Docker stops containers with SIGTERM; treat it like Ctrl+C so running
    # pads and module sessions are reaped instead of killed.
    previous = (
        signal.signal(signal.SIGTERM, _stop_serving)
        if threading.current_thread() is threading.main_thread()
        else None
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if previous is not None:
            signal.signal(signal.SIGTERM, previous)
