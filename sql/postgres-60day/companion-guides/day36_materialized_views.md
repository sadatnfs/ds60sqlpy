# Day 36: Materialized Views and Caching

## How to run this lesson

Start `./classroom`, pick **sql-36** and run **Whole SQL lesson (psql)**.
The learner file builds `mv_category_month_revenue`, reads its newest 50
rows, refreshes it and rolls everything back, so the view never outlives
the run. Edit your copy at
`.learning/sql/sql-36/lesson/workspace/sql/postgres-60day/day36_materialized_views.sql`;
it runs against `advanced_sql_training`. See
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom)
for launch details.

Because the whole file is one transaction, a view you create in it is
invisible to any other session, which matters for the concurrent-refresh
discussion later in this guide.

### Optional contributor notebook route

A notebook lets you query the view between the build and the refresh
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-36
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 35; performance pitfalls](day35_avoiding_pitfalls.md)
- **Artifacts:** [learner SQL](../day36_materialized_views.sql) ·
  [solution reasoning](../solutions/day36_solutions.md) ·
  [executable solution](../solutions/day36_solutions.sql)

## A beginner's mental model for this lesson

An ordinary view is a saved query: every read reruns the joins. A
**materialized view** runs its query once and stores the rows, like a table
filled by `CREATE TABLE ... AS`, except that PostgreSQL remembers the query
so `REFRESH MATERIALIZED VIEW` can rerun it later. Between refreshes the
stored rows do not follow changes to `orders` or `order_items`.

The learner view joins 13,085 order lines to `products` and `orders`, then
groups them into one row per category and calendar month. All six
categories sell in every month, so the row count is six times the number of
months: 276 on a late-2026 load, from February 2023 through the current
month. Its revenue column keeps the unrounded line value
`unit_price * quantity * (1 - discount)`, which totals 2,355,647.1235. The
header column `orders.total_amount` sums to 2,355,646.89 because each order
was rounded to cents, so reconcile the view against `order_items`, not
against order totals.

**Freshness** is how far the stored rows lag their sources. It is a fact
about time, not about query speed, and the person who relies on the view
needs to know when it was last refreshed.

## Two worked SQL examples

### Example 1

```sql
CREATE MATERIALIZED VIEW mv_category_month_revenue AS
SELECT
  p.category,
  date_trunc('month', o.order_date)::date AS month,
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
GROUP BY
  p.category,
  date_trunc('month', o.order_date);
```

**How to read it:** This is data definition: the `SELECT`
inside runs once, and `psql` reports the number of stored rows as a
`SELECT` command tag. The `date_trunc` expression in `GROUP BY` must match
the one in the select list; the `::date` cast only changes how the month
is displayed.

**Expected result/shape:** `SELECT 276` on a late-2026
load, one row per `(category, month)`. Check that no pair repeats by
grouping the view on both columns with `HAVING COUNT(*) > 1`, which returns
nothing, and that `SUM(revenue)` equals the same line expression summed
over `order_items`.

### Example 2

```sql
SELECT
  *
FROM
  mv_category_month_revenue
ORDER BY
  month DESC,
  revenue DESC
LIMIT 50;
```

**How to read it:** The read touches only the stored rows. It
sorts by `month DESC` and then `revenue DESC`, so the six categories of the
newest month come first, ranked by revenue.

**Expected result/shape:** 50 rows: eight months of six
categories, then the two best categories of a ninth month. The first six
rows belong to the current, partial month, so their revenue is roughly half
of the full month that follows. Within a month, two categories with equal
revenue would have no tie-breaker, so add `category` to the sort if you
compare runs.

## Learning objectives

- Materialize a query at a declared grain and reconcile it with source data.
- Design refresh, freshness, ownership, and failure expectations.

## Vocabulary and concepts

- **Materialized view:** stored rows produced by a query and refreshed
  explicitly.
- **Freshness:** how current cached output is relative to its sources.
- **Concurrent refresh:** a read-preserving refresh mode with unique-index and
  populated-view requirements.

## Worked example / walkthrough

Create the monthly-category materialized view inside the learner transaction,
reconcile its total revenue and row-grain uniqueness with the source query,
then refresh it. Query speed is only one dimension; record when the stored rows
become stale and who would own refresh failures.

## Exercises

Complete these in the [learner SQL](../day36_materialized_views.sql):

1. Create weekly country revenue materialization.
   **Inputs/evidence:** For sql-36 Exercise 1, read from `orders` joined to `customers` and create the materialized view `mv_weekly_country_revenue_solution` with one row per Monday-based `week` (`date_trunc('week', order_date)::date`) and `country`, carrying `revenue` (`SUM(total_amount)`) and `orders` (`COUNT(*)`), then add a unique index on `(week, country)`.
   **Expected result/shape:** For sql-36 Exercise 1, `SELECT 1080` on this load for the view build, one row per observed week-country pair across 193 Monday weeks and 7 countries (Brazil has no orders), then `CREATE INDEX`. The view's columns are `week`, `country`, `revenue`, and `orders`.
   **Verify:** For sql-36 Exercise 1, confirm that the view's row count equals `SELECT COUNT(*) FROM (SELECT DISTINCT date_trunc('week', o.order_date), c.country FROM orders o JOIN customers c USING (customer_id)) d`, that `SUM(revenue)` is 2355646.89 and `SUM(orders)` is 4362, and that `EXTRACT(ISODOW FROM week)` is 1 (Monday) on every row.
2. Compare source-query and materialized-query plans.
   **Inputs/evidence:** For sql-36 Exercise 2, run `EXPLAIN (ANALYZE, BUFFERS)` on the base-table aggregate that defines the view, then on `SELECT week, country, revenue, orders FROM mv_weekly_country_revenue_solution`.
   **Expected result/shape:** For sql-36 Exercise 2, expected output: two plans. The base-table plan aggregates all 4362 joined orders in a `HashAggregate`, while the view plan is a single `Seq Scan` on the materialized view; both top nodes report the same number of actual rows.
   **Verify:** For sql-36 Exercise 2, compare the top node's actual `rows` in both plans (they must match) and the buffers each plan touched; then run both queries without `EXPLAIN` and confirm that `EXCEPT` in both directions returns no rows. Timings vary from run to run, so compare buffers and row counts rather than milliseconds.
3. Predict and verify stale results before refresh.
   **Inputs/evidence:** For sql-36 Exercise 3, read `orders` and `mv_weekly_country_revenue_solution`: add 1.00 to order 1, the smallest `order_id` (240.20 becomes 241.20), compare `SUM(total_amount)` with `SUM(revenue)` from the view as `live_total` and `stale_mv_total`, then run `REFRESH MATERIALIZED VIEW` and compare again as `live_total` and `refreshed_mv_total`.
   **Expected result/shape:** For sql-36 Exercise 3, expected output: `UPDATE 1`, then one row with `live_total` 2,355,647.89 and `stale_mv_total` 2,355,646.89, exactly one dollar apart, then after the refresh one row with both `live_total` and `refreshed_mv_total` at 2,355,647.89. The final columns are `live_total`, and `refreshed_mv_total`.
   **Verify:** For sql-36 Exercise 3, confirm, before the refresh, that a fresh weekly aggregate `EXCEPT` the view returns one row, US in the week of 2026-10-12 on this load with revenue 5,847.26 against the view's 5,846.26 over 10 orders, and that the same `EXCEPT` returns 0 rows after the refresh; everything runs inside the file's `BEGIN ... ROLLBACK`, so order 1 is back to 240.20 afterward.
4. Design the unique index required by concurrent refresh.
   **Inputs/evidence:** For sql-36 Exercise 4, read `pg_indexes` for `schemaname = 'training'` and `tablename = 'mv_weekly_country_revenue_solution'` after exercise 1 has built the view and its unique index on `(week, country)`.
   **Expected result/shape:** For sql-36 Exercise 4, expected output: exactly one row, `CREATE UNIQUE INDEX idx_mv_weekly_country_solution ON training.mv_weekly_country_revenue_solution USING btree (week, country)`. The final columns are `indexdef`.
   **Verify:** For sql-36 Exercise 4, confirm `REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_country_revenue_solution` succeeds inside the transaction; then, after a `SAVEPOINT`, drop the index and confirm the concurrent refresh fails with the error message `cannot refresh materialized view ... concurrently` and a hint to create a unique index with no `WHERE` clause, and confirm a unique index on `week` alone fails with `could not create unique index` because each week holds several countries.
5. Reconcile line revenue with the chosen business definition.
   **Inputs/evidence:** For sql-36 Exercise 5, read `orders` for the header total `SUM(total_amount)` and `order_items` for the line total `SUM(quantity * unit_price * (1 - discount))`, as two scalar subqueries in one `SELECT` with no `FROM` clause.
   **Expected result/shape:** For sql-36 Exercise 5, one row, read after exercise 3's update and refresh: `header_revenue` is 2,355,647.89 and `line_revenue` is 2,355,647.1235, so the header total is 0.7665 higher, the 1.00 added to order 1 less the 0.2335 that per-order rounding removes. The final columns are `header_revenue`, and `line_revenue`.
   **Verify:** For sql-36 Exercise 5, confirm per order that order 1 is now the only `total_amount` that differs from `ROUND(SUM(line value), 2)`, by exactly 1.00, while 2,856 orders differ before rounding; then insert an order with `total_amount = 50.00` and no items and confirm `header_revenue` rises to 2,355,697.89 while `line_revenue` stays 2,355,647.1235.
6. Explain absent dimension combinations versus explicit zeros.
   **Inputs/evidence:** For sql-36 Exercise 6, read `orders` for 193 distinct Monday weeks (the CTE is named `months`), `customers` for all 8 countries, and `mv_weekly_country_revenue_solution`; cross join weeks with countries and `LEFT JOIN` the view on both `week` and `country`, turning gaps into 0 with `COALESCE`.
   **Expected result/shape:** For sql-36 Exercise 6, expected output: exactly 20 rows on this load: all 8 countries for the newest week, 2026-11-23, where only CA has revenue (742.14), then the weeks of 2026-11-16 and 2026-11-09, with 9 of the 20 rows showing 0. The final columns are `week`, `country`, and `revenue`. The final order is `m.week DESC, c.country`.
   **Verify:** For sql-36 Exercise 6, confirm that without the `LIMIT` the grid has 1,544 rows, 193 times 8, of which 1,080 match the view and 464 are zero-filled, and that BR is 0 in every week; then, inside `BEGIN ... ROLLBACK`, insert a 100.00 order for BR customer 8 at the newest `order_date`, refresh the view, and confirm the 2026-11-23 BR row changes from 0 to 100.00.

Write a freshness expectation and validation query beside the refresh design.

## Self-check

- Does a declared key uniquely identify every materialized row?
- Can the consumer tolerate the documented refresh interval and failure mode?

## Next step

Continue to [Day 37; partitioning and sharding](day37_partitioning_sharding.md).

## Deep dive and reference

## What you will learn

- Store the result of an expensive query in a materialized view (MV).
- Refresh cached results when source tables change.
- Compare freshness, storage, and query cost with querying base tables.

## How the learner script uses the current schema

The script creates `mv_category_month_revenue` from `orders`, `order_items`, and
`products`. Its grain is one row per `(category, month)`, and revenue is line
price times quantity after discount. It queries and refreshes the MV, then rolls
the object back.

A normal view stores only SQL and executes it on every read. A materialized view
stores rows and can be indexed, but those rows are stale until refreshed.

## Refresh behavior

- `REFRESH MATERIALIZED VIEW` replaces the stored contents and takes an
  `ACCESS EXCLUSIVE` lock, so it blocks reads of that MV during refresh.
- `REFRESH ... CONCURRENTLY` keeps the view readable, but needs an already
  populated view and a unique index on plain columns covering every row (for
  example `(category, month)`); only one refresh per view runs at a time.
  Unlike `CREATE INDEX CONCURRENTLY`, it may run inside a transaction block.
  It computes a difference against the old contents, so it can be slower than
  an ordinary refresh when many rows change.
- PostgreSQL 17 requires the `MAINTAIN` privilege on the view (granted to the
  owner, or through the predefined `pg_maintain` role) to refresh it.
- PostgreSQL does not provide general native incremental MV refresh; selective
  rollup tables are a separate design.

## Errors that explain the refresh rules

Each rule in the previous section has an error message. Run this block
after Example 1 has built the view. The savepoint lets the transaction
continue after the failure, and the final `ROLLBACK` removes the index
again.

```sql expect-error
BEGIN;
SAVEPOINT a;

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_month_revenue;

-- ERROR: cannot refresh materialized view ... concurrently
-- HINT: Create a unique index with no WHERE clause on one or more columns
ROLLBACK TO a;

CREATE UNIQUE INDEX ON mv_category_month_revenue (category, month);

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_month_revenue;

ROLLBACK;
```

With the unique index in place the concurrent refresh succeeds, even inside
a transaction block. A view created `WITH NO DATA` fails differently:
selecting from it reports that it "has not been populated", and a
concurrent refresh reports that `CONCURRENTLY` cannot be used until it is.
`pg_class.relispopulated` shows which state a view is in.

## Practice map

Several prompts above change `orders` inside the transaction; read the
view before and after each `REFRESH` so you can see which numbers moved and
which stayed stale.

## Pitfalls and validation

- Reconcile the MV's total revenue to the source query before measuring speed.
- A fast stale result can be wrong for the consumer's freshness requirement.
- The compact seed may make the raw query as fast as or faster than the MV.
- Document refresh ownership and failure behavior before relying on an MV.
- The learner transaction safely removes the demonstration MV at rollback.

## Expanded practice lab

Prompts 3-6 focus on the materialized view's data contract. A new base row is
invisible until refresh, so record both data time and refresh time. Concurrent
refresh requires a qualifying unique index and cannot be demonstrated as a
first population inside this rollback-only lesson.

Reconcile the view to the exact line-revenue definition it materializes; stored
order totals are a separate measure. Grouped aggregates emit no row for an
absent dimension combination, so any displayed zero must come from an explicit
dimension/date spine and outer join.

## Ask an AI tutor about this lesson

A tutor can quiz you on what a stale view returns: describe a change to
`orders` and ask it which rows of the view would differ before and after a
refresh
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-36: Materialized Views and Caching.

I have completed the direct catalog prerequisite: `sql-35`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day36_materialized_views.md
- Answer-free learner SQL: sql/postgres-60day/day36_materialized_views.sql

Key terms to teach in context: Materialized view, Freshness, Concurrent refresh. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-36/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
