-- Day 34 solutions: query optimization
BEGIN;
SET search_path TO training, public;

-- Exercise 1: compare a correlated aggregate with pre-aggregation plus JOIN.
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id,
       (
         SELECT COUNT(*)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS order_count
FROM customers c;

EXPLAIN (ANALYZE, BUFFERS)
WITH order_counts AS (
  SELECT customer_id, COUNT(*) AS order_count
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id, COALESCE(oc.order_count, 0) AS order_count
FROM customers c
LEFT JOIN order_counts oc USING (customer_id);

-- Exercise 2: compare aggregating every order before LIMIT...
EXPLAIN (ANALYZE, BUFFERS)
WITH all_order_units AS (
  SELECT o.order_id,
         o.customer_id,
         o.order_date,
         SUM(oi.quantity) AS units
  FROM orders o
  JOIN order_items oi USING (order_id)
  GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT *
FROM all_order_units
ORDER BY order_date DESC, order_id DESC
LIMIT 100;

-- ...with finding the 100 newest orders before aggregating their lines.
-- Both return one row per selected order; the second version reduces work.
EXPLAIN (ANALYZE, BUFFERS)
WITH recent_orders AS MATERIALIZED (
  SELECT order_id, customer_id, order_date
  FROM orders
  ORDER BY order_date DESC, order_id DESC
  LIMIT 100
)
SELECT ro.order_id,
       ro.customer_id,
       ro.order_date,
       SUM(oi.quantity) AS units
FROM recent_orders ro
JOIN order_items oi USING (order_id)
GROUP BY ro.order_id, ro.customer_id, ro.order_date
ORDER BY ro.order_date DESC, ro.order_id DESC;

ROLLBACK;
