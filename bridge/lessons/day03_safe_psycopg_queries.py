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
-- TODO: write a PostgreSQL query with two %s value placeholders.
-- Keep the country and minimum lifetime value out of this string.
""".strip()


def find_customers(
    cursor: ReadCursor,
    *,
    country: str,
    minimum_lifetime_value: Decimal,
) -> list[Customer]:
    """Core implementation: bind values separately and map rows to ``Customer`` objects."""

    raise NotImplementedError("execute one parameterized query and map its rows")


def build_count_query(table_name: str) -> object:
    """Core implementation: allowlist then compose an identifier with ``psycopg.sql``."""

    raise NotImplementedError("compose a dynamic identifier without string interpolation")


# Exercises (answer-free)
# Focus: Keep SQL structure trusted, bind data values separately, and compose the rare dynamic
#    identifier through an allowlist plus Psycopg.
# Assumptions: The course uses PostgreSQL semantics, `Decimal` money, and fake-backed imports
#    that remain usable without Psycopg installed.
# Failure to watch for: String interpolation, quoted placeholders, and treating identifiers as
#    value parameters all break the security boundary.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [SQL implementation] Write `FIND_CUSTOMERS_SQL` for customer ID, name, and lifetime order
#    value by country and minimum total with deterministic ordering.
#    Hint: Left join orders, aggregate at customer grain, and keep two `%s` placeholders
#    unquoted.
#    Verify: Inspect `FIND_CUSTOMERS_SQL`: it selects customer ID/name, uses `LEFT JOIN`,
#    `COALESCE`, `GROUP BY`, and `HAVING`, contains exactly two `%s` placeholders, and orders by
#    lifetime value descending then customer ID.
# 2. [Implementation] Implement `find_customers()` with two bound parameters and map rows to
#    `Customer` while preserving `Decimal` money.
#    Hint: Execute once, fetch once, and make row conversion explicit at the application
#    boundary.
#    Verify: Configure rows with integer/string/Decimal fields; assert one execute call receives
#    `(country, minimum_lifetime_value)` and the returned tuple contains exact typed `Customer`
#    objects with `Decimal` money.
# 3. [Security testing] Use a recording cursor and an injection-shaped country to prove values
#    never enter SQL text.
#    Hint: Assert both halves: placeholder remains in structure and hostile text appears only in
#    parameters.
#    Verify: Use country `US' OR TRUE --`; assert that sentinel is absent from SQL text, appears
#    unchanged as the first bound parameter, and cannot add rows to the fake result.
# 4. [Identifier safety] Implement `build_count_query()` for only `customers`, `orders`, and
#    `order_items` using `psycopg.sql.Identifier`.
#    Hint: Allowlist first, import Psycopg inside the optional boundary, then compose schema and
#    table identifiers.
#    Verify: Assert each of `customers`, `orders`, and `order_items` composes through
#    `sql.Identifier`, while `users` and an injection-shaped name raise `ValueError` before
#    cursor execution.
# 5. [Reasoning] Explain why an allowlist remains valuable when `Identifier` already quotes
#    safely.
#    Hint: Quoting protects syntax; authorization controls which valid object may be selected.
#    Verify: Show that `Identifier` quotes a syntactically valid but unauthorized name, whereas
#    the allowlist rejects it; record authorization and quoting as separate guarantees.
# 6. [Prediction] Predict the result for a customer with no orders and explain the roles of
#    `LEFT JOIN`, `COALESCE`, `GROUP BY`, and `HAVING`.
#    Hint: Track row preservation first, then aggregation, then threshold filtering.
#    Verify: For a customer with no orders and minimum total zero, predict and assert lifetime
#    value `Decimal('0')`; explain that the left join retains the row and `COALESCE` supplies
#    zero before `HAVING` evaluates it.
# 7. [Boundary testing] Test rows containing integer, string, and already-Decimal values plus an
#    empty result; document conversion failures.
#    Hint: Mapping is application validation, not a blind cast after trust.
#    Verify: Assert integer, numeric string, and `Decimal` money rows map predictably, an empty
#    fetch returns `()`, and malformed ID or money data raises the documented conversion
#    exception.
# 8. [Debugging] Repair queries that use `f"...{country}..."` or `WHERE country = '%s'` and
#    explain both failures.
#    Hint: Placeholders are driver syntax and must not be interpolated or quoted.
#    Verify: Show the f-string version embeds the sentinel and the quoted-placeholder version
#    sends literal `%s`; after repair, SQL stays static and the sentinel exists only in
#    parameters.
# 9. [Protocol testing] Verify that `find_customers()` does not depend on the return value of
#    `execute()` and calls `fetchall()` exactly once.
#    Hint: Model only the cursor behavior the consumer uses.
#    Verify: Use an `execute()` method that returns `None`; assert `find_customers()` still
#    succeeds, `execute` is called once, and `fetchall` is called exactly once.
# 10. [Optional integration] Design a bounded, read-only PostgreSQL smoke test gated by
#    `DS60_DATABASE_URL` without importing Psycopg during normal fake tests.
#    Hint: Skip clearly when the opt-in dependency or variable is absent; never print the URL.
#    Verify: With the live gate off, assert no Psycopg import or connection occurs; if enabled,
#    run one ordered read-only query against `advanced_sql_training`, cap rows, and close
#    cleanly.


def main() -> int:
    print("Bridge Day 3 starter loaded; no live database was contacted.")
    print("Implement parameter binding and Identifier-based SQL composition.")
    print("Prove safety with a recording fake before trying the optional live step.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
