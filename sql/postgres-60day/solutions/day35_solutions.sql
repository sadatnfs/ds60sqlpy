-- Day 35 solutions: avoiding common query pitfalls
BEGIN;
SET search_path TO training, public;

-- Exercise 1: three sargable rewrites.
-- 1a. Range bounds instead of date_trunc(order_date).
SELECT COUNT(*)
FROM orders
WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP)
  AND order_date < date_trunc('month', CURRENT_TIMESTAMP) + interval '1 month';

-- 1b. Exact comparison can use the unique email B-tree.
SELECT customer_id
FROM customers
WHERE email = 'customer100@example.com';

-- 1c. country is NOT NULL, so COALESCE is unnecessary.
SELECT COUNT(*)
FROM customers
WHERE country = 'US';

-- Exercise 2: replace a per-customer correlated aggregate with one grouped CTE.
WITH order_totals AS (
  SELECT customer_id,
         COUNT(*) AS orders,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id,
       c.full_name,
       COALESCE(ot.orders, 0) AS orders,
       COALESCE(ot.revenue, 0) AS revenue
FROM customers c
LEFT JOIN order_totals ot USING (customer_id)
ORDER BY revenue DESC, c.customer_id;

ROLLBACK;
