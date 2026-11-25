#!/usr/bin/env python3
"""Fail when a tracked text file contains an em dash or an en dash.

Course prose, generated pages, code and tests use colons, commas, parentheses,
hyphenated ranges or "to" instead. Third-party vendored bundles are exempt
because they are copied byte for byte from upstream releases.
"""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHES = {"\u2014": "em dash", "\u2013": "en dash"}
VENDORED = (
    "src/ds60sqlpy/assets/vendor/*.min.js",
    "src/ds60sqlpy/assets/vendor/*LICENSE*",
    "src/ds60sqlpy/assets/vendor/textbook/katex*.js",
    "src/ds60sqlpy/assets/vendor/textbook/*LICENSE*",
)
BINARY_PROBE_BYTES = 8192


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    kind: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: {self.kind}"


def is_vendored(path: str) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in VENDORED)


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [name for name in result.stdout.decode("utf-8").split("\0") if name]


def _text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except (FileNotFoundError, IsADirectoryError):
        return None
    if b"\0" in data[:BINARY_PROBE_BYTES]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan(root: Path, paths: Iterable[str]) -> list[Finding]:
    findings: list[Finding] = []
    for relative in sorted(set(paths)):
        if is_vendored(relative):
            continue
        text = _text(root / relative)
        if text is None:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for column, character in enumerate(line, start=1):
                kind = DASHES.get(character)
                if kind is not None:
                    findings.append(Finding(relative, number, column, kind))
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths", nargs="*", help="repository-relative paths (default: git ls-files)"
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    paths = args.paths or tracked_files(root)
    findings = scan(root, paths)
    for finding in findings:
        print(finding)
    if findings:
        files = len({finding.path for finding in findings})
        print(
            f"{len(findings)} dash(es) in {files} file(s). Use a colon, comma, "
            "parentheses, a hyphenated range or 'to'.",
            file=sys.stderr,
        )
        return 1
    print(f"No em or en dashes in {len(paths)} tracked files (vendored bundles exempt).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
