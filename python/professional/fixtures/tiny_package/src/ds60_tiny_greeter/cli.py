"""Console entry point for the tiny fixture package."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from ds60_tiny_greeter.core import greeting


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description="Print a local greeting.")
    parser.add_argument("name", nargs="?", default="learner")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the console command and return a process exit code."""

    args = build_parser().parse_args(argv)
    print(greeting(args.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
