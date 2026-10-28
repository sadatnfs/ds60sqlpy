"""Format SQL/Jinja without evaluating templates or connecting to a database."""

from __future__ import annotations

import argparse
import importlib
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("format", "lint", "parse"))
    operation = parser.parse_args().operation
    raw = sys.stdin.buffer.read(5_000_001)
    if len(raw) > 5_000_000 or b"\x00" in raw:
        raise ValueError("dbt SQL source exceeds limits")
    format_string = importlib.import_module("sqlfmt.api").format_string
    mode = importlib.import_module("sqlfmt.mode").Mode(line_length=100)
    formatted = format_string(raw.decode("utf-8"), mode)
    if operation == "format":
        print(formatted.rstrip("\r\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
