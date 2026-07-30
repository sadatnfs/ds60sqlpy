"""BRIDGE-OPS-01: migration delivery and application observability.

Prerequisites: SQL-FOUND-02, Bridge Day 4, Bridge Day 5, and Bridge Day 8.
Read the companion guide before completing these exercises. This learner file
does not contact PostgreSQL or call unfinished functions from ``main()``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

LESSON_ID = "bridge-ops-01"
PREREQUISITES = ("sql-found-02", "bridge-04", "bridge-05", "bridge-08")
LEVEL = "advanced"


class QueryResult(Protocol):
    """Small result boundary shared by a Psycopg adapter and test fakes."""

    def fetchone(self) -> Sequence[object] | None: ...

    def fetchall(self) -> Sequence[Sequence[object]]: ...


class DatabaseSession(Protocol):
    """One transaction-owning database session."""

    def execute(
        self,
        query: str,
        params: Sequence[object] | None = None,
    ) -> QueryResult: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class Metrics(Protocol):
    """Low-cardinality counter and timing boundary."""

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
    """Structured-event boundary; fields must already be safe to emit."""

    def emit(self, event: str, fields: Mapping[str, object]) -> None: ...


@dataclass(frozen=True)
class SqlCommand:
    """Trusted SQL structure plus separately bound data values."""

    text: str
    params: tuple[object, ...] = ()


@dataclass(frozen=True)
class Migration:
    """One immutable, ordered schema change."""

    migration_id: str
    description: str
    commands: tuple[SqlCommand, ...]
    verification: SqlCommand

    @property
    def checksum(self) -> str:
        """Exercise 1: compute a stable checksum over migration identity and content."""

        raise NotImplementedError("serialize immutable migration content and hash it")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.05


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


def redact_fields(fields: Mapping[str, object]) -> dict[str, object]:
    """Exercise 2: redact credential-bearing names and URL-shaped values."""

    raise NotImplementedError("return JSON-safe fields without credentials or payloads")


def plan_pending(
    migrations: Sequence[Migration],
    applied_checksums: Mapping[str, str],
) -> tuple[Migration, ...]:
    """Exercise 3: validate order and checksum history, then return pending work."""

    raise NotImplementedError("reject drift and preserve immutable migration order")


def deliver_migrations(
    session_factory: Callable[[], DatabaseSession],
    migrations: Sequence[Migration],
    *,
    request_id: str,
    retry_policy: RetryPolicy,
    logger: EventLogger,
    metrics: Metrics,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
) -> DeliveryResult:
    """Exercise 4: deliver each migration in a fresh, retryable transaction."""

    raise NotImplementedError("lock, re-check, execute, verify, record, and commit")


def check_readiness(
    session_factory: Callable[[], DatabaseSession],
    migrations: Sequence[Migration],
) -> ReadinessResult:
    """Exercise 5: distinguish process liveness from schema readiness."""

    raise NotImplementedError("use read-only probes and report missing or drifted versions")


def decide_recovery(evidence: RecoveryEvidence) -> RecoveryDecision:
    """Exercise 6: choose only when the required recovery evidence exists."""

    raise NotImplementedError("prefer a pause over an unevidenced destructive action")


def main() -> int:
    print("BRIDGE-OPS-01 starter loaded; no database was contacted.")
    print("Implement the orchestration against Protocol-based fakes first.")
    print("Use only DS60_DATABASE_URL and the disposable course database for the live lab.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
