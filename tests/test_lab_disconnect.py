"""Expected client disconnects must not produce unhandled Lab GET tracebacks."""

from __future__ import annotations

from http import HTTPStatus
from http.client import HTTPMessage
from types import SimpleNamespace
from typing import Any, cast

import pytest

from ds60sqlpy.lab import LabRequestHandler


class BodyWriter:
    def __init__(self, error: OSError | None = None) -> None:
        self.error = error
        self.calls = 0
        self.body: bytes | None = None

    def write(self, body: bytes) -> int:
        self.calls += 1
        if self.error is not None:
            raise self.error
        self.body = body
        return len(body)


def handler_for(
    path: str, writer: BodyWriter, monkeypatch: pytest.MonkeyPatch
) -> tuple[LabRequestHandler, list[int]]:
    handler = LabRequestHandler.__new__(LabRequestHandler)
    handler.path = path
    headers = HTTPMessage()
    headers["Host"] = "127.0.0.1:8765"
    handler.headers = headers
    handler.server = cast(Any, SimpleNamespace(expected_host="127.0.0.1:8765", token="test-token"))
    handler.wfile = cast(Any, writer)
    statuses: list[int] = []

    def send_response(status: int) -> None:
        statuses.append(status)

    def send_header(name: str, value: str) -> None:
        return None

    def end_headers() -> None:
        return None

    monkeypatch.setattr(handler, "send_response", send_response)
    monkeypatch.setattr(handler, "send_header", send_header)
    monkeypatch.setattr(handler, "end_headers", end_headers)
    return handler, statuses


@pytest.mark.parametrize("path", ["/classroom", "/browser-sandbox"])
@pytest.mark.parametrize("disconnect", [BrokenPipeError, ConnectionResetError])
def test_expected_disconnect_during_get_body_is_ignored(
    path: str, disconnect: type[OSError], monkeypatch: pytest.MonkeyPatch
) -> None:
    writer = BodyWriter(disconnect("client left after headers"))
    handler, statuses = handler_for(path, writer, monkeypatch)

    handler.do_GET()

    assert statuses == [HTTPStatus.OK]
    assert writer.calls == 1


@pytest.mark.parametrize("path", ["/classroom", "/browser-sandbox"])
def test_other_get_body_error_still_propagates(path: str, monkeypatch: pytest.MonkeyPatch) -> None:
    writer = BodyWriter(OSError("unrelated body failure"))
    handler, statuses = handler_for(path, writer, monkeypatch)

    with pytest.raises(OSError, match="unrelated body failure"):
        handler.do_GET()

    assert statuses == [HTTPStatus.OK]
    assert writer.calls == 1


def test_unrelated_header_error_still_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    writer = BodyWriter()
    handler, statuses = handler_for("/classroom", writer, monkeypatch)

    def broken_header(name: str, value: str) -> None:
        raise OSError("unrelated header failure")

    monkeypatch.setattr(handler, "send_header", broken_header)
    with pytest.raises(OSError, match="unrelated header failure"):
        handler.do_GET()

    assert statuses == [HTTPStatus.OK]
    assert writer.calls == 0


def test_complete_classroom_body_is_still_written(monkeypatch: pytest.MonkeyPatch) -> None:
    writer = BodyWriter()
    handler, statuses = handler_for("/classroom", writer, monkeypatch)

    handler.do_GET()

    assert statuses == [HTTPStatus.OK]
    assert writer.calls == 1
    assert writer.body is not None and b"<html" in writer.body.lower()
