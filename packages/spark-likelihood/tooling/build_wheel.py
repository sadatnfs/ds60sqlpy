# SPDX-License-Identifier: Apache-2.0
"""Build the pure wheel from a temporary copy, keeping the source project unchanged."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.is_symlink() or (
        args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir()))
    ):
        parser.error("Use a fresh empty wheel output directory")
    sources = [
        PACKAGE / "pyproject.toml",
        PACKAGE / "README.md",
        PACKAGE / "LICENSE",
        PACKAGE / "MANIFEST.in",
    ]
    for directory in ("src", "docs", "examples"):
        if any(path.is_symlink() for path in (PACKAGE / directory).rglob("*")):
            parser.error("Package trees must not contain symlinks")
    sources += list((PACKAGE / "src").rglob("*.py"))
    if any(path.is_symlink() or not path.is_file() for path in sources):
        parser.error("Package build inputs must be regular files")
    before = {
        str(path.relative_to(PACKAGE)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sources
    }
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="spark-likelihood-wheel-") as scratch:
        copied = Path(scratch) / "source"
        copied.mkdir()
        for name in ("pyproject.toml", "README.md", "LICENSE", "MANIFEST.in"):
            shutil.copyfile(PACKAGE / name, copied / name)
        for name in ("src", "docs", "examples"):
            shutil.copytree(
                PACKAGE / name,
                copied / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
        env = dict(os.environ, SOURCE_DATE_EPOCH="315532800")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-index",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir",
                str(args.output.resolve()),
                str(copied),
            ],
            env=env,
            check=True,
        )
    if before != {
        str(path.relative_to(PACKAGE)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sources
    }:
        raise RuntimeError("Package source changed during wheel preparation")
    wheels = list(args.output.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("Expected exactly one prepared wheel")
    print(
        json.dumps(
            {
                "wheel": wheels[0].name,
                "sha256": hashlib.sha256(wheels[0].read_bytes()).hexdigest(),
                "source_unchanged": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
