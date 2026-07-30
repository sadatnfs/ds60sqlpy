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
        """Core implementation: compute a stable checksum over migration identity and content."""

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
    """Core implementation: redact credential-bearing names and URL-shaped values."""

    raise NotImplementedError("return JSON-safe fields without credentials or payloads")


def plan_pending(
    migrations: Sequence[Migration],
    applied_checksums: Mapping[str, str],
) -> tuple[Migration, ...]:
    """Core implementation: validate order and checksum history, then return pending work."""

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
    """Core implementation: deliver each migration in a fresh, retryable transaction."""

    raise NotImplementedError("lock, re-check, execute, verify, record, and commit")


def check_readiness(
    session_factory: Callable[[], DatabaseSession],
    migrations: Sequence[Migration],
) -> ReadinessResult:
    """Core implementation: distinguish process liveness from schema readiness."""

    raise NotImplementedError("use read-only probes and report missing or drifted versions")


def decide_recovery(evidence: RecoveryEvidence) -> RecoveryDecision:
    """Core implementation: choose only when the required recovery evidence exists."""

    raise NotImplementedError("prefer a pause over an unevidenced destructive action")


# Exercises (answer-free)
# Focus: Deliver immutable ordered PostgreSQL migrations with fake-tested retry/commit
#    uncertainty, redacted observability, readiness probes, and evidence-driven recovery.
# Assumptions: Each migration has stable identity/content/checksum; every attempt owns a fresh
#    transaction; optional live work targets only the disposable course database.
# Failure to watch for: Mutable history, retry after uncertain commit without re-checking
#    metadata, or recovery without complete evidence can corrupt schema state.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Validation] Implement `Migration` validation and a stable checksum over identity,
#    description, command text/parameters, and verification.
#    Hint: Canonical serialization must distinguish structure and parameter types without
#    depending on object repr.
# 2. [Redaction] Implement `redact_fields()` for sensitive key names, URL-shaped values,
#    non-serializable objects, and ordinary scalars.
#    Hint: Use key classification and safe type conversion; never echo rejected values.
# 3. [Planning] Implement `plan_pending()` with duplicate/order validation, unknown
#    applied-version rejection, and checksum-drift detection.
#    Hint: Applied history is immutable and must be a prefix of known ordered migrations.
# 4. [Test double] Build a recording session fake that stores SQL separately from parameter
#    tuples and never parses PostgreSQL through SQLite.
#    Hint: Model transactional state and prepared query results explicitly.
# 5. [Delivery] Implement the documented nine-step delivery order and prove rollback/close
#    happen before injected retry delay.
#    Hint: One attempt must acquire, lock, re-check, apply, verify, record, commit, close, then
#    report.
# 6. [Commit uncertainty] Simulate an uncertain commit whose retry sees a matching metadata row
#    and prove commands are not applied twice.
#    Hint: Re-check immutable metadata under lock before every attempt.
# 7. [Observability] Add event and metric fakes; require request/migration IDs in logs, exclude
#    request IDs from metric tags, and prove secrets are absent.
#    Hint: Logs support correlation; metrics require bounded dimensions.
# 8. [Readiness] Implement read-only readiness for current, pending, drifted, and unreachable
#    states while keeping liveness database-independent.
#    Hint: Readiness describes safe traffic acceptance, not process existence.
# 9. [Recovery] Build a scenario table for recovery decisions, including incomplete evidence
#    that must pause.
#    Hint: Destructive or forward actions require rehearsed, compatible evidence.
# 10. [Optional integration] After fake tests, run the disposable live lab twice and inspect
#    migration metadata with a read-only query.
#    Hint: The second run demonstrates idempotency; cleanup evidence is part of completion.
# 11. [Immutability] Change only SQL whitespace after a migration is applied and decide whether
#    checksum drift should be accepted.
#    Hint: A stored checksum is an immutable history contract, not a semantic SQL parser.
# 12. [Concurrency] Model two deployers contending for the same advisory lock and specify
#    timeout/ownership behavior.
#    Hint: Only one delivery transaction may make planning decisions at a time.
# 13. [PostgreSQL semantics] Identify which DDL is transactional in PostgreSQL and how
#    non-transactional commands alter the migration policy.
#    Hint: Do not assume every administrative statement can share ordinary transaction rollback.
# 14. [Timeouts] Set statement and lock timeouts per attempt without leaking settings to later
#    pooled work.
#    Hint: Transaction-local settings should expire with commit/rollback.
# 15. [Telemetry design] Define a bounded migration metric schema and a redaction test for
#    exception objects and URL-like fields.
#    Hint: Migration IDs may still become unbounded over years; choose dimensions deliberately.
# 16. [Probe semantics] Distinguish current-but-stale application readiness from database
#    reachability and migration currency.
#    Hint: Each probe should answer one operational question.
# 17. [Decision analysis] Compare forward fix and release rollback when the new schema has
#    already received writes.
#    Hint: Data written under the new contract can make old code incompatible even if DDL
#    reversal is possible.
# 18. [Expand-contract] Design a three-release expand/migrate/contract sequence for renaming a
#    populated column.
#    Hint: Maintain compatibility while old and new application versions overlap.
# 19. [Cleanup] Prove the optional live lab leaves no table, metadata row, lock, connection, or
#    credential-bearing output behind.
#    Hint: A passing mutation test is incomplete without postconditions.
# 20. [Failure simulation] Inject a network-like error immediately after fake commit and require
#    the retry to gather evidence rather than blindly replay.
#    Hint: Client exceptions after commit do not prove server rollback.


def main() -> int:
    print("BRIDGE-OPS-01 starter loaded; no database was contacted.")
    print("Implement the orchestration against Protocol-based fakes first.")
    print("Use only DS60_DATABASE_URL and the disposable course database for the live lab.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
