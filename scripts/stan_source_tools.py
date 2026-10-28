"""Use the pinned Stan compiler for formatting and semantic source checks only."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("format", "parse", "lint"))
    args = parser.parse_args()
    data = sys.stdin.buffer.read(5_000_001)
    if len(data) > 5_000_000 or b"\x00" in data:
        raise ValueError("Stan source exceeds limits")
    source = data.decode("utf-8")
    with tempfile.TemporaryDirectory(prefix="stan-style-") as temporary:
        path = Path(temporary) / "main.stan"
        path.write_text(source, encoding="utf-8")
        options = (
            ["--auto-format", "--max-line-length=100"]
            if args.operation == "format"
            else ["--o=/dev/null"]
        )
        result = subprocess.run(
            ["stanc", *options, str(path)], capture_output=True, timeout=60, check=False
        )
    if result.returncode:
        sys.stderr.buffer.write(result.stderr)
        return result.returncode
    if args.operation == "format":
        # stanc emits spaces after unbraced control statements. Strip only
        # line-end horizontal whitespace, retaining literal spaces inside strings.
        formatted = b"\n".join(line.rstrip(b" \t\r") for line in result.stdout.split(b"\n"))
        sys.stdout.buffer.write(formatted.rstrip(b"\n") + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
