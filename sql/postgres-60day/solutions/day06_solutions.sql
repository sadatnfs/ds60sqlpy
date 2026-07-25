-- Day 06 solutions: UNION, INTERSECT, and EXCEPT
SET search_path TO training, public;

-- Exercise 1: products that occur in both purchases and promotions.
SELECT product_id
FROM order_items
INTERSECT
SELECT product_id
FROM promotions
ORDER BY product_id;

-- Exercise 2: countries that have customers but no orders.
SELECT country
FROM customers
EXCEPT
SELECT c.country
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
ORDER BY country;

-- Exercise 3: compare UNION (deduplicated) with UNION ALL.
WITH union_rows AS (
  SELECT order_id
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '365 days'
  UNION
  SELECT order_id
  FROM orders
  WHERE total_amount >= 500
), union_all_rows AS (
  SELECT order_id
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '365 days'
  UNION ALL
  SELECT order_id
  FROM orders
  WHERE total_amount >= 500
)
SELECT 'UNION' AS operation, COUNT(*) AS rows_returned
FROM union_rows
UNION ALL
SELECT 'UNION ALL', COUNT(*)
FROM union_all_rows
ORDER BY operation;
