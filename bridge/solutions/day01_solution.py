"""Day 1 reference: safe configuration, logging, and a typed CLI boundary."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, cast
from urllib.parse import quote, urlsplit, urlunsplit

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
_LOG_LEVELS: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


@dataclass(frozen=True)
class Settings:
    """Validated settings at the application boundary."""

    database_url: str | None
    log_level: LogLevel
    dry_run: bool


def parse_log_level(raw: str) -> LogLevel:
    """Normalize and validate a user-provided logging level."""

    normalized = raw.strip().upper()
    if normalized not in _LOG_LEVELS:
        choices = ", ".join(sorted(_LOG_LEVELS))
        raise ValueError(f"invalid log level {raw!r}; choose one of: {choices}")
    return cast(LogLevel, normalized)


def load_settings(
    environ: Mapping[str, str],
    *,
    database_url: str | None = None,
    log_level: str | None = None,
    dry_run: bool = False,
) -> Settings:
    """Load settings with explicit CLI values taking precedence over the environment."""

    selected_url = database_url if database_url is not None else environ.get("DS60_DATABASE_URL")
    selected_level = log_level if log_level is not None else environ.get("DS60_LOG_LEVEL", "INFO")
    return Settings(
        database_url=selected_url,
        log_level=parse_log_level(selected_level),
        dry_run=dry_run,
    )


def redact_database_url(database_url: str | None) -> str:
    """Return a useful connection label without credentials or query parameters."""

    if not database_url:
        return "<not configured>"
    if "://" not in database_url:
        return "<redacted database URL>"

    try:
        parsed = urlsplit(database_url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return "<redacted database URL>"

    if not parsed.scheme or not hostname:
        return "<redacted database URL>"

    host = f"[{hostname}]" if ":" in hostname else hostname
    user = f"{quote(parsed.username, safe='')}:***@" if parsed.username else ""
    port_text = f":{port}" if port is not None else ""
    return urlunsplit((parsed.scheme, f"{user}{host}{port_text}", parsed.path, "", ""))


def configure_logging(level: LogLevel) -> None:
    """Configure one concise process-wide log format."""

    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def settings_summary(settings: Settings) -> dict[str, str | bool]:
    """Build a log-safe diagnostic summary."""

    return {
        "database": redact_database_url(settings.database_url),
        "log_level": settings.log_level,
        "dry_run": settings.dry_run,
    }


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser without reading global process state."""

    parser = argparse.ArgumentParser(description="Inspect bridge configuration safely.")
    parser.add_argument("--database-url", help="Overrides DS60_DATABASE_URL for this run.")
    parser.add_argument("--log-level", help="Overrides DS60_LOG_LEVEL.")
    parser.add_argument("--dry-run", action="store_true", help="Do not perform writes.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse the CLI, validate configuration, and report only safe fields."""

    import os

    args = build_parser().parse_args(argv)
    try:
        settings = load_settings(
            os.environ,
            database_url=args.database_url,
            log_level=args.log_level,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        build_parser().error(str(exc))

    configure_logging(settings.log_level)
    logging.getLogger(__name__).info("configuration=%s", settings_summary(settings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
