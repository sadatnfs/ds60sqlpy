"""Catalog integration and real HTTP boundaries of the unified classroom."""

from __future__ import annotations

import json
import threading
from copy import deepcopy
from dataclasses import replace
from http.client import HTTPConnection
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom import ClassroomService
from ds60sqlpy.lab import LabServer


def fixture_service(
    tmp_path: Path,
) -> tuple[ClassroomService, list[dict[str, Any]], dict[str, Any]]:
    lesson = replace(Catalog.load().get("python-01"), prerequisites=())
    catalog = Catalog(tmp_path, [lesson], tracks={"python": {"title": "Python", "plan": "plan.md"}})
    fixture = {
        "tracks": [
            {
                "id": "scala-spark",
                "title": "Scala and Spark",
                "summary": "Distributed data workflows",
                "lessons": [
                    {
                        "id": "spark-013",
                        "title": "Spark data",
                        "level": "intermediate",
                        "minutes": 90,
                        "status": "authored",
                        "prerequisites": [],
                        "learning_mode": "practice",
                        "variants": [
                            {"id": "spark-013", "title": "Scala"},
                            {"id": "spark-013@pyspark", "title": "PySpark"},
                        ],
                    }
                ],
            }
        ],
        "lesson_links": {
            "/reference-pages/courses/scala-spark/guides/spark-013.md.html": "spark-013",
            "/reference-pages/courses/scala-spark/lessons/spark-013.py.html": "spark-013@pyspark",
        },
        "active_job": {"job_id": "owned-job", "lesson_id": "spark-013"},
    }
    calls: list[dict[str, Any]] = []

    def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
        calls.append(payload)
        if payload["action"] == "module-index":
            return deepcopy(fixture)
        if payload["action"] == "paths":
            return {"completed": [lesson.id], "paths": {"start": {"targets": [lesson.id]}}}
        if payload["action"] == "module-solutions":
            return {"documents": [{"path": "reference.md", "html": "<p>Explained</p>"}]}
        raise AssertionError("Unexpected backend operation: " + payload["action"])

    return ClassroomService(catalog, dispatch, {}), calls, fixture


def test_subject_directory_unifies_without_mutating_or_reading_solutions(tmp_path: Path) -> None:
    service, calls, _ = fixture_service(tmp_path)
    index = service.action({"action": "classroom-index"})
    assert [track["id"] for track in index["tracks"]] == ["python", "scala-spark"]
    assert [track["engine"] for track in index["tracks"]] == ["legacy", "module"]
    assert index["subject_count"] == 2 and index["lesson_count"] == 2
    assert index["authored_count"] == 2 and index["planned_count"] == 0
    assert index["variant_count"] == 1
    assert index["lesson_links"]["/lesson-pages/python-01.html"] == "python-01"
    assert (
        index["lesson_links"]["/reference-pages/courses/scala-spark/lessons/spark-013.py.html"]
        == "spark-013@pyspark"
    )
    assert not any("solutions" in key for key in index["lesson_links"])

    assert index["tracks"][0]["lessons"][0]["completed"] is True
    assert index["tracks"][0]["lessons"][0]["level"] == "beginner"
    assert index["tracks"][0]["lessons"][0]["source_level"] == "foundation"
    assert index["tracks"][1]["estimated_minutes"] == 90
    assert index["active_job"]["lesson_id"] == "spark-013"
    assert [call["action"] for call in calls] == ["module-index", "paths"]
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("duplicate", ["track", "lesson"])
def test_subject_directory_rejects_identity_collisions(tmp_path: Path, duplicate: str) -> None:
    service, _, fixture = fixture_service(tmp_path)
    if duplicate == "track":
        fixture["tracks"][0]["id"] = "python"
    else:
        fixture["tracks"][0]["lessons"][0]["id"] = "python-01"
    with pytest.raises(ValueError, match="registered"):
        service.index()


@pytest.mark.parametrize("reveal", [None, False, 1, "true"])
def test_shared_solution_boundary_requires_explicit_boolean(tmp_path: Path, reveal: object) -> None:
    service, calls, _ = fixture_service(tmp_path)
    with pytest.raises(ValueError, match="Explicitly"):
        service.action(
            {"action": "classroom-solutions", "lesson_id": "spark-013", "reveal": reveal}
        )
    assert not calls


def test_shared_solution_renderer_uses_only_cataloged_paths(tmp_path: Path) -> None:
    service, calls, _ = fixture_service(tmp_path)
    lesson = service.catalog.get("python-01")
    for path in lesson.solution_paths:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        content = "# Explained\n\n<script>bad()</script>\n"
        if target.suffix == ".ipynb":
            content = json.dumps(
                {
                    "nbformat": 4,
                    "nbformat_minor": 5,
                    "metadata": {"language_info": {"name": "python"}},
                    "cells": [{"cell_type": "markdown", "metadata": {}, "source": content}],
                }
            )
        target.write_text(content, encoding="utf-8")
    result = service.action(
        {"action": "classroom-solutions", "lesson_id": lesson.id, "reveal": True}
    )
    assert len(result["documents"]) == len(lesson.solution_paths)
    assert all("<script>" not in doc["html"] for doc in result["documents"])
    assert not calls
    assert (
        service.action({"action": "classroom-solutions", "lesson_id": "spark-013", "reveal": True})[
            "documents"
        ][0]["html"]
        == "<p>Explained</p>"
    )
    assert calls[-1] == {"action": "module-solutions", "lesson_id": "spark-013", "reveal": True}
    with pytest.raises(ValueError, match="cataloged"):
        service.solutions({"lesson_id": [], "reveal": True})


def test_unified_http_shell_assets_and_authenticated_endpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, calls, _ = fixture_service(tmp_path)
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(service.catalog, progress_path=tmp_path / "progress.json")
    server._classroom = service
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def request(
        path: str, payload: dict[str, Any] | None = None, **overrides: str
    ) -> tuple[int, dict[str, str], bytes]:
        headers = {
            "Host": server.expected_host,
            "Origin": server.url.rstrip("/"),
            "X-DS60-Token": server.token,
            "Content-Type": "application/json",
            **overrides,
        }
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            connection.request(
                "GET" if payload is None else "POST",
                path,
                body=None if payload is None else json.dumps(payload),
                headers=headers,
            )
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    try:
        documents = []
        for path in ("/", "/classroom", "/learn", "/journeys?lesson=python-01"):
            status, headers, document = request(path)
            assert status == 200
            assert server.token.encode() in document
            assert b"/assets/classroom.js" in document
            assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
            documents.append(document)
        assert len(set(documents)) == 1
        for path, mime in (
            ("/assets/classroom.js", "text/javascript"),
            ("/assets/classroom.css", "text/css"),
            ("/assets/rich-content.css", "text/css"),
        ):
            status, headers, body = request(path)
            assert status == 200 and headers["Content-Type"].startswith(mime) and body
            assert server.token.encode() not in body
            assert request(path, Host="attacker.invalid")[0] == 400
        assert request("/assets/lab.py")[0] in {400, 403, 404}
        action = {"action": "classroom-index"}
        assert request("/api/classroom", action, **{"X-DS60-Token": "wrong"})[0] == 403
        assert request("/api/classroom", action, Origin="https://attacker.invalid")[0] == 403
        assert request("/api/classroom", action, Host="attacker.invalid")[0] == 400
        assert not calls
        assert request("/api/classroom", {"action": "prepare-sql"})[0] == 400
        assert request("/api/classroom", {"action": "classroom-unknown"})[0] == 400
        status, _, body = request("/api/classroom", action)
        assert status == 200 and json.loads(body)["subject_count"] == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize(
    "source,language",
    [
        (None, "python"),
        ("x" * 60001, "python"),
        ("🙂" * 15001, "python"),
        ("x", "../../python"),
        ("x", []),
        ("x", "<script>"),
    ],
)
def test_syntax_preview_rejects_unbounded_or_invalid_inputs(
    tmp_path: Path, source: object, language: object
) -> None:
    service, calls, _ = fixture_service(tmp_path)
    with pytest.raises(ValueError):
        service.action({"action": "classroom-highlight", "source": source, "language": language})
    assert not calls


def test_syntax_preview_is_escaped_and_unknown_languages_are_readable(tmp_path: Path) -> None:
    import re
    from html import unescape

    service, calls, _ = fixture_service(tmp_path)
    source = 'print("<script>bad()</script>")\n'
    result = service.action(
        {"action": "classroom-highlight", "source": source, "language": "python"}
    )
    assert "syntax-" in result["html"] and "<script>" not in result["html"]
    assert unescape(re.sub(r"<[^>]+>", "", result["html"])) == source
    unknown = service.action(
        {"action": "classroom-highlight", "source": source, "language": "futurelang"}
    )
    assert unescape(unknown["html"]) == source and not calls


def test_completed_legacy_run_is_readable_after_server_recreation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _, _ = fixture_service(tmp_path)
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    calls: list[str] = []
    server = LabServer(service.catalog, progress_path=tmp_path / "progress.json")

    def execute(lesson_id: str, language: str, source: str) -> dict[str, Any]:
        calls.append(source)
        return {
            "returncode": 0,
            "output": "42\n",
            "elapsed_seconds": 0.02,
            "language": language,
            "figures": [],
        }

    monkeypatch.setattr(server.pads, "run", execute)
    try:
        result = server.action(
            {"action": "run", "lesson_id": "python-01", "language": "python", "code": "print(42)"}
        )
        assert result["receipt_saved"] is True and result["output"] == "42\n"
        receipt_id = result["receipt_id"]
    finally:
        server.server_close()
    reopened = LabServer(service.catalog, progress_path=tmp_path / "progress.json")
    try:
        context = {"lesson_id": "python-01", "language": "python", "mode": "snippet"}
        history = reopened.action({"action": "classroom-history", **context})["history"]
        assert len(history) == 1 and history[0]["id"] == receipt_id
        assert "source" not in history[0] and "result" not in history[0]
        saved = reopened.action(
            {"action": "classroom-run-result", **context, "receipt_id": receipt_id}
        )["receipt"]
        assert saved["source"] == "print(42)" and saved["result"]["output"] == "42\n"
        assert calls == ["print(42)"]
    finally:
        reopened.server_close()


def test_receipt_failure_never_relabels_or_replays_completed_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _, _ = fixture_service(tmp_path)
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(service.catalog, progress_path=tmp_path / "progress.json")
    calls: list[str] = []

    def execute(lesson_id: str, language: str, source: str) -> dict[str, Any]:
        calls.append(source)
        return {"returncode": 0, "output": "committed once", "elapsed_seconds": 0.02}

    def unavailable(*args: Any, **kwargs: Any) -> None:
        raise OSError("private-path-must-not-appear")

    monkeypatch.setattr(server.pads, "run", execute)
    monkeypatch.setattr(server._classroom.runs, "record", unavailable)
    try:
        result = server.action(
            {"action": "run", "lesson_id": "python-01", "language": "python", "code": "print(42)"}
        )
        assert result["returncode"] == 0 and result["output"] == "committed once"
        assert result["receipt_saved"] is False and "Do not rerun" in result["receipt_error"]
        assert "private-path" not in result["receipt_error"]
        assert calls == ["print(42)"] and not server.execution_lock.locked()
    finally:
        server.server_close()


def test_whole_sql_run_receipt_retains_its_separate_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lesson = replace(Catalog.load().get("sql-01"), prerequisites=())
    catalog = Catalog(tmp_path, [lesson])
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(catalog, progress_path=tmp_path / "progress.json")

    def execute(lesson_id: str, code: str, *, timeout_seconds: int) -> dict[str, Any]:
        assert timeout_seconds == 60
        return {
            "returncode": 0,
            "output": "whole script done",
            "elapsed_seconds": 0.01,
            "language": "sql",
            "mode": "lesson",
        }

    monkeypatch.setattr(server.sql_lessons, "run", execute)
    try:
        result = server.action(
            {"action": "run-lesson", "lesson_id": "sql-01", "code": "SELECT 42;"}
        )
        assert result["receipt_saved"] is True
        assert (
            server.action(
                {
                    "action": "classroom-history",
                    "lesson_id": "sql-01",
                    "language": "sql",
                    "mode": "snippet",
                }
            )["history"]
            == []
        )
        history = server.action(
            {
                "action": "classroom-history",
                "lesson_id": "sql-01",
                "language": "sql",
                "mode": "lesson",
            }
        )["history"]
        assert history[0]["id"] == result["receipt_id"] and history[0]["mode"] == "lesson"
    finally:
        server.server_close()
