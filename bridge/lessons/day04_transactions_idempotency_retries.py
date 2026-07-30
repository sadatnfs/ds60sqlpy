"""Bridge Day 4: transactions, idempotency, and bounded retries.

Prerequisite: Bridge Day 3.
Read ``bridge/companion-guides/day04_transactions_idempotency_retries.md`` first.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol, TypeVar

LESSON_ID = "bridge-04"
PREREQUISITES = ("bridge-03",)
LEVEL = "intermediate"

T = TypeVar("T")


class WriteCursor(Protocol):
    def execute(
        self,
        query: object,
        params: Sequence[object] | None = None,
    ) -> object: ...

    def fetchone(self) -> Sequence[object] | None: ...


class TransactionConnection(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class TransientDatabaseError(RuntimeError):
    """Use this fake-friendly exception to classify retryable exercise failures."""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.05


DEFAULT_RETRY_POLICY = RetryPolicy()


def create_job_once(
    cursor: WriteCursor,
    *,
    idempotency_key: str,
    payload: str,
) -> int | None:
    """Core implementation: use ``ON CONFLICT`` and a unique idempotency key."""

    raise NotImplementedError("perform an idempotent parameterized insert")


def run_in_transaction(
    connection: TransactionConnection,
    operation: Callable[[], T],
) -> T:
    """Core implementation: commit success and roll back failure."""

    raise NotImplementedError("define one explicit transaction boundary")


def run_with_retry(
    operation: Callable[[], T],
    *,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    sleep: Callable[[float], None],
) -> T:
    """Core implementation: retry only transient failures with a bounded delay schedule."""

    raise NotImplementedError("implement bounded retry behavior")


# Exercises (answer-free)
# Focus: Make writes safe to repeat by combining a database uniqueness boundary, explicit
#    transaction ownership, and narrowly classified retries.
# Assumptions: One stable source key identifies one logical job; each retry executes a fresh
#    transaction attempt; fake sleepers keep tests deterministic.
# Failure to watch for: Retrying a non-idempotent or ambiguously committed write can duplicate
#    effects even when backoff logic is correct.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Validation] Validate `RetryPolicy` so attempts are at least one and base delay is finite
#    and non-negative.
#    Hint: Reject unusable policy at construction rather than inside a failing retry loop.
# 2. [SQL implementation] Implement `create_job_once()` with one parameterized `INSERT`, a
#    unique idempotency key, `ON CONFLICT DO NOTHING`, and `RETURNING job_id`.
#    Hint: Let the uniqueness constraint arbitrate concurrency; do not pre-read.
# 3. [Mapping] Return the inserted ID when `fetchone()` yields a row and `None` for a duplicate
#    without issuing a second statement.
#    Hint: Treat `None` as the documented `DO NOTHING` result.
# 4. [Transaction] Implement `run_in_transaction()` so success commits and any operation failure
#    rolls back before re-raising.
#    Hint: The wrapper owns the boundary; the operation owns only domain work.
# 5. [Retry] Implement `run_with_retry()` for only `TransientDatabaseError`, stopping at
#    `max_attempts` with delays `base * 2**(attempt - 1)`.
#    Hint: Never sleep after the last failed attempt and never catch permanent errors.
# 6. [Testing] Test two transient failures followed by success with a list append sleeper, plus
#    a permanent `ValueError` that escapes immediately.
#    Hint: Assert result, call count, and the complete delay sequence.
# 7. [Design] Decide whether retry owns a statement, a complete transaction attempt, or an
#    entire command and justify the chosen scope.
#    Hint: A failed PostgreSQL transaction cannot safely continue; retry needs fresh state.
# 8. [Composition] Compose retry with transaction ownership so every attempt receives fresh
#    connection state and cleanup happens before delay.
#    Hint: The retry operation should create and finish one complete transaction attempt.
# 9. [Extension] Add optional jitter through an injected function while keeping tests
#    deterministic and delays bounded.
#    Hint: Randomness is another effect boundary and should be injected.
# 10. [Failure analysis] Explain how a connection loss during commit creates an uncertain
#    outcome and how the idempotency key resolves the next attempt.
#    Hint: The client may not know whether the server committed.
# 11. [Input validation] Define and test boundaries for blank idempotency keys and oversized
#    payloads before opening a transaction.
#    Hint: Fast local validation avoids obviously invalid database work but does not replace
#    constraints.
# 12. [Concurrency] Model two workers racing on the same idempotency key and identify which
#    outcome the unique constraint guarantees.
#    Hint: A read-then-insert sequence cannot provide the same atomic guarantee.
# 13. [Observability] Design retry metrics with low-cardinality tags and no payload, key,
#    exception message, or request ID.
#    Hint: Dimensions should describe bounded classes, not individual events.
# 14. [Interruption] Decide how cancellation or `KeyboardInterrupt` crosses transaction and
#    retry layers without being mistaken for a transient database error.
#    Hint: Cleanup may be broad, but retry classification should remain narrow.


def main() -> int:
    print("Bridge Day 4 starter loaded.")
    print("Implement idempotency, transaction ownership, and classified retries.")
    print("Use fake sleepers and failures so tests remain fast and deterministic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
