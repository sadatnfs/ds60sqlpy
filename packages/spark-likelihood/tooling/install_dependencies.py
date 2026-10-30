# SPDX-License-Identifier: Apache-2.0
"""Explicit image preparation only; package runtime never invokes this installer."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

from locks import check_versions, selected_lock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("cpu", "scientific", "build"), required=True)
    parser.add_argument("--architecture", choices=("amd64", "arm64"), required=True)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--wheelhouse", type=Path, default=Path(__file__).parent / "wheelhouse")
    parser.add_argument(
        "--prepared", action="store_true", help="Verify exact installed pins instead of installing"
    )
    args = parser.parse_args()
    native = {"aarch64": "arm64", "x86_64": "amd64"}.get(platform.machine())
    if platform.system() != "Linux" or native != args.architecture:
        parser.error("Preparation must use the requested native Linux architecture")
    if sys.version_info[:2] != (3, 12):
        parser.error("These image locks target Python 3.12")
    lock = selected_lock(args.group, args.architecture)
    if not args.prepared:
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "--require-hashes",
            "--only-binary=:all:",
        ]
        if args.offline:
            if not args.wheelhouse.is_dir():
                parser.error("Offline preparation needs an explicit wheelhouse")
            command += ["--no-index", "--find-links", str(args.wheelhouse)]
        else:
            index = (
                "https://download.pytorch.org/whl/cpu"
                if args.group == "cpu"
                else "https://pypi.org/simple"
            )
            command += ["--index-url", index]
        subprocess.run([*command, "-r", str(lock)], check=True)
    versions = check_versions(lock)
    print(
        json.dumps(
            {
                "group": args.group,
                "architecture": args.architecture,
                "mode": "verified-existing" if args.prepared else "installed",
                "versions": versions,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
