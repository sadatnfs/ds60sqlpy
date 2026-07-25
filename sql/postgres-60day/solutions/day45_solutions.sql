-- Day 45 solution: optimization project
BEGIN;
SET search_path TO training, public;

-- Baseline: correlated item aggregation for each recent order.
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.country,
       SUM((
         SELECT SUM(oi.quantity)
         FROM order_items oi
         WHERE oi.order_id = o.order_id
       )) AS units
FROM orders o
JOIN customers c USING (customer_id)
WHERE o.order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY c.country;

-- Candidate indexes. They are course-owned and rolled back with the solution.
CREATE INDEX idx_orders_recent_customer_solution
  ON orders(order_date, customer_id, order_id);
CREATE INDEX idx_order_items_order_quantity_solution
  ON order_items(order_id) INCLUDE (quantity);

-- Optimized set-based answer with a sargable date predicate.
EXPLAIN (ANALYZE, BUFFERS)
WITH recent_orders AS (
  SELECT order_id, customer_id
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
), item_totals AS (
  SELECT oi.order_id, SUM(oi.quantity) AS units
  FROM order_items oi
  JOIN recent_orders ro USING (order_id)
  GROUP BY oi.order_id
)
SELECT c.country, SUM(it.units) AS units
FROM recent_orders ro
JOIN item_totals it USING (order_id)
JOIN customers c USING (customer_id)
GROUP BY c.country
ORDER BY units DESC;

-- The lesson's 70% target is a measurement goal, not a guaranteed result on
-- the compact seed. Compare Execution Time and buffer counts in both plans.
ROLLBACK;
