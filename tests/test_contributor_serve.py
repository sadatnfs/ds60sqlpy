"""The contributor CLI serves the same classroom with no native launch API."""

from __future__ import annotations

from pathlib import Path

import pytest

from ds60sqlpy import cli
from ds60sqlpy.catalog import Catalog


def test_serve_passes_explicit_options_to_the_unified_classroom(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(__file__).resolve().parents[1]
    calls: list[tuple[Path, int, bool, str | None]] = []

    def serve(catalog: Catalog, *, port: int, open_browser: bool, python: str | None) -> None:
        calls.append((catalog.repo_root, port, open_browser, python))

    monkeypatch.setattr(cli, "serve_lab", serve)
    assert (
        cli.main(
            [
                "--repo",
                str(root),
                "serve",
                "--port",
                "8766",
                "--no-browser",
                "--python",
                "/prepared/.venv/bin/python",
            ]
        )
        == 0
    )
    assert calls == [(root, 8766, False, "/prepared/.venv/bin/python")]


def test_removed_native_portal_is_not_a_cli_command() -> None:
    with pytest.raises(SystemExit) as rejected:
        cli.main(["portal"])
    assert rejected.value.code == 2


def test_serve_reports_bind_failure_without_a_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def unavailable(*args: object, **kwargs: object) -> None:
        raise OSError("Address already in use")

    monkeypatch.setattr(cli, "serve_lab", unavailable)
    assert cli.main(["serve", "--no-browser"]) == 2
    assert "Address already in use" in capsys.readouterr().err
