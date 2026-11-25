# Day 36: Solutions: Materialized Views


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The executable file runs all six answers in one transaction and rolls back,
including the update to order 1 in exercise 3. Read each `SELECT n` tag and
plan before the timing lines. General advice is in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day36_solutions.sql
```

## How these answers fit together

The answers build one view, `mv_weekly_country_revenue_solution`, and then
question it: what it costs to read, how it goes stale, what makes a
concurrent refresh possible, which revenue it stores and how missing
combinations appear. The view sums `orders.total_amount` and counts
orders per Monday week and country, with a unique index on
`(week, country)`. The learner file is
[day36_materialized_views.sql](../day36_materialized_views.sql).

## Exercise 1: Weekly revenue by country

The view is built inside the file's transaction and stays there for
exercises 2 to 6, which all read it. The file's final `ROLLBACK` removes the
view and its index, so nothing is left behind.

```sql
BEGIN;
SET search_path TO training, public;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_solution AS
SELECT
  date_trunc('week', o.order_date)::date AS week,
  c.country,
  SUM(o.total_amount) AS revenue,
  COUNT(*) AS orders
FROM
  orders o
  JOIN customers c USING (customer_id)
GROUP BY
  date_trunc('week', o.order_date),
  c.country;

CREATE UNIQUE INDEX idx_mv_weekly_country_solution ON mv_weekly_country_revenue_solution (week, country);
```

Expected shape: one row per observed week-country pair. PostgreSQL weeks begin
on Monday under `date_trunc('week', ...)`.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 1, read from `orders` joined to `customers` and create the materialized view `mv_weekly_country_revenue_solution` with one row per Monday-based `week` (`date_trunc('week', order_date)::date`) and `country`, carrying `revenue` (`SUM(total_amount)`) and `orders` (`COUNT(*)`), then add a unique index on `(week, country)`.
- **Expected result/shape:** For sql-36 Exercise 1, `SELECT 1080` on this load for the view build, one row per observed week-country pair across 193 Monday weeks and 7 countries (Brazil has no orders), then `CREATE INDEX`. The view's columns are `week`, `country`, `revenue`, and `orders`.
- **Independent verification:** For sql-36 Exercise 1, confirm that the view's row count equals `SELECT COUNT(*) FROM (SELECT DISTINCT date_trunc('week', o.order_date), c.country FROM orders o JOIN customers c USING (customer_id)) d`, that `SUM(revenue)` is 2355646.89 and `SUM(orders)` is 4362, and that `EXTRACT(ISODOW FROM week)` is 1 (Monday) on every row.

- **Intermediate relation check:** On a late-2026 load the query behind the view returns 1,080 rows: 193 weeks that have orders times the countries that ordered in them. Brazil never appears, because its 62 customers have no orders. The `DISTINCT` count in the contract is also 1,080, so `(week, country)` is unique before the index is built.
- **Clause check:** Grouping by `date_trunc('week', o.order_date)` and selecting its `::date` cast gives one Monday per group, so `EXTRACT(ISODOW FROM week)` is 1 on every row. The view's `revenue` totals 2,355,646.89 and `orders` totals 4,362, matching the base tables.
- **Alternative/trade-off:** `CREATE MATERIALIZED VIEW ... WITH NO DATA` defines the view without running the query, and a later `REFRESH` fills it. That splits a slow build from the deployment, but a read before the first refresh fails instead of returning zero rows.
- **Edge case:** `date_trunc('week', ...)` on a `timestamptz` uses the session `TimeZone`; an order placed late on a Sunday in one zone can belong to the next week in another.

## Exercise 2: Compare base-table and snapshot plans

Run this in the same transaction, after exercise 1 has built the view.

```sql
EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  date_trunc('week', o.order_date)::date AS week,
  c.country,
  SUM(o.total_amount) AS revenue,
  COUNT(*) AS orders
FROM
  orders o
  JOIN customers c USING (customer_id)
GROUP BY
  date_trunc('week', o.order_date),
  c.country;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  week,
  country,
  revenue,
  orders
FROM
  mv_weekly_country_revenue_solution;
```

The materialized-view plan should avoid source joins and aggregation. On this
small dataset, wall-clock differences can be noisy; compare plan work and
buffers as well as execution time.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 2, run `EXPLAIN (ANALYZE, BUFFERS)` on the base-table aggregate that defines the view, then on `SELECT week, country, revenue, orders FROM mv_weekly_country_revenue_solution`.
- **Expected result/shape:** For sql-36 Exercise 2, expected output: two plans. The base-table plan aggregates all 4362 joined orders in a `HashAggregate`, while the view plan is a single `Seq Scan` on the materialized view; both top nodes report the same number of actual rows.
- **Independent verification:** For sql-36 Exercise 2, compare the top node's actual `rows` in both plans (they must match) and the buffers each plan touched; then run both queries without `EXPLAIN` and confirm that `EXCEPT` in both directions returns no rows. Timings vary from run to run, so compare buffers and row counts rather than milliseconds.

- **Intermediate relation check:** Both top nodes report 1,080 actual rows. The base plan hash-joins 4,362 orders to 500 customers before its `HashAggregate`; the view plan is one `Seq Scan` on the stored rows.
- **Clause check:** The base plan touches 74 shared buffers, 65 for `orders` and 9 for `customers`, while the view scan touches 8. The aggregate is estimated at 4,362 groups but produces 1,080, because the planner has no statistics for the `date_trunc` expression, the same blind spot Day 35 measured.
- **Alternative/trade-off:** One run took about 3.7 ms for the base query and 0.07 ms for the view. The saving is real but small at this size, and it is paid back at every refresh, which reruns the full aggregate.
- **Edge case:** Equal results here only show that the view is fresh immediately after it was built. In a running system the same comparison doubles as a freshness test: any rows returned by `EXCEPT` are changes the view has not caught up with.

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

- **Inputs/evidence:** For sql-36 Exercise 3, read `orders` and `mv_weekly_country_revenue_solution`: add 1.00 to order 1, the smallest `order_id` (240.20 becomes 241.20), compare `SUM(total_amount)` with `SUM(revenue)` from the view as `live_total` and `stale_mv_total`, then run `REFRESH MATERIALIZED VIEW` and compare again as `live_total` and `refreshed_mv_total`.
- **Expected result/shape:** For sql-36 Exercise 3, expected output: `UPDATE 1`, then one row with `live_total` 2,355,647.89 and `stale_mv_total` 2,355,646.89, exactly one dollar apart, then after the refresh one row with both `live_total` and `refreshed_mv_total` at 2,355,647.89. The final columns are `live_total`, and `refreshed_mv_total`.
- **Independent verification:** For sql-36 Exercise 3, confirm, before the refresh, that a fresh weekly aggregate `EXCEPT` the view returns one row, US in the week of 2026-10-12 on this load with revenue 5,847.26 against the view's 5,846.26 over 10 orders, and that the same `EXCEPT` returns 0 rows after the refresh; everything runs inside the file's `BEGIN ... ROLLBACK`, so order 1 is back to 240.20 afterward.

- **Intermediate relation check:** The `UPDATE` reports `UPDATE 1`: order 1, the smallest id, goes from 240.20 to 241.20.
- **Clause check:** Before the refresh the extra query shows `live_total` 2,355,647.89 against `stale_mv_total` 2,355,646.89, exactly one dollar apart. After `REFRESH MATERIALIZED VIEW` both columns read 2,355,647.89, which is the contract's `live_total` and `refreshed_mv_total` pair.
- **Alternative/trade-off:** Totals can hide offsetting changes. A stricter check joins the view to a fresh aggregate on `(week, country)` and lists the rows whose revenue differs; before the refresh only one row, the week and country of order 1, should appear.
- **Edge case:** The stale view is visible here only to this session, because nothing has been committed. In production, readers keep seeing the old rows until the refresh commits, and an ordinary refresh blocks them while it runs.

## Exercise 4: Explain concurrent-refresh eligibility

The unique `(week, country)` index supplies a stable row identity required by
concurrent refresh. Initial population still uses an ordinary refresh, because
`CONCURRENTLY` requires an already populated view. This rollback lab also keeps
the ordinary refresh because the view was created inside the uncommitted
lesson transaction: no other session can read it, so there is no read
availability to preserve, and the concurrent diff-and-apply refresh would only
add work.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 4, read `pg_indexes` for `schemaname = 'training'` and `tablename = 'mv_weekly_country_revenue_solution'` after exercise 1 has built the view and its unique index on `(week, country)`.
- **Expected result/shape:** For sql-36 Exercise 4, expected output: exactly one row, `CREATE UNIQUE INDEX idx_mv_weekly_country_solution ON training.mv_weekly_country_revenue_solution USING btree (week, country)`. The final columns are `indexdef`.
- **Independent verification:** For sql-36 Exercise 4, confirm `REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_country_revenue_solution` succeeds inside the transaction; then, after a `SAVEPOINT`, drop the index and confirm the concurrent refresh fails with the error message `cannot refresh materialized view ... concurrently` and a hint to create a unique index with no `WHERE` clause, and confirm a unique index on `week` alone fails with `could not create unique index` because each week holds several countries.

- **Intermediate relation check:** `pg_indexes` returns one row: `CREATE UNIQUE INDEX idx_mv_weekly_country_solution ON training.mv_weekly_country_revenue_solution USING btree (week, country)`.
- **Clause check:** The filter names both `schemaname` and `tablename`. A view with the same name in another schema would otherwise add a row and hide which index belongs to this one.
- **Alternative/trade-off:** Instead of reading the catalog, try the refresh. `REFRESH MATERIALIZED VIEW CONCURRENTLY` succeeds on this view inside the transaction, and fails on the learner's `mv_category_month_revenue` with a hint to create a unique index with no `WHERE` clause.
- **Edge case:** A view created `WITH NO DATA` cannot be refreshed concurrently even with the index; PostgreSQL reports that `CONCURRENTLY` cannot be used until the view is populated, so the first fill is always an ordinary refresh.

## Exercise 5: Name the revenue definition

The view stores order-header totals. The control query prints header and
line-item revenue side by side so a consumer must choose a business definition.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 5, read `orders` for the header total `SUM(total_amount)` and `order_items` for the line total `SUM(quantity * unit_price * (1 - discount))`, as two scalar subqueries in one `SELECT` with no `FROM` clause.
- **Expected result/shape:** For sql-36 Exercise 5, one row, read after exercise 3's update and refresh: `header_revenue` is 2,355,647.89 and `line_revenue` is 2,355,647.1235, so the header total is 0.7665 higher, the 1.00 added to order 1 less the 0.2335 that per-order rounding removes. The final columns are `header_revenue`, and `line_revenue`.
- **Independent verification:** For sql-36 Exercise 5, confirm per order that order 1 is now the only `total_amount` that differs from `ROUND(SUM(line value), 2)`, by exactly 1.00, while 2,856 orders differ before rounding; then insert an order with `total_amount = 50.00` and no items and confirm `header_revenue` rises to 2,355,697.89 while `line_revenue` stays 2,355,647.1235.

- **Intermediate relation check:** One row. This query runs after exercise 3 added 1.00 to order 1, so `header_revenue` is 2,355,647.89 against `line_revenue` 2,355,647.1235, a gap of 0.7665.
- **Clause check:** The gap has two parts. Exercise 3's update adds 1.00 to the header side, and per-order rounding takes 0.2335 off it, because each order header is rounded to cents while line values keep four decimals.
- **Alternative/trade-off:** The two views in this lesson disagree on purpose: the learner's category view stores line revenue and this exercise's view stores header totals. A name such as `header_revenue` for the column would stop a dashboard from mixing them.
- **Edge case:** Neither measure filters on `status`, so the 872 returned orders count as revenue in both. A net-revenue view needs its own filter and its own name.

## Exercise 6: Materialize missing combinations explicitly

A cross-joined week/country spine defines requested combinations. The left join
and `COALESCE` then implement a deliberate zero-display policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-36 Exercise 6, read `orders` for 193 distinct Monday weeks (the CTE is named `months`), `customers` for all 8 countries, and `mv_weekly_country_revenue_solution`; cross join weeks with countries and `LEFT JOIN` the view on both `week` and `country`, turning gaps into 0 with `COALESCE`.
- **Expected result/shape:** For sql-36 Exercise 6, expected output: exactly 20 rows on this load: all 8 countries for the newest week, 2026-11-23, where only CA has revenue (742.14), then the weeks of 2026-11-16 and 2026-11-09, with 9 of the 20 rows showing 0. The final columns are `week`, `country`, and `revenue`. The final order is `m.week DESC, c.country`.
- **Independent verification:** For sql-36 Exercise 6, confirm that without the `LIMIT` the grid has 1,544 rows, 193 times 8, of which 1,080 match the view and 464 are zero-filled, and that BR is 0 in every week; then, inside `BEGIN ... ROLLBACK`, insert a 100.00 order for BR customer 8 at the newest `order_date`, refresh the view, and confirm the 2026-11-23 BR row changes from 0 to 100.00.

- **Intermediate relation check:** The CTE called `months` holds 193 distinct Monday weeks, and `countries` holds all 8 countries, Brazil included. The cross join makes 1,544 pairs, the view supplies 1,080 of them and the other 464 become zeros.
- **Clause check:** The `LEFT JOIN` matches on both `week` and `country`, and `COALESCE(v.revenue, 0)` turns each unmatched pair into 0. On a late-2026 load 9 of the first 20 rows are zeros: Brazil in each week, and six countries with no order yet in the newest, partial week.
- **Alternative/trade-off:** Taking weeks from `orders` skips any week with no order at all. A spine from `generate_series` between the first and last Monday has 198 weeks on the same load, so five empty weeks would appear as zeros too.
- **Edge case:** A zero for Brazil says "no revenue", while the truth is that its customers have never ordered. Whether to show 0, `NULL` or no row is a reporting decision, so state it where the view is published.

## Final self-check

1. Why does the learner view total 2,355,647.1235 while `orders` totals
   2,355,646.89?
2. What did `stale_mv_total` show after order 1 changed, and what made it
   match `live_total`?
3. Which two conditions must hold before `REFRESH ... CONCURRENTLY` runs?
4. How many zero rows does the spine add, and why is Brazil one of them?
