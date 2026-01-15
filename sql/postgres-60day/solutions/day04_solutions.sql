-- Day 04 - Solutions: OUTER JOINs
-- Assumes: products, order_items, orders, customers

/*
Exercise 1) List categories that had no orders last month.
Why: LEFT JOIN order_items, aggregate by category, then filter categories with zero matched rows.
*/
WITH last_month AS (
  SELECT DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' AS start_m,
         DATE_TRUNC('month', CURRENT_DATE) AS end_m
)
SELECT p.category
FROM products p
LEFT JOIN order_items oi
  ON oi.product_id = p.product_id
LEFT JOIN orders o
  ON o.order_id = oi.order_id
  AND o.order_date >= (SELECT start_m FROM last_month)
  AND o.order_date <  (SELECT end_m FROM last_month)
GROUP BY p.category
HAVING SUM(CASE WHEN o.order_id IS NOT NULL THEN 1 ELSE 0 END) = 0
ORDER BY p.category;

/*
Exercise 2) Compute number of customers without any orders, by country.
Why: LEFT JOIN orders and count NULLs on the right side.
*/
SELECT c.country,
       SUM(CASE WHEN o.order_id IS NULL THEN 1 ELSE 0 END) AS customers_without_orders
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY customers_without_orders DESC;

/*
Exercise 3) FULL JOIN reconciliation showing keys present only in A, only in B, and in both.
Why: FULL JOIN and a merge flag using CASE on IS NULL tests.
*/
WITH a AS (
  SELECT order_id FROM orders
), b AS (
  SELECT DISTINCT order_id FROM payments
)
SELECT COALESCE(a.order_id, b.order_id) AS order_id,
       CASE
         WHEN a.order_id IS NOT NULL AND b.order_id IS NOT NULL THEN 'both'
         WHEN a.order_id IS NOT NULL AND b.order_id IS NULL THEN 'orders_only'
         WHEN a.order_id IS NULL AND b.order_id IS NOT NULL THEN 'payments_only'
         ELSE 'unknown'
       END AS presence
FROM a
FULL JOIN b ON b.order_id = a.order_id
ORDER BY order_id
LIMIT 200;

-- End of Day 04 solutions
