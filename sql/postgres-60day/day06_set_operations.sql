-- Day 6: UNION, UNION ALL, INTERSECT, EXCEPT
-- BEGINNER WORKFLOW — sql-06: Set Operations
-- Guide: sql/postgres-60day/companion-guides/day06_set_operations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-06/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, events, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
-- Assumptions: Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
-- Pitfall: `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
-- Predict row grain and NULL/order behavior before executing each example.

-- Customers who purchased AND generated support events
WITH purchasers AS (
  SELECT DISTINCT o.customer_id FROM orders o
), supporters AS (
  SELECT DISTINCT e.customer_id FROM events e WHERE e.event_type = 'support'
)
SELECT * FROM purchasers
INTERSECT
SELECT * FROM supporters
ORDER BY customer_id;

-- Customers who browsed but never purchased
WITH browsers AS (
  SELECT DISTINCT e.customer_id FROM events e WHERE e.event_type = 'page_view'
), purchasers AS (
  SELECT DISTINCT o.customer_id FROM orders o
)
SELECT * FROM browsers
EXCEPT
SELECT * FROM purchasers
ORDER BY customer_id;

-- UNION vs UNION ALL (dedupe demo)
SELECT country FROM customers WHERE country IN ('US','CA')
UNION ALL
SELECT country FROM customers WHERE country IN ('CA','GB')
ORDER BY country;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return customer IDs that have either an order or a support event.
--    Hint: `UNION` expresses set membership and removes duplicates across both sources.
--    Inputs: For sql-06 Exercise 1, read from `orders`, and `events`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-06 Exercise 1, expected output: One distinct customer ID per qualifying customer. The final columns are `customer_id`. The final order is `customer_id`.
--    Verify: For sql-06 Exercise 1, run an anti-check that counts rows where NOT ((e.event_type = 'support')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `orders`, and `events`. Add one row for which `(e.event_type = 'support')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-06 Exercise 1, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
-- 2. [Query writing] Return customer IDs that have both an order and a support event.
--    Hint: `INTERSECT` keeps keys present in both compatible sets.
--    Inputs: For sql-06 Exercise 2, read from `orders`, and `events`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-06 Exercise 2, expected output: One distinct customer ID in both sets. The final columns are `customer_id`. The final order is `customer_id`.
--    Verify: For sql-06 Exercise 2, run an anti-check that counts rows where NOT ((e.event_type = 'support')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `orders`, and `events`. Add one row for which `(e.event_type = 'support')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-06 Exercise 2, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
-- 3. [Query writing] Return customers who have no orders.
--    Hint: `EXCEPT` subtracts the order-customer set from all customers.
--    Inputs: For sql-06 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-06 Exercise 3, expected output: One row per customer absent from orders. The final columns are `customer_id`. The final order is `customer_id`.
--    Verify: For sql-06 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `customers`, and `orders`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-06 Exercise 3, check `customer_id` before applying the row cap.
-- 4. [Prediction] Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
--    Hint: `UNION ALL` preserves every input row; `UNION` returns distinct rows.
--    Inputs: For sql-06 Exercise 4, read from `orders`. Build the answer toward `operation`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-06 Exercise 4, expected output: Two labeled summary rows showing all-count >= distinct-count. The final columns are `operation`, and `row_count`. The final order is `operation`.
--    Verify: For sql-06 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `operation`, and `row_count` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-06 Exercise 4, run `combined_all`, and `combined_distinct` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
--    Hint: Each branch below returns one text label and one numeric amount at the same report grain.
--    Inputs: For sql-06 Exercise 5, read from `orders`, and `expenses`. Build the answer toward `measure`, and `amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-06 Exercise 5, expected output: Rows identify revenue and expense measures with compatible types. The final columns are `measure`, and `amount`. The final order is `measure`.
--    Verify: For sql-06 Exercise 5, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `measure`, and `amount` against `orders`, and `expenses`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-06 Exercise 5, check `measure` before applying the row cap.
-- 6. [Extension] Return the symmetric difference between customers with orders and customers with support events.
--    Hint: Subtract each set from the other, then union the two differences.
--    Inputs: For sql-06 Exercise 6, read from `orders`, and `events`. Build the answer toward `customer_id`, and `source`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-06 Exercise 6, expected output: Customers present in exactly one of the two source sets. The final columns are `customer_id`, and `source`. The final order is `customer_id, source`.
--    Verify: For sql-06 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `source` against `orders`, and `events`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-06 Exercise 6, run `ordering_customers`, `support_customers`, `only_orders`, and `only_support` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.

ROLLBACK;
