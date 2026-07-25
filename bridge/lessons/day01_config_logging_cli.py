"""Bridge Day 1: configuration, safe logging, and a typed CLI boundary.

Prerequisites: Python Day 15 and SQL Day 15.
Read ``bridge/companion-guides/day01_config_logging_cli.md`` before starting.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

LESSON_ID = "bridge-01"
PREREQUISITES = ("python-15", "sql-15")
LEVEL = "intermediate"

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    log_level: LogLevel
    dry_run: bool


def load_settings(
    environ: Mapping[str, str],
    *,
    database_url: str | None = None,
    log_level: str | None = None,
    dry_run: bool = False,
) -> Settings:
    """Exercise 1: validate settings with CLI values taking precedence."""

    raise NotImplementedError("load and validate the application settings")


def redact_database_url(database_url: str | None) -> str:
    """Exercise 2: return a diagnostic label that never exposes credentials."""

    raise NotImplementedError("redact the connection string")


def build_parser() -> argparse.ArgumentParser:
    """Exercise 3: add database, log-level, and dry-run options."""

    raise NotImplementedError("build the command-line parser")


def main(argv: Sequence[str] | None = None) -> int:
    """Keep unfinished exercises out of the default execution path."""

    del argv
    print("Bridge Day 1 starter loaded.")
    print("Complete load_settings(), redact_database_url(), and build_parser().")
    print("Then add tests for precedence, validation, and secret redaction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
