-- Day 42 solutions: data-quality validation
-- SOLUTION READING MAP — sql-42: Data Quality Validation
-- Explanation: sql/postgres-60day/solutions/day42_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day42_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
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

-- Exercise 3: a CHECK passes TRUE or UNKNOWN. The catalog query shows which
-- course columns also carry NOT NULL, the separate rule that rejects NULL.
SELECT table_name, column_name, is_nullable
FROM information_schema.columns
WHERE table_schema = 'training'
  AND table_name IN ('orders', 'payments')
  AND column_name IN ('total_amount', 'amount')
ORDER BY table_name, column_name;

-- Exercise 4: aggregate lines to order grain before comparing with the stored
-- header. The one-cent tolerance is an explicit currency policy.
WITH calculated AS (
  SELECT order_id,
         SUM(quantity * unit_price * (1 - discount)) AS line_total
  FROM order_items
  GROUP BY order_id
)
SELECT o.order_id, o.total_amount, c.line_total,
       o.total_amount - c.line_total AS difference
FROM orders o
JOIN calculated c USING (order_id)
WHERE ABS(o.total_amount - c.line_total) > 0.01
ORDER BY o.order_id;

-- Exercise 5: keep both normalized key and raw variants for remediation.
SELECT lower(trim(email)) AS normalized_email,
       array_agg(email ORDER BY email) AS raw_variants,
       COUNT(*) AS rows
FROM customers
WHERE email IS NOT NULL
GROUP BY lower(trim(email))
HAVING COUNT(*) > 1
ORDER BY normalized_email;

-- Exercise 6: compare each promotion pair once. Inclusive endpoints overlap
-- when neither range ends strictly before the other starts.
SELECT a.promotion_id AS promotion_a,
       b.promotion_id AS promotion_b,
       a.product_id
FROM promotions a
JOIN promotions b
  ON b.product_id = a.product_id
 AND b.promotion_id > a.promotion_id
 AND a.start_date <= b.end_date
 AND b.start_date <= a.end_date
ORDER BY a.product_id, promotion_a, promotion_b;
