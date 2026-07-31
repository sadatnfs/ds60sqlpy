-- Day 34: Query Optimization Techniques
-- BEGINNER WORKFLOW — sql-34: Query Optimization
-- Guide: sql/postgres-60day/companion-guides/day34_query_optimization.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-34/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Predicate pushdown by filtering early in CTE
WITH filtered_orders AS (
  SELECT order_id, customer_id FROM orders WHERE order_date >= now() - interval '30 days'
)
SELECT c.country, COUNT(*)
FROM filtered_orders fo
JOIN customers c ON c.customer_id = fo.customer_id
GROUP BY c.country
ORDER BY COUNT(*) DESC;

-- Avoid SELECT * and unnecessary columns to reduce I/O
EXPLAIN ANALYZE
SELECT o.order_id, o.customer_id
FROM orders o
WHERE o.order_date >= now() - interval '7 days';

-- Join order rewrite (ensure correct join conditions, indexes)
EXPLAIN
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status IN ('paid','shipped','delivered')
GROUP BY p.category;

-- Exercises
-- 1. Replace subqueries with joins and compare plans.
--    Inputs: For sql-34 Exercise 1, run the underlying read-only query over `orders`, `order_items`, and `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-34 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, and `order_date`.
--    Verify: For sql-34 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-34 Exercise 1, start with the first relation in `orders`, `order_items`, and `products`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 2. Limit rows as early as possible and compare performance.
--    Inputs: For sql-34 Exercise 2, run the underlying read-only query over `orders`, `customers`, and `top_orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-34 Exercise 2, expected output: at most 100 rows keyed by `order_id`. The final columns are `order_id`, `order_date`, and `country`. The final order is `t.order_date DESC, t.order_id DESC`.
--    Verify: For sql-34 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-34 Exercise 2, start with the first relation in `orders`, `customers`, and `top_orders`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 3. Prediction: compare a MATERIALIZED CTE with NOT MATERIALIZED for a recent
--    orders query. Predict which version permits more planner reordering.
--    Inputs: For sql-34 Exercise 3, run the underlying read-only query over `orders`, `recent`, and `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-34 Exercise 3, expected output: one row per `order_id`. The final columns are `materialized`.
--    Verify: For sql-34 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-34 Exercise 3, start with the first relation in `orders`, `recent`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 4. Construction: pre-aggregate order_items to one row per order before
--    joining orders and customers; verify that totals match the direct join.
--    Inputs: For sql-34 Exercise 4, read from `order_items`, `orders`, and `customers`. Build the answer toward `country`, and `units`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-34 Exercise 4, expected output: one row per order before customer/country joins. The final columns are `country`, and `units`. The final order is `c.country`.
--    Verify: For sql-34 Exercise 4, independently aggregate `order_items`, `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `units` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `units` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-34 Exercise 4, run `item_totals` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 5. Debugging: repair a query that joins orders and payments before
--    order_items and therefore multiplies both payment and line-item amounts.
--    Inputs: For sql-34 Exercise 5, read from `payments`, `order_items`, and `orders`. Build the answer toward `order_id`, `paid_amount`, and `line_revenue`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-34 Exercise 5, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, `paid_amount`, and `line_revenue`. The final order is `o.order_id`.
--    Verify: For sql-34 Exercise 5, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `payments`, `order_items`, and `orders` to confirm `order_id`, `paid_amount`, and `line_revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.
--    Hint ladder, rung 1: For sql-34 Exercise 5, run `paid`, and `sold` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. Edge case: replace NOT IN with NOT EXISTS for an anti-join and explain how
--    a NULL in the subquery changes NOT IN semantics.
--    Inputs: For sql-34 Exercise 6, read from `customers`, and `orders`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-34 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_id`. The final order is `c.customer_id`.
--    Verify: For sql-34 Exercise 6, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `customers`, and `orders`. Repeat with `NULL` in `customer_id` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-34 Exercise 6, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.

ROLLBACK;
