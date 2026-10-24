"""Day 6 reference: deterministic validation, batching, and parameterized loading."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Protocol, TypeVar

T = TypeVar("T")


class RowValidationError(ValueError):
    """One input row failed the course contract."""


@dataclass(frozen=True)
class Sale:
    source_id: str
    customer_id: int
    amount: Decimal
    occurred_on: date


@dataclass(frozen=True)
class RejectedRow:
    source_id: str
    reason: str


@dataclass(frozen=True)
class LoadPlan:
    accepted: tuple[Sale, ...]
    rejected: tuple[RejectedRow, ...]


class BulkCursor(Protocol):
    def executemany(
        self,
        query: object,
        params_seq: Iterable[Sequence[object]],
    ) -> object: ...


UPSERT_SALES_SQL = """
INSERT INTO pg_temp.bridge_sales (source_id, customer_id, amount, occurred_on)
VALUES (%s, %s, %s, %s)
ON CONFLICT (source_id) DO UPDATE
SET customer_id = EXCLUDED.customer_id,
    amount = EXCLUDED.amount,
    occurred_on = EXCLUDED.occurred_on
""".strip()


def parse_sale(raw: Mapping[str, str]) -> Sale:
    """Validate and convert one external row without mutating it."""

    source_id = raw.get("source_id", "").strip()
    if not source_id or len(source_id) > 64:
        raise RowValidationError("source_id must contain 1 to 64 characters")

    try:
        customer_id = int(raw.get("customer_id", ""))
    except ValueError as exc:
        raise RowValidationError("customer_id must be an integer") from exc
    if customer_id < 1:
        raise RowValidationError("customer_id must be positive")

    try:
        amount = Decimal(raw.get("amount", ""))
    except InvalidOperation as exc:
        raise RowValidationError("amount must be a decimal number") from exc
    if not amount.is_finite() or amount <= 0:
        raise RowValidationError("amount must be finite and positive")
    amount = amount.quantize(Decimal("0.01"))

    try:
        occurred_on = date.fromisoformat(raw.get("occurred_on", ""))
    except ValueError as exc:
        raise RowValidationError("occurred_on must use YYYY-MM-DD") from exc

    return Sale(source_id, customer_id, amount, occurred_on)


def plan_load(rows: Iterable[Mapping[str, str]]) -> LoadPlan:
    """Partition rows into accepted records and minimal rejection diagnostics."""

    accepted: list[Sale] = []
    rejected: list[RejectedRow] = []
    for raw in rows:
        try:
            accepted.append(parse_sale(raw))
        except RowValidationError as exc:
            rejected.append(
                RejectedRow(
                    source_id=raw.get("source_id", "<missing>") or "<missing>",
                    reason=str(exc),
                )
            )
    return LoadPlan(tuple(accepted), tuple(rejected))


def batches(items: Sequence[T], size: int) -> list[tuple[T, ...]]:
    """Split a finite sequence into deterministic, non-empty batches."""

    if size < 1:
        raise ValueError("batch size must be at least 1")
    return [tuple(items[start : start + size]) for start in range(0, len(items), size)]


def load_sales(cursor: BulkCursor, sales: Sequence[Sale]) -> int:
    """Submit validated sales with parameters separate from SQL text."""

    if not sales:
        return 0
    parameters = [
        (sale.source_id, sale.customer_id, sale.amount, sale.occurred_on) for sale in sales
    ]
    cursor.executemany(UPSERT_SALES_SQL, parameters)
    return len(parameters)
