-- Day 36: Materialized Views & Caching
-- BEGINNER WORKFLOW - sql-36: Materialized Views
-- Guide: sql/postgres-60day/companion-guides/day36_materialized_views.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-36.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders, mv_category_month_revenue.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Materialized view for category revenue by month
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

-- Query the MV
SELECT
  *
FROM
  mv_category_month_revenue
ORDER BY
  month DESC,
  revenue DESC
LIMIT 50;

-- Refresh when needed (will be rolled back)
REFRESH MATERIALIZED VIEW mv_category_month_revenue;

-- Exercises
-- 1. Create a MV for weekly revenue by country.
--    Inputs: For sql-36 Exercise 1, read from `orders` joined to `customers` and create the materialized view `mv_weekly_country_revenue_solution` with one row per Monday-based `week` (`date_trunc('week', order_date)::date`) and `country`, carrying `revenue` (`SUM(total_amount)`) and `orders` (`COUNT(*)`), then add a unique index on `(week, country)`.
--    Expected result/shape: For sql-36 Exercise 1, `SELECT 1080` on this load for the view build, one row per observed week-country pair across 193 Monday weeks and 7 countries (Brazil has no orders), then `CREATE INDEX`. The view's columns are `week`, `country`, `revenue`, and `orders`.
--    Verify: For sql-36 Exercise 1, confirm that the view's row count equals `SELECT COUNT(*) FROM (SELECT DISTINCT date_trunc('week', o.order_date), c.country FROM orders o JOIN customers c USING (customer_id)) d`, that `SUM(revenue)` is 2355646.89 and `SUM(orders)` is 4362, and that `EXTRACT(ISODOW FROM week)` is 1 (Monday) on every row.
--    Hint ladder, rung 1: For sql-36 Exercise 1, run the `SELECT` behind the view first and check that (`week`, `country`) is unique in its output before you create the view and its unique index.
-- 2. Compare query time against base tables vs MV.
--    Inputs: For sql-36 Exercise 2, run `EXPLAIN (ANALYZE, BUFFERS)` on the base-table aggregate that defines the view, then on `SELECT week, country, revenue, orders FROM mv_weekly_country_revenue_solution`.
--    Expected result/shape: For sql-36 Exercise 2, expected output: two plans. The base-table plan aggregates all 4362 joined orders in a `HashAggregate`, while the view plan is a single `Seq Scan` on the materialized view; both top nodes report the same number of actual rows.
--    Verify: For sql-36 Exercise 2, compare the top node's actual `rows` in both plans (they must match) and the buffers each plan touched; then run both queries without `EXPLAIN` and confirm that `EXCEPT` in both directions returns no rows. Timings vary from run to run, so compare buffers and row counts rather than milliseconds.
--    Hint ladder, rung 1: For sql-36 Exercise 2, start with the first relation in `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_compare`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 3. Prediction: insert a temporary order after the materialized view is built.
--    Predict whether the view changes before REFRESH, then verify.
--    Inputs: For sql-36 Exercise 3, read `orders` and `mv_weekly_country_revenue_solution`: add 1.00 to order 1, the smallest `order_id` (240.20 becomes 241.20), compare `SUM(total_amount)` with `SUM(revenue)` from the view as `live_total` and `stale_mv_total`, then run `REFRESH MATERIALIZED VIEW` and compare again as `live_total` and `refreshed_mv_total`.
--    Expected result/shape: For sql-36 Exercise 3, expected output: `UPDATE 1`, then one row with `live_total` 2,355,647.89 and `stale_mv_total` 2,355,646.89, exactly one dollar apart, then after the refresh one row with both `live_total` and `refreshed_mv_total` at 2,355,647.89. The final columns are `live_total`, and `refreshed_mv_total`.
--    Verify: For sql-36 Exercise 3, confirm, before the refresh, that a fresh weekly aggregate `EXCEPT` the view returns one row, US in the week of 2026-10-12 on this load with revenue 5,847.26 against the view's 5,846.26 over 10 orders, and that the same `EXCEPT` returns 0 rows after the refresh; everything runs inside the file's `BEGIN ... ROLLBACK`, so order 1 is back to 240.20 afterward.
--    Hint ladder, rung 1: For sql-36 Exercise 3, inspect the source keys that survive `WHERE`.
-- 4. Construction: add a unique index that would make a concurrent refresh
--    structurally possible; explain why this lesson still uses ordinary refresh.
--    Inputs: For sql-36 Exercise 4, read `pg_indexes` for `schemaname = 'training'` and `tablename = 'mv_weekly_country_revenue_solution'` after exercise 1 has built the view and its unique index on `(week, country)`.
--    Expected result/shape: For sql-36 Exercise 4, expected output: exactly one row, `CREATE UNIQUE INDEX idx_mv_weekly_country_solution ON training.mv_weekly_country_revenue_solution USING btree (week, country)`. The final columns are `indexdef`.
--    Verify: For sql-36 Exercise 4, confirm `REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_country_revenue_solution` succeeds inside the transaction; then, after a `SAVEPOINT`, drop the index and confirm the concurrent refresh fails with the error message `cannot refresh materialized view ... concurrently` and a hint to create a unique index with no `WHERE` clause, and confirm a unique index on `week` alone fails with `could not create unique index` because each week holds several countries.
--    Hint ladder, rung 1: For sql-36 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. Debugging: compare SUM(orders.total_amount) with line-item revenue and
--    identify which business definition the materialized view actually stores.
--    Inputs: For sql-36 Exercise 5, read `orders` for the header total `SUM(total_amount)` and `order_items` for the line total `SUM(quantity * unit_price * (1 - discount))`, as two scalar subqueries in one `SELECT` with no `FROM` clause.
--    Expected result/shape: For sql-36 Exercise 5, one row, read after exercise 3's update and refresh: `header_revenue` is 2,355,647.89 and `line_revenue` is 2,355,647.1235, so the header total is 0.7665 higher, the 1.00 added to order 1 less the 0.2335 that per-order rounding removes. The final columns are `header_revenue`, and `line_revenue`.
--    Verify: For sql-36 Exercise 5, confirm per order that order 1 is now the only `total_amount` that differs from `ROUND(SUM(line value), 2)`, by exactly 1.00, while 2,856 orders differ before rounding; then insert an order with `total_amount = 50.00` and no items and confirm `header_revenue` rises to 2,355,697.89 while `line_revenue` stays 2,355,647.1235.
--    Hint ladder, rung 1: For sql-36 Exercise 5, select `order_id` from `orders`, and `order_items` before adding derived columns.
-- 6. Edge case: query a month/category combination with no source rows and
--    explain why a materialized aggregate has no automatic zero-valued row.
--    Inputs: For sql-36 Exercise 6, read `orders` for 193 distinct Monday weeks (the CTE is named `months`), `customers` for all 8 countries, and `mv_weekly_country_revenue_solution`; cross join weeks with countries and `LEFT JOIN` the view on both `week` and `country`, turning gaps into 0 with `COALESCE`.
--    Expected result/shape: For sql-36 Exercise 6, expected output: exactly 20 rows on this load: all 8 countries for the newest week, 2026-11-23, where only CA has revenue (742.14), then the weeks of 2026-11-16 and 2026-11-09, with 9 of the 20 rows showing 0. The final columns are `week`, `country`, and `revenue`. The final order is `m.week DESC, c.country`.
--    Verify: For sql-36 Exercise 6, confirm that without the `LIMIT` the grid has 1,544 rows, 193 times 8, of which 1,080 match the view and 464 are zero-filled, and that BR is 0 in every week; then, inside `BEGIN ... ROLLBACK`, insert a 100.00 order for BR customer 8 at the newest `order_date`, refresh the view, and confirm the 2026-11-23 BR row changes from 0 to 100.00.
--    Hint ladder, rung 1: For sql-36 Exercise 6, run `months`, and `countries` one at a time. Record each CTE's row count and `week`, and `country` uniqueness before the next stage uses it.
ROLLBACK;
