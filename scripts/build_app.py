#!/usr/bin/env python3
"""Build a native executable containing the UI and complete offline course."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ds60sqlpy.desktop import BUNDLE_PATHS  # noqa: E402


def stage_course(destination: Path) -> None:
    """Copy an allowlisted course payload, excluding all learner-local state."""

    destination.mkdir(parents=True, exist_ok=False)
    for name in BUNDLE_PATHS:
        source, target = ROOT / name, destination / name
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    "*.egg-info",
                    "*.dist-info",
                    ".DS_Store",
                    "cache",
                    ".ipynb_checkpoints",
                ),
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
