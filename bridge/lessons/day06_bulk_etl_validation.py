"""Bridge Day 6: bulk extract-transform-load work and validation.

Prerequisite: Bridge Day 5.
Read ``bridge/companion-guides/day06_bulk_etl_validation.md`` first.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol, TypeVar

LESSON_ID = "bridge-06"
PREREQUISITES = ("bridge-05",)
LEVEL = "advanced"

T = TypeVar("T")


class RowValidationError(ValueError):
    """One source row did not satisfy the input contract."""


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


class BulkCursor(Protocol):
    def executemany(
        self,
        query: object,
        params_seq: Iterable[Sequence[object]],
    ) -> object: ...


def parse_sale(raw: Mapping[str, str]) -> Sale:
    """Exercise 1: validate identifiers, numeric fields, and ISO dates."""

    raise NotImplementedError("convert one raw row or raise RowValidationError")


def partition_rows(
    rows: Iterable[Mapping[str, str]],
) -> tuple[list[Sale], list[RejectedRow]]:
    """Exercise 2: retain valid rows and minimal diagnostics for rejected rows."""

    raise NotImplementedError("partition without logging complete source records")


def batches(items: Sequence[T], size: int) -> list[tuple[T, ...]]:
    """Exercise 3: create deterministic batches and reject invalid sizes."""

    raise NotImplementedError("split a sequence into non-empty batches")


def load_sales(cursor: BulkCursor, sales: Sequence[Sale]) -> int:
    """Exercise 4: use parameterized ``executemany`` or a Psycopg COPY path."""

    raise NotImplementedError("bulk-load already validated records")


def main() -> int:
    print("Bridge Day 6 starter loaded; it performs no I/O by default.")
    print("Validate, partition, batch, and load deterministic sales rows.")
    print("Track accepted, rejected, and submitted counts separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
