-- Day 32: Index Fundamentals (B-tree, hash, basics)
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
-- 2. Drop vs create index and observe planner differences.
-- 3. Prediction: inspect category frequency first, then predict whether the
--    planner will prefer a sequential scan or the category index on this small
--    seed. Verify with EXPLAIN (ANALYZE, BUFFERS).
-- 4. Construction: create a B-tree index on payments(payment_date), query a
--    bounded half-open date range, and identify its scan node.
-- 5. Debugging: run a filter with lower(country) = 'us'. Explain why the plain
--    country index may not match it, then create and test an expression index.
-- 6. Edge case: prove that an index does not provide a guaranteed output order
--    by contrasting a query without ORDER BY with one ordered explicitly.

ROLLBACK;
