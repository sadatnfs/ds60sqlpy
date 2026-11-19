# Day 36: Solutions: Materialized Views


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day36_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Materialized view, Freshness, Concurrent refresh. Its worked-model focus is:
Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.

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

A materialized view stores query results. Reads can become cheaper, but the
result is a snapshot and must be refreshed when source data changes.

## Exercise 1: Weekly revenue by country

This demonstration is transactional and leaves no materialized view behind.

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP MATERIALIZED VIEW IF EXISTS mv_weekly_country_revenue_solution;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_solution AS
SELECT
  date_trunc('week', o.order_date)::date AS week_start,
  c.country,
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY
  date_trunc('week', o.order_date),
  c.country;

SELECT
  week_start,
  country,
  ROUND(revenue, 2) AS revenue
FROM
  mv_weekly_country_revenue_solution
ORDER BY
  week_start DESC,
  revenue DESC;

ROLLBACK;
```

Expected shape: one row per observed week-country pair. PostgreSQL weeks begin
on Monday under `date_trunc('week', ...)`.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 1, read from `orders` joined to `customers` and create the materialized view `mv_weekly_country_revenue_solution` with one row per Monday-based `week` (`date_trunc('week', order_date)::date`) and `country`, carrying `revenue` (`SUM(total_amount)`) and `orders` (`COUNT(*)`), then add a unique index on `(week, country)`.
- **Expected result/shape:** For sql-36 Exercise 1, expected output: a `SELECT n` command tag for the view build, one row per observed week-country pair, then `CREATE INDEX`. The view's columns are `week`, `country`, `revenue`, and `orders`.
- **Independent verification:** For sql-36 Exercise 1, confirm that the view's row count equals `SELECT COUNT(*) FROM (SELECT DISTINCT date_trunc('week', o.order_date), c.country FROM orders o JOIN customers c USING (customer_id)) d`, that `SUM(revenue)` is 2355646.89 and `SUM(orders)` is 4362, and that `EXTRACT(ISODOW FROM week)` is 1 (Monday) on every row.
- **Intermediate relation check:** For sql-36 Exercise 1, run the `SELECT` behind the view first and check that (`week`, `country`) is unique in its output before you create the view and its unique index.
- **Clause check:** For sql-36 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_solution`, preserve one row per `week` and `country`, and finish with `week_start`, `country`, and `revenue` ordered by `week_start DESC, revenue DESC`.
- **Alternative/trade-off:** For sql-36 Exercise 1, the chosen form is justified by this lesson-specific rationale: This demonstration is transactional and leaves no materialized view behind. Evaluate another form against the concrete expected result (one row per observed week-country pair. PostgreSQL weeks begin on Monday under `date_trunc('week',) and the verification above.
- **Edge case:** `date_trunc('week', ...)` on a `timestamptz` uses the session `TimeZone`; an order placed late on a Sunday in one zone can belong to the next week in another.

## Exercise 2: Compare base-table and snapshot plans

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP MATERIALIZED VIEW IF EXISTS mv_weekly_country_revenue_compare;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_compare AS
SELECT
  date_trunc('week', o.order_date)::date AS week_start,
  c.country,
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY
  date_trunc('week', o.order_date),
  c.country;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  date_trunc('week', o.order_date)::date AS week_start,
  c.country,
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY
  date_trunc('week', o.order_date),
  c.country;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  week_start,
  country,
  revenue
FROM
  mv_weekly_country_revenue_compare;

ROLLBACK;
```

The materialized-view plan should avoid source joins and aggregation. On this
small dataset, wall-clock differences can be noisy; compare plan work and
buffers as well as execution time.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 2, run `EXPLAIN (ANALYZE, BUFFERS)` on the base-table aggregate that defines the view, then on `SELECT week, country, revenue, orders FROM mv_weekly_country_revenue_solution`.
- **Expected result/shape:** For sql-36 Exercise 2, expected output: two plans. The base-table plan aggregates all 4362 joined orders in a `HashAggregate`, while the view plan is a single `Seq Scan` on the materialized view; both top nodes report the same number of actual rows.
- **Independent verification:** For sql-36 Exercise 2, compare the top node's actual `rows` in both plans (they must match) and the buffers each plan touched; then run both queries without `EXPLAIN` and confirm that `EXCEPT` in both directions returns no rows. Timings vary from run to run, so compare buffers and row counts rather than milliseconds.
- **Intermediate relation check:** For sql-36 Exercise 2, start with the first relation in `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_compare`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-36 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_compare`, preserve one row per `country`, and finish with `week_start`, `country`, and `revenue`.
- **Alternative/trade-off:** For sql-36 Exercise 2, the chosen form is justified by this lesson-specific rationale: The materialized-view plan should avoid source joins and aggregation. Evaluate another form against the concrete expected result (one row per `country`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- A normal `REFRESH MATERIALIZED VIEW` blocks concurrent reads of that view.
  `REFRESH ... CONCURRENTLY` keeps the view readable, but needs an already
  populated view and a unique index on plain columns covering every row (for
  example `(category, month)`); only one refresh per view runs at a time.
  Unlike `CREATE INDEX CONCURRENTLY`, it may run inside a transaction block.
- Refresh is not automatic. Define freshness ownership and monitoring before
  using a materialized view for reporting.
- Materialized views duplicate data and add refresh cost; they are not a default
  replacement for indexing or query repair.

## Exercise 3: Observe stale then refreshed data

The transaction changes one disposable source row after materialization.
Source and view totals diverge until `REFRESH`, making the freshness contract
visible instead of merely described.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 3, read from `orders`, and `mv_weekly_country_revenue_solution`. Compute `live_total`, and `refreshed_mv_total` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-36 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `live_total`, and `refreshed_mv_total`.
- **Independent verification:** For sql-36 Exercise 3, evaluate each of `live_total`, and `refreshed_mv_total` in a separate control `SELECT` over `orders`, and `mv_weekly_country_revenue_solution` using `(order_id = (SELECT MIN(order_id) FROM orders))`; require one final row and compare every value. Add one row for which `(order_id = (SELECT MIN(order_id) FROM orders))` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-36 Exercise 3, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-36 Exercise 3, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, and `mv_weekly_country_revenue_solution`, preserve exactly one summary row, and finish with `live_total`, and `refreshed_mv_total`.
- **Alternative/trade-off:** For sql-36 Exercise 3, the chosen form is justified by this lesson-specific rationale: The transaction changes one disposable source row after materialization. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one row for which `(order_id = (SELECT MIN(order_id) FROM orders))` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 4: Explain concurrent-refresh eligibility

The unique `(week, country)` index supplies a stable row identity required by
concurrent refresh. Initial population still uses an ordinary refresh, because
`CONCURRENTLY` requires an already populated view. This rollback lab also keeps
the ordinary refresh because the view was created inside the uncommitted
lesson transaction: no other session can read it, so there is no read
availability to preserve, and the concurrent diff-and-apply refresh would only
add work.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 4, read from `pg_indexes`. Build the answer toward `indexdef`; keep `indexdef` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-36 Exercise 4, expected output: one row per `indexdef`. The final columns are `indexdef`.
- **Independent verification:** For sql-36 Exercise 4, run an anti-check that counts rows where NOT ((schemaname = 'training' AND tablename = 'mv_weekly_country_revenue_solution')); require unique `indexdef` where the expected grain is one row per key and confirm the projected `indexdef` against `pg_indexes`. Add duplicate source candidates for `indexdef`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-36 Exercise 4, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-36 Exercise 4, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pg_indexes`, preserve one row per `indexdef`, and finish with `indexdef`.
- **Alternative/trade-off:** For sql-36 Exercise 4, the chosen form is justified by this lesson-specific rationale: The unique `(week, country)` index supplies a stable row identity required by concurrent refresh. Evaluate another form against the concrete expected result (one row per `indexdef`) and the verification above.
- **Edge case:** Add duplicate source candidates for `indexdef`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 5: Name the revenue definition

The view stores order-header totals. The control query prints header and
line-item revenue side by side so a consumer must choose a business definition.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 5, read from `orders`, and `order_items`. Compute `header_revenue`, and `line_revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-36 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `header_revenue`, and `line_revenue`.
- **Independent verification:** For sql-36 Exercise 5, evaluate each of `header_revenue`, and `line_revenue` in a separate control `SELECT` over `orders`, and `order_items`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-36 Exercise 5, select `order_id` from `orders`, and `order_items` before adding derived columns.
- **Clause check:** For sql-36 Exercise 5, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `orders`, and `order_items`, preserve exactly one summary row, and finish with `header_revenue`, and `line_revenue`.
- **Alternative/trade-off:** For sql-36 Exercise 5, the chosen form is justified by this lesson-specific rationale: The view stores order-header totals. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 6: Materialize missing combinations explicitly

A cross-joined week/country spine defines requested combinations. The left join
and `COALESCE` then implement a deliberate zero-display policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 6, read from `orders`, `customers`, and `mv_weekly_country_revenue_solution`. Build the answer toward `week`, `country`, and `revenue`; keep `week`, and `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-36 Exercise 6, expected output: at most 20 rows keyed by `week`, and `country`. The final columns are `week`, `country`, and `revenue`. The final order is `m.week DESC, c.country`.
- **Independent verification:** For sql-36 Exercise 6, assert no more than 20 rows, no duplicate `week`, and `country`, and no adjacent pair that violates `m.week DESC, c.country`. Rejoin the returned keys to `orders`, `customers`, and `mv_weekly_country_revenue_solution` to confirm `week`, `country`, and `revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `m.week DESC, c.country`.
- **Intermediate relation check:** For sql-36 Exercise 6, run `months`, and `countries` one at a time. Record each CTE's row count and `week`, and `country` uniqueness before the next stage uses it.
- **Clause check:** For sql-36 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, `customers`, and `mv_weekly_country_revenue_solution`, preserve one row per `week`, and `country`, and finish with `week`, `country`, and `revenue` ordered by `m.week DESC, c.country`.
- **Alternative/trade-off:** For sql-36 Exercise 6, the chosen form is justified by this lesson-specific rationale: A cross-joined week/country spine defines requested combinations. Evaluate another form against the concrete expected result (at most 20 rows keyed by `week`, and `country`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `m.week DESC, c.country`.
