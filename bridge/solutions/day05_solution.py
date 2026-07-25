"""Day 5 reference: database seams, fakes, and rollback-only fixtures."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from decimal import Decimal
from typing import Protocol


class OrderRepository(Protocol):
    """Domain-facing interface; callers do not need to know about cursors."""

    def amounts_for_customer(self, customer_id: int) -> Sequence[Decimal]: ...


class QueryCursor(Protocol):
    def execute(
        self,
        query: object,
        params: Sequence[object] | None = None,
    ) -> object: ...

    def fetchall(self) -> Sequence[Sequence[object]]: ...


class RollbackConnection(Protocol):
    def rollback(self) -> None: ...


ORDER_AMOUNTS_SQL = """
SELECT total_amount
FROM training.orders
WHERE customer_id = %s
ORDER BY order_id
""".strip()


class CursorOrderRepository:
    """PostgreSQL adapter behind the small ``OrderRepository`` Protocol."""

    def __init__(self, cursor: QueryCursor) -> None:
        self._cursor = cursor

    def amounts_for_customer(self, customer_id: int) -> list[Decimal]:
        if customer_id < 1:
            raise ValueError("customer_id must be positive")
        self._cursor.execute(ORDER_AMOUNTS_SQL, (customer_id,))
        return [Decimal(str(row[0])) for row in self._cursor.fetchall()]


class FakeOrderRepository:
    """Deterministic test double with observable calls."""

    def __init__(self, amounts: Mapping[int, Sequence[Decimal]]) -> None:
        self._amounts = {key: tuple(value) for key, value in amounts.items()}
        self.requested_customer_ids: list[int] = []

    def amounts_for_customer(self, customer_id: int) -> tuple[Decimal, ...]:
        self.requested_customer_ids.append(customer_id)
        return self._amounts.get(customer_id, ())


def customer_order_total(repository: OrderRepository, customer_id: int) -> Decimal:
    """Apply domain logic to any repository implementation."""

    if customer_id < 1:
        raise ValueError("customer_id must be positive")
    return sum(repository.amounts_for_customer(customer_id), start=Decimal("0.00"))


@contextmanager
def rollback_only(connection: RollbackConnection) -> Iterator[None]:
    """Always roll back fixture changes, whether the test passes or fails."""

    try:
        yield
    finally:
        connection.rollback()


def live_database_url(environ: Mapping[str, str]) -> str | None:
    """Require two explicit switches before a test can use live PostgreSQL."""

    if environ.get("DS60_RUN_LIVE_DB_TESTS") != "1":
        return None
    return environ.get("DS60_DATABASE_URL")
