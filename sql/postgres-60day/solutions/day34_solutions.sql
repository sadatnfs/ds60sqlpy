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

-- Exercise 3: MATERIALIZED creates an optimization boundary; NOT MATERIALIZED
-- permits the CTE to be folded into its single parent query.
EXPLAIN
WITH recent AS MATERIALIZED (
  SELECT order_id, customer_id FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
)
SELECT COUNT(*) FROM recent JOIN customers USING (customer_id);

EXPLAIN
WITH recent AS NOT MATERIALIZED (
  SELECT order_id, customer_id FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
)
SELECT COUNT(*) FROM recent JOIN customers USING (customer_id);

-- Exercise 4: reduce items to one row per order before crossing the next grain.
WITH item_totals AS (
  SELECT order_id, SUM(quantity) AS units
  FROM order_items
  GROUP BY order_id
)
SELECT c.country, SUM(it.units) AS units
FROM item_totals it
JOIN orders o USING (order_id)
JOIN customers c USING (customer_id)
GROUP BY c.country
ORDER BY c.country;

-- Exercise 5: aggregate each independent many-side to order grain. Joining raw
-- payments and items would multiply both amounts.
WITH paid AS (
  SELECT order_id, SUM(amount) AS paid_amount FROM payments GROUP BY order_id
), sold AS (
  SELECT order_id,
         SUM(quantity * unit_price * (1 - discount)) AS line_revenue
  FROM order_items
  GROUP BY order_id
)
SELECT o.order_id, p.paid_amount, s.line_revenue
FROM orders o
LEFT JOIN paid p USING (order_id)
LEFT JOIN sold s USING (order_id)
ORDER BY o.order_id
LIMIT 20;

-- Exercise 6: NOT EXISTS remains two-valued for each customer even if the
-- subquery's projected expression could contain NULL.
SELECT c.customer_id
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;

ROLLBACK;
