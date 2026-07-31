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

        status, reader = _request(f"{server.url}lesson-pages/sql-01.html")
        assert status == 200
        assert 'const SERVER_TOKEN = "test-token";' in reader
        assert 'const SERVER_TOKEN = "";' not in reader
        assert 'action: "jupyter-sql"' in reader

        status, reference = _request(f"{server.url}reference-pages/docs/setup/windows.md.html")
        assert status == 200
        assert "<title>Windows setup · DS60 reference</title>" in reference
        assert "Back to lessons" in reference

        status, raw = _request(f"{server.url}api/status", token=server.token)
        assert status == 200
        status_payload = json.loads(raw)
        assert status_payload["completed"] == []
        assert any(item["name"] == "Python" for item in status_payload["diagnostics"])

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

        with pytest.raises(HTTPError) as rebinding:
            _request(server.url, host="attacker.example")
        assert rebinding.value.code == 400

        with pytest.raises(HTTPError) as raw_source:
            _request(f"{server.url}README.md")
        assert raw_source.value.code == 404
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
    guide_path = catalog.resolve(catalog.get("python-01").guide_path)
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.touch()
    solution_paths = tuple(
        catalog.resolve(path) for path in catalog.get("python-01").solution_paths
    )
    for solution_path in solution_paths:
        solution_path.parent.mkdir(parents=True, exist_ok=True)
        solution_path.touch()
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(PortalLauncher, "_code_executable", staticmethod(lambda: "code"))
    launcher = PortalLauncher(catalog)

    assert launcher.command("open-repo") == ("code", str(tmp_path))
    assert launcher.command("open-lesson", lesson_id="python-01") == (
        "code",
        "--reuse-window",
        str(tmp_path),
        "--goto",
        str(learner_path),
    )
    assert launcher.command(
        "open-artifact",
        lesson_id="python-01",
        artifact="guide",
    )[-1] == str(guide_path)
    assert launcher.command(
        "open-artifact",
        lesson_id="python-01",
        artifact="solution",
        solution_index=1,
    )[-1] == str(solution_paths[1])
    assert launcher.command("jupyter-lesson", lesson_id="python-01") == (
        str(python),
        "-m",
        "jupyterlab",
        str(learner_path),
    )
    assert launcher.command("jupyter-python")[:4] == (
        str(python),
        "-m",
        "jupyterlab",
        str(tmp_path / "python" / "ds-60day" / "notebooks"),
    )
    assert launcher.command("jupyter-sql") == (
        str(python),
        "-m",
        "jupyterlab",
        str(tmp_path / "bridge" / "professional" / "notebooks"),
    )
    with pytest.raises(PortalError, match="Unsupported portal action"):
        launcher.command("shell")
    with pytest.raises(KeyError, match="Unknown lesson"):
        launcher.command("open-lesson", lesson_id="does-not-exist")
    with pytest.raises(PortalError, match="solution index"):
        launcher.command(
            "open-artifact",
            lesson_id="python-01",
            artifact="solution",
            solution_index=99,
        )


def test_launcher_can_disable_every_native_process_action() -> None:
    launcher = PortalLauncher(Catalog.load(), enabled=False)

    with pytest.raises(PortalError, match="Native launches are disabled"):
        launcher.launch("open-repo")


def test_windows_vscode_command_shim_resolves_to_native_executable(tmp_path: Path) -> None:
    install = tmp_path / "Microsoft VS Code"
    shim = install / "bin" / "code.cmd"
    executable = install / "Code.exe"
    shim.parent.mkdir(parents=True)
    shim.touch()
    executable.touch()

    assert PortalLauncher._native_code_path(shim) == str(executable)

    orphan = tmp_path / "orphan" / "code.cmd"
    orphan.parent.mkdir()
    orphan.touch()
    assert PortalLauncher._native_code_path(orphan) is None


def test_launcher_supports_conda_prefix_and_rejects_non_notebook_jupyter(
    tmp_path: Path,
) -> None:
    source_catalog = Catalog.load()
    catalog = Catalog(tmp_path, tuple(source_catalog))
    conda_python = tmp_path / ".venv" / "python.exe"
    conda_python.parent.mkdir(parents=True)
    conda_python.touch()
    sql_path = catalog.resolve(catalog.get("sql-01").lesson_path)
    sql_path.parent.mkdir(parents=True)
    sql_path.touch()
    launcher = PortalLauncher(catalog)

    assert launcher.command("jupyter-python")[0] == str(conda_python)
    with pytest.raises(PortalError, match="open it in VS Code instead"):
        launcher.command("jupyter-lesson", lesson_id="sql-01")


def test_launcher_generates_cataloged_sql_notebook_before_jupyter(
    tmp_path: Path,
) -> None:
    source_catalog = Catalog.load()
    catalog = Catalog(tmp_path, tuple(source_catalog))
    lesson = catalog.get("sql-01")
    for relative in (lesson.lesson_path, lesson.guide_path):
        path = catalog.resolve(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "SELECT 1;\n" if path.suffix == ".sql" else "# SQL lesson\n",
            encoding="utf-8",
        )
    python = tmp_path / ".venv" / "Scripts" / "python.exe"
    python.parent.mkdir(parents=True)
    python.touch()

    command = PortalLauncher(catalog).command(
        "jupyter-sql",
        lesson_id="sql-01",
        artifact="lesson",
        solution_index=1,
    )

    notebook = tmp_path / ".learning" / "sql" / "sql-01" / "lesson" / "guided.ipynb"
    sql_copy = notebook.parent / "workspace" / lesson.lesson_path
    assert command == (
        str(python),
        "-m",
        "jupyterlab",
        str(notebook),
    )
    assert notebook.is_file()
    assert sql_copy.read_text(encoding="utf-8") == "SELECT 1;\n"
    with pytest.raises(PortalError, match="one-based"):
        PortalLauncher(catalog).command(
            "jupyter-sql",
            lesson_id="sql-01",
            solution_index=0,
        )
