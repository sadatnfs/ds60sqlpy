#!/usr/bin/env python3
"""Build a native executable containing the UI and complete offline course."""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ds60sqlpy.curriculum_framework import is_content_link  # noqa: E402
from ds60sqlpy.desktop import BUNDLE_PATHS  # noqa: E402


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
        ".learning",
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
        if is_content_link(Path(directory) / name) or (
            name.casefold() != ".env.example"
            and any(fnmatch.fnmatchcase(name.casefold(), pattern) for pattern in patterns)
        ):
            ignored.add(name)
    return ignored


def stage_course(destination: Path, *, source_root: Path | None = None) -> None:
    """Copy an allowlisted course payload, excluding all learner-local state."""

    destination.mkdir(parents=True, exist_ok=False)
    root = ROOT if source_root is None else source_root
    for name in BUNDLE_PATHS:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    for checker in ("build_course_guide.py", "build_lesson_readers.py"):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / checker), "--check"],
            cwd=ROOT,
            check=False,
        )
        if result.returncode:
            print("Refresh course outputs with make generate before building the application.")
            return result.returncode
    work = ROOT / "build" / "native"
    # Build intermediates only. Never remove a course or learner workspace.
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    payload = work / "course"
    stage_course(payload)
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "DS60LearningLab",
        "--distpath",
        str(args.output.resolve()),
        "--workpath",
        str(work / "pyinstaller"),
        "--specpath",
        str(work),
        "--paths",
        str(ROOT / "src"),
        "--add-data",
        f"{payload}:course",
        "--add-data",
        f"{ROOT / 'src/ds60sqlpy/assets'}:ds60sqlpy/assets",
        str(ROOT / "scripts/learning_lab.py"),
    ]
    environment = {**os.environ, "PYINSTALLER_CONFIG_DIR": str(work / "cache")}
    return subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
