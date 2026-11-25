-- Day 42: Data Quality & Validation
-- BEGINNER WORKFLOW - sql-42: Data Quality Validation
-- Guide: sql/postgres-60day/companion-guides/day42_data_quality_validation.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-42.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  'customers' AS table,
  COUNT(*) AS rows,
  SUM(
    CASE WHEN email IS NULL THEN
      1
    ELSE
      0
    END) AS null_emails,
  SUM(
    CASE WHEN country IS NULL THEN
      1
    ELSE
      0
    END) AS null_country
FROM
  customers;

-- Duplicate detection (emails should be unique ideally)
SELECT
  email,
  COUNT(*) AS cnt
FROM
  customers
GROUP BY
  email
HAVING
  COUNT(*) > 1
ORDER BY
  cnt DESC;

-- Orphan checks (should be zero due to FK, but as validation queries)
SELECT
  oi.order_id
FROM
  order_items oi
  LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE
  o.order_id IS NULL
LIMIT 10;

SELECT
  p.payment_id
FROM
  payments p
  LEFT JOIN orders o ON o.order_id = p.order_id
WHERE
  o.order_id IS NULL
LIMIT 10;

-- Domain/constraint validation examples
SELECT
  *
FROM
  orders
WHERE
  total_amount < 0
LIMIT 10;

SELECT
  *
FROM
  payments
WHERE
  amount < 0
LIMIT 10;

-- Exercises
-- 1. Build a validation report summarizing nulls, duplicates, and constraint violations across core tables.
--    Inputs: For sql-42 Exercise 1, write seven single-count queries joined with `UNION ALL`: `NULL` emails and duplicate `lower(trim(email))` keys in `customers`, negative totals and orphan `customer_id` values in `orders`, orphan orders or products and bad quantity or discount in `order_items`, and negative or orphan rows in `payments`; orphans are found with `LEFT JOIN ... WHERE parent key IS NULL`.
--    Expected result/shape: For sql-42 Exercise 1, return exactly seven rows, one per `check_name`, and every `failing_rows` value is 0 on a fresh load because the course constraints already block these faults. A nonzero result is evidence to investigate, not permission to delete data automatically. The final columns are `check_name` and `failing_rows`. The final order is `check_name`.
--    Verify: For sql-42 Exercise 1, confirm seven distinct `check_name` values, all with 0; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET email = NULL WHERE customer_id = 1` and confirm `customers.null_email` becomes 1 while the other six stay 0, and separately insert a customer with email `' Customer7@Example.com'` and confirm `customers.duplicate_normalized_email` becomes 1.
--    Hint ladder, rung 1: For sql-42 Exercise 1, run each `UNION ALL` branch alone first; each must return exactly one count row, and the orphan branches need `LEFT JOIN` because an inner join hides the very rows they count.
-- 2. Detect customers with invalid email patterns using regex.
--    Inputs: For sql-42 Exercise 2, read `customers.customer_id` and `email` and keep a row when `email IS NULL` or when `email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'`; the explicit `NULL` branch is needed because a regex test on `NULL` is unknown, not true.
--    Expected result/shape: For sql-42 Exercise 2, return 0 rows on a fresh load, because all 500 addresses have the form `customerN@example.com`; when rows do appear there is one per failing `customer_id`. The final columns are `customer_id` and `email`. The final order is `customer_id`.
--    Verify: For sql-42 Exercise 2, confirm 0 rows and that `SELECT count(*) FROM customers WHERE email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'` returns 500; then, inside `BEGIN ... ROLLBACK`, set customer 1's email to `'customer1(at)example.com'` and customer 2's to `NULL` and confirm exactly those two rows appear, the second only because of the `email IS NULL` branch.
--    Hint ladder, rung 1: For sql-42 Exercise 2, test the pattern on a few literals such as `'a@b.co'`, `'a@b'`, and `NULL` before running it on `customers`; then check `customer_id` order.
-- 3. Prediction: explain why CHECK (amount >= 0) rejects negative values but,
--    without NOT NULL, would accept NULL under SQL's three-valued logic.
--    Inputs: For sql-42 Exercise 3, read `information_schema.columns` filtered to `table_schema = 'training'`, tables `orders` and `payments`, and columns `total_amount` and `amount`; the catalog shows `NOT NULL`, which is a separate rule from the `CHECK (amount >= 0)` constraint on `payments`.
--    Expected result/shape: For sql-42 Exercise 3, return 2 rows, one per (`table_name`, `column_name`): `orders`/`total_amount` and `payments`/`amount`, both with `is_nullable = NO`. The final columns are `table_name`, `column_name`, and `is_nullable`. The final order is `table_name, column_name`.
--    Verify: For sql-42 Exercise 3, confirm the two rows and that `SELECT NULL::numeric >= 0` returns `NULL`, which a `CHECK` treats as a pass; then, inside `BEGIN ... ROLLBACK`, run `ALTER TABLE payments ALTER COLUMN amount DROP NOT NULL`, confirm `INSERT INTO payments (order_id, amount, method) VALUES (1, NULL, 'card')` succeeds, and confirm the same insert with `-1` fails on `payments_amount_check`.
--    Hint ladder, rung 1: For sql-42 Exercise 3, filter on `table_schema`, `table_name`, and `column_name` so only the two money columns survive; then check `table_name, column_name` order.
-- 4. Construction: reconcile each order's stored total_amount with calculated
--    line-item revenue and return only differences greater than one cent.
--    Inputs: For sql-42 Exercise 4, sum `quantity * unit_price * (1 - discount)` from `order_items` by `order_id` in a `calculated` CTE (4,362 rows, one per order), join it to `orders` on `order_id`, and keep orders whose `ABS(o.total_amount - c.line_total)` exceeds the one-cent tolerance `0.01`.
--    Expected result/shape: For sql-42 Exercise 4, return 0 rows on a fresh load: 2,855 of the 4,362 orders differ from their line sums, but never by more than 0.0045, because stored totals keep two decimals and discounted line sums keep four. The final columns are `order_id`, `total_amount`, `line_total`, and `difference`. The final order is `o.order_id`.
--    Verify: For sql-42 Exercise 4, confirm 0 rows, then replace the test with `o.total_amount <> c.line_total` and confirm 2,855 rows with a maximum absolute difference of 0.0045; finally, inside `BEGIN ... ROLLBACK`, add 0.02 to order 3's `total_amount` and confirm one row: `order_id` 3, `total_amount` 601.75, `line_total` 601.7295, and `difference` 0.0205.
--    Hint ladder, rung 1: For sql-42 Exercise 4, run `calculated` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. Debugging: repair a duplicate check that groups by lower(email) but reports
--    only the normalized value, losing the raw variants needed for diagnosis.
--    Inputs: For sql-42 Exercise 5, read `customers` rows with a non-`NULL` email, group by `lower(trim(email))`, keep groups with `COUNT(*) > 1`, and report the raw spellings with `array_agg(email ORDER BY email)` next to the normalized key.
--    Expected result/shape: For sql-42 Exercise 5, return 0 rows on a fresh load, because no two emails differ only by case or surrounding spaces; when duplicates exist there is one row per `normalized_email`, with every raw spelling in `raw_variants`. The final columns are `normalized_email`, `raw_variants`, and `rows`. The final order is `normalized_email`.
--    Verify: For sql-42 Exercise 5, confirm 0 rows; then, inside `BEGIN ... ROLLBACK`, insert a customer with email `' Customer7@Example.com'` and confirm one row: `normalized_email` = `customer7@example.com`, `raw_variants` = `{customer7@example.com," Customer7@Example.com"}`, and `rows` = 2. The broken version that selects only the normalized key returns the same row without the two spellings.
--    Hint ladder, rung 1: For sql-42 Exercise 5, group by the normalized expression only; then confirm `array_agg(email ORDER BY email)` keeps every raw spelling, and check `normalized_email` order.
-- 6. Edge case: detect overlapping promotion date ranges for the same product,
--    treating touching inclusive endpoints as an overlap.
--    Inputs: For sql-42 Exercise 6, join `promotions` (200 rows) to itself on `product_id` with `b.promotion_id > a.promotion_id`, so each pair is tested once, and keep pairs where `a.start_date <= b.end_date AND b.start_date <= a.end_date`, which treats a shared endpoint date as an overlap.
--    Expected result/shape: For sql-42 Exercise 6, return 0 rows on a fresh load, because the 200 promotions cover 200 different products; when overlaps exist there is one row per overlapping pair (`promotion_a`, `promotion_b`), not per product. The final columns are `promotion_a`, `promotion_b`, and `product_id`. The final order is `a.product_id, promotion_a, promotion_b`.
--    Verify: For sql-42 Exercise 6, confirm 0 rows and that `count(DISTINCT product_id)` equals `count(*)` (200) in `promotions`; then, inside `BEGIN ... ROLLBACK`, copy promotion 1 with `start_date = end_date` (touching) and promotion 2 with `start_date = end_date + 1` (a one-day gap) and confirm exactly one pair: promotion 1 with the touching copy, for product 43.
--    Hint ladder, rung 1: For sql-42 Exercise 6, join `promotions` to itself on `product_id` with `b.promotion_id > a.promotion_id` and count the candidate pairs before adding the two date comparisons.
ROLLBACK;
