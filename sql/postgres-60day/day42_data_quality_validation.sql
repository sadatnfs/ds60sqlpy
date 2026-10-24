-- Day 42: Data Quality & Validation
-- BEGINNER WORKFLOW — sql-42: Data Quality Validation
-- Guide: sql/postgres-60day/companion-guides/day42_data_quality_validation.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-42/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, order_items, orders, payments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-42 Exercise 1, read from `customers`, `orders`, `order_items`, `products`, and `payments`. Build the answer toward `check_name`, and `failing_rows`; keep `check_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-42 Exercise 1, expected output: seven rows with `check_name` and `failing_rows`. A nonzero result is evidence to investigate, not permission to delete data automatically. The final columns are `check_name`, and `failing_rows`. The final order is `check_name`.
--    Verify: For sql-42 Exercise 1, project `check_name` plus the raw source columns from `customers`, `orders`, `order_items`, `products`, and `payments` at each join stage; record row count and distinct `check_name`, then assert the final `check_name`, and `failing_rows` values match those staged rows without unintended fanout or loss. Add one row for which `(email IS NULL) OR (total_amount < 0) OR (c.customer_id IS NULL)` is true and one for which it is false; verify only the matching `check_name` value is returned.
--    Hint ladder, rung 1: For sql-42 Exercise 1, start with the first relation in `customers`, `orders`, `order_items`, `products`, and `payments`; after each join, record total rows and distinct `check_name` so the exact fanout or loss is visible.
-- 2. Detect customers with invalid email patterns using regex.
--    Inputs: For sql-42 Exercise 2, read from `customers`. Build the answer toward `customer_id`, and `email`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-42 Exercise 2, expected output: one row per `customer_id`. The final columns are `customer_id`, and `email`. The final order is `customer_id`.
--    Verify: For sql-42 Exercise 2, run an anti-check that counts rows where NOT ((email IS NULL OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `email` against `customers`. Repeat with `NULL` in `customer_id`, and `email` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-42 Exercise 2, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
-- 3. Prediction: explain why CHECK (amount >= 0) rejects negative values but,
--    without NOT NULL, would accept NULL under SQL's three-valued logic.
--    Inputs: For sql-42 Exercise 3, read from `information_schema.columns`. Build the answer toward `table_name`, `column_name`, and `is_nullable`; keep `table_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-42 Exercise 3, expected output: one row per `table_name`. The final columns are `table_name`, `column_name`, and `is_nullable`. The final order is `table_name, column_name`.
--    Verify: For sql-42 Exercise 3, run an anti-check that counts rows where NOT ((table_schema = 'training' AND table_name IN ('orders', 'payments') AND column_name IN ('total_amount', 'amount'))); require unique `table_name` where the expected grain is one row per key and confirm the projected `table_name`, `column_name`, and `is_nullable` against `information_schema.columns`. Repeat with `NULL` in `table_name`, and `column_name` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-42 Exercise 3, inspect the source keys that survive `WHERE`; then check `table_name, column_name` before applying the row cap.
-- 4. Construction: reconcile each order's stored total_amount with calculated
--    line-item revenue and return only differences greater than one cent.
--    Inputs: For sql-42 Exercise 4, read from `order_items`, and `orders`. Build the answer toward `order_id`, `total_amount`, `line_total`, and `difference`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-42 Exercise 4, expected output: one row per order before comparison. The final columns are `order_id`, `total_amount`, `line_total`, and `difference`. The final order is `o.order_id`.
--    Verify: For sql-42 Exercise 4, project `order_id` plus the raw source columns from `order_items`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `total_amount`, `line_total`, and `difference` values match those staged rows without unintended fanout or loss. Add one row for which `(ABS(o.total_amount - c.line_total) > 0.01)` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-42 Exercise 4, run `calculated` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. Debugging: repair a duplicate check that groups by lower(email) but reports
--    only the normalized value, losing the raw variants needed for diagnosis.
--    Inputs: For sql-42 Exercise 5, read from `customers`. Build the answer toward `normalized_email`, `raw_variants`, and `rows`; keep `normalized_email`, and `raw_variants` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-42 Exercise 5, expected output: one row per `normalized_email`, and `raw_variants`. The final columns are `normalized_email`, `raw_variants`, and `rows`. The final order is `normalized_email`.
--    Verify: For sql-42 Exercise 5, independently aggregate `customers` by `normalized_email`, and `raw_variants`; require one output row for every distinct `normalized_email`, and `raw_variants` tuple satisfying `(email IS NOT NULL)` and compare `rows` tuple by tuple. Add duplicate source candidates for `normalized_email`, and `raw_variants`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-42 Exercise 5, inspect the source keys that survive `WHERE`; then confirm the groups are `normalized_email`, and `raw_variants`; then check `normalized_email` before applying the row cap.
-- 6. Edge case: detect overlapping promotion date ranges for the same product,
--    treating touching inclusive endpoints as an overlap.
--    Inputs: For sql-42 Exercise 6, read from `promotions`. Build the answer toward `promotion_a`, `promotion_b`, and `product_id`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-42 Exercise 6, expected output: one row per `product_id`. The final columns are `promotion_a`, `promotion_b`, and `product_id`. The final order is `a.product_id, promotion_a, promotion_b`.
--    Verify: For sql-42 Exercise 6, project `product_id` plus the raw source columns from `promotions` at each join stage; record row count and distinct `product_id`, then assert the final `promotion_a`, `promotion_b`, and `product_id` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-42 Exercise 6, start with the first relation in `promotions`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.

ROLLBACK;
