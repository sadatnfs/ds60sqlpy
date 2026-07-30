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

-- Exercise 1: the original date_trunc(column) expression hides the raw search
-- key. A half-open direct range is eligible for the order_date index.
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('day', CURRENT_TIMESTAMP) - interval '180 days'
  AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day';

-- Exercise 2: JSON keeps node, row, time, and buffer evidence structured.
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT customer_id, SUM(total_amount) AS revenue
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY customer_id;

-- Exercise 3: build both equivalent results once, then compare each direction.
WITH direct AS (
  SELECT c.country, SUM(oi.quantity) AS units
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  WHERE o.order_date >= CURRENT_TIMESTAMP - interval '180 days'
  GROUP BY c.country
), items AS (
  SELECT order_id, SUM(quantity) AS units FROM order_items GROUP BY order_id
), preaggregated AS (
  SELECT c.country, SUM(i.units) AS units
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN items i USING (order_id)
  WHERE o.order_date >= CURRENT_TIMESTAMP - interval '180 days'
  GROUP BY c.country
)
SELECT 'direct_minus_preaggregated' AS difference_side, * FROM (
  SELECT * FROM direct EXCEPT SELECT * FROM preaggregated
) d
UNION ALL
SELECT 'preaggregated_minus_direct', * FROM (
  SELECT * FROM preaggregated EXCEPT SELECT * FROM direct
) p;

-- Exercise 4: both shapes must produce zero rows for an impossible old window.
SELECT COUNT(*) AS impossible_window_rows
FROM orders
WHERE order_date >= timestamptz '1900-01-01 00:00:00+00'
  AND order_date < timestamptz '1900-01-02 00:00:00+00';

-- Exercise 5: the existing (order_date, customer_id, order_id) candidate serves
-- date-bounded customer work but adds storage and write maintenance.
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'training'
  AND indexname LIKE '%solution'
ORDER BY indexname;

-- Exercise 6: the executable evidence above supports a report with separate
-- correctness, plan, timing, and operational-cost sections. No timing result
-- from this compact seed is a universal performance promise.
ROLLBACK;
