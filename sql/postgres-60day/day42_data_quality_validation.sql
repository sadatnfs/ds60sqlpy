-- Day 42: Data Quality & Validation
BEGIN;
SET search_path TO training, public;

-- Null analysis and basic profiling
SELECT 'customers' AS table,
       COUNT(*) AS rows,
       SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_emails,
       SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) AS null_country
FROM customers;

-- Duplicate detection (emails should be unique ideally)
SELECT email, COUNT(*) AS cnt
FROM customers
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY cnt DESC;

-- Orphan checks (should be zero due to FK, but as validation queries)
SELECT oi.order_id
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_id IS NULL
LIMIT 10;

SELECT p.payment_id
FROM payments p
LEFT JOIN orders o ON o.order_id = p.order_id
WHERE o.order_id IS NULL
LIMIT 10;

-- Domain/constraint validation examples
SELECT * FROM orders WHERE total_amount < 0 LIMIT 10;
SELECT * FROM payments WHERE amount < 0 LIMIT 10;

-- Exercises
-- 1. Build a validation report summarizing nulls, duplicates, and constraint violations across core tables.
-- 2. Detect customers with invalid email patterns using regex.
-- 3. Prediction: explain why CHECK (amount >= 0) rejects negative values but,
--    without NOT NULL, would accept NULL under SQL's three-valued logic.
-- 4. Construction: reconcile each order's stored total_amount with calculated
--    line-item revenue and return only differences greater than one cent.
-- 5. Debugging: repair a duplicate check that groups by lower(email) but reports
--    only the normalized value, losing the raw variants needed for diagnosis.
-- 6. Edge case: detect overlapping promotion date ranges for the same product,
--    treating touching inclusive endpoints as an overlap.

ROLLBACK;
