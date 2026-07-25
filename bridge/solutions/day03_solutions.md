# Bridge Day 3 — Solution notes

Start with the [learner file](../lessons/day03_safe_psycopg_queries.py). The
reference implementation is [day03_solution.py](day03_solution.py).

## Value binding

`FIND_CUSTOMERS_SQL` contains two `%s` placeholders. `find_customers()` supplies
the country and minimum `Decimal` as a separate tuple. A recording fake proves
that injection-shaped input is data in `params`, never text in the query.

The SQL left-joins orders, groups per customer, converts no-order totals to zero,
filters aggregates with `HAVING`, and uses customer ID as a deterministic
tie-breaker. Returned driver rows become immutable `Customer` objects at the
adapter boundary.

## Identifier composition

`build_count_query()` first allowlists three course tables. It then imports
`psycopg.sql` at the live boundary and combines `SQL` with `Identifier`.
Identifiers cannot be parameters, and manually quoting them is brittle.

The allowlist and `Identifier` solve different problems:

- `Identifier` produces valid, injection-safe SQL syntax.
- The allowlist enforces the application's authorization and intent.

## Tradeoffs

- A positional row mapper is lightweight but depends on selected column order.
  Psycopg row factories can return mappings or dataclasses when that improves a
  larger adapter.
- Converting through `Decimal(str(value))` is tolerant of fake values and common
  driver outputs. A strict application may reject unexpected driver types.
- Local Psycopg import keeps fake tests offline and importable. It moves a
  missing dependency error to the optional live function, where the message is
  more actionable.
- One aggregate query is efficient for this lesson. At higher volume, verify
  its plan and indexes against real PostgreSQL data.

Never replace the PostgreSQL integration check with SQLite. The recording fake
proves application composition; PostgreSQL proves PostgreSQL behavior.

