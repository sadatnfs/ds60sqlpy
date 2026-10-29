"""Offline delivery, owned lifecycle and actual bounded ASGI-body contracts."""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import re
import shutil
import subprocess
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "courses/python-web/projects/web-lab"


def test_compose_keeps_state_owned_and_ports_loopback() -> None:
    yaml = importlib.import_module("yaml")
    config = yaml.safe_load((PROJECT / "compose.yaml").read_text())
    services = config["services"]
    assert set(services) == {"postgres", "migrate", "flask", "fastapi", "django", "worker"}
    assert "ports" not in services["postgres"]
    # The official image's temporary initialization server exposes only a Unix socket.
    # Migrations in another container require the final server's TCP listener.
    assert services["postgres"]["healthcheck"]["test"] == [
        "CMD",
        "pg_isready",
        "-h",
        "127.0.0.1",
        "-U",
        "web_lab",
        "-d",
        "web_lab",
    ]
    for name, service in services.items():
        assert service["labels"]["ds60.workshop"] == "python-web-lab"
        assert service["pull_policy"] == "never"
        if name != "postgres":
            assert service["read_only"] is True
            assert service["cap_drop"] == ["ALL"]
            assert service["tmpfs"] == ["/tmp:rw,nosuid,exec,size=64m"]
        for mapping in service.get("ports", []):
            assert mapping.startswith("127.0.0.1:")
    assert config["volumes"]["postgres-data"]["labels"]["ds60.workshop"] == "python-web-lab"
    launcher = (PROJECT / "workshop").read_text()
    assert "source .workshop" not in launcher
    assert (
        "down -v" not in launcher and "volume rm" not in launcher and "system prune" not in launcher
    )
    assert '[[ "$before" == "$after" ]]' in launcher
    assert re.search(r"--verify-saved\s*<\s*\.workshop/acceptance\.json", launcher)


def test_local_explorer_assets_and_no_untrusted_html_sink() -> None:
    from html.parser import HTMLParser

    class Assets(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.urls: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag in {"script", "link", "iframe", "img"}:
                self.urls.extend(
                    value for key, value in attrs if key in {"src", "href"} and value is not None
                )

    for name in ("index.html", "docs.html"):
        parser = Assets()
        parser.feed((PROJECT / "static" / name).read_text())
        assert parser.urls and all(url.startswith("/static/") for url in parser.urls)
        for url in parser.urls:
            assert (PROJECT / url.lstrip("/")).is_file()
    for name in ("app.js", "docs.js"):
        source = (PROJECT / "static" / name).read_text()
        assert ".innerHTML" not in source
        assert "https://" not in source and "http://" not in source
    fastapi = ast.parse((PROJECT / "fastapi_app.py").read_text())
    constructor = next(
        node
        for node in ast.walk(fastapi)
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "FastAPI"
    )
    keywords = {entry.arg: ast.literal_eval(entry.value) for entry in constructor.keywords}
    assert keywords["docs_url"] is None and keywords["redoc_url"] is None
    assert "collectstatic" in (PROJECT / "Dockerfile").read_text()
    assert "pip install" not in (PROJECT / "Dockerfile").read_text()


def test_asgi_actual_body_limit_includes_chunked_input() -> None:
    pytest.importorskip("starlette")
    path = PROJECT / "request_limits.py"
    spec = importlib.util.spec_from_file_location("web_body_limit", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    async def exercise(chunks: list[bytes]) -> tuple[list[dict[str, Any]], list[bytes]]:
        events: list[dict[str, Any]] = []
        entered: list[bytes] = []
        messages = iter(
            [
                {"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1}
                for index, chunk in enumerate(chunks)
            ]
        )

        async def receive() -> dict[str, Any]:
            return next(messages)

        async def send(event: dict[str, Any]) -> None:
            events.append(event)

        async def app(
            scope: dict[str, Any],
            receive: Callable[[], Awaitable[dict[str, Any]]],
            send: Callable[[dict[str, Any]], Awaitable[None]],
        ) -> None:
            entered.append((await receive())["body"])
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/",
            "headers": [],
            "asgi": {"version": "3.0"},
        }
        await module.BodyLimit(app, limit=5)(scope, receive, send)
        return events, entered

    accepted, bodies = asyncio.run(exercise([b"ab", b"cde"]))
    assert bodies == [b"abcde"] and accepted[0]["status"] == 200
    refused, bodies = asyncio.run(exercise([b"abc", b"def"]))
    assert bodies == [] and refused[0]["status"] == 413


def test_browser_form_retains_event_target_across_awaits() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the actual JavaScript event-lifetime regression")
    result = subprocess.run(
        [node, str(PROJECT / "check_ui.mjs")],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "refreshes committed data" in result.stdout
