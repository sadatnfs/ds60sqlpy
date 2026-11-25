-- Day 45: Phase 3 Project - Performance Optimization
-- BEGINNER WORKFLOW - sql-45: Phase3 Optimization Project
-- Guide: sql/postgres-60day/companion-guides/day45_phase3_optimization_project.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-45.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Baseline (intentionally suboptimal):
EXPLAIN ANALYZE
SELECT
  c.country,
  SUM(oi.quantity)
FROM
  customers c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')
GROUP BY
  c.country
ORDER BY
  2 DESC;

-- Optimized rewrite: avoid function on column and add helpful index
CREATE INDEX IF NOT EXISTS idx_orders_order_date_only ON orders (order_date);

EXPLAIN ANALYZE
SELECT
  c.country,
  SUM(oi.quantity)
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  o.order_date >= (date_trunc('day', now()) - interval '180 days')
GROUP BY
  c.country
ORDER BY
  2 DESC;

-- Additional optimization: pre-aggregate items by order to reduce rows early
EXPLAIN ANALYZE WITH items AS (
  SELECT
    order_id,
    SUM(quantity) AS qty
  FROM
    order_items
  GROUP BY
    order_id
)
SELECT
  c.country,
  SUM(i.qty)
FROM
  orders o
  JOIN items i ON i.order_id = o.order_id
  JOIN customers c ON c.customer_id = o.customer_id
WHERE
  o.order_date >= (date_trunc('day', now()) - interval '180 days')
GROUP BY
  c.country
ORDER BY
  2 DESC;

-- Target: Reduce runtime by >70% vs baseline on your dataset
-- The percentage is a measurement goal, never a guaranteed result on the small
-- deterministic seed. Record plan shape, rows, buffers, and execution time.
-- Exercises
-- 1. Prediction: identify which baseline expression is non-sargable and predict
--    how the half-open timestamp range changes index eligibility.
--    Inputs: For sql-45 Exercise 1, compare the learner baseline predicate `date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')` with the half-open range `order_date >= date_trunc('day', CURRENT_TIMESTAMP) - interval '180 days' AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day'` on `orders`, reading each through `EXPLAIN (ANALYZE, BUFFERS)` after the solution indexes are built.
--    Expected result/shape: For sql-45 Exercise 1, expected output: a text plan, not rows. With `idx_orders_recent_customer_solution` on (`order_date`, `customer_id`, `order_id`) in place, the half-open range becomes an `Index Only Scan` with an `Index Cond` on both `order_date` bounds, while the wrapped baseline stays a `Seq Scan on orders` with a `Filter`, because no index stores `date_trunc('day', order_date)`. Run without `EXPLAIN`, the range returns one row per `order_id`; its only column is `order_id`.
--    Verify: For sql-45 Exercise 1, run both predicates without `EXPLAIN` and confirm that `EXCEPT` in each direction returns 0 rows, so the rewrite keeps exactly the same `order_id` set (1,539 orders on our load); then run `EXPLAIN (COSTS OFF)` on each with the solution indexes present and confirm `Index Cond` for the range and `Filter: (date_trunc('day'::text, order_date) >= ...)` for the baseline. The plans may differ by machine; the predicate form decides eligibility, not the timing.
--    Hint ladder, rung 1: For sql-45 Exercise 1, look for a function wrapped around the indexed column on the left side of the comparison; a predicate on the bare `order_date` is the form an index on `order_date` can serve.
-- 2. Construction: capture EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) for the
--    baseline and rewrite, then compare root-node execution time and buffers.
--    Inputs: For sql-45 Exercise 2, wrap `SELECT customer_id, SUM(total_amount) AS revenue FROM orders WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days' GROUP BY customer_id` in `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`; the solution captures this rewrite, and the baseline is captured the same way for the comparison.
--    Expected result/shape: For sql-45 Exercise 2, expected output: one row with one `QUERY PLAN` value holding a JSON array; its first element has `Plan` with `"Node Type": "Aggregate"`, `"Strategy": "Hashed"`, `Actual Rows` equal to the number of customers, and `Shared Hit Blocks`, while `Execution Time` sits beside `Plan`, not inside it. Run without `EXPLAIN`, the query returns one row per `customer_id` with columns `customer_id` and `revenue`.
--    Verify: For sql-45 Exercise 2, run the query without `EXPLAIN` and confirm that its row count equals the root `Actual Rows` (410 on our load) and that `SUM(revenue)` equals `SELECT SUM(total_amount) FROM orders` under the same filter; then confirm that `Plans[0]` is a `Bitmap Heap Scan` fed by a `Bitmap Index Scan` on `idx_orders_recent_customer_solution`, and that without the solution indexes (after `ROLLBACK`) the same query plans a `Seq Scan on orders`.
--    Hint ladder, rung 1: For sql-45 Exercise 2, run the query once without `EXPLAIN` and note its row count; then find that number as `Actual Rows` on the root node of the JSON plan.
-- 3. Debugging: prove that the pre-aggregated rewrite returns the same country
--    totals as the direct join by comparing them with EXCEPT in both directions.
--    Inputs: For sql-45 Exercise 3, build `direct` (orders joined to customers and `order_items`, last 180 days, `SUM(quantity)` by `country`), `items` (`order_items` summed by `order_id`), and `preaggregated` (orders joined to `items` and customers with the same filter, summed by `country`), then compare `direct EXCEPT preaggregated` and `preaggregated EXCEPT direct`, labeling each side with `difference_side`.
--    Expected result/shape: For sql-45 Exercise 3, expected output: 0 rows with columns `difference_side`, `country`, and `units`, because both CTEs return the same 7 country totals (BR has no orders); any disagreement would appear as a labeled row, one per differing country on each side.
--    Verify: For sql-45 Exercise 3, run `direct` and `preaggregated` alone and confirm 7 rows each with identical (`country`, `units`) pairs, such as AU with 1947 on our load; confirm `items` returns 4,362 rows with unique `order_id` and `SUM(units)` of 39257, equal to `SELECT SUM(quantity) FROM order_items`; then change only the `preaggregated` interval to `'179 days'` and confirm rows appear in pairs, one from each `difference_side` for every country whose total moved.
--    Hint ladder, rung 1: For sql-45 Exercise 3, run `direct`, `items`, and `preaggregated` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 4. Edge case: test a date window with zero matching orders and ensure every
--    rewrite returns the same empty result rather than an invented zero row.
--    Inputs: For sql-45 Exercise 4, read from `orders` with a window that matches no rows, `order_date >= TIMESTAMPTZ '1900-01-01 00:00:00+00' AND order_date < TIMESTAMPTZ '1900-01-02 00:00:00+00'`, and count the matching orders.
--    Expected result/shape: For sql-45 Exercise 4, expected output: one row with `impossible_window_rows` 0. The final columns are `impossible_window_rows`.
--    Verify: For sql-45 Exercise 4, confirm the count is 0, then run a grouped form of the same filter, such as `SELECT c.country, COUNT(*) FROM orders o JOIN customers c USING (customer_id) WHERE <same window> GROUP BY c.country`, and confirm it returns no rows: an ungrouped aggregate always returns one row, while a grouped query over empty input returns none, so every rewrite of the report must keep the same shape.
--    Hint ladder, rung 1: For sql-45 Exercise 4, run the window predicate with `SELECT COUNT(*)` and with a `GROUP BY` version, and compare the number of result rows.
-- 5. Design: propose one composite or covering index, state the exact query it
--    serves, and explain its write/storage tradeoff.
--    Inputs: For sql-45 Exercise 5, inside the lesson transaction, after `idx_orders_recent_customer_solution` on `orders (order_date, customer_id, order_id)` and `idx_order_items_order_quantity_solution` on `order_items (order_id) INCLUDE (quantity)` are built, read `pg_indexes` where `schemaname = 'training'` and `indexname LIKE '%solution'`.
--    Expected result/shape: For sql-45 Exercise 5, expected output: 2 rows, one per `indexname`: `idx_order_items_order_quantity_solution`, then `idx_orders_recent_customer_solution`, each with its full `CREATE INDEX` text in `indexdef`. The final columns are `indexname` and `indexdef`. The final order is `indexname`.
--    Verify: For sql-45 Exercise 5, confirm the 2 rows and that `training` holds 16 indexes at that moment, so the `LIKE '%solution'` filter removed 14; read `pg_size_pretty(pg_relation_size(indexname::regclass))` for each (304 kB for the `INCLUDE` index and 152 kB for the composite one on our load) as the storage cost; then, after `ROLLBACK`, rerun the query and confirm 0 rows, proving the candidates were not left behind.
--    Hint ladder, rung 1: For sql-45 Exercise 5, filter `pg_indexes` by schema and by the `%solution` name pattern; then check `indexname` order. There is no row cap.
-- 6. Explanation: write a short optimization report separating semantic
--    equivalence, planner evidence, and environment-dependent timing.
--    Inputs: For sql-45 Exercise 6, write a short report with three labeled parts, semantic equivalence, planner evidence, and environment-dependent timing, and support each claim with read-only output from this lesson: the empty two-way `EXCEPT` from Exercise 3, the plan nodes and buffer counts from Exercises 1 and 2, the index sizes from Exercise 5, and several timings of each form.
--    Expected result/shape: For sql-45 Exercise 6, expected output: a written report, not a result set, with one entry per recommendation carrying `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`; for example, keep the half-open range (evidence: the same `order_id` set and an `Index Cond` in place of a `Filter`) and keep or drop the `INCLUDE` index (evidence: 304 kB of storage against the time it saves).
--    Verify: For sql-45 Exercise 6, check that each equivalence claim cites the empty `EXCEPT` result, each plan claim names a node type and buffer count you printed, and each timing claim reports several runs of each form; then test the counterexample that `idx_order_items_order_quantity_solution` alone takes the correlated baseline from hundreds of milliseconds (about 380 ms on our load) to a few milliseconds, and state which `fallback` and `rollback_limit` entries apply when the index, not the rewrite, earns most of the speedup.
--    Hint ladder, rung 1: For sql-45 Exercise 6, list each claim first and next to it the query output that proves it; any claim without printed evidence is an assumption and must be labeled as one.
ROLLBACK;
