-- Day 31: Query Execution Plans (EXPLAIN/ANALYZE)
-- BEGINNER WORKFLOW - sql-31: EXPLAIN and EXPLAIN ANALYZE
-- Guide: sql/postgres-60day/companion-guides/day31_explain_analyze.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-31.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Baseline query
EXPLAIN
SELECT
  o.order_id,
  o.total_amount
FROM
  orders o
WHERE
  o.total_amount > 500;

EXPLAIN ANALYZE
SELECT
  o.order_id,
  o.total_amount
FROM
  orders o
WHERE
  o.total_amount > 500
LIMIT 100;

-- Join with filter
EXPLAIN
SELECT
  c.country,
  SUM(oi.quantity) AS qty
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  o.order_date >= now() - interval '90 days'
GROUP BY
  c.country
ORDER BY
  qty DESC;

-- Using an index candidate (to be added on Day 32) and compare
-- Rerun EXPLAIN after creating indexes in Day 32 to observe plan changes.
-- Exercises
-- 1. Add WHERE predicates and observe selectivity effects.
--    Inputs: For sql-31 Exercise 1, plan `SELECT * FROM orders` twice with `EXPLAIN (ANALYZE, BUFFERS)`: once with the broad filter `order_date >= CURRENT_TIMESTAMP - interval '3 years'`, and once with a selective filter that adds `status = 'returned'` and `total_amount >= 1000` to a 7-day window.
--    Expected result/shape: For sql-31 Exercise 1, expected output: two plans, each a `Seq Scan on orders` with a `Filter` line; the broad plan reports thousands of actual rows (4,247 of 4,362 on a freshly seeded database) and the selective plan reports `actual ... rows=0`. Both read the same `Buffers: shared hit=` count, because a sequential scan reads every page whatever the filter keeps.
--    Verify: For sql-31 Exercise 1, run `SELECT COUNT(*)` with each `WHERE` clause and no `EXPLAIN`, and confirm it equals the plan's actual rows; for each plan, actual rows plus `Rows Removed by Filter` must equal `SELECT COUNT(*) FROM orders` (4,362).
--    Hint ladder, rung 1: For sql-31 Exercise 1, selectivity is the fraction of rows a predicate keeps; read it from actual rows and `Rows Removed by Filter`, not from timing.
-- 2. Compare EXPLAIN vs EXPLAIN ANALYZE outputs; note actual vs estimated rows.
--    Inputs: For sql-31 Exercise 2, plan the same revenue query, `SELECT c.country, SUM(o.total_amount) AS revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.country`, first with plain `EXPLAIN` and then with `EXPLAIN (ANALYZE, BUFFERS)`.
--    Expected result/shape: For sql-31 Exercise 2, expected output: the same plan tree twice (on the course seed a `HashAggregate` above a `Hash Join`); only the second adds `actual time=... rows=... loops=...`, `Buffers:` lines, `Planning Time`, and `Execution Time`. The aggregate's actual rows are `7`, one per customer country, against an estimate of `8`.
--    Verify: For sql-31 Exercise 2, run the query without `EXPLAIN` and confirm it returns 7 rows with columns `country` and `revenue`, matching the aggregate node's actual rows; then compare each node's estimated `rows=` with its actual rows multiplied by `loops`.
--    Hint ladder, rung 1: For sql-31 Exercise 2, plain `EXPLAIN` never runs the query, so it cannot show actual rows; `EXPLAIN ANALYZE` runs it and adds measurements to the same tree.
-- 3. Prediction: before running it, decide whether total_amount > 0 or
--    total_amount > 900 should produce the smaller row estimate. Run both with
--    EXPLAIN (ANALYZE, BUFFERS) and record estimated rows, actual rows, and
--    shared buffer hits.
--    Inputs: For sql-31 Exercise 3, predict which predicate has the smaller row estimate, then run `EXPLAIN (ANALYZE, BUFFERS) SELECT order_id FROM orders WHERE total_amount > 0` and the same query with `total_amount > 900`.
--    Expected result/shape: For sql-31 Exercise 3, expected output: with current statistics, `total_amount > 0` is estimated at `rows=4362` and returns 4,362 actual rows, while `total_amount > 900` is estimated near `rows=593` and returns 605; both plans report the same `shared hit` count because both are sequential scans.
--    Verify: For sql-31 Exercise 3, confirm the actual counts with `SELECT COUNT(*) FILTER (WHERE total_amount > 0), COUNT(*) FILTER (WHERE total_amount > 900) FROM orders` (4,362 and 605); if both estimates are identical (for example `rows=1454`), the table has no statistics yet, so run `ANALYZE orders;` and plan again.
--    Hint ladder, rung 1: For sql-31 Exercise 3, the planner estimates selectivity from the column's histogram, which `ANALYZE` builds; without it, every inequality gets the same default fraction.
-- 4. Construction: explain a customer -> orders join filtered to one country.
--    Include VERBOSE and identify the scan node, join node, and aggregate node.
--    Inputs: For sql-31 Exercise 4, run `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)` on `SELECT c.country, COUNT(*) AS order_count FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE c.country = 'US' GROUP BY c.country`.
--    Expected result/shape: For sql-31 Exercise 4, expected output: on the course seed, a `GroupAggregate` root with 1 actual row, a `Hash Join` with 625 actual rows, a filtered `Seq Scan on training.customers` with 63 actual rows, and a `Seq Scan on training.orders` with 4,362 rows; `VERBOSE` adds `Output:` lines and schema-qualified relation names.
--    Verify: For sql-31 Exercise 4, run the query without `EXPLAIN` and confirm one row, `('US', 625)`; then confirm that `SELECT COUNT(*) FROM customers WHERE country = 'US'` returns 63, the actual rows of the `customers` scan.
--    Hint ladder, rung 1: For sql-31 Exercise 4, read the plan from the innermost scans upward: scan nodes feed the join, and the join feeds the aggregate.
-- 5. Debugging: explain why EXPLAIN ANALYZE is unsafe around an UPDATE you do
--    not intend to execute. Demonstrate safely by wrapping a no-op UPDATE
--    (SET status = status) in a savepoint and rolling back to it.
--    Inputs: For sql-31 Exercise 5, inside the lesson transaction, set a savepoint, run `EXPLAIN (ANALYZE, BUFFERS) UPDATE orders SET status = status WHERE order_id = -1`, then roll back to the savepoint and release it.
--    Expected result/shape: For sql-31 Exercise 5, expected output: an `Update on orders` node above an `Index Scan using orders_pkey`, whose actual rows are `0` because no order has `order_id = -1`. The `UPDATE` really executed; only the impossible key and the savepoint keep it harmless.
--    Verify: For sql-31 Exercise 5, confirm that `SELECT COUNT(*) FROM orders` returns 4,362 before and after the rollback; in a scratch transaction, compare `SELECT xmin FROM orders WHERE order_id = 1` before and after `EXPLAIN ANALYZE UPDATE orders SET status = status WHERE order_id = 1`: the `xmin` changes, which proves that `ANALYZE` wrote a new row version, then roll back.
--    Hint ladder, rung 1: For sql-31 Exercise 5, `EXPLAIN ANALYZE` runs the statement it explains; only plain `EXPLAIN` is safe for a write you do not want to happen.
-- 6. Edge case: find one predicate that returns zero rows. Compare the estimate
--    with the actual count and write one sentence about stale statistics versus
--    data that is merely rare.
--    Inputs: For sql-31 Exercise 6, plan `SELECT order_id FROM orders WHERE total_amount < 0` with `EXPLAIN (ANALYZE, BUFFERS)`.
--    Expected result/shape: For sql-31 Exercise 6, expected output: `actual ... rows=0` with `Rows Removed by Filter: 4362`, and an estimate of `rows=1` when statistics exist, because the planner never estimates fewer than one row. The seed simply contains no negative totals; `orders.total_amount` has no `CHECK` constraint.
--    Verify: For sql-31 Exercise 6, confirm that `SELECT MIN(total_amount) FROM orders` is positive (20.74 on the course seed) and that `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'orders'::regclass` lists only the primary key and the foreign key; then compare the estimate with and without statistics to separate missing statistics from rare data.
--    Hint ladder, rung 1: For sql-31 Exercise 6, an estimate of one row for a predicate that matches nothing is the planner's floor, not a bug.
ROLLBACK;
