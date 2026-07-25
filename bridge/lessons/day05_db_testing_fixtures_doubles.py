"""Bridge Day 5: database tests, fixtures, and test doubles.

Prerequisite: Bridge Day 4.
Read ``bridge/companion-guides/day05_db_testing_fixtures_doubles.md`` first.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from decimal import Decimal
from typing import Protocol

LESSON_ID = "bridge-05"
PREREQUISITES = ("bridge-04",)
LEVEL = "intermediate"


class OrderRepository(Protocol):
    def amounts_for_customer(self, customer_id: int) -> Sequence[Decimal]: ...


class RollbackConnection(Protocol):
    def rollback(self) -> None: ...


def customer_order_total(repository: OrderRepository, customer_id: int) -> Decimal:
    """Exercise 1: implement domain logic against a small Protocol."""

    raise NotImplementedError("sum customer order amounts without importing Psycopg")


class FakeOrderRepository:
    """Exercise 2: create a configurable fake that also records calls."""

    def __init__(self) -> None:
        raise NotImplementedError("accept deterministic customer amounts")

    def amounts_for_customer(self, customer_id: int) -> Sequence[Decimal]:
        raise NotImplementedError("record the request and return configured amounts")


@contextmanager
def rollback_only(connection: RollbackConnection) -> Iterator[None]:
    """Exercise 3: always roll back changes made by an optional live test."""

    raise NotImplementedError("implement rollback-only fixture behavior")
    yield  # pragma: no cover - keeps this function a generator while unfinished


def main() -> int:
    print("Bridge Day 5 starter loaded.")
    print("Build fast fake-backed tests first, then one opt-in PostgreSQL integration test.")
    print("The integration fixture must roll back even when the assertion fails.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
