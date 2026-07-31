-- Day 1: SELECT, WHERE, ORDER BY, LIMIT
-- BEGINNER WORKFLOW — sql-01: Select Where Orderby
-- Guide: sql/postgres-60day/companion-guides/day01_select_where_orderby.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Focus: Query execution order and basic filtering/sorting

BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
-- Assumptions: Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
-- Pitfall: Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
-- Predict row grain and NULL/order behavior before executing each example.

-- Example 1: Select specific columns with filtering and sorting
SELECT customer_id, full_name, country, created_at
FROM customers
WHERE country IN ('US','CA')
-- `customer_id` makes ties on the timestamp deterministic before LIMIT.
ORDER BY created_at DESC, customer_id DESC
LIMIT 10;

-- Example 2: Derived column and alias
SELECT 
  product_id,
  name,
  price,
  cost,
  (price - cost) AS gross_margin
FROM products
WHERE price > 50
ORDER BY gross_margin DESC, price DESC, product_id
LIMIT 15;

-- Example 3: Basic filtering with patterns
SELECT *
FROM customers
WHERE email LIKE '%@example.com'
  AND full_name ILIKE 'customer %1_'
ORDER BY customer_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List the 20 newest orders with customer ID and total amount.
--    Hint: Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.
--    Inputs: For sql-01 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-01 Exercise 1, expected output: At most 20 rows; one row per order, newest first. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-01 Exercise 1, assert the result has at most 20 rows, no duplicate `order_id`, and no adjacent pair out of `(order_date DESC, order_id DESC)` order. Check that each projected `customer_id`, `total_amount`, and `order_date` matches the same `orders.order_id` source row. Give two rows the same `o.order_date DESC` value and different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-01 Exercise 1, check `o.order_date DESC, o.order_id DESC` before applying the row cap.
-- 2. [Query writing] Find the 10 most expensive products created in the last 90 days.
--    Hint: Filter the timestamp directly, then sort by price and a stable product key.
--    Inputs: For sql-01 Exercise 2, read from `products`. Build the answer toward `product_id`, `name`, `price`, and `created_at`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-01 Exercise 2, expected output: At most 10 product rows; every row is in the 90-day window. The final columns are `product_id`, `name`, `price`, and `created_at`. The final order is `p.price DESC, p.product_id`.
--    Verify: For sql-01 Exercise 2, assert no more than 10 rows, no duplicate `product_id`, and no adjacent pair that violates `p.price DESC, p.product_id`. Rejoin the returned keys to `products` to confirm `product_id`, `name`, `price`, and `created_at` came from the same source rows. Tie two rows on `p.price DESC` and give them different `p.product_id` values; verify `p.price DESC, p.product_id` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-01 Exercise 2, inspect the source keys that survive `WHERE`; then check `p.price DESC, p.product_id` before applying the row cap.
-- 3. [Query writing] Show customers from GB or DE created in the last year, newest first.
--    Hint: Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
--    Inputs: For sql-01 Exercise 3, read from `customers`. Build the answer toward `customer_id`, `full_name`, `country`, and `created_at`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-01 Exercise 3, expected output: Only GB/DE customers from the declared window. The final columns are `customer_id`, `full_name`, `country`, and `created_at`. The final order is `c.created_at DESC, c.customer_id`.
--    Verify: For sql-01 Exercise 3, run an anti-check that counts rows where NOT ((c.country IN ('GB', 'DE') AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, `country`, and `created_at` against `customers`. Give two rows the same `c.created_at DESC` value and different `c.customer_id` values; verify `c.created_at DESC, c.customer_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-01 Exercise 3, inspect the source keys that survive `WHERE`; then check `c.created_at DESC, c.customer_id` before applying the row cap.
-- 4. [Prediction] Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
--    Hint: Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
--    Inputs: For sql-01 Exercise 4, read from `customers`. Build the answer toward `missing_email_count`, `present_email_count`, and `customer_count`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-01 Exercise 4, expected output: Exactly one summary row with counts whose sum equals all customers. The final columns are `missing_email_count`, `present_email_count`, and `customer_count`.
--    Verify: For sql-01 Exercise 4, assert exactly one row. Independently run `SELECT COUNT(*) FROM customers`; verify `missing_email_count + present_email_count = customer_count` and that `customer_count` equals the independent count. Repeat with `NULL` in `email` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-01 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. [Debugging] Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
--    Hint: Define the business ranking first; use a unique final key for tied prices.
--    Inputs: For sql-01 Exercise 5, read from `products`. Build the answer toward `product_id`, `name`, and `price`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-01 Exercise 5, expected output: At most 10 rows, highest prices first, stable across repeated runs on unchanged data. The final columns are `product_id`, `name`, and `price`. The final order is `p.price DESC, p.product_id`.
--    Verify: For sql-01 Exercise 5, assert no more than 10 rows, no duplicate `product_id`, and no adjacent pair that violates `p.price DESC, p.product_id`. Rejoin the returned keys to `products` to confirm `product_id`, `name`, and `price` came from the same source rows. Give two rows the same `p.price DESC` value and different `p.product_id` values; verify `p.price DESC, p.product_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-01 Exercise 5, check `p.price DESC, p.product_id` before applying the row cap.
-- 6. [Extension] Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.
--    Hint: Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.
--    Inputs: For sql-01 Exercise 6, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-01 Exercise 6, expected output: Up to 10 rows strictly after the first page with no overlap. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-01 Exercise 6, assert no more than 10 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_date DESC, o.order_id DESC`. Rejoin the returned keys to `orders` to confirm `order_id`, `customer_id`, `total_amount`, and `order_date` came from the same source rows. Give two rows the same `o.order_date DESC` value and different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-01 Exercise 6, run `first_page`, and `cursor_row` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.

ROLLBACK;
