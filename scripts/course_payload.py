#!/usr/bin/env python3
"""Stage the supported Docker classroom source without private learner state."""

from __future__ import annotations

import fnmatch
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ds60sqlpy.course_paths import COURSE_PATHS  # noqa: E402
from ds60sqlpy.curriculum_framework import is_content_link  # noqa: E402
from scripts.check_public_release import scan as scan_public_payload  # noqa: E402


def toolchain_output_directory(parent: Path, name: str) -> bool:
    """Recognize generated directories by their neighboring project contract.

    A course may legitimately teach a concept in a directory named target or
    bin. Those names are not globally private; the actual toolchain manifest
    must establish that this is a project build directory.
    """
    candidate = parent / name
    if not candidate.is_dir():
        return False

    def manifest(filename: str) -> bool:
        path = parent / filename
        return not is_content_link(path) and path.is_file()

    if manifest("dbt_project.yml") and (
        name in {"target", "logs", "dbt_packages"} or name.endswith(".duckdb.tmp")
    ):
        return True
    ml_marker = parent / ".ds60-ml-project.json"
    if name == "state" and is_content_link(ml_marker):
        raise ValueError("Owned ML project marker must not be a link")
    if name == "state" and manifest(".ds60-ml-project.json"):
        marker_path = parent / ".ds60-ml-project.json"
        if marker_path.stat().st_size > 1000:
            raise ValueError("ML project marker exceeds its metadata limit")
        marker = json.loads(marker_path.read_text("utf-8"))
        if (
            not isinstance(marker, dict)
            or set(marker) != {"schema_version", "kind"}
            or type(marker.get("schema_version")) is not int
            or marker["schema_version"] != 1
            or marker.get("kind") != "local-ml-service"
        ):
            raise ValueError("Invalid owned ML project marker")
        return True
    if name == "target" and manifest("Cargo.toml"):
        return True
    if name in {".build", ".swiftpm"} and manifest("Package.swift"):
        return True
    if name.casefold() in {"bin", "obj"} and any(
        path.suffix.casefold() in {".csproj", ".fsproj", ".vbproj"}
        and not is_content_link(path)
        and path.is_file()
        for path in parent.iterdir()
    ):
        return True
    return name == "xcuserdata" and any(
        ancestor.suffix in {".xcodeproj", ".xcworkspace"} for ancestor in (parent, *parent.parents)
    )


def toolchain_output_file(parent: Path, name: str) -> bool:
    marker = parent / "dbt_project.yml"
    if is_content_link(marker):
        raise ValueError("dbt project marker must not be a link")
    return (
        not is_content_link(marker)
        and marker.is_file()
        and (name == ".user.yml" or name.endswith((".duckdb", ".duckdb.wal")))
    )


def ignore_private_files(directory: str, names: list[str]) -> set[str]:
    """Exclude local state and authentication files, including nested copies."""
    ignored = set()
    patterns = (
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".hypothesis",
        "*.pyc",
        "*.egg-info",
        "*.dist-info",
        ".ds_store",
        "cache",
        ".ipynb_checkpoints",
        ".git",
        ".serena",
        ".codex",
        ".module-runtime",
        ".module-runtime-not-prepared",
        ".app-build",
        ".cache",
        "work",
        "build",
        "dist",
        "artifacts",
        "mlruns",
        "wandb",
        "classroom-runs",
        "ds60-figures.json",
        ".ds60-output-*",
        ".learning",
        ".workshop",
        ".classroom",
        ".venv",
        ".env",
        ".env.*",
        ".ssh",
        ".aws",
        ".oci",
        ".pgpass",
        "pgpass.conf",
        ".npmrc",
        ".pypirc",
        "credentials",
        "credentials.json",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "*.pem",
        "*.key",
        "*.p12",
        "*.pfx",
        "*.jks",
    )
    for name in names:
        if (
            is_content_link(Path(directory) / name)
            or toolchain_output_directory(Path(directory), name)
            or toolchain_output_file(Path(directory), name)
            or (
                name.casefold() != ".env.example"
                and any(fnmatch.fnmatchcase(name.casefold(), pattern) for pattern in patterns)
            )
        ):
            ignored.add(name)
    return ignored


def stage_course(destination: Path, *, source_root: Path | None = None) -> None:
    """Copy an allowlisted course payload, excluding all learner-local state."""

    destination.mkdir(parents=True, exist_ok=False)
    root = ROOT if source_root is None else source_root
    for name in COURSE_PATHS:
        source, target = root / name, destination / name
        if is_content_link(source):
            continue
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=ignore_private_files,
            )
        elif source.is_file():
            shutil.copy2(source, target)

    findings, _ = scan_public_payload(destination, payload=True)
    if findings:
        raise ValueError("Staged distribution failed the public-release boundary check.")
