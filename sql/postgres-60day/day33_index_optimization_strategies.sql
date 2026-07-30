-- Day 33: Index Optimization Strategies (composite, covering, partial)
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
-- 2. Create a partial index for high-value orders (total_amount > 1000) and test.
-- 3. Prediction: test the composite product index with created_at alone. Explain
--    why the leftmost category column affects how useful the index can be.
-- 4. Construction: build an INCLUDE index for a customer order-history query
--    that returns order_id, order_date, status, and total_amount.
-- 5. Debugging: write a query whose WHERE clause does not imply the partial
--    index predicate. Compare it with a query that does and explain eligibility
--    separately from the planner's final cost choice.
-- 6. Edge case: query a nullable column (customers.segment) with IS NULL and
--    discuss whether a partial index for only NULL rows would be worthwhile.

ROLLBACK;
