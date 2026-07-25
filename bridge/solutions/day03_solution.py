"""Day 3 reference: parameterized Psycopg queries and safe identifiers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from importlib import import_module
from typing import Protocol, cast


class ReadCursor(Protocol):
    """Minimal cursor behavior needed by the query function."""

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
SELECT
    c.customer_id,
    c.full_name,
    COALESCE(sum(o.total_amount), 0) AS lifetime_value
FROM training.customers AS c
LEFT JOIN training.orders AS o USING (customer_id)
WHERE c.country = %s
GROUP BY c.customer_id, c.full_name
HAVING COALESCE(sum(o.total_amount), 0) >= %s
ORDER BY lifetime_value DESC, c.customer_id
""".strip()


def find_customers(
    cursor: ReadCursor,
    *,
    country: str,
    minimum_lifetime_value: Decimal,
) -> list[Customer]:
    """Fetch customers while keeping values separate from SQL text."""

    cursor.execute(FIND_CUSTOMERS_SQL, (country, minimum_lifetime_value))
    return [
        Customer(
            customer_id=int(cast(int, row[0])),
            full_name=str(row[1]),
            lifetime_value=Decimal(str(row[2])),
        )
        for row in cursor.fetchall()
    ]


def build_count_query(table_name: str) -> object:
    """Compose a trusted dynamic table identifier with Psycopg's SQL objects."""

    allowed_tables = {"customers", "orders", "order_items"}
    if table_name not in allowed_tables:
        raise ValueError(f"unsupported training table: {table_name!r}")

    try:
        sql = import_module("psycopg.sql")
    except ImportError as exc:  # pragma: no cover - depends on optional installation
        raise RuntimeError("install the bridge dependency group to use live SQL") from exc

    query: object = sql.SQL("SELECT count(*) FROM training.{}").format(sql.Identifier(table_name))
    return query


def count_training_rows(cursor: ReadCursor, table_name: str) -> int:
    """Run the safely composed identifier query and return its count."""

    cursor.execute(build_count_query(table_name))
    rows = cursor.fetchall()
    if len(rows) != 1 or len(rows[0]) != 1:
        raise ValueError("count query returned an unexpected result shape")
    return int(cast(int, rows[0][0]))
