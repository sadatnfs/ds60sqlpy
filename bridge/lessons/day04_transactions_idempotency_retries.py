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
    """Exercise 1: use ``ON CONFLICT`` and a unique idempotency key."""

    raise NotImplementedError("perform an idempotent parameterized insert")


def run_in_transaction(
    connection: TransactionConnection,
    operation: Callable[[], T],
) -> T:
    """Exercise 2: commit success and roll back failure."""

    raise NotImplementedError("define one explicit transaction boundary")


def run_with_retry(
    operation: Callable[[], T],
    *,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    sleep: Callable[[float], None],
) -> T:
    """Exercise 3: retry only transient failures with a bounded delay schedule."""

    raise NotImplementedError("implement bounded retry behavior")


def main() -> int:
    print("Bridge Day 4 starter loaded.")
    print("Implement idempotency, transaction ownership, and classified retries.")
    print("Use fake sleepers and failures so tests remain fast and deterministic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
