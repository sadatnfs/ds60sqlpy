# SPDX-License-Identifier: Apache-2.0
"""Explicitly download locked wheels for a later offline native image build."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

from locks import read_lock, selected_lock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    architecture = {"aarch64": "arm64", "x86_64": "amd64"}.get(platform.machine())
    if platform.system() != "Linux" or architecture is None or sys.version_info[:2] != (3, 12):
        parser.error("Prepare these wheels in native Linux with Python 3.12")
    if args.output.is_symlink() or (args.output.exists() and not args.output.is_dir()):
        parser.error("Use an owned regular wheelhouse directory")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in ("cpu", "scientific", "build"):
        lock = selected_lock(group, architecture)
        read_lock(lock)
        index = (
            "https://download.pytorch.org/whl/cpu" if group == "cpu" else "https://pypi.org/simple"
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "download",
                "--disable-pip-version-check",
                "--require-hashes",
                "--only-binary=:all:",
                "--no-deps",
                "--index-url",
                index,
                "--dest",
                str(args.output),
                "-r",
                str(lock),
            ],
            check=True,
        )
    files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(args.output.glob("*.whl"))
    }
    receipt = {
        "architecture": architecture,
        "python": platform.python_version(),
        "wheel_sha256": files,
        "runtime_executed": False,
    }
    (args.output / "download-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"wheel_count": len(files), "architecture": architecture}))


if __name__ == "__main__":
    main()
