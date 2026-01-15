-- Day 33: Index Optimization Strategies (composite, covering, partial)
BEGIN;
SET search_path TO training, public;

-- Composite index where predicates use (customer_id, order_date)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Covering index (Postgres INCLUDE) for frequent query on order_items
CREATE INDEX idx_oi_order_product_inc ON order_items(order_id, product_id) INCLUDE (quantity, unit_price, discount);

-- Partial index for recent orders
CREATE INDEX idx_orders_recent ON orders(order_date) WHERE order_date >= now() - interval '90 days';

-- Test with EXPLAIN
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date
FROM orders o
WHERE o.customer_id = 1 AND o.order_date >= now() - interval '365 days';

EXPLAIN ANALYZE
SELECT oi.order_id, oi.product_id, oi.quantity
FROM order_items oi
WHERE oi.order_id IN (
  SELECT order_id FROM orders WHERE order_date >= now() - interval '90 days'
);

-- Exercises
-- 1) Add a composite index for (category, created_at) on products and test.
-- 2) Create a partial index for high-value orders (total_amount > 1000) and test.

ROLLBACK;
