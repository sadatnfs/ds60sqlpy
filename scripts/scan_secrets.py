#!/usr/bin/env python3
"""Fail when repository files contain common credential material.

This is a fast, offline guard for obvious secrets. It complements—not
replaces—review and a dedicated secret scanner when one is available.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ds60sqlpy.secret_scan import scan_repository  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        findings = scan_repository(args.repo_root)
    except subprocess.CalledProcessError as exc:
        print(f"Secret scan could not enumerate Git files: {exc}")
        return 2

    for finding in findings:
        location = f":{finding.line}" if finding.line else ""
        print(f"FAIL {finding.path.as_posix()}{location}: {finding.kind}")
    if findings:
        print(f"Sensitive-content findings: {len(findings)}")
        return 1
    print("Sensitive-content scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
