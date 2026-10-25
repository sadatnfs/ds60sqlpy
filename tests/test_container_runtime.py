"""Validate container identities and durable learning-folder boundaries."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from ds60sqlpy.container_runtime import (
    ContainerSettings,
    container_settings,
    learning_environment,
    prepare_workspace_root,
    warm_matplotlib,
)
from ds60sqlpy.sql_runner import DEFAULT_DATABASE_URL, default_course_database_url


def test_host_and_container_database_defaults_are_distinct_and_passwords_are_encoded() -> None:
    assert urlsplit(default_course_database_url({})).port == 55432
    assert default_course_database_url({}) == DEFAULT_DATABASE_URL
    value = default_course_database_url(
        {
            "DS60_CONTAINER": "1",
            "DS60_COURSE_USER": "admin",
            "DS60_COURSE_PASSWORD": "fake @:/?password",
        }
    )
    parsed = urlsplit(value)
    assert parsed.hostname == "127.0.0.1"
    assert parsed.port == 5432
    assert parsed.username == "admin"
    assert parsed.password == "fake%20%40%3A%2F%3Fpassword"


def test_container_identity_and_alternate_port_are_explicit() -> None:
    settings = container_settings(
        {"DS60_CONTAINER": "1", "DS60_UID": "501", "DS60_GID": "20", "DS60_LAB_PORT": "8766"}
    )
    assert settings == ContainerSettings(501, 20, 8766, False)
    with pytest.raises(ValueError, match="container image"):
        container_settings({})


@pytest.mark.parametrize(
    "key,value",
    [
        ("DS60_UID", "-1"),
        ("DS60_UID", "501; command"),
        ("DS60_GID", "unknown"),
        ("DS60_LAB_PORT", "0"),
        ("DS60_LAB_PORT", "65536"),
        ("DS60_COURSE_USER", "ds60_admin"),
    ],
)
def test_bad_runtime_settings_fail_before_storage_changes(key: str, value: str) -> None:
    with pytest.raises(ValueError):
        container_settings({"DS60_CONTAINER": "1", key: value})


def test_rootless_zero_requires_both_explicit_intent_and_actual_namespace_mapping() -> None:
    settings = {"DS60_CONTAINER": "1", "DS60_UID": "0", "DS60_ROOTLESS": "1"}
    assert container_settings(settings, uid_map="0 501 1\n1 100000 65536").uid == 0
    with pytest.raises(ValueError, match="verified rootless"):
        container_settings(settings, uid_map="0 0 4294967295")
    with pytest.raises(ValueError, match="verified rootless"):
        container_settings({"DS60_CONTAINER": "1", "DS60_UID": "0"}, uid_map="0 501 1")


def test_narrow_initialization_chowns_only_ephemeral_workspace_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    learning = workspace / ".learning"
    learning.mkdir(parents=True)
    note = learning / "coaching.json"
    note.write_text('{"my_notes":"keep"}', encoding="utf-8")
    original = (note.read_bytes(), note.stat().st_mode, learning.stat().st_mode)
    calls: list[tuple[Path, int, int]] = []
    monkeypatch.setattr(os, "geteuid", lambda: 0, raising=False)
    monkeypatch.setattr(
        os, "chown", lambda path, uid, gid: calls.append((path, uid, gid)), raising=False
    )
    # Hosted macOS already owns files as 501:20. Choose a different target
    # rather than accidentally exercising the correct already-owned no-op.
    current = workspace.stat()
    target = (current.st_uid + 1, current.st_gid + 1)
    prepare_workspace_root(workspace, ContainerSettings(*target, 8765, False))
    assert calls == [(workspace, *target)]
    assert (note.read_bytes(), note.stat().st_mode, learning.stat().st_mode) == original


def test_already_owned_workspace_does_not_chown_learner_storage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "owned"
    learning = workspace / ".learning"
    learning.mkdir(parents=True)
    note = learning / "notes.txt"
    note.write_text("Keep my notes", encoding="utf-8")
    owner = workspace.stat()
    before = (note.read_bytes(), note.stat().st_mode, learning.stat().st_mode)
    monkeypatch.setattr(os, "geteuid", lambda: 0, raising=False)

    def unexpected_chown(*args: object, **kwargs: object) -> None:
        pytest.fail("Already-owned storage must not be chowned")

    monkeypatch.setattr(os, "chown", unexpected_chown, raising=False)
    prepare_workspace_root(workspace, ContainerSettings(owner.st_uid, owner.st_gid, 8765, False))
    assert (note.read_bytes(), note.stat().st_mode, learning.stat().st_mode) == before


def test_bind_preflight_keeps_notes_and_permissions_and_ignores_host_database_url(
    tmp_path: Path,
) -> None:
    learning = tmp_path / ".learning"
    learning.mkdir(mode=0o700)
    note = learning / "progress.json"
    note.write_text('{"completed":{}}', encoding="utf-8")
    before = (note.read_bytes(), learning.stat().st_mode, note.stat().st_mode)
    result = learning_environment(
        tmp_path,
        {
            "DS60_CONTAINER": "1",
            "DS60_COURSE_USER": "admin",
            "DS60_COURSE_PASSWORD": "synthetic-secret",
            "DS60_DATABASE_URL": "postgresql://host/other",
        },
        ContainerSettings(501, 20, 8766, False),
    )
    assert result["HOME"] == str(learning / "home")
    assert urlsplit(result["DS60_DATABASE_URL"]).hostname == "127.0.0.1"
    assert urlsplit(result["DS60_DATABASE_URL"]).port == 5432
    assert result["DS60_LAB_PORT"] == "8766"
    assert (note.read_bytes(), learning.stat().st_mode, note.stat().st_mode) == before
    assert not list(learning.glob(".write-check-*"))


def test_missing_or_unwritable_bind_does_not_reset_existing_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = ContainerSettings(501, 20, 8765, False)
    with pytest.raises(ValueError, match="Mount the learning-data volume"):
        learning_environment(tmp_path, {"DS60_CONTAINER": "1"}, settings)
    learning = tmp_path / ".learning"
    learning.mkdir()
    note = learning / "coaching.json"
    note.write_text("keep", encoding="utf-8")

    def denied(*args: object, **kwargs: object) -> None:
        raise PermissionError("Synthetic permission denial")

    monkeypatch.setattr("ds60sqlpy.container_runtime.tempfile.NamedTemporaryFile", denied)
    with pytest.raises(ValueError, match="not writable"):
        learning_environment(tmp_path, {"DS60_CONTAINER": "1"}, settings)
    assert note.read_text(encoding="utf-8") == "keep"


def test_explicit_internal_override_still_rejects_remote_or_wrong_database(tmp_path: Path) -> None:
    (tmp_path / ".learning").mkdir()
    for target in (
        "postgresql://remote.invalid/advanced_sql_training",
        "postgresql://localhost/private",
    ):
        with pytest.raises(ValueError):
            learning_environment(
                tmp_path,
                {"DS60_CONTAINER": "1", "DS60_LAB_DATABASE_URL": target},
                ContainerSettings(501, 20, 8765, False),
            )


def test_plot_prewarm_is_bounded_and_shares_the_durable_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[dict[str, object]] = []

    def execute(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        calls.append({"command": command, **kwargs})
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr("ds60sqlpy.container_runtime.subprocess.run", execute)
    assert warm_matplotlib(tmp_path)
    assert calls[0]["timeout"] == 30
    environment = calls[0]["env"]
    assert isinstance(environment, dict)
    assert environment["MPLBACKEND"] == "Agg"
    assert Path(environment["MPLCONFIGDIR"]).is_relative_to(tmp_path / ".learning/cache")

    def timeout(*args: object, **kwargs: object) -> None:
        raise subprocess.TimeoutExpired("trusted warmup", 30)

    monkeypatch.setattr("ds60sqlpy.container_runtime.subprocess.run", timeout)
    assert not warm_matplotlib(tmp_path)
    assert "first plot may reach" in capsys.readouterr().err


def test_container_start_stages_course_and_uses_the_mounted_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy import container_runtime, lab
    from ds60sqlpy.catalog import Catalog

    settings = ContainerSettings(501, 20, 8765, False)
    catalog = Catalog.load()
    calls: list[tuple[object, ...]] = []
    monkeypatch.setattr(container_runtime, "container_settings", lambda environment: settings)
    monkeypatch.setattr(os, "geteuid", lambda: 501)
    monkeypatch.setattr(container_runtime, "WORKSPACE", tmp_path)
    monkeypatch.setattr(container_runtime, "learning_environment", lambda *args: {})
    monkeypatch.setattr(container_runtime, "warm_matplotlib", lambda path: True)

    def stage(source: Path, destination: Path) -> Path:
        calls.append(("stage", source, destination))
        return tmp_path

    def load(source: Path) -> Catalog:
        calls.append(("catalog", source))
        return catalog

    def serve(value: Catalog, *, port: int, open_browser: bool, container: bool) -> None:
        calls.append(("serve", value, port, open_browser, container))

    monkeypatch.setattr(container_runtime, "prepare_workspace", stage)
    monkeypatch.setattr(Catalog, "load", load)
    monkeypatch.setattr(lab, "serve_lab", serve)
    assert container_runtime.start_lab() == 0
    assert calls == [
        ("stage", Path("/opt/course"), tmp_path),
        ("catalog", tmp_path),
        ("serve", catalog, 8765, False, True),
    ]
