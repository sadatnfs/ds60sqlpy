-- Day 04 solutions: OUTER JOINs and NULL handling
SET search_path TO training, public;

-- Exercise 1: reconcile orders and payments.
-- A valid foreign key prevents payment-only rows; order-only rows are expected.
WITH order_keys AS (
  SELECT order_id FROM orders
), payment_keys AS (
  SELECT DISTINCT order_id FROM payments
)
SELECT COALESCE(o.order_id, p.order_id) AS order_id,
       CASE
         WHEN o.order_id IS NULL THEN 'payment_without_order'
         WHEN p.order_id IS NULL THEN 'order_without_payment'
       END AS mismatch
FROM order_keys o
FULL OUTER JOIN payment_keys p USING (order_id)
WHERE o.order_id IS NULL OR p.order_id IS NULL
ORDER BY mismatch, order_id;

-- Exercise 2: products that have never appeared in an order.
SELECT p.product_id, p.name, p.category
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL
ORDER BY p.product_id;

-- Exercise 3: customers with no order in the last 90 days.
-- Keeping the predicate inside the JOIN preserves customers with no orders ever.
SELECT c.customer_id,
       c.full_name,
       c.country,
       MAX(o.order_date) AS last_order_in_window
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.customer_id
 AND o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
GROUP BY c.customer_id, c.full_name, c.country
HAVING COUNT(o.order_id) = 0
ORDER BY c.country, c.customer_id;
