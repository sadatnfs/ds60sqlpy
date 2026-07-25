"""Day 4 reference: explicit transactions, idempotency keys, and bounded retries."""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol, TypeVar, cast

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
    """A retryable failure used by deterministic exercises and fakes."""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.05

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds cannot be negative")


DEFAULT_RETRY_POLICY = RetryPolicy()


INSERT_JOB_SQL = """
INSERT INTO pg_temp.bridge_jobs (idempotency_key, payload)
VALUES (%s, %s)
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING job_id
""".strip()


def create_job_once(
    cursor: WriteCursor,
    *,
    idempotency_key: str,
    payload: str,
) -> int | None:
    """Insert once; return ``None`` when the key already exists."""

    if not idempotency_key.strip():
        raise ValueError("idempotency_key cannot be blank")
    cursor.execute(INSERT_JOB_SQL, (idempotency_key, payload))
    row = cursor.fetchone()
    return None if row is None else int(cast(int, row[0]))


def run_in_transaction(
    connection: TransactionConnection,
    operation: Callable[[], T],
) -> T:
    """Commit one unit of work or roll it back before re-raising."""

    try:
        result = operation()
    except BaseException:
        connection.rollback()
        raise
    connection.commit()
    return result


def run_with_retry(
    operation: Callable[[], T],
    *,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    retry_on: tuple[type[BaseException], ...] = (TransientDatabaseError,),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Retry only classified transient failures with bounded exponential delay."""

    for attempt in range(1, policy.max_attempts + 1):
        try:
            return operation()
        except retry_on:
            if attempt == policy.max_attempts:
                raise
            sleep(policy.base_delay_seconds * (2 ** (attempt - 1)))
    raise AssertionError("retry loop exhausted without returning or raising")
