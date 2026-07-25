-- Day 09 solutions: correlated subqueries and EXISTS
SET search_path TO training, public;

-- Exercise 1: customers with at least one order over $1,000.
SELECT c.customer_id, c.full_name, c.country
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  WHERE o.customer_id = c.customer_id
    AND o.total_amount > 1000
)
ORDER BY c.customer_id;

-- Exercise 2: products never purchased.
SELECT p.product_id, p.name, p.category
FROM products p
WHERE NOT EXISTS (
  SELECT 1
  FROM order_items oi
  WHERE oi.product_id = p.product_id
)
ORDER BY p.product_id;
