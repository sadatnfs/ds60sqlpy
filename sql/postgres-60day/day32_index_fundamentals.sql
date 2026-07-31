-- Day 32: Index Fundamentals (B-tree, hash, basics)
-- BEGINNER WORKFLOW — sql-32: Index Fundamentals
-- Guide: sql/postgres-60day/companion-guides/day32_index_fundamentals.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-32/ copy, and prints the full
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

-- Create simple indexes (demonstration; rolled back)
CREATE INDEX idx_orders_total_amount ON orders(total_amount);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_customers_country ON customers(country);

-- Observe plan changes
EXPLAIN ANALYZE SELECT order_id FROM orders WHERE total_amount > 500 LIMIT 100;
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date >= now() - interval '30 days';
EXPLAIN ANALYZE SELECT * FROM customers WHERE country = 'US';

-- Hash index example (not commonly needed; Postgres B-tree supports = well)
-- CREATE INDEX idx_customers_email_hash ON customers USING hash(email);

-- Exercises
-- 1. Create an index on products(category) and test a category filter.
--    Inputs: For sql-32 Exercise 1, run the underlying read-only query over `products`, `training.idx_products_category_solution`, and `idx_products_category_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-32 Exercise 1, expected output: one row per `product_id`. The final columns are `product_id`, `name`, and `price`.
--    Verify: For sql-32 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-32 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 2. Drop vs create index and observe planner differences.
--    Inputs: For sql-32 Exercise 2, run the underlying read-only query over `products`, `training.idx_products_category_compare`, and `idx_products_category_compare` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-32 Exercise 2, expected output: one row per `product_id`. The final columns are `product_id`.
--    Verify: For sql-32 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-32 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 3. Prediction: inspect category frequency first, then predict whether the
--    planner will prefer a sequential scan or the category index on this small
--    seed. Verify with EXPLAIN (ANALYZE, BUFFERS).
--    Inputs: For sql-32 Exercise 3, run the underlying read-only query over `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-32 Exercise 3, expected output: one row per `category`. The final columns are `category`, and `products`. The final order is `products DESC, category`.
--    Verify: For sql-32 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `category` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-32 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `category` rows.
-- 4. Construction: create a B-tree index on payments(payment_date), query a
--    bounded half-open date range, and identify its scan node.
--    Inputs: For sql-32 Exercise 4, run the underlying read-only query over `payments`, and `idx_payments_date_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-32 Exercise 4, expected output: one row per `payment_id`. The final columns are `payment_id`, and `amount`.
--    Verify: For sql-32 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `payment_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-32 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `payment_id` rows.
-- 5. Debugging: run a filter with lower(country) = 'us'. Explain why the plain
--    country index may not match it, then create and test an expression index.
--    Inputs: For sql-32 Exercise 5, run the underlying read-only query over `customers`, and `idx_customers_lower_country_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-32 Exercise 5, expected output: one row per `customer_id`. The final columns are `customer_id`.
--    Verify: For sql-32 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-32 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
-- 6. Edge case: prove that an index does not provide a guaranteed output order
--    by contrasting a query without ORDER BY with one ordered explicitly.
--    Inputs: For sql-32 Exercise 6, read from `customers`. Build the answer toward `customer_id`, and `country`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-32 Exercise 6, expected output: at most 10 rows keyed by `customer_id`. The final columns are `customer_id`, and `country`. The final order is `country, customer_id`.
--    Verify: For sql-32 Exercise 6, assert no more than 10 rows, no duplicate `customer_id`, and no adjacent pair that violates `country, customer_id`. Rejoin the returned keys to `customers` to confirm `customer_id`, and `country` came from the same source rows. Run with 10 minus one and 10 plus one eligible rows; require the output cap of 10 while retaining `country, customer_id`.
--    Hint ladder, rung 1: For sql-32 Exercise 6, check `country, customer_id` before applying the row cap.

ROLLBACK;
