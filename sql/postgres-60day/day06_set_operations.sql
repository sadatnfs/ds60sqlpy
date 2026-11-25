-- Day 6: UNION, UNION ALL, INTERSECT, EXCEPT
-- BEGINNER WORKFLOW - sql-06: Set Operations
-- Guide: sql/postgres-60day/companion-guides/day06_set_operations.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-06.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT DISTINCT
    o.customer_id
  FROM
    orders o
),
supporters AS (
  SELECT DISTINCT
    e.customer_id
  FROM
    events e
  WHERE
    e.event_type = 'support'
)
SELECT
  *
FROM
  purchasers
INTERSECT
SELECT
  *
FROM
  supporters
ORDER BY
  customer_id;

-- Customers who browsed but never purchased
WITH browsers AS (
  SELECT DISTINCT
    e.customer_id
  FROM
    events e
  WHERE
    e.event_type = 'page_view'
),
purchasers AS (
  SELECT DISTINCT
    o.customer_id
  FROM
    orders o
)
SELECT
  *
FROM
  browsers
EXCEPT
SELECT
  *
FROM
  purchasers
ORDER BY
  customer_id;

-- UNION vs UNION ALL (dedupe demo)
SELECT
  country
FROM
  customers
WHERE
  country IN ('US', 'CA')
UNION ALL
SELECT
  country
FROM
  customers
WHERE
  country IN ('CA', 'GB')
ORDER BY
  country;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return customer IDs that have either an order or a support event.
--    Hint: `UNION` expresses set membership and removes duplicates across both sources.
--    Inputs: For sql-06 Exercise 1, combine `customer_id` from all 4,362 `orders` rows with `customer_id` from the 4,000 `events` rows whose `event_type` is `support`; every one of the 500 customers has support events, while only 438 have orders.
--    Expected result/shape: For sql-06 Exercise 1, return 500 rows, one per distinct customer, customer 1 through customer 500, because `UNION` removes the duplicates from the 8,362 combined input rows. The final columns are `customer_id`. The final order is `customer_id`.
--    Verify: For sql-06 Exercise 1, confirm 500 distinct values and that `UNION ALL` over the same two branches returns 8,362 rows. Inside a rolled-back transaction, delete customer 8's support events; customer 8 has no orders, so the result must drop to 499 rows.
--    Hint ladder, rung 1: For sql-06 Exercise 1, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
-- 2. [Query writing] Return customer IDs that have both an order and a support event.
--    Hint: `INTERSECT` keeps keys present in both compatible sets.
--    Inputs: For sql-06 Exercise 2, intersect the distinct `customer_id` values from `orders` (438 buyers) with those from `events` filtered to `event_type = 'support'` (all 500 customers).
--    Expected result/shape: For sql-06 Exercise 2, return 438 rows, one per customer found in both sets; customer 8 and the other 61 customers without orders are missing. The final columns are `customer_id`. The final order is `customer_id`.
--    Verify: For sql-06 Exercise 2, confirm the 438 rows match `SELECT DISTINCT customer_id FROM orders` exactly, since every buyer also has support events. Inside a rolled-back transaction, delete customer 1's support events; the result must drop to 437 rows without customer 1.
--    Hint ladder, rung 1: For sql-06 Exercise 2, inspect the source keys that survive `WHERE`; then check `customer_id` before applying the row cap.
-- 3. [Query writing] Return customers who have no orders.
--    Hint: `EXCEPT` subtracts the order-customer set from all customers.
--    Inputs: For sql-06 Exercise 3, subtract the `customer_id` values in `orders` from the 500 `customers` keys with `EXCEPT`.
--    Expected result/shape: For sql-06 Exercise 3, return 62 rows, one per customer with no orders, from customer 8 to customer 496 in steps of 8. The final columns are `customer_id`. The final order is `customer_id`.
--    Verify: For sql-06 Exercise 3, confirm a `NOT EXISTS` anti-join and a `NOT IN (SELECT customer_id FROM orders)` filter both return the same 62 customers. Inside a rolled-back transaction, insert one order for customer 8; the result must drop to 61 rows.
--    Hint ladder, rung 1: For sql-06 Exercise 3, check `customer_id` before applying the row cap.
-- 4. [Prediction] Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
--    Hint: `UNION ALL` preserves every input row; `UNION` returns distinct rows.
--    Inputs: For sql-06 Exercise 4, read `status` from `orders` twice, once for `paid` or `shipped` and once for `shipped` or `delivered`, then count the combined rows under `UNION ALL` and under `UNION`.
--    Expected result/shape: For sql-06 Exercise 4, return two rows: `UNION` with `row_count` 3 and `UNION ALL` with `row_count` 3490. The final columns are `operation`, and `row_count`. The final order is `operation`.
--    Verify: For sql-06 Exercise 4, confirm that `UNION ALL` returns 3490 rows, the sum of the two branch counts (1745 + 1745), while `UNION` returns 3 because it keeps only the distinct statuses `delivered`, `paid`, and `shipped`; the `shipped` rows appear in both branches.
--    Hint ladder, rung 1: For sql-06 Exercise 4, count each branch separately before combining them; the `UNION ALL` count must equal the sum of the branch counts.
-- 5. [Debugging] Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
--    Hint: Each branch below returns one text label and one numeric amount at the same report grain.
--    Inputs: For sql-06 Exercise 5, stack one row labeled `order_revenue` holding `SUM(total_amount)` from `orders` and one row labeled `expense` holding `SUM(amount)` from `expenses` with `UNION ALL`, using a text label column followed by a numeric amount column.
--    Expected result/shape: For sql-06 Exercise 5, return two rows: `expense` with 50483850.00 and `order_revenue` with 2355646.89, both typed as `numeric` under one shared `amount` column. The final columns are `measure`, and `amount`. The final order is `measure`.
--    Verify: For sql-06 Exercise 5, confirm exactly two rows, `expense` = 50483850.00 and `order_revenue` = 2355646.89, each equal to its own standalone `SUM`; both branches must list the label first and the amount second, because swapping them in one branch raises `UNION types text and numeric cannot be matched`.
--    Hint ladder, rung 1: For sql-06 Exercise 5, run each branch alone and check that it returns one row with a `text` label and a `numeric` amount.
-- 6. [Extension] Return the symmetric difference between customers with orders and customers with support events.
--    Hint: Subtract each set from the other, then union the two differences.
--    Inputs: For sql-06 Exercise 6, compute the distinct ordering customers (438) and the distinct support-event customers (500), apply `EXCEPT` in both directions, and label each side with `source` before stacking them with `UNION ALL`.
--    Expected result/shape: For sql-06 Exercise 6, return 62 rows, all labeled `support_only`, from customer 8 to customer 496; no row is `orders_only` because every buyer also has support events. The final columns are `customer_id`, and `source`. The final order is `customer_id, source`.
--    Verify: For sql-06 Exercise 6, confirm 62 distinct `customer_id` values that equal the Exercise 3 result, and 0 `orders_only` rows. Inside a rolled-back transaction, delete customer 1's support events; the result must grow to 63 rows with one new `(1, 'orders_only')` row.
--    Hint ladder, rung 1: For sql-06 Exercise 6, run `ordering_customers`, `support_customers`, `only_orders`, and `only_support` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
ROLLBACK;
