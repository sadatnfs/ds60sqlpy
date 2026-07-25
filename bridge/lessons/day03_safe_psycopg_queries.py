"""Bridge Day 3: safe parameterized Psycopg 3 queries.

Prerequisite: Bridge Day 2.
Read ``bridge/companion-guides/day03_safe_psycopg_queries.md`` first.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

LESSON_ID = "bridge-03"
PREREQUISITES = ("bridge-02",)
LEVEL = "intermediate"


class ReadCursor(Protocol):
    def execute(
        self,
        query: object,
        params: Sequence[object] | None = None,
    ) -> object: ...

    def fetchall(self) -> Sequence[Sequence[object]]: ...


@dataclass(frozen=True)
class Customer:
    customer_id: int
    full_name: str
    lifetime_value: Decimal


FIND_CUSTOMERS_SQL = """
-- Exercise 1: write a PostgreSQL query with two %s value placeholders.
-- Keep the country and minimum lifetime value out of this string.
""".strip()


def find_customers(
    cursor: ReadCursor,
    *,
    country: str,
    minimum_lifetime_value: Decimal,
) -> list[Customer]:
    """Exercise 2: bind values separately and map rows to ``Customer`` objects."""

    raise NotImplementedError("execute one parameterized query and map its rows")


def build_count_query(table_name: str) -> object:
    """Exercise 3: allowlist then compose an identifier with ``psycopg.sql``."""

    raise NotImplementedError("compose a dynamic identifier without string interpolation")


def main() -> int:
    print("Bridge Day 3 starter loaded; no live database was contacted.")
    print("Implement parameter binding and Identifier-based SQL composition.")
    print("Prove safety with a recording fake before trying the optional live step.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
