"""Local startup must not consult reverse DNS before serving an offline course."""

from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom_http import CourseHTTPServer
from ds60sqlpy.http_server import LocalHTTPServer, LocalThreadingHTTPServer
from ds60sqlpy.module_worker import WorkerHTTPServer, WorkerState


class ReadyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ready")

    def log_message(self, format: str, *args: object) -> None:
        pass


def no_dns(*args: object, **kwargs: object) -> str:
    raise AssertionError("A local server must not perform reverse DNS during startup")


@pytest.mark.parametrize("server_type", [LocalHTTPServer, LocalThreadingHTTPServer])
def test_local_server_binds_and_serves_while_reverse_dns_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, server_type: type[LocalHTTPServer]
) -> None:
    monkeypatch.setattr(socket, "getfqdn", no_dns)
    server = server_type(("127.0.0.1", 0), ReadyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert server.server_name == "127.0.0.1" and server.server_port > 0
        opener = build_opener(ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{server.server_port}/", timeout=3) as response:
            assert response.status == 200 and response.read() == b"ready"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    assert not thread.is_alive()


def test_worker_and_classroom_use_dns_independent_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(socket, "getfqdn", no_dns)
    state = WorkerState("python-core", ready=True, isolate_jobs=False)
    worker = WorkerHTTPServer(("127.0.0.1", 0), state, "x" * 64)
    try:
        assert worker.server_name == "127.0.0.1" and worker.server_port > 0
    finally:
        worker.server_close()
    classroom = CourseHTTPServer(Catalog.load(), progress_path=tmp_path / "progress.json")
    try:
        assert classroom.server_name == "127.0.0.1" and classroom.server_port > 0
    finally:
        classroom.server_close()
