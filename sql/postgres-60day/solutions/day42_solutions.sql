-- Day 42 solutions: data-quality validation
SET search_path TO training, public;

-- Exercise 1: one compact validation report. Constraints make most counts zero;
-- keeping the checks executable protects future changes and imported data.
SELECT 'customers.null_email' AS check_name,
       COUNT(*) AS failing_rows
FROM customers
WHERE email IS NULL
UNION ALL
SELECT 'customers.duplicate_normalized_email',
       COUNT(*)
FROM (
  SELECT lower(trim(email))
  FROM customers
  GROUP BY lower(trim(email))
  HAVING COUNT(*) > 1
) duplicates
UNION ALL
SELECT 'orders.negative_total', COUNT(*)
FROM orders
WHERE total_amount < 0
UNION ALL
SELECT 'orders.orphan_customer', COUNT(*)
FROM orders o
LEFT JOIN customers c USING (customer_id)
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'order_items.orphan_order_or_product', COUNT(*)
FROM order_items oi
LEFT JOIN orders o USING (order_id)
LEFT JOIN products p USING (product_id)
WHERE o.order_id IS NULL OR p.product_id IS NULL
UNION ALL
SELECT 'order_items.invalid_quantity_or_discount', COUNT(*)
FROM order_items
WHERE quantity <= 0 OR discount NOT BETWEEN 0 AND 1
UNION ALL
SELECT 'payments.negative_or_orphan', COUNT(*)
FROM payments p
LEFT JOIN orders o USING (order_id)
WHERE p.amount < 0 OR o.order_id IS NULL
ORDER BY check_name;

-- Exercise 2: email-format validation.
SELECT customer_id, email
FROM customers
WHERE email IS NULL
   OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
ORDER BY customer_id;
