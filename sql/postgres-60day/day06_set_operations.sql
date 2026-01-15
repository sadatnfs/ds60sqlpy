-- Day 6: UNION, UNION ALL, INTERSECT, EXCEPT
BEGIN;
SET search_path TO training, public;

-- Customers who purchased AND generated support events
WITH purchasers AS (
  SELECT DISTINCT o.customer_id FROM orders o
), supporters AS (
  SELECT DISTINCT e.customer_id FROM events e WHERE e.event_type = 'support'
)
SELECT * FROM purchasers
INTERSECT
SELECT * FROM supporters;

-- Customers who browsed but never purchased
WITH browsers AS (
  SELECT DISTINCT e.customer_id FROM events e WHERE e.event_type = 'page_view'
), purchasers AS (
  SELECT DISTINCT o.customer_id FROM orders o
)
SELECT * FROM browsers
EXCEPT
SELECT * FROM purchasers;

-- UNION vs UNION ALL (dedupe demo)
SELECT country FROM customers WHERE country IN ('US','CA')
UNION ALL
SELECT country FROM customers WHERE country IN ('CA','GB');

-- Exercises
-- 1) Find products appearing in orders AND promotions.
-- 2) Countries with customers but no orders.
-- 3) Combine two filtered order sets using UNION vs UNION ALL and compare counts.

ROLLBACK;
