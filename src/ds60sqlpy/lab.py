"""Guided local application with opt-in coding-pad execution."""

from __future__ import annotations

import json
import math
import os
import threading
import webbrowser
from http import HTTPStatus
from importlib.resources import files
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from ds60sqlpy.capabilities import CapabilityService
from ds60sqlpy.catalog import Catalog
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.curriculum_framework import RUNNERS
from ds60sqlpy.execution import ALLOWED_TIMEOUT_SECONDS, PadRunner
from ds60sqlpy.lesson_reader import render_artifact, rendered_targets
from ds60sqlpy.portal import PortalError, PortalRequestHandler, PortalServer
from ds60sqlpy.sql_lesson import SqlLessonRunner
from ds60sqlpy.sql_runner import SqlRunner, SqlRunnerError


class LabServer(PortalServer):
    """A separate execution-capable server; the original portal stays read-only."""

    is_learning_lab = True

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
        super().__init__(
            catalog,
            port=port,
            progress_path=progress_path,
            allow_launches=False,
            bind_host="0.0.0.0" if container else "127.0.0.1",
        )
        self.RequestHandlerClass = LabRequestHandler
        self.coaching = CoachingService(catalog, self.progress)
        self.pads = PadRunner(catalog, python=python)
        self.sql_lessons = SqlLessonRunner(catalog, self.pads)
        self.capabilities = CapabilityService(catalog, self.pads.python)
        self.execution_lock = threading.Lock()
        self.targets = rendered_targets(catalog)

    def action(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Dispatch only catalog-bound operations, with strict input types."""

        action = payload.get("action")
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
        if action == "lesson":
            return {
                **self.coaching.lesson(lesson_id),
                "capabilities": self.capabilities.lesson(lesson_id),
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
                    output_path="learn",
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
                return self.sql_lessons.run(lesson_id, code, timeout_seconds=timeout)
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
            if not self.execution_lock.acquire(blocking=False):
                raise ValueError(
                    "A pad is already running. Wait for its result before running again."
                )
            try:
                return (
                    self.pads.run(lesson_id, language, code)
                    if timeout is None
                    else self.pads.run(lesson_id, language, code, timeout_seconds=timeout)
                )
            finally:
                self.execution_lock.release()
        raise ValueError("Unknown learning-lab action.")


class LabRequestHandler(PortalRequestHandler):
    """Keep the original exact-Host, origin, token, and content limits."""

    @property
    def lab(self) -> LabServer:
        return cast(LabServer, self.server)

    def do_GET(self) -> None:  # noqa: N802
        if urlsplit(self.path).path != "/learn":
            super().do_GET()
            return
        if self.headers.get("Host") != self.lab.expected_host:
            self._send_error(HTTPStatus.BAD_REQUEST, "Unexpected Host header.")
            return
        document = (
            files("ds60sqlpy").joinpath("assets/learning_lab.html").read_text(encoding="utf-8")
        )
        document = document.replace(
            'const SERVER_TOKEN = "";', f"const SERVER_TOKEN = {json.dumps(self.lab.token)};", 1
        )
        encoded = document.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self._security_headers("text/html; charset=utf-8", len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self) -> None:  # noqa: N802
        if urlsplit(self.path).path != "/api/lab":
            super().do_POST()
            return
        if not self._authorized_api_request(require_origin=True):
            return
        try:
            self._send_json(self.lab.action(self._read_json()))
        except (KeyError, OSError, PortalError, TypeError, ValueError) as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, str(exc))


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
    url = f"{server.url}learn"
    print(f"DS60 Learning Lab: {url}")
    print("Coding pads run trusted local code. Saved work is in .learning/. Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
