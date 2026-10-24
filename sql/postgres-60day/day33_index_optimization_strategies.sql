-- Day 33: Index Optimization Strategies (composite, covering, partial)
-- BEGINNER WORKFLOW — sql-33: Index Optimization Strategies
-- Guide: sql/postgres-60day/companion-guides/day33_index_optimization_strategies.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-33/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Composite index where predicates use (customer_id, order_date)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Covering index (Postgres INCLUDE) for frequent query on order_items
CREATE INDEX idx_oi_order_product_inc ON order_items(order_id, product_id) INCLUDE (quantity, unit_price, discount);

-- Partial index for an active subset. Partial-index predicates must be
-- immutable, so a moving expression such as now() - interval '90 days' is
-- not valid in PostgreSQL.
CREATE INDEX idx_orders_open
  ON orders(order_date)
  WHERE status IN ('placed', 'paid');

-- Test with EXPLAIN
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date
FROM orders o
WHERE o.customer_id = 1 AND o.order_date >= now() - interval '365 days';

EXPLAIN ANALYZE
SELECT oi.order_id, oi.product_id, oi.quantity
FROM order_items oi
WHERE oi.order_id IN (
  SELECT order_id
  FROM orders
  WHERE status IN ('placed', 'paid')
    AND order_date >= now() - interval '90 days'
);

-- Exercises
-- 1. Add a composite index for (category, created_at) on products and test.
--    Inputs: For sql-33 Exercise 1, run the underlying read-only query over `products`, `training.idx_products_category_created_solution`, and `idx_products_category_created_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-33 Exercise 1, expected output: one row per `product_id`. The final columns are `product_id`, `name`, and `created_at`. The final order is `created_at DESC`.
--    Verify: For sql-33 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-33 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 2. Create a partial index for high-value orders (total_amount > 1000) and test.
--    Inputs: For sql-33 Exercise 2, run the underlying read-only query over `orders`, `training.idx_orders_high_value_solution`, and `idx_orders_high_value_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-33 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `total_amount`, and `order_date`. The final order is `total_amount DESC`.
--    Verify: For sql-33 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-33 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 3. Prediction: test the composite product index with created_at alone. Explain
--    why the leftmost category column affects how useful the index can be.
--    Inputs: For sql-33 Exercise 3, run the underlying read-only query over `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-33 Exercise 3, expected output: one row per `product_id`. The final columns are `product_id`, and `created_at`.
--    Verify: For sql-33 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-33 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 4. Construction: build an INCLUDE index for a customer order-history query
--    that returns order_id, order_date, status, and total_amount.
--    Inputs: For sql-33 Exercise 4, run the underlying read-only query over `orders`, and `idx_orders_history_cover_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-33 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`, `order_date`, `status`, and `total_amount`. The final order is `order_date DESC`.
--    Verify: For sql-33 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-33 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 5. Debugging: write a query whose WHERE clause does not imply the partial
--    index predicate. Compare it with a query that does and explain eligibility
--    separately from the planner's final cost choice.
--    Inputs: For sql-33 Exercise 5, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-33 Exercise 5, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-33 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-33 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 6. Edge case: query a nullable column (customers.segment) with IS NULL and
--    discuss whether a partial index for only NULL rows would be worthwhile.
--    Inputs: For sql-33 Exercise 6, run the underlying read-only query over `customers`, `idx_customers_null_segment_solution`, and `customers.segment` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-33 Exercise 6, expected output: one row per `customer_id`. The final columns are `all_customers`, and `null_segments`.
--    Verify: For sql-33 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-33 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.

ROLLBACK;
