from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.portal import PortalError, PortalLauncher, create_portal_server


def _request(
    url: str,
    *,
    token: str | None = None,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    origin: str | None = None,
) -> tuple[int, str]:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {}
    if token is not None:
        headers["X-DS60-Token"] = token
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if origin is not None:
        headers["Origin"] = origin
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=3) as response:  # noqa: S310 - loopback test server
        return response.status, response.read().decode()


def test_portal_serves_injected_guide_and_persists_progress(tmp_path: Path) -> None:
    catalog = Catalog.load()
    progress_path = tmp_path / "progress.json"
    server = create_portal_server(
        catalog,
        progress_path=progress_path,
        allow_launches=False,
        token="test-token",
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, guide = _request(server.url)
        assert status == 200
        assert 'const SERVER_TOKEN = "test-token";' in guide
        assert 'const SERVER_TOKEN = "";' not in guide

        status, raw = _request(f"{server.url}api/status", token=server.token)
        assert status == 200
        assert json.loads(raw)["completed"] == []

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


def test_portal_rejects_cross_origin_and_hidden_files(tmp_path: Path) -> None:
    server = create_portal_server(
        Catalog.load(),
        progress_path=tmp_path / "progress.json",
        allow_launches=False,
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

        with pytest.raises(HTTPError) as hidden_file:
            _request(f"{server.url}.git/config")
        assert hidden_file.value.code == 404

        with pytest.raises(HTTPError) as windows_hidden_file:
            _request(f"{server.url}folder%5C..%5C.git%5Cconfig")
        assert windows_hidden_file.value.code == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_launcher_builds_only_cataloged_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_catalog = Catalog.load()
    catalog = Catalog(tmp_path, tuple(source_catalog))
    learner_path = catalog.resolve(catalog.get("python-01").lesson_path)
    learner_path.parent.mkdir(parents=True)
    learner_path.touch()
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(PortalLauncher, "_code_executable", staticmethod(lambda: "code"))
    launcher = PortalLauncher(catalog)

    assert launcher.command("open-repo") == ("code", str(tmp_path))
    assert launcher.command("open-lesson", lesson_id="python-01") == (
        "code",
        "-g",
        str(learner_path),
    )
    assert launcher.command("jupyter-python")[:4] == (
        str(python),
        "-m",
        "jupyterlab",
        str(tmp_path / "python" / "ds-60day" / "notebooks"),
    )
    with pytest.raises(PortalError, match="Unsupported portal action"):
        launcher.command("shell")
    with pytest.raises(KeyError, match="Unknown lesson"):
        launcher.command("open-lesson", lesson_id="does-not-exist")
