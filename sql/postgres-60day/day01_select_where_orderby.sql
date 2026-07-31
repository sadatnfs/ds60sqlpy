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
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: List the 20 newest orders with customer ID and total amount” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `id`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Sort by orderdate DESC and add orderid DESC as a unique tie-breaker before applying LIMIT.
-- 2. [Query writing] Find the 10 most expensive products created in the last 90 days.
--    Hint: Filter the timestamp directly, then sort by price and a stable product key.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Find the 10 most expensive products created in the last 90 days” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Filter the timestamp directly, then sort by price and a stable product key.
-- 3. [Query writing] Show customers from GB or DE created in the last year, newest first.
--    Hint: Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Show customers from GB or DE created in the last year, newest first” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `c`, `gb`, `de`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Use IN for the country set, combine the time condition with AND, and break timestamp ties.
-- 4. [Prediction] Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
--    Hint: Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Predict which rows survive email = NULL, then write a query that counts missing and present emails correctly”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `missing_email_count`, `present_email_count`, `customer_count`, `c`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `customers`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Comparisons with NULL are unknown; use IS NULL and IS NOT NULL.
-- 5. [Debugging] Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
--    Hint: Define the business ranking first; use a unique final key for tied prices.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 needs the plan evidence for “Debugging: Repair a top-price query that uses LIMIT 10 without ORDER BY and explain why the original is nondeterministic”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `p`, `limit`.
--    Verify: For Exercise 5, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `products` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
--    Hint ladder, rung 1: Start with the guide's first rung: Define the business ranking first; use a unique final key for tied prices.
-- 6. [Extension] Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.
--    Hint: Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than OFFSET” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `o`, `fp`, `cursor`, `offset`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `o`, `fp`, `cursor`, `offset`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Use the last (orderdate, orderid) pair from page one and compare row values in the same descending order.

ROLLBACK;
