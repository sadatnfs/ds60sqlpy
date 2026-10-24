-- Day 35: Avoiding Common Performance Pitfalls
-- BEGINNER WORKFLOW — sql-35: Avoiding Pitfalls
-- Guide: sql/postgres-60day/companion-guides/day35_avoiding_pitfalls.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-35/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Pitfall: function on column prevents index usage
EXPLAIN ANALYZE SELECT * FROM orders WHERE date_trunc('day', order_date) = date_trunc('day', now());
-- Better:
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date >= date_trunc('day', now()) AND order_date < date_trunc('day', now()) + interval '1 day';

-- Pitfall: Correlated subquery per row
EXPLAIN ANALYZE
SELECT c.customer_id,
       (SELECT SUM(o.total_amount) FROM orders o WHERE o.customer_id = c.customer_id)
FROM customers c;
-- Better: pre-aggregate and join
EXPLAIN ANALYZE
WITH agg AS (
  SELECT customer_id, SUM(total_amount) AS sum_total FROM orders GROUP BY customer_id
)
SELECT c.customer_id, a.sum_total
FROM customers c LEFT JOIN agg a ON a.customer_id = c.customer_id;

-- N+1 pattern in application layer (illustrated only)
-- Prefer set-based queries over per-row queries.

-- Exercises
-- 1. Rewrite 3 queries to avoid functions on indexed columns.
--    Inputs: For sql-35 Exercise 1, run the underlying read-only query over `orders`, `order_date`, and `CURRENT_DATE` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-35 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-35 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-35 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 2. Replace correlated subqueries with joins/CTEs.
--    Inputs: For sql-35 Exercise 2, run the underlying read-only query over `orders`, and `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-35 Exercise 2, expected output: one row per customer in both forms. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer. The final columns are `customer_id`, and `lifetime_revenue`.
--    Verify: For sql-35 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-35 Exercise 2, run `order_totals` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 3. Prediction: compare LIKE 'A%' with LIKE '%A%'. State which pattern can use
--    a normal B-tree text index more directly and why the leading wildcard
--    changes the search.
--    Inputs: For sql-35 Exercise 3, run the underlying read-only query over `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-35 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`.
--    Verify: For sql-35 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-35 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
-- 4. Construction: replace an OFFSET-based “next page” query with keyset
--    pagination ordered by (order_date DESC, order_id DESC).
--    Inputs: For sql-35 Exercise 4, read from `orders`. Build the answer toward `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-35 Exercise 4, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-35 Exercise 4, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_date DESC, o.order_id DESC`. Rejoin the returned keys to `orders` to confirm `order_id`, and `order_date` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_date DESC, o.order_id DESC`.
--    Hint ladder, rung 1: For sql-35 Exercise 4, run `boundary` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. Debugging: find and repair a join that calculates revenue after joining
--    both payments and order_items at their raw grains.
--    Inputs: For sql-35 Exercise 5, read from `payments`, `order_items`, and `orders`. Build the answer toward `order_id`, `paid`, and `sold`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-35 Exercise 5, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, `paid`, and `sold`. The final order is `o.order_id`.
--    Verify: For sql-35 Exercise 5, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `payments`, `order_items`, and `orders` to confirm `order_id`, `paid`, and `sold` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.
--    Hint ladder, rung 1: For sql-35 Exercise 5, run `paid`, and `sold` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. Edge case: compare COUNT(*) and COUNT(email) for customers, and explain
--    why nullable inputs make the two counts intentionally different.
--    Inputs: For sql-35 Exercise 6, read from `customers`. Build the answer toward `customer_rows`, `customers_with_email`, and `customers_without_email`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-35 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_rows`, `customers_with_email`, and `customers_without_email`.
--    Verify: For sql-35 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_rows`, `customers_with_email`, and `customers_without_email` against `customers`. Repeat with `NULL` in `customer_rows`, and `customers_with_email` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-35 Exercise 6, select `customer_id` from `customers` before adding derived columns.

ROLLBACK;
