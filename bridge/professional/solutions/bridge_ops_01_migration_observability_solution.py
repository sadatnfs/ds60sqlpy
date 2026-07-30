"""BRIDGE-OPS-01 reference: safe, observable, retryable migration delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from typing import Protocol, cast
from urllib.parse import unquote, urlsplit

LESSON_ID = "bridge-ops-01"
PREREQUISITES = ("sql-found-02", "bridge-04", "bridge-05", "bridge-08")
LEVEL = "advanced"

MIGRATION_ID = re.compile(r"^\d{8}_\d{3}_[a-z][a-z0-9_]*$")
RETRYABLE_SQLSTATES = frozenset({"40001", "40P01", "55P03"})
SENSITIVE_KEY_PARTS = (
    "credential",
    "database_url",
    "dsn",
    "password",
    "payload",
    "secret",
    "token",
)

CREATE_METADATA_SQL = """
CREATE TABLE IF NOT EXISTS training.ds60_schema_migrations (
    migration_id text PRIMARY KEY,
    checksum text NOT NULL,
    request_id text NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
)
""".strip()

LOCK_SQL = "SELECT pg_advisory_xact_lock(%s)"
MIGRATION_LOCK_KEY = 6_060_170_001
READ_ONE_SQL = """
SELECT checksum
FROM training.ds60_schema_migrations
WHERE migration_id = %s
""".strip()
READ_ALL_SQL = """
SELECT migration_id, checksum
FROM training.ds60_schema_migrations
ORDER BY migration_id
""".strip()
RECORD_MIGRATION_SQL = """
INSERT INTO training.ds60_schema_migrations (migration_id, checksum, request_id)
VALUES (%s, %s, %s)
""".strip()


class QueryResult(Protocol):
    def fetchone(self) -> Sequence[object] | None: ...

    def fetchall(self) -> Sequence[Sequence[object]]: ...


class DatabaseSession(Protocol):
    def execute(
        self,
        query: str,
        params: Sequence[object] | None = None,
    ) -> QueryResult: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class Metrics(Protocol):
    def increment(
        self,
        name: str,
        value: int = 1,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None: ...

    def observe(
        self,
        name: str,
        value: float,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None: ...


class EventLogger(Protocol):
    def emit(self, event: str, fields: Mapping[str, object]) -> None: ...


@dataclass(frozen=True)
class SqlCommand:
    """Trusted SQL structure plus separately bound data values."""

    text: str
    params: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("SQL command text cannot be blank")
        if self.text.count("%s") != len(self.params):
            raise ValueError("each SQL value placeholder must have one separate parameter")
        supported = (str, int, float, bool, type(None))
        if any(not isinstance(value, supported) for value in self.params):
            raise TypeError("migration parameters must use stable JSON scalar values")


@dataclass(frozen=True)
class Migration:
    """One immutable, ordered schema change and its verification query."""

    migration_id: str
    description: str
    commands: tuple[SqlCommand, ...]
    verification: SqlCommand

    def __post_init__(self) -> None:
        if not MIGRATION_ID.fullmatch(self.migration_id):
            raise ValueError("migration_id must look like YYYYMMDD_NNN_lowercase_description")
        if not self.description.strip():
            raise ValueError("migration description cannot be blank")
        if not self.commands:
            raise ValueError("a migration needs at least one command")

    @property
    def checksum(self) -> str:
        """Hash immutable content so an applied migration cannot change silently."""

        content = {
            "commands": [
                {"params": list(command.params), "text": command.text} for command in self.commands
            ],
            "description": self.description,
            "migration_id": self.migration_id,
            "verification": {
                "params": list(self.verification.params),
                "text": self.verification.text,
            },
        }
        encoded = json.dumps(
            content,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.05

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds cannot be negative")

    def delay_after(self, failed_attempt: int) -> float:
        return self.base_delay_seconds * (2.0 ** (failed_attempt - 1))


@dataclass(frozen=True)
class DeliveryResult:
    applied: tuple[str, ...]
    skipped: tuple[str, ...]
    attempts: int


@dataclass(frozen=True)
class ReadinessResult:
    ready: bool
    current_version: str | None
    target_version: str | None
    reasons: tuple[str, ...]


class RecoveryDecision(Enum):
    PAUSE_AND_GATHER_EVIDENCE = "pause-and-gather-evidence"
    FORWARD_FIX = "forward-fix"
    ROLLBACK_RELEASE = "rollback-release"


@dataclass(frozen=True)
class RecoveryEvidence:
    diagnosis_confirmed: bool
    migration_committed: bool
    new_schema_received_writes: bool
    previous_app_compatible: bool
    reverse_change_rehearsed: bool
    forward_fix_rehearsed: bool


class RetryableDatabaseError(RuntimeError):
    """Fake-friendly stand-in for a narrowly classified transient failure."""


class JsonEventLogger:
    """Write one redacted, deterministic JSON object per event."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(__name__)

    def emit(self, event: str, fields: Mapping[str, object]) -> None:
        payload = {"event": event, **redact_fields(fields)}
        self._logger.info(
            json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        )


class NullMetrics:
    """No-op adapter for the optional command-line demonstration."""

    def increment(
        self,
        name: str,
        value: int = 1,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        del name, value, tags

    def observe(
        self,
        name: str,
        value: float,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        del name, value, tags


def redact_fields(fields: Mapping[str, object]) -> dict[str, object]:
    """Return JSON-safe telemetry fields without credential-bearing content."""

    safe: dict[str, object] = {}
    for key, value in fields.items():
        normalized_key = key.casefold()
        key_is_sensitive = any(part in normalized_key for part in SENSITIVE_KEY_PARTS)
        value_looks_like_url = isinstance(value, str) and "://" in value and "@" in value
        if key_is_sensitive or value_looks_like_url:
            safe[key] = "[REDACTED]"
        elif value is None or isinstance(value, (str, int, float, bool)):
            safe[key] = value
        else:
            safe[key] = f"<{type(value).__name__}>"
    return safe


def _validate_migration_order(migrations: Sequence[Migration]) -> None:
    identifiers = [migration.migration_id for migration in migrations]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("migration IDs must be unique")
    if identifiers != sorted(identifiers):
        raise ValueError("migrations must be supplied in immutable ID order")


def plan_pending(
    migrations: Sequence[Migration],
    applied_checksums: Mapping[str, str],
) -> tuple[Migration, ...]:
    """Reject checksum drift and return unapplied migrations in ID order."""

    _validate_migration_order(migrations)
    known = {migration.migration_id: migration for migration in migrations}
    unknown_applied = sorted(set(applied_checksums) - set(known))
    if unknown_applied:
        raise ValueError(f"database contains unknown migration IDs: {unknown_applied}")

    pending: list[Migration] = []
    for migration in migrations:
        applied_checksum = applied_checksums.get(migration.migration_id)
        if applied_checksum is None:
            pending.append(migration)
        elif applied_checksum != migration.checksum:
            raise ValueError(f"checksum drift detected for {migration.migration_id}")
    return tuple(pending)


def is_retryable_database_error(error: Exception) -> bool:
    """Classify only explicit transient failures and selected PostgreSQL states."""

    if isinstance(error, RetryableDatabaseError):
        return True
    sqlstate = getattr(error, "sqlstate", None)
    if not isinstance(sqlstate, str):
        return False
    return sqlstate in RETRYABLE_SQLSTATES or sqlstate.startswith("08")


def _safe_rollback(
    session: DatabaseSession, logger: EventLogger, fields: Mapping[str, object]
) -> None:
    try:
        session.rollback()
    except Exception as error:
        logger.emit(
            "migration.rollback_failed",
            {**fields, "error_type": type(error).__name__},
        )


def _safe_close(
    session: DatabaseSession, logger: EventLogger, fields: Mapping[str, object]
) -> None:
    try:
        session.close()
    except Exception as error:
        logger.emit(
            "migration.close_failed",
            {**fields, "error_type": type(error).__name__},
        )


def _deliver_one(
    session_factory: Callable[[], DatabaseSession],
    migration: Migration,
    *,
    request_id: str,
    retry_policy: RetryPolicy,
    logger: EventLogger,
    metrics: Metrics,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
) -> tuple[bool, int]:
    started = clock()
    base_fields = {"migration_id": migration.migration_id, "request_id": request_id}
    tags = {"migration_id": migration.migration_id}

    for attempt in range(1, retry_policy.max_attempts + 1):
        session = session_factory()
        delay: float | None = None
        attempt_fields = {**base_fields, "attempt": attempt}
        metrics.increment("migration_attempts_total", tags=tags)
        logger.emit("migration.attempt_started", attempt_fields)

        try:
            session.execute(LOCK_SQL, (MIGRATION_LOCK_KEY,))
            existing = session.execute(READ_ONE_SQL, (migration.migration_id,)).fetchone()
            if existing is not None:
                existing_checksum = str(existing[0])
                if existing_checksum != migration.checksum:
                    raise ValueError(f"checksum drift detected for {migration.migration_id}")
                session.commit()
                metrics.increment(
                    "migration_outcomes_total",
                    tags={**tags, "outcome": "skipped"},
                )
                logger.emit("migration.already_applied", attempt_fields)
                return False, attempt

            for command in migration.commands:
                session.execute(command.text, command.params)

            verification = session.execute(
                migration.verification.text,
                migration.verification.params,
            ).fetchone()
            if verification is None or not bool(verification[0]):
                raise ValueError("migration verification did not return true")

            session.execute(
                RECORD_MIGRATION_SQL,
                (migration.migration_id, migration.checksum, request_id),
            )
            session.commit()
            duration = max(0.0, clock() - started)
            metrics.increment(
                "migration_outcomes_total",
                tags={**tags, "outcome": "applied"},
            )
            metrics.observe("migration_duration_seconds", duration, tags=tags)
            logger.emit(
                "migration.applied",
                {**attempt_fields, "duration_seconds": duration},
            )
            return True, attempt
        except Exception as error:
            _safe_rollback(session, logger, attempt_fields)
            retry = is_retryable_database_error(error) and attempt < retry_policy.max_attempts
            outcome = "retrying" if retry else "failed"
            metrics.increment(
                "migration_outcomes_total",
                tags={**tags, "outcome": outcome},
            )
            logger.emit(
                "migration.attempt_failed",
                {
                    **attempt_fields,
                    "error_type": type(error).__name__,
                    "retrying": retry,
                },
            )
            if not retry:
                raise
            delay = retry_policy.delay_after(attempt)
        finally:
            _safe_close(session, logger, attempt_fields)

        if delay is not None:
            sleep(delay)

    raise AssertionError("migration retry loop exhausted without returning or raising")


def _bootstrap_metadata(
    session_factory: Callable[[], DatabaseSession],
    *,
    request_id: str,
    logger: EventLogger,
) -> None:
    session = session_factory()
    fields = {"request_id": request_id}
    try:
        session.execute(CREATE_METADATA_SQL)
        session.commit()
    except Exception:
        _safe_rollback(session, logger, fields)
        raise
    finally:
        _safe_close(session, logger, fields)


def deliver_migrations(
    session_factory: Callable[[], DatabaseSession],
    migrations: Sequence[Migration],
    *,
    request_id: str,
    retry_policy: RetryPolicy | None = None,
    logger: EventLogger,
    metrics: Metrics,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> DeliveryResult:
    """Apply ordered migrations with fresh transactions and bounded retries."""

    if not request_id.strip():
        raise ValueError("request_id cannot be blank")
    if retry_policy is None:
        retry_policy = RetryPolicy()
    _validate_migration_order(migrations)
    _bootstrap_metadata(session_factory, request_id=request_id, logger=logger)

    applied: list[str] = []
    skipped: list[str] = []
    attempts = 0
    for migration in migrations:
        was_applied, used_attempts = _deliver_one(
            session_factory,
            migration,
            request_id=request_id,
            retry_policy=retry_policy,
            logger=logger,
            metrics=metrics,
            sleep=sleep,
            clock=clock,
        )
        attempts += used_attempts
        target = applied if was_applied else skipped
        target.append(migration.migration_id)
    return DeliveryResult(tuple(applied), tuple(skipped), attempts)


def liveness() -> Mapping[str, str]:
    """Report that the process can serve a probe without touching PostgreSQL."""

    return {"status": "healthy"}


def check_readiness(
    session_factory: Callable[[], DatabaseSession],
    migrations: Sequence[Migration],
) -> ReadinessResult:
    """Read PostgreSQL migration state without mutating it."""

    _validate_migration_order(migrations)
    target = migrations[-1].migration_id if migrations else None
    session = session_factory()
    try:
        ping = session.execute("SELECT 1").fetchone()
        if ping is None or int(cast(int, ping[0])) != 1:
            return ReadinessResult(False, None, target, ("database ping failed",))

        metadata_table = session.execute(
            "SELECT to_regclass(%s)",
            ("training.ds60_schema_migrations",),
        ).fetchone()
        if metadata_table is None or metadata_table[0] is None:
            return ReadinessResult(False, None, target, ("migration metadata is absent",))

        rows = session.execute(READ_ALL_SQL).fetchall()
        applied = {str(row[0]): str(row[1]) for row in rows}
        current = max(applied, default=None)
        try:
            pending = plan_pending(migrations, applied)
        except ValueError as error:
            return ReadinessResult(False, current, target, (str(error),))
        if pending:
            missing = ", ".join(migration.migration_id for migration in pending)
            return ReadinessResult(False, current, target, (f"pending migrations: {missing}",))
        return ReadinessResult(True, current, target, ())
    except Exception as error:
        return ReadinessResult(
            False,
            None,
            target,
            (f"database probe failed: {type(error).__name__}",),
        )
    finally:
        with suppress(Exception):
            session.rollback()
        with suppress(Exception):
            session.close()


def decide_recovery(evidence: RecoveryEvidence) -> RecoveryDecision:
    """Return a decision aid; never automate a schema reversal from this result."""

    if not evidence.diagnosis_confirmed:
        return RecoveryDecision.PAUSE_AND_GATHER_EVIDENCE
    if evidence.migration_committed and evidence.new_schema_received_writes:
        if evidence.forward_fix_rehearsed:
            return RecoveryDecision.FORWARD_FIX
        return RecoveryDecision.PAUSE_AND_GATHER_EVIDENCE
    if evidence.previous_app_compatible and evidence.reverse_change_rehearsed:
        return RecoveryDecision.ROLLBACK_RELEASE
    if evidence.forward_fix_rehearsed:
        return RecoveryDecision.FORWARD_FIX
    return RecoveryDecision.PAUSE_AND_GATHER_EVIDENCE


def require_course_database_url(environment: Mapping[str, str]) -> str:
    """Read and validate the disposable course URL without echoing it."""

    database_url = environment.get("DS60_DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError("DS60_DATABASE_URL is required for --live")
    parsed = urlsplit(database_url)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname:
        raise ValueError("DS60_DATABASE_URL must be a PostgreSQL URL")
    database_name = unquote(parsed.path.lstrip("/"))
    if database_name != "advanced_sql_training":
        raise ValueError("--live is restricted to the disposable advanced_sql_training database")
    return database_url


LIVE_MIGRATIONS = (
    Migration(
        migration_id="20260730_001_release_events",
        description="Create a disposable release-event lab table",
        commands=(
            SqlCommand(
                """
CREATE TABLE training.bridge_release_lab (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id text NOT NULL,
    event_name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
)
""".strip()
            ),
        ),
        verification=SqlCommand(
            "SELECT to_regclass(%s) IS NOT NULL",
            ("training.bridge_release_lab",),
        ),
    ),
    Migration(
        migration_id="20260730_002_release_source",
        description="Expand the lab with an additive source label",
        commands=(
            SqlCommand("ALTER TABLE training.bridge_release_lab ADD COLUMN source_label text"),
            SqlCommand(
                """
UPDATE training.bridge_release_lab
SET source_label = %s
WHERE source_label IS NULL
""".strip(),
                ("legacy",),
            ),
        ),
        verification=SqlCommand(
            """
SELECT count(*) = 1
FROM information_schema.columns
WHERE table_schema = %s
  AND table_name = %s
  AND column_name = %s
""".strip(),
            ("training", "bridge_release_lab", "source_label"),
        ),
    ),
)


def run_live(database_url: str, *, request_id: str) -> tuple[DeliveryResult, ReadinessResult]:
    """Run the opt-in lab against DS60_DATABASE_URL using Psycopg 3."""

    psycopg = import_module("psycopg")

    def session_factory() -> DatabaseSession:
        session = psycopg.connect(database_url, connect_timeout=5)
        return cast(DatabaseSession, session)

    logger = JsonEventLogger()
    result = deliver_migrations(
        session_factory,
        LIVE_MIGRATIONS,
        request_id=request_id,
        logger=logger,
        metrics=NullMetrics(),
    )
    return result, check_readiness(session_factory, LIVE_MIGRATIONS)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="apply the lab migrations to the disposable course database",
    )
    parser.add_argument(
        "--request-id",
        help="operator-supplied change/request ID required by --live",
    )
    args = parser.parse_args(None if argv is None else list(argv))

    if not args.live:
        print("BRIDGE-OPS-01 reference loaded; no database was contacted.")
        print("Run the fake-backed tests before choosing the optional --live lab.")
        return 0
    if not args.request_id or not args.request_id.strip():
        parser.error("--request-id is required with --live")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    database_url = require_course_database_url(os.environ)
    delivery, readiness = run_live(database_url, request_id=args.request_id)
    print(
        "Migration lab complete: "
        f"applied={len(delivery.applied)} skipped={len(delivery.skipped)} "
        f"ready={readiness.ready}"
    )
    return 0 if readiness.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
