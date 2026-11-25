-- Day 1: SELECT, WHERE, ORDER BY, LIMIT
-- BEGINNER WORKFLOW - sql-01: SELECT, WHERE, ORDER BY and LIMIT
-- Guide: sql/postgres-60day/companion-guides/day01_select_where_orderby.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-01.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
-- Prerequisite: sql-start-03 (query construction and debugging on-ramp).
-- Focus: Query execution order and basic filtering/sorting
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
-- Assumptions: Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
-- Pitfall: Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
-- Predict row grain and NULL/order behavior before executing each example.
-- Example 1: Select specific columns with filtering and sorting
SELECT
  customer_id,
  full_name,
  country,
  created_at
FROM
  customers
WHERE
  country IN ('US', 'CA')
  -- `customer_id` makes ties on the timestamp deterministic before LIMIT.
ORDER BY
  created_at DESC,
  customer_id DESC
LIMIT 10;

-- Example 2: Derived column and alias
SELECT
  product_id,
  name,
  price,
  cost,
  (price -
    cost) AS gross_margin
FROM
  products
WHERE
  price > 50
ORDER BY
  gross_margin DESC,
  price DESC,
  product_id
LIMIT 15;

-- Example 3: Basic filtering with patterns
SELECT
  *
FROM
  customers
WHERE
  email LIKE '%@example.com'
  AND full_name ILIKE 'customer %1_'
ORDER BY
  customer_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List the 20 newest orders with customer ID and total amount.
--    Hint: Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.
--    Inputs: For sql-01 Exercise 1, read the 4,362 `orders` rows, one per `order_id`; `order_date` is `NOT NULL` and holds 4,362 distinct timestamps, so `order_id` only breaks future ties. Project `order_id`, `customer_id`, `total_amount`, and `order_date`.
--    Expected result/shape: For sql-01 Exercise 1, return exactly 20 rows, one per order, newest first; on a freshly loaded fixture the list starts with order 2258 and ends with order 743. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-01 Exercise 1, confirm 20 rows and 20 distinct `order_id` values, then compare them with `SELECT order_id FROM orders ORDER BY order_date DESC, order_id DESC LIMIT 20`. Inside a rolled-back transaction, copy order 2258's `order_date` onto order 1; the first rows must become 2258, 1, 745, showing the higher ID wins the tie.
--    Hint ladder, rung 1: For sql-01 Exercise 1, check `o.order_date DESC, o.order_id DESC` before applying the row cap.
-- 2. [Query writing] Find the 10 most expensive products created in the last 90 days.
--    Hint: Filter the timestamp directly, then sort by price and a stable product key.
--    Inputs: For sql-01 Exercise 2, read `products` (300 rows, 300 distinct prices); 25 of them have `created_at` inside the last 90 days, priced from 112.12 to 121.00. Project `product_id`, `name`, `price`, and `created_at`.
--    Expected result/shape: For sql-01 Exercise 2, return exactly 10 of those 25 recent products, highest price first: product 300 at 121.00 down to product 291 at 117.67. The final columns are `product_id`, `name`, `price`, and `created_at`. The final order is `p.price DESC, p.product_id`.
--    Verify: For sql-01 Exercise 2, confirm `SELECT COUNT(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'` returns 25 and that every returned `created_at` passes that test. Inside a rolled-back transaction, set product 299's price to 121.00; the first two rows must then be 299 and 300, because `product_id` ascending breaks the price tie.
--    Hint ladder, rung 1: For sql-01 Exercise 2, inspect the source keys that survive `WHERE`; then check `p.price DESC, p.product_id` before applying the row cap.
-- 3. [Query writing] Show customers from GB or DE created in the last year, newest first.
--    Hint: Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
--    Inputs: For sql-01 Exercise 3, read `customers` (500 rows); 119 were created in the last year, of which 15 are `GB` and 14 are `DE`. Project `customer_id`, `full_name`, `country`, and `created_at`.
--    Expected result/shape: For sql-01 Exercise 3, return 29 rows on a freshly loaded fixture, all `GB` or `DE` and all created within one year, newest first starting with customer 172. The final columns are `customer_id`, `full_name`, `country`, and `created_at`. The final order is `c.created_at DESC, c.customer_id`.
--    Verify: For sql-01 Exercise 3, group the one-year window by `country` and confirm `GB` 15 plus `DE` 14 equals the 29 returned rows; grouping the output by `country` must show only those two values. The 29 rows carry 29 distinct `created_at` values, so `customer_id` only matters if a tie is added.
--    Hint ladder, rung 1: For sql-01 Exercise 3, inspect the source keys that survive `WHERE`; then check `c.created_at DESC, c.customer_id` before applying the row cap.
-- 4. [Prediction] Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
--    Hint: Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
--    Inputs: For sql-01 Exercise 4, read all 500 `customers` rows; `email` is nullable but currently filled on every row. The query returns counts only, so no customer key appears.
--    Expected result/shape: For sql-01 Exercise 4, return exactly one row: `missing_email_count` 0, `present_email_count` 500, `customer_count` 500. The final columns are `missing_email_count`, `present_email_count`, and `customer_count`.
--    Verify: For sql-01 Exercise 4, confirm 0 + 500 equals `customer_count` and matches `SELECT COUNT(*) FROM customers`. Inside a rolled-back transaction, set customer 1's `email` to `NULL` and rerun; the counts must become 1, 499, and 500, proving `COUNT(email)` skips the `NULL` while `COUNT(*)` keeps the row.
--    Hint ladder, rung 1: For sql-01 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. [Debugging] Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
--    Hint: Define the business ranking first; use a unique final key for tied prices.
--    Inputs: For sql-01 Exercise 5, read all 300 `products` rows; every price is distinct, from product 1 up to product 300 at 121.00. Project `product_id`, `name`, and `price`.
--    Expected result/shape: For sql-01 Exercise 5, return exactly 10 rows, products 300 down to 291 with prices 121.00 down to 117.67, identical on every rerun. The final columns are `product_id`, `name`, and `price`. The final order is `p.price DESC, p.product_id`.
--    Verify: For sql-01 Exercise 5, confirm 10 distinct `product_id` values and that `SELECT COUNT(DISTINCT price) FROM products` returns 300, so the current fixture has no price tie. Inside a rolled-back transaction, set product 299's price to 121.00; the top three must read 299, 300, 298 on every run.
--    Hint ladder, rung 1: For sql-01 Exercise 5, check `p.price DESC, p.product_id` before applying the row cap.
-- 6. [Extension] Return the second page of 10 newest orders using the same deterministic order, LIMIT 10 and OFFSET 10.
--    Hint: Sort by order_date DESC and order_id DESC; skip the first ten ordered rows and keep the next ten.
--    Inputs: For sql-01 Exercise 6, read the 4,362 `orders` rows at one row per `order_id`, sorted by the Exercise 1 key, and compare pages only on an unchanged fixture.
--    Expected result/shape: For sql-01 Exercise 6, return 10 rows equal to positions 11 through 20 of the ordered input, one row per `order_id`; on a freshly loaded fixture the page runs from order 1500 to order 743. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-01 Exercise 6, list the first 20 ordered IDs (2258 through 743) and confirm the page equals the last 10 of them, from 1500 to 743, with no ID shared with page one (2258 through 3014).
--    Hint ladder, rung 1: Write the ordered first page, then add OFFSET 10 without changing its ORDER BY.
ROLLBACK;
