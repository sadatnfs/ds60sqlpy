"""Bounded retries recover transport races without hiding fixture-contract failures."""

from __future__ import annotations

import importlib.util
import io
import socket
import threading
import urllib.error
import urllib.request
from http.client import HTTPMessage, IncompleteRead
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
URL = "http://hello:8080/version"
VERSION = "ds60-fixture-v1"


@pytest.fixture
def fixture() -> Any:
    spec = importlib.util.spec_from_file_location(
        "retry_fixture", ROOT / "docker/kubernetes/fixture.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Clock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, duration: float) -> None:
        assert duration > 0
        self.sleeps.append(duration)
        self.now += duration


class Response(io.BytesIO):
    status = 200

    def read(self, size: int | None = -1) -> bytes:
        assert size == 257
        return super().read(size)


def install_clock(fixture: Any, monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(
        fixture, "time", SimpleNamespace(monotonic=clock.monotonic, sleep=clock.sleep)
    )
    return clock


def install_opener(fixture: Any, monkeypatch: pytest.MonkeyPatch, opener: Any) -> None:
    def build(*handlers: Any) -> Any:
        proxy = next(item for item in handlers if isinstance(item, urllib.request.ProxyHandler))
        assert vars(proxy)["proxies"] == {}
        assert any(isinstance(item, fixture.NoRedirect) for item in handlers)
        return opener

    monkeypatch.setattr(fixture.urllib.request, "build_opener", build)


@pytest.mark.parametrize(
    "error",
    [
        ConnectionRefusedError("synthetic route not ready"),
        urllib.error.URLError(socket.gaierror(socket.EAI_AGAIN, "synthetic DNS delay")),
        urllib.error.URLError(socket.gaierror(socket.EAI_NONAME, "synthetic name not ready")),
    ],
)
def test_transient_connection_or_dns_failure_recovers_at_the_same_url(
    fixture: Any, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    clock = install_clock(fixture, monkeypatch)
    calls: list[tuple[str, float]] = []

    def open_url(url: str, *, timeout: float) -> Response:
        calls.append((url, timeout))
        if len(calls) == 1:
            raise error
        return Response((VERSION + "\n").encode())

    install_opener(fixture, monkeypatch, SimpleNamespace(open=open_url))
    assert fixture.check_version(URL, VERSION)
    assert [url for url, _ in calls] == [URL, URL]
    assert all(0 < timeout <= 2 for _, timeout in calls)
    assert clock.sleeps and clock.now < 6


def test_persistent_transport_failure_exhausts_one_budget_without_late_attempts(
    fixture: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = install_clock(fixture, monkeypatch)
    calls: list[tuple[float, float]] = []

    def open_url(url: str, *, timeout: float) -> Response:
        calls.append((clock.now, timeout))
        assert timeout <= 6 - clock.now
        clock.now += timeout
        raise TimeoutError("synthetic timeout")

    install_opener(fixture, monkeypatch, SimpleNamespace(open=open_url))
    assert not fixture.check_version(URL, VERSION)
    assert 1 < len(calls) <= 4
    assert all(start < 6 and timeout <= 2 for start, timeout in calls)
    assert calls[-1][1] < calls[0][1]
    assert clock.now == pytest.approx(6)


@pytest.mark.parametrize("body", [b"wrong-version", b"x" * 257, b"\xff"])
def test_wrong_oversized_or_malformed_body_is_not_retried(
    fixture: Any, monkeypatch: pytest.MonkeyPatch, body: bytes
) -> None:
    clock = install_clock(fixture, monkeypatch)
    calls = 0

    def open_url(url: str, *, timeout: float) -> Response:
        nonlocal calls
        calls += 1
        return Response(body)

    install_opener(fixture, monkeypatch, SimpleNamespace(open=open_url))
    assert not fixture.check_version(URL, VERSION)
    assert calls == 1 and clock.sleeps == []


@pytest.mark.parametrize(
    "error",
    [
        PermissionError("synthetic local permission error"),
        urllib.error.URLError("synthetic nontransport protocol failure"),
        IncompleteRead(b"truncated-body", 100),
        urllib.error.HTTPError(URL, 404, "synthetic missing endpoint", HTTPMessage(), None),
    ],
)
def test_nontransient_and_malformed_response_errors_fail_without_retry(
    fixture: Any, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    clock = install_clock(fixture, monkeypatch)
    calls = 0

    def open_url(url: str, *, timeout: float) -> Response:
        nonlocal calls
        calls += 1
        raise error

    install_opener(fixture, monkeypatch, SimpleNamespace(open=open_url))
    assert not fixture.check_version(URL, VERSION)
    assert calls == 1 and clock.sleeps == []


@pytest.mark.parametrize(
    "url",
    [
        "https://hello:8080/version",
        "http://external.example:8080/version",
        "http://hello:8080/message",
        "http://hello:8080/version?extra=1",
        "http://user@hello:8080/version",
    ],
)
def test_invalid_url_is_rejected_before_opener_or_retry(
    fixture: Any, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Invalid fixture URL must not open a connection")

    monkeypatch.setattr(fixture.urllib.request, "build_opener", forbidden)
    with pytest.raises(ValueError):
        fixture.check_version(url, VERSION)


def test_version_and_both_message_reads_share_the_original_deadline(
    fixture: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    clock = install_clock(fixture, monkeypatch)
    calls: list[tuple[str, float]] = []

    def open_url(url: str, *, timeout: float) -> Response:
        calls.append((url, timeout))
        clock.now += timeout
        body = VERSION if url.endswith("/version") else "reviewer"
        return Response((body + "\n").encode())

    install_opener(fixture, monkeypatch, SimpleNamespace(open=open_url))
    assert (
        fixture.main(
            [
                "client",
                "--url",
                URL,
                "--expect",
                VERSION,
                "--expect-message",
                "reviewer",
                "--expect-file-message",
                "reviewer",
            ]
        )
        == 2
    )
    assert [url for url, _ in calls] == [
        URL,
        "http://hello:8080/message",
        "http://hello:8080/file-message",
    ]
    assert clock.now == pytest.approx(6)
    assert "CHECK_FAILED" in capsys.readouterr().out


@pytest.mark.parametrize("first_status", [302, 503])
def test_real_http_redirect_is_refused_and_service_unavailable_can_recover(
    fixture: Any, first_status: int
) -> None:
    requests: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def do_GET(self) -> None:
            requests.append(self.path)
            status = first_status if len(requests) == 1 else 200
            body = (VERSION + "\n").encode() if status == 200 else b""
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            if status == 302:
                self.send_header("Location", "/unexpected-redirect")
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = fixture.check_version(f"http://127.0.0.1:{server.server_port}/version", VERSION)
        assert result is (first_status == 503)
        assert requests == (["/version", "/version"] if first_status == 503 else ["/version"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
