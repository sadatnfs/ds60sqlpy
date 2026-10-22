from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from zipfile import ZipFile

import pytest

from scripts.build_windows_starter import build_archive


def test_starter_includes_launch_assets_and_excludes_private_files(tmp_path: Path) -> None:
    root = tmp_path / "course"
    assets = {
        "START_DOCKER_LAB.cmd": "@echo off\r\n",
        "scripts/start_docker_windows.ps1": "Write-Host 'Welcome'\n",
        "scripts/docker_lab.ps1": "Write-Host 'Docker'\n",
        "Dockerfile": "FROM python:3.12-slim-bookworm\n",
        "compose.yaml": "services: {}\n",
        "curriculum/catalog.json": "{}\n",
        ".env.example": "DS60_LAB_PORT=8765\n",
        "docs/guide.md": "Read the guide.\n",
        "docs/.env.example": "PUBLIC_SETTING=42\n",
        "docs/.env": "private configuration\n",
        "docs/local.KEY": "private key fixture\n",
        "docs/Credentials.json": "private fixture\n",
        "docs/.learning/notes.json": "private learner notes\n",
        ".learning/progress.json": "private learner progress\n",
        ".env": "private root configuration\n",
        "src/example.egg-info/PKG-INFO": "generated metadata\n",
    }
    for name, text in assets.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode())
    if os.name != "nt":
        outside = tmp_path / "private-outside.txt"
        outside.write_text("private outside fixture", encoding="utf-8")
        (root / "docs/linked.txt").symlink_to(outside)
    output = tmp_path / "release/Windows-Starter.zip"
    build_archive(output, source_root=root)
    with ZipFile(output) as archive:
        names = {name.removeprefix("DS60LearningLab/") for name in archive.namelist()}
        assert archive.testzip() is None
        assert {
            "START_DOCKER_LAB.cmd",
            "scripts/start_docker_windows.ps1",
            "scripts/docker_lab.ps1",
            "Dockerfile",
            "compose.yaml",
            "curriculum/catalog.json",
            "docs/guide.md",
            ".env.example",
            "docs/.env.example",
            "START-WINDOWS.txt",
        } <= names
        assert not names & {
            "docs/.env",
            "docs/local.KEY",
            "docs/Credentials.json",
            "docs/.learning/notes.json",
            ".learning/progress.json",
            ".env",
            "src/example.egg-info/PKG-INFO",
            "docs/linked.txt",
        }
        assert b"\r\n" in archive.read("DS60LearningLab/START-WINDOWS.txt")
        assert all(name.startswith("DS60LearningLab/") for name in archive.namelist())


def test_starter_refuses_incomplete_source_without_replacing_archive(tmp_path: Path) -> None:
    output = tmp_path / "existing.zip"
    output.write_bytes(b"keep existing release")
    with pytest.raises(FileNotFoundError, match="START_DOCKER_LAB.cmd"):
        build_archive(output, source_root=tmp_path / "incomplete")
    assert output.read_bytes() == b"keep existing release"


def test_staging_omits_windows_junction_contents_on_python_311(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.build_app import stage_course

    source = tmp_path / "source"
    linked = source / "docs/redirected-folder"
    linked.mkdir(parents=True)
    (linked / "private.txt").write_text("Do not distribute redirected content.")
    (source / "docs/guide.md").write_text("Public authored guide.")
    original_lstat = Path.lstat

    def windows_lstat(path: Path) -> Any:
        information = original_lstat(path)
        if path == linked:
            return SimpleNamespace(st_mode=information.st_mode, st_reparse_tag=0xA0000003)
        return information

    monkeypatch.setattr(Path, "lstat", windows_lstat)
    destination = tmp_path / "payload"
    stage_course(destination, source_root=source)
    assert (destination / "docs/guide.md").read_text() == "Public authored guide."
    assert not (destination / "docs/redirected-folder").exists()
