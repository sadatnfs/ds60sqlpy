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
    """Core implementation: validate settings with CLI values taking precedence."""

    raise NotImplementedError("load and validate the application settings")


def redact_database_url(database_url: str | None) -> str:
    """Core implementation: return a diagnostic label that never exposes credentials."""

    raise NotImplementedError("redact the connection string")


def build_parser() -> argparse.ArgumentParser:
    """Core implementation: add database, log-level, and dry-run options."""

    raise NotImplementedError("build the command-line parser")


# Exercises (answer-free)
# Focus: Build one typed configuration boundary that combines environment and CLI input without
#    leaking connection credentials.
# Assumptions: CLI values override environment values; a missing database URL remains `None`;
#    log levels are normalized to the five declared values.
# Failure to watch for: Configuration objects and exception text can expose passwords just as
#    easily as an explicit print statement.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Implementation] Implement `load_settings()` with CLI-over-environment precedence,
#    uppercase log-level normalization, and `None` for a missing URL.
#    Hint: Resolve each source once, then validate the final selected value at the boundary.
# 2. [Security] Implement `redact_database_url()` so diagnostics retain scheme, user, host,
#    port, and database but remove password, query, and fragment.
#    Hint: Parsing components is safer than replacing substrings in an opaque secret.
# 3. [Implementation] Implement `build_parser()` with `--database-url`, `--log-level`, and
#    `--dry-run` without reading global process state during parser construction.
#    Hint: Parser construction and argument parsing are separate responsibilities.
# 4. [Integration] Implement `main(argv)` so it parses the supplied sequence, loads settings,
#    configures logging, and emits only a safe summary.
#    Hint: A testable CLI accepts an argument sequence instead of rewriting `sys.argv`.
# 5. [Testing] Create a table-driven test matrix for defaults, CLI precedence, mixed-case
#    levels, invalid levels, malformed URLs, credentials, and a missing URL.
#    Hint: Include both successful values and exact failure types; assert secrets are absent
#    from all diagnostics.
# 6. [Prediction] Predict the result when the environment says `WARNING`, the CLI supplies
#    `debug`, `dry_run=True`, and no database URL exists; then verify it.
#    Hint: Apply precedence independently per setting rather than treating one source as an
#    all-or-nothing bundle.
# 7. [Debugging] Repair a redactor that catches parse errors but returns `f'invalid:
#    {database_url}'` and explain why the exception path is still a leak.
#    Hint: Failure messages are an output boundary and need the same secrecy rule as normal
#    logs.
# 8. [Design] Add configuration provenance such as `cli`, `environment`, or `default` without
#    storing or logging the selected secret value twice.
#    Hint: Metadata about a source can be safe even when the source value is not.
# 9. [Security testing] Use a recording logger or `caplog` to prove that startup, success, and
#    validation-failure paths contain no password, query token, or full URL.
#    Hint: Test the emitted boundary, not only the return value of the redaction helper.
# 10. [Portability] Write equivalent Windows PowerShell and POSIX invocations that set
#    environment values outside Python and pass CLI overrides through `argv`; identify what
#    remains platform-neutral.
#    Hint: Environment-setting syntax differs, but `argparse`, `Mapping`, and the Python entry
#    point do not.


def main(argv: Sequence[str] | None = None) -> int:
    """Keep unfinished exercises out of the default execution path."""

    del argv
    print("Bridge Day 1 starter loaded.")
    print("Complete load_settings(), redact_database_url(), and build_parser().")
    print("Then add tests for precedence, validation, and secret redaction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
