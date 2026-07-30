-- Day 6: UNION, UNION ALL, INTERSECT, EXCEPT
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
-- 2. [Query writing] Return customer IDs that have both an order and a support event.
--    Hint: `INTERSECT` keeps keys present in both compatible sets.
-- 3. [Query writing] Return customers who have no orders.
--    Hint: `EXCEPT` subtracts the order-customer set from all customers.
-- 4. [Prediction] Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
--    Hint: `UNION ALL` preserves every input row; `UNION` returns distinct rows.
-- 5. [Debugging] Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
--    Hint: Each branch below returns one text label and one numeric amount at the same report grain.
-- 6. [Extension] Return the symmetric difference between customers with orders and customers with support events.
--    Hint: Subtract each set from the other, then union the two differences.

ROLLBACK;
