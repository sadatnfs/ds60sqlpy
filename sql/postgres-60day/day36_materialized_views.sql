-- Day 36: Materialized Views & Caching
-- BEGINNER WORKFLOW — sql-36: Materialized Views
-- Guide: sql/postgres-60day/companion-guides/day36_materialized_views.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-36/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
SELECT p.category,
       date_trunc('month', o.order_date)::date AS month,
       SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
GROUP BY p.category, date_trunc('month', o.order_date);

-- Query the MV
SELECT * FROM mv_category_month_revenue ORDER BY month DESC, revenue DESC LIMIT 50;

-- Refresh when needed (will be rolled back)
REFRESH MATERIALIZED VIEW mv_category_month_revenue;

-- Exercises
-- 1. Create a MV for weekly revenue by country.
--    Inputs: For sql-36 Exercise 1, read from `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_solution`. Compute `week_start`, `country`, and `revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-36 Exercise 1, expected output: one row per observed week-country pair. PostgreSQL weeks begin on Monday under `date_trunc('week',. The final columns are `week_start`, `country`, and `revenue`. The final order is `week_start DESC, revenue DESC`.
--    Verify: For sql-36 Exercise 1, evaluate each of `revenue` in a separate control `SELECT` over `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_solution`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-36 Exercise 1, start with the first relation in `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_solution`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 2. Compare query time against base tables vs MV.
--    Inputs: For sql-36 Exercise 2, run the underlying read-only query over `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_compare` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-36 Exercise 2, expected output: one row per `country`. The final columns are `week_start`, `country`, and `revenue`.
--    Verify: For sql-36 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-36 Exercise 2, start with the first relation in `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_compare`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 3. Prediction: insert a temporary order after the materialized view is built.
--    Predict whether the view changes before REFRESH, then verify.
--    Inputs: For sql-36 Exercise 3, read from `orders`, and `mv_weekly_country_revenue_solution`. Compute `live_total`, and `refreshed_mv_total` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-36 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `live_total`, and `refreshed_mv_total`.
--    Verify: For sql-36 Exercise 3, evaluate each of `live_total`, and `refreshed_mv_total` in a separate control `SELECT` over `orders`, and `mv_weekly_country_revenue_solution` using `(order_id = (SELECT MIN(order_id) FROM orders))`; require one final row and compare every value. Add one row for which `(order_id = (SELECT MIN(order_id) FROM orders))` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-36 Exercise 3, inspect the source keys that survive `WHERE`.
-- 4. Construction: add a unique index that would make a concurrent refresh
--    structurally possible; explain why this lesson still uses ordinary refresh.
--    Inputs: For sql-36 Exercise 4, read from `pg_indexes`. Build the answer toward `indexdef`; keep `indexdef` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-36 Exercise 4, expected output: one row per `indexdef`. The final columns are `indexdef`.
--    Verify: For sql-36 Exercise 4, run an anti-check that counts rows where NOT ((schemaname = 'training' AND tablename = 'mv_weekly_country_revenue_solution')); require unique `indexdef` where the expected grain is one row per key and confirm the projected `indexdef` against `pg_indexes`. Add duplicate source candidates for `indexdef`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-36 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. Debugging: compare SUM(orders.total_amount) with line-item revenue and
--    identify which business definition the materialized view actually stores.
--    Inputs: For sql-36 Exercise 5, read from `orders`, and `order_items`. Compute `header_revenue`, and `line_revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-36 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `header_revenue`, and `line_revenue`.
--    Verify: For sql-36 Exercise 5, evaluate each of `header_revenue`, and `line_revenue` in a separate control `SELECT` over `orders`, and `order_items`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-36 Exercise 5, select `order_id` from `orders`, and `order_items` before adding derived columns.
-- 6. Edge case: query a month/category combination with no source rows and
--    explain why a materialized aggregate has no automatic zero-valued row.
--    Inputs: For sql-36 Exercise 6, read from `orders`, `customers`, and `mv_weekly_country_revenue_solution`. Build the answer toward `week`, `country`, and `revenue`; keep `week`, and `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-36 Exercise 6, expected output: at most 20 rows keyed by `week`, and `country`. The final columns are `week`, `country`, and `revenue`. The final order is `m.week DESC, c.country`.
--    Verify: For sql-36 Exercise 6, assert no more than 20 rows, no duplicate `week`, and `country`, and no adjacent pair that violates `m.week DESC, c.country`. Rejoin the returned keys to `orders`, `customers`, and `mv_weekly_country_revenue_solution` to confirm `week`, `country`, and `revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `m.week DESC, c.country`.
--    Hint ladder, rung 1: For sql-36 Exercise 6, run `months`, and `countries` one at a time. Record each CTE's row count and `week`, and `country` uniqueness before the next stage uses it.

ROLLBACK;
