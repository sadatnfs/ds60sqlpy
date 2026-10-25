from __future__ import annotations

import os
import re
import shlex
import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from zipfile import ZipFile

import pytest

from scripts.build_starter import build_archive


def test_starter_includes_launch_assets_and_excludes_private_files(tmp_path: Path) -> None:
    root = tmp_path / "course"
    assets = {
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
    # Local checkout permission bits must not leak into a public source archive.
    # In particular, Docker COPY makes a mode600 lockfile root-owned and unreadable
    # to the unprivileged classroom unless the source payload is normalized.
    (root / "Dockerfile").chmod(0o600)
    (root / "classroom").chmod(0o700)
    (root / "docs/guide.md").chmod(0o660)
    original_modes = {
        name: stat.S_IMODE((root / name).stat().st_mode)
        for name in ("Dockerfile", "classroom", "docs/guide.md")
    }
    original_owners = {name: (root / name).stat().st_uid for name in original_modes}
    output = tmp_path / "release/Docker-Starter.zip"
    build_archive(output, source_root=root)
    with ZipFile(output) as archive:
        names = {name.removeprefix("DS60LearningLab/") for name in archive.namelist()}
        assert archive.testzip() is None
        for member in archive.infolist():
            mode = member.external_attr >> 16
            assert member.create_system == 3
            assert stat.S_ISREG(mode)
            assert stat.S_IMODE(mode) in (0o644, 0o755)
            assert not mode & 0o022
        for name, expected in (
            ("Dockerfile", 0o644),
            ("classroom", 0o755),
            ("docs/guide.md", 0o644),
        ):
            mode = archive.getinfo("DS60LearningLab/" + name).external_attr >> 16
            assert stat.S_IMODE(mode) == expected
        assert {
            "START_DOCKER_CLASSROOM.cmd",
            "START_DOCKER_CLASSROOM.command",
            "compose.classroom.yaml",
            "compose.classroom.kubernetes.yaml",
            "courses/browser/favicon.svg",
            "docker/workers/typescript/package-lock.json",
            "Dockerfile",
            "compose.yaml",
            "curriculum/catalog.json",
            "docs/guide.md",
            ".env.example",
            "docs/.env.example",
            "START.txt",
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
        assert b"\r\n" in archive.read("DS60LearningLab/START.txt")
        assert all(name.startswith("DS60LearningLab/") for name in archive.namelist())
    assert {
        name: stat.S_IMODE((root / name).stat().st_mode) for name in original_modes
    } == original_modes
    assert {name: (root / name).stat().st_uid for name in original_modes} == original_owners


def test_starter_refuses_incomplete_source_without_replacing_archive(tmp_path: Path) -> None:
    output = tmp_path / "existing.zip"
    output.write_bytes(b"keep existing release")
    with pytest.raises(FileNotFoundError, match="classroom"):
        build_archive(output, source_root=tmp_path / "incomplete")
    assert output.read_bytes() == b"keep existing release"


def test_staging_omits_windows_junction_contents_on_python_311(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.course_payload import stage_course

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
    from scripts import build_starter as builder

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

    monkeypatch.setattr("scripts.build_starter.subprocess.run", run_check)
    monkeypatch.setattr(builder, "build_archive", record_archive)
    output = tmp_path / "starter.zip"
    assert builder.main(["--output", str(output)]) == 0
    assert len(validated) == 1
    assert validated[0].returncode == 0, validated[0].stderr
    assert "Validated" in validated[0].stdout
    assert packaged == [output]


def test_project_staging_excludes_toolchain_products_but_preserves_authored_contracts(
    tmp_path: Path,
) -> None:
    from scripts.course_payload import stage_course

    source = tmp_path / "source"
    apple_project = "courses/swift/fixtures/JourneyApp/JourneyApp.xcodeproj"
    authored = {
        "courses/rust/fixtures/InventoryLab/Cargo.toml": '[package]\nname="fixture"\n',
        "courses/rust/fixtures/InventoryLab/Cargo.lock": "version = 4\n",
        "courses/rust/fixtures/InventoryLab/src/main.rs": "fn main() {}\n",
        "courses/swift/fixtures/JourneyCore/Package.swift": "import PackageDescription\n",
        "courses/swift/fixtures/JourneyCore/Package.resolved": '{"version":3}\n',
        "courses/swift/fixtures/JourneyCore/Sources/Core.swift": "struct Core {}\n",
        "courses/csharp/fixtures/DomainLab/Checks/Checks.csproj": "<Project />\n",
        "courses/csharp/fixtures/DomainLab/Checks/packages.lock.json": '{"version":1}\n',
        "courses/csharp/fixtures/DomainLab/Checks/Program.cs": 'Console.WriteLine("fixture");\n',
        "courses/swift/fixtures/JourneyApp/project.yml": "name: JourneyApp\n",
        f"{apple_project}/project.pbxproj": "authored project\n",
        f"{apple_project}/xcshareddata/xcschemes/Journey.xcscheme": "shared scheme\n",
        f"{apple_project}/project.xcworkspace/xcshareddata/swiftpm/Package.resolved": (
            '{"version":3}\n'
        ),
        # These names have no matching project manifest and are legitimate content.
        "courses/rust/guides/target/README.md": "Teach compilation targets.\n",
        "courses/swift/fixtures/data/.build/README.md": "An authored path example.\n",
        "courses/csharp/guides/bin/README.md": "Teach binary representation.\n",
        "courses/csharp/guides/obj/README.md": "Teach object representation.\n",
        "courses/example/xcuserdata/README.md": "An authored path example.\n",
        "courses/rust/fixtures/InventoryLab/target-notes/README.md": "Keep these notes.\n",
        "courses/csharp/fixtures/DomainLab/Checks/obj-format.md": "Keep this document.\n",
    }
    generated = {
        "courses/rust/fixtures/InventoryLab/target/debug/compiled.bin",
        "courses/swift/fixtures/JourneyCore/.build/debug/compiled.bin",
        "courses/swift/fixtures/JourneyCore/.swiftpm/configuration/local.json",
        "courses/csharp/fixtures/DomainLab/Checks/bin/Debug/compiled.dll",
        "courses/csharp/fixtures/DomainLab/Checks/obj/project.assets.json",
        "courses/swift/fixtures/JourneyApp/JourneyApp.xcodeproj/xcuserdata/local.xcuserdatad/state.bin",
        "courses/swift/fixtures/JourneyApp/JourneyApp.xcodeproj/project.xcworkspace/xcuserdata/local.xcuserdatad/state.bin",
    }
    for relative, content in authored.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for relative in generated:
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic local build product\n")
    before = {path: (source / path).read_bytes() for path in authored.keys() | generated}
    destination = tmp_path / "payload"
    stage_course(destination, source_root=source)
    for relative, content in authored.items():
        assert (destination / relative).read_text(encoding="utf-8") == content
    assert not any((destination / relative).exists() for relative in generated)
    assert {path: (source / path).read_bytes() for path in before} == before


def test_project_named_files_are_not_mistaken_for_build_directories(tmp_path: Path) -> None:
    from scripts.course_payload import stage_course

    source = tmp_path / "source"
    project = source / "courses/example"
    project.mkdir(parents=True)
    for filename, content in {
        "Cargo.toml": '[package]\nname="fixture"\n',
        "Package.swift": "import PackageDescription\n",
        "Example.csproj": "<Project />\n",
        "target": "authored file named target\n",
        "bin": "authored file named bin\n",
        "obj": "authored file named obj\n",
        ".build": "authored file named .build\n",
    }.items():
        (project / filename).write_text(content, encoding="utf-8")
    destination = tmp_path / "payload"
    stage_course(destination, source_root=source)
    for filename in ("target", "bin", "obj", ".build"):
        assert (destination / "courses/example" / filename).read_bytes() == (
            project / filename
        ).read_bytes()


@pytest.mark.skipif(os.name != "posix", reason="The source image is a Linux/POSIX build")
def test_image_source_permission_command_preserves_venv_ownership_and_write_bits(
    tmp_path: Path,
) -> None:
    dockerfile = (Path(__file__).resolve().parents[1] / "Dockerfile").read_text(encoding="utf-8")
    match = re.search(r"&& (find /opt/course .*?)\s*\\\n\s*&& mkdir /workspace", dockerfile, re.S)
    assert match is not None, "The image must normalize only public source permissions"
    public = tmp_path / "public course"
    dependency = public / ".venv"
    dependency.mkdir(parents=True)
    dependency_file = dependency / "untouched-dependency"
    dependency_file.write_text("prepared environment", encoding="utf-8")
    dependency_file.chmod(0o600)
    dependency.chmod(0o700)
    private_source = public / "Cargo.lock"
    private_source.write_text("public dependency lock", encoding="utf-8")
    private_source.chmod(0o600)
    executable = public / "launcher"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o700)
    readable = public / "README.md"
    readable.write_text("already readable", encoding="utf-8")
    readable.chmod(0o644)
    private_directory = public / "guides"
    private_directory.mkdir(mode=0o700)
    outside = tmp_path / "outside"
    outside.write_text("outside the public source boundary", encoding="utf-8")
    outside.chmod(0o600)
    (public / "linked-file").symlink_to(outside)
    paths = [
        public,
        dependency,
        dependency_file,
        private_source,
        executable,
        readable,
        private_directory,
        outside,
    ]
    before = {path: path.stat() for path in paths}
    command = (
        match.group(1)
        .replace("\\\n", " ")
        .replace("/opt/course/.venv", shlex.quote(str(dependency)))
        .replace("/opt/course", shlex.quote(str(public)))
    )
    subprocess.run(["sh", "-n"], input=command, text=True, check=True)
    subprocess.run(["sh", "-c", command], check=True)
    assert stat.S_IMODE(private_source.stat().st_mode) == 0o644
    assert stat.S_IMODE(executable.stat().st_mode) == 0o755
    assert stat.S_IMODE(private_directory.stat().st_mode) == 0o755
    for path in (dependency, dependency_file, readable, outside):
        assert path.stat().st_mode == before[path].st_mode
        assert path.stat().st_ctime_ns == before[path].st_ctime_ns
    for path in paths:
        after = path.stat()
        assert after.st_uid == before[path].st_uid
        assert after.st_gid == before[path].st_gid
        assert after.st_mode & 0o222 == before[path].st_mode & 0o222
        assert after.st_mode & 0o700 == before[path].st_mode & 0o700
