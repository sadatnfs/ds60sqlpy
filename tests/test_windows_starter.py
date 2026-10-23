from __future__ import annotations

import os
import subprocess
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
        "classroom": "#!/usr/bin/env bash\n",
        "classroom.cmd": "@echo off\r\n",
        "scripts/classroom.sh": "#!/usr/bin/env bash\n",
        "START_DOCKER_CLASSROOM.cmd": "@echo off\r\n",
        "START_DOCKER_CLASSROOM.command": "#!/usr/bin/env bash\n",
        "compose.classroom.yaml": "services: {}\n",
        "compose.classroom.kubernetes.yaml": "services: {}\n",
        "courses/browser/favicon.svg": "<svg></svg>\n",
        "docker/workers/typescript/package-lock.json": "{}\n",
        "docker/workers/typescript/node_modules/pkg/index.js": "local installed dependency\n",
        "courses/example/.mypy_cache/local.json": "local checker cache\n",
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
            "START_DOCKER_CLASSROOM.cmd",
            "START_DOCKER_CLASSROOM.command",
            "compose.classroom.yaml",
            "compose.classroom.kubernetes.yaml",
            "courses/browser/favicon.svg",
            "docker/workers/typescript/package-lock.json",
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
            "docker/workers/typescript/node_modules/pkg/index.js",
            "courses/example/.mypy_cache/local.json",
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


def test_starter_cli_invokes_the_real_module_validator_with_supported_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import build_windows_starter as builder

    original_run = subprocess.run
    validated: list[subprocess.CompletedProcess[str]] = []
    packaged: list[Path] = []

    def run_check(command: list[str], **kwargs: Any) -> Any:
        if Path(command[1]).name == "check_modules.py":
            result = original_run(command, **kwargs, capture_output=True, text=True)
            validated.append(result)
            return result
        return SimpleNamespace(returncode=0)

    def record_archive(output: Path) -> int:
        packaged.append(output)
        return 1

    monkeypatch.setattr("scripts.build_windows_starter.subprocess.run", run_check)
    monkeypatch.setattr(builder, "build_archive", record_archive)
    output = tmp_path / "starter.zip"
    assert builder.main(["--output", str(output)]) == 0
    assert len(validated) == 1
    assert validated[0].returncode == 0, validated[0].stderr
    assert "Validated" in validated[0].stdout
    assert packaged == [output]
