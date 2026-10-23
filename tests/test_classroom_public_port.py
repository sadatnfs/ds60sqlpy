"""A mapped Docker port retains one exact Host/Origin authentication boundary."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lab import LabServer
from ds60sqlpy.portal import PortalServer

ROOT = Path(__file__).resolve().parents[1]


def test_container_public_port_retains_exact_host_origin_and_token_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DS60_CONTAINER", "1")
    monkeypatch.setenv("DS60_PUBLIC_PORT", "80")
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    original = PortalServer.__init__

    def bind_only_loopback(self: PortalServer, catalog: Catalog, **kwargs: Any) -> None:
        assert kwargs["bind_host"] == "0.0.0.0"
        kwargs["bind_host"] = "127.0.0.1"
        original(self, catalog, **kwargs)

    monkeypatch.setattr(PortalServer, "__init__", bind_only_loopback)
    server = LabServer(Catalog.load(), container=True, progress_path=tmp_path / "progress.json")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def request(method: str, path: str, headers: dict[str, str]) -> int:
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            body = (
                json.dumps({"action": "lesson", "lesson_id": "python-01"})
                if method == "POST"
                else None
            )
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            response.read()
            return response.status
        finally:
            connection.close()

    try:
        assert server.expected_host == "127.0.0.1" and server.url == "http://127.0.0.1/"
        assert request("GET", "/journeys", {"Host": server.expected_host}) == 200
        assert request("GET", "/journeys", {"Host": f"127.0.0.1:{server.server_port}"}) == 400
        headers = {
            "Host": server.expected_host,
            "Origin": "http://127.0.0.1",
            "X-DS60-Token": server.token,
            "Content-Type": "application/json",
        }
        assert request("POST", "/api/lab", headers) == 200
        assert request("POST", "/api/lab", {**headers, "Host": "attacker.invalid"}) == 400
        assert request("POST", "/api/lab", {**headers, "X-DS60-Token": "wrong"}) == 403
        assert (
            request(
                "POST", "/api/lab", {**headers, "Origin": f"http://127.0.0.1:{server.server_port}"}
            )
            == 403
        )
        assert (
            request("POST", "/api/lab", {k: v for k, v in headers.items() if k != "Origin"}) == 403
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("value", ["0", "65536", "-1", " 80", "80:extra", "localhost", "١٢"])
def test_invalid_public_port_is_rejected_before_a_socket_is_bound(
    value: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DS60_CONTAINER", "1")
    monkeypatch.setenv("DS60_PUBLIC_PORT", value)

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("invalid configuration reached socket creation")

    monkeypatch.setattr(PortalServer, "__init__", forbidden)
    with pytest.raises(ValueError, match="DS60_PUBLIC_PORT"):
        LabServer(Catalog.load(), container=True, progress_path=tmp_path / "progress.json")


def test_native_server_does_not_adopt_a_container_public_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DS60_PUBLIC_PORT", "80")
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(Catalog.load(), progress_path=tmp_path / "progress.json")
    try:
        assert server.expected_host == f"127.0.0.1:{server.server_port}"
    finally:
        server.server_close()


def test_container_healthcheck_uses_public_host_on_the_internal_connection() -> None:
    observed = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            observed.append(self.headers.get("Host"))
            self.send_response(200 if self.headers.get("Host") == "127.0.0.1" else 400)
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        environment = dict(os.environ, DS60_LAB_PORT=str(server.server_port), DS60_PUBLIC_PORT="80")
        result = subprocess.run(
            [sys.executable, str(ROOT / "docker/healthcheck.py")],
            env=environment,
            capture_output=True,
            timeout=5,
        )
        assert result.returncode == 0 and observed == ["127.0.0.1"]
        environment["DS60_PUBLIC_PORT"] = "0"
        result = subprocess.run(
            [sys.executable, str(ROOT / "docker/healthcheck.py")],
            env=environment,
            capture_output=True,
            timeout=5,
        )
        assert result.returncode == 1 and observed == ["127.0.0.1"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
