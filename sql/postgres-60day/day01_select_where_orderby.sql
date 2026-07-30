-- Day 1: SELECT, WHERE, ORDER BY, LIMIT
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
ORDER BY created_at DESC, customer_id
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
-- 2. [Query writing] Find the 10 most expensive products created in the last 90 days.
--    Hint: Filter the timestamp directly, then sort by price and a stable product key.
-- 3. [Query writing] Show customers from GB or DE created in the last year, newest first.
--    Hint: Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
-- 4. [Prediction] Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
--    Hint: Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
-- 5. [Debugging] Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
--    Hint: Define the business ranking first; use a unique final key for tied prices.
-- 6. [Extension] Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.
--    Hint: Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.

ROLLBACK;
