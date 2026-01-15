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
-- 1) Create an index on products(category) and test a category filter.
-- 2) Drop vs create index and observe planner differences.

ROLLBACK;
