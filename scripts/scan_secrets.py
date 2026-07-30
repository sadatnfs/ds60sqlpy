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

from ds60sqlpy.secret_scan import scan_git_history, scan_repository  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--history",
        action="store_true",
        help="Also scan every unique blob reachable from local Git references.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        findings = scan_repository(args.repo_root)
        history_findings = scan_git_history(args.repo_root) if args.history else []
    except subprocess.CalledProcessError as exc:
        print(f"Secret scan could not enumerate Git files: {exc}")
        return 2

    for repo_finding in findings:
        location = f":{repo_finding.line}" if repo_finding.line else ""
        print(f"FAIL {repo_finding.path.as_posix()}{location}: {repo_finding.kind}")
    if findings:
        print(f"Sensitive-content findings: {len(findings)}")
        return 1
    for history_finding in history_findings:
        location = f":{history_finding.line}" if history_finding.line else ""
        print(
            f"FAIL history {history_finding.object_id} "
            f"{history_finding.path.as_posix()}{location}: {history_finding.kind}"
        )
    if history_findings:
        print(f"Git-history sensitive-content findings: {len(history_findings)}")
        return 1
    suffix = " and Git history" if args.history else ""
    print(f"Sensitive-content{suffix} scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
