# Day 31: Solutions: `EXPLAIN` and `EXPLAIN ANALYZE`


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day31_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Plan node, Cost estimate, Loop count. Its worked-model focus is:
Run the same safe filter first with `EXPLAIN` and then with `EXPLAIN (ANALYZE, BUFFERS)`. Start at the scan leaf, compare estimated rows with `actual rows × loops`, note rows removed by the filter, and only then read the parent `LIMIT` or aggregate node.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

Execution plans are observations, not fixed expected text. PostgreSQL may choose
different nodes after a version change, data refresh, or statistics update.
Compare estimates, actuals, buffers, and timing rather than memorizing one plan.

## Exercise 1: Change predicates and observe selectivity

These three queries ask for progressively smaller portions of `orders`.

```sql
SET search_path TO training, public;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id,
  total_amount
FROM
  orders;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id,
  total_amount
FROM
  orders
WHERE
  total_amount > 500;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id,
  total_amount
FROM
  orders
WHERE
  total_amount > 500
  AND order_date >= CURRENT_TIMESTAMP - interval '30 days';
```

Compare `rows=` on each plan node and the top-level actual row count. A more
selective predicate returns fewer rows, but it does not guarantee an index scan:
the setup table is small and PostgreSQL can reasonably prefer a sequential
scan.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 1, plan `SELECT * FROM orders` twice with `EXPLAIN (ANALYZE, BUFFERS)`: once with the broad filter `order_date >= CURRENT_TIMESTAMP - interval '3 years'`, and once with a selective filter that adds `status = 'returned'` and `total_amount >= 1000` to a 7-day window.
- **Expected result/shape:** For sql-31 Exercise 1, expected output: two plans, each a `Seq Scan on orders` with a `Filter` line; the broad plan reports thousands of actual rows (4,247 of 4,362 on a freshly seeded database) and the selective plan reports `actual ... rows=0`. Both read the same `Buffers: shared hit=` count, because a sequential scan reads every page whatever the filter keeps.
- **Independent verification:** For sql-31 Exercise 1, run `SELECT COUNT(*)` with each `WHERE` clause and no `EXPLAIN`, and confirm it equals the plan's actual rows; for each plan, actual rows plus `Rows Removed by Filter` must equal `SELECT COUNT(*) FROM orders` (4,362).
- **Intermediate relation check:** For sql-31 Exercise 1, run `SELECT MIN(order_date), MAX(order_date) FROM orders` first: the seeded order dates run from each customer's signup up to the moment `00_setup.sql` ran (early 2023 to the setup day on a recent seed), so the 3-year window keeps most rows.
- **Clause check:** For sql-31 Exercise 1, the solution uses two `EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE ...` statements that differ only in their `WHERE` predicates.
- **Alternative/trade-off:** For sql-31 Exercise 1, plain `EXPLAIN` would show only the estimates; `ANALYZE` is needed to see actual rows and `Rows Removed by Filter`, and it is safe here because the statements are read-only.
- **Edge case:** Because `CURRENT_TIMESTAMP` moves, the broad count drifts slowly as the seed ages; compare counts taken in the same session rather than across days.

## Exercise 2: Compare estimated and actual rows

`EXPLAIN` plans but does not run the `SELECT`; `EXPLAIN ANALYZE` executes it and
adds actual timing, loops, and row counts.

```sql
SET search_path TO training, public;

EXPLAIN
SELECT
  c.country,
  SUM(oi.quantity) AS units
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
GROUP BY
  c.country;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  c.country,
  SUM(oi.quantity) AS units
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
GROUP BY
  c.country;
```

For each node, compare estimated `rows` with `actual ... rows`. Large,
repeatable discrepancies can indicate stale statistics or correlated columns
that ordinary statistics do not model well.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 2, plan the same revenue query, `SELECT c.country, SUM(o.total_amount) AS revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.country`, first with plain `EXPLAIN` and then with `EXPLAIN (ANALYZE, BUFFERS)`.
- **Expected result/shape:** For sql-31 Exercise 2, expected output: the same plan tree twice (on the course seed a `HashAggregate` above a `Hash Join`); only the second adds `actual time=... rows=... loops=...`, `Buffers:` lines, `Planning Time`, and `Execution Time`. The aggregate's actual rows are `7`, one per customer country, against an estimate of `8`.
- **Independent verification:** For sql-31 Exercise 2, run the query without `EXPLAIN` and confirm it returns 7 rows with columns `country` and `revenue`, matching the aggregate node's actual rows; then compare each node's estimated `rows=` with its actual rows multiplied by `loops`.
- **Intermediate relation check:** For sql-31 Exercise 2, the `Hash Join` reports 4,362 actual rows, one per order, before the aggregate collapses them to seven country rows.
- **Clause check:** For sql-31 Exercise 2, the solution runs one plain `EXPLAIN` and one `EXPLAIN (ANALYZE, BUFFERS)` over the same `SELECT ... JOIN ... GROUP BY c.country`.
- **Alternative/trade-off:** For sql-31 Exercise 2, `EXPLAIN (ANALYZE, TIMING OFF)` keeps actual row counts but skips per-node clock calls, which reduces measurement overhead on large plans.
- **Edge case:** A one-row difference between the estimated `8` groups and the actual `7` is normal: the estimate comes from column statistics, not from running the query.

## Pitfalls

- `EXPLAIN ANALYZE` really executes the statement. Use `BEGIN`/`ROLLBACK` when
  analyzing writes and never assume it is harmless in production.
- One timing run includes cache and system noise. Repeat measurements and use
  representative parameters.
- Planning cost units are not milliseconds. Actual time is shown separately.
- A sequential scan is often correct for a small table or a low-selectivity
  predicate.

## Exercise 3: Predict broad and selective plans

The two queries differ only in threshold, so estimated/actual rows and buffers
are comparable. `> 0` should be broader than `> 900`; scan choice still depends
on table size and cost. See the fully runnable query in
[`day31_solutions.sql`](day31_solutions.sql).

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 3, predict which predicate has the smaller row estimate, then run `EXPLAIN (ANALYZE, BUFFERS) SELECT order_id FROM orders WHERE total_amount > 0` and the same query with `total_amount > 900`.
- **Expected result/shape:** For sql-31 Exercise 3, expected output: with current statistics, `total_amount > 0` is estimated at `rows=4362` and returns 4,362 actual rows, while `total_amount > 900` is estimated near `rows=593` and returns 605; both plans report the same `shared hit` count because both are sequential scans.
- **Independent verification:** For sql-31 Exercise 3, confirm the actual counts with `SELECT COUNT(*) FILTER (WHERE total_amount > 0), COUNT(*) FILTER (WHERE total_amount > 900) FROM orders` (4,362 and 605); if both estimates are identical (for example `rows=1454`), the table has no statistics yet, so run `ANALYZE orders;` and plan again.
- **Intermediate relation check:** For sql-31 Exercise 3, `SELECT MIN(total_amount), MAX(total_amount) FROM orders` (20.74 and 1,432.49 on the course seed) shows that `> 0` keeps every row.
- **Clause check:** For sql-31 Exercise 3, the solution runs two `EXPLAIN (ANALYZE, BUFFERS) SELECT order_id FROM orders WHERE total_amount > ...` statements with different constants.
- **Alternative/trade-off:** For sql-31 Exercise 3, an index on `total_amount` would let the selective predicate read fewer pages; without one, row estimates change but the scan and its buffer count do not.
- **Edge case:** Right after `00_setup.sql`, before autovacuum has analyzed `orders`, both estimates can be the same default value; that is missing statistics, not a planner error.

## Exercise 4: Read a verbose join plan

Start at each scan, follow rows into the join, then into the aggregate and root.
`VERBOSE` identifies qualified output expressions; it does not make the query
faster.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 4, run `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)` on `SELECT c.country, COUNT(*) AS order_count FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE c.country = 'US' GROUP BY c.country`.
- **Expected result/shape:** For sql-31 Exercise 4, expected output: on the course seed, a `GroupAggregate` root with 1 actual row, a `Hash Join` with 625 actual rows, a filtered `Seq Scan on training.customers` with 63 actual rows, and a `Seq Scan on training.orders` with 4,362 rows; `VERBOSE` adds `Output:` lines and schema-qualified relation names.
- **Independent verification:** For sql-31 Exercise 4, run the query without `EXPLAIN` and confirm one row, `('US', 625)`; then confirm that `SELECT COUNT(*) FROM customers WHERE country = 'US'` returns 63, the actual rows of the `customers` scan.
- **Intermediate relation check:** For sql-31 Exercise 4, the `Hash` node above the `customers` scan holds the 63 US customers; the join probes it once for each of the 4,362 orders and keeps 625 matches.
- **Clause check:** For sql-31 Exercise 4, the solution uses one `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)` over `SELECT ... FROM customers c JOIN orders o ON ... WHERE c.country = 'US' GROUP BY c.country`.
- **Alternative/trade-off:** For sql-31 Exercise 4, an index on `orders (customer_id)` could turn the join into a nested loop with 63 index lookups; whether that is cheaper depends on how many orders each customer has.
- **Edge case:** Filter on a country with no customers, such as `'ZZ'`: the scan returns 0 rows, the join and the grouped aggregate return 0 rows, and the query returns no row at all rather than a count of zero.

## Exercise 5: Analyze DML safely

`EXPLAIN ANALYZE UPDATE` performs the update. The answer uses an impossible key
and a savepoint, then rolls back to and releases that savepoint.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 5, inside the lesson transaction, set a savepoint, run `EXPLAIN (ANALYZE, BUFFERS) UPDATE orders SET status = status WHERE order_id = -1`, then roll back to the savepoint and release it.
- **Expected result/shape:** For sql-31 Exercise 5, expected output: an `Update on orders` node above an `Index Scan using orders_pkey`, whose actual rows are `0` because no order has `order_id = -1`. The `UPDATE` really executed; only the impossible key and the savepoint keep it harmless.
- **Independent verification:** For sql-31 Exercise 5, confirm that `SELECT COUNT(*) FROM orders` returns 4,362 before and after the rollback; in a scratch transaction, compare `SELECT xmin FROM orders WHERE order_id = 1` before and after `EXPLAIN ANALYZE UPDATE orders SET status = status WHERE order_id = 1`: the `xmin` changes, which proves that `ANALYZE` wrote a new row version, then roll back.
- **Intermediate relation check:** For sql-31 Exercise 5, run `SELECT COUNT(*) FROM orders WHERE order_id = -1` first: it returns 0, so the `UPDATE` cannot match any row.
- **Clause check:** For sql-31 Exercise 5, the solution uses `SAVEPOINT`, one `EXPLAIN (ANALYZE, BUFFERS) UPDATE ... SET status = status WHERE order_id = -1`, `ROLLBACK TO SAVEPOINT`, and `RELEASE SAVEPOINT`.
- **Alternative/trade-off:** For sql-31 Exercise 5, plain `EXPLAIN UPDATE ...` shows the same plan shape without executing; use `ANALYZE` on writes only inside a transaction you will roll back.
- **Edge case:** The `Update on orders` node always reports `rows=0` without `RETURNING`; count changed rows from the scan below it or from the command tag of a real `UPDATE`.

## Exercise 6: Interpret an empty result

The negative-total predicate returns zero because the seed generates no negative
totals; `orders.total_amount` has no `CHECK` constraint, and the planner does not
use `CHECK` constraints on plain tables (`constraint_exclusion = partition`). A
zero actual with an estimate of one row is the planner's floor, not proof that
statistics are stale.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 6, plan `SELECT order_id FROM orders WHERE total_amount < 0` with `EXPLAIN (ANALYZE, BUFFERS)`.
- **Expected result/shape:** For sql-31 Exercise 6, expected output: `actual ... rows=0` with `Rows Removed by Filter: 4362`, and an estimate of `rows=1` when statistics exist, because the planner never estimates fewer than one row. The seed simply contains no negative totals; `orders.total_amount` has no `CHECK` constraint.
- **Independent verification:** For sql-31 Exercise 6, confirm that `SELECT MIN(total_amount) FROM orders` is positive (20.74 on the course seed) and that `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'orders'::regclass` lists only the primary key and the foreign key; then compare the estimate with and without statistics to separate missing statistics from rare data.
- **Intermediate relation check:** For sql-31 Exercise 6, `SELECT COUNT(*) FROM orders WHERE total_amount < 0` returns 0 before you read the plan.
- **Clause check:** For sql-31 Exercise 6, the solution uses one `EXPLAIN (ANALYZE, BUFFERS) SELECT order_id FROM orders WHERE total_amount < 0`.
- **Alternative/trade-off:** For sql-31 Exercise 6, adding `CHECK (total_amount >= 0)` would make negative totals impossible for future writes, but the planner still would not skip the scan, because `constraint_exclusion = partition` applies constraints only to partitions and inheritance children.
- **Edge case:** A predicate that is rare rather than impossible, such as `total_amount > 1400`, gets a small but nonzero estimate from the histogram and returns a few rows.
