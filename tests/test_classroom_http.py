from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom_http import CourseHTTPServer, CourseRequestHandler


def test_idle_or_partial_request_timeout_does_not_break_logging(
    capsys: pytest.CaptureFixture[str],
) -> None:
    handler = object.__new__(CourseRequestHandler)
    handler.log_message("Request timed out: %r", TimeoutError())
    handler.path = "/api/lab"
    handler.log_message("Request timed out: %r", TimeoutError())
    assert capsys.readouterr().out == ""


def _request(
    url: str,
    *,
    token: str | None = None,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    origin: str | None = None,
    host: str | None = None,
) -> tuple[int, str]:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {}
    if token is not None:
        headers["X-DS60-Token"] = token
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if origin is not None:
        headers["Origin"] = origin
    if host is not None:
        headers["Host"] = host
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=3) as response:  # noqa: S310 - loopback test server
        return response.status, response.read().decode()


def test_classroom_http_serves_injected_guide_and_persists_progress(tmp_path: Path) -> None:
    catalog = Catalog.load()
    progress_path = tmp_path / "progress.json"
    server = CourseHTTPServer(
        catalog,
        progress_path=progress_path,
        token="test-token",
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, guide = _request(server.url)
        assert status == 200
        assert 'const SERVER_TOKEN = "test-token";' in guide
        assert 'const SERVER_TOKEN = "";' not in guide

        status, reader = _request(f"{server.url}lesson-pages/sql-01.html")
        assert status == 200
        assert 'const SERVER_TOKEN = "test-token";' in reader
        assert 'const SERVER_TOKEN = "";' not in reader
        assert "const LAB_MODE = true;" in reader

        status, reference = _request(f"{server.url}reference-pages/docs/setup/windows.md.html")
        assert status == 200
        assert "· DS60 reference</title>" in reference
        assert "WSL 2" in reference
        assert "Back to lessons" in reference

        status, raw = _request(f"{server.url}api/status", token=server.token)
        assert status == 200
        status_payload = json.loads(raw)
        assert status_payload["completed"] == []
        assert status_payload["mode"] == "classroom"

        status, raw = _request(
            f"{server.url}api/progress",
            token=server.token,
            method="POST",
            origin=server.url.rstrip("/"),
            payload={"lesson_id": "python-01", "complete": True},
        )
        assert status == 200
        assert json.loads(raw)["ok"]
        assert "python-01" in progress_path.read_text(encoding="utf-8")

        _request(
            f"{server.url}api/progress/replace",
            token=server.token,
            method="POST",
            origin=server.url.rstrip("/"),
            payload={"completed": ["sql-01"]},
        )
        saved = json.loads(progress_path.read_text(encoding="utf-8"))
        assert list(saved["completed"]) == ["sql-01"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_classroom_http_rejects_cross_origin_and_hidden_files(tmp_path: Path) -> None:
    server = CourseHTTPServer(
        Catalog.load(),
        progress_path=tmp_path / "progress.json",
        token="test-token",
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(HTTPError) as cross_origin:
            _request(
                f"{server.url}api/progress",
                token=server.token,
                method="POST",
                origin="https://attacker.example",
                payload={"lesson_id": "python-01", "complete": True},
            )
        assert cross_origin.value.code == 403

        with pytest.raises(HTTPError) as missing_origin:
            _request(
                f"{server.url}api/progress",
                token=server.token,
                method="POST",
                payload={"lesson_id": "python-01", "complete": True},
            )
        assert missing_origin.value.code == 403

        with pytest.raises(HTTPError) as hidden_file:
            _request(f"{server.url}.git/config")
        assert hidden_file.value.code == 404

        with pytest.raises(HTTPError) as windows_hidden_file:
            _request(f"{server.url}folder%5C..%5C.git%5Cconfig")
        assert windows_hidden_file.value.code == 404

        with pytest.raises(HTTPError) as rebinding:
            _request(server.url, host="attacker.example")
        assert rebinding.value.code == 400

        with pytest.raises(HTTPError) as raw_source:
            _request(f"{server.url}README.md")
        assert raw_source.value.code == 404

        with pytest.raises(HTTPError) as native_launch:
            _request(
                f"{server.url}api/launch",
                token=server.token,
                method="POST",
                origin=server.url.rstrip("/"),
                payload={"action": "open-repo"},
            )
        assert native_launch.value.code == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.mark.parametrize(
    "payload,content_type", [(b"[]", "application/json"), (b"{}", "text/plain")]
)
def test_progress_api_rejects_invalid_body_without_changing_progress(
    tmp_path: Path, payload: bytes, content_type: str
) -> None:
    server = CourseHTTPServer(Catalog.load(), progress_path=tmp_path / "progress.json")
    server.progress.mark_complete("python-01")
    original = server.progress.path.read_bytes()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = Request(
            server.url + "api/progress",
            data=payload,
            headers={
                "X-DS60-Token": server.token,
                "Origin": server.url.rstrip("/"),
                "Content-Type": content_type,
            },
            method="POST",
        )
        with pytest.raises(HTTPError) as rejected:
            urlopen(request, timeout=3)
        assert rejected.value.code == 400
        assert server.progress.path.read_bytes() == original
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
