-- Day 31 solutions: EXPLAIN and EXPLAIN ANALYZE
BEGIN;
SET search_path TO training, public;

-- Exercise 1: compare a broad predicate with a selective predicate.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '3 years';

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '7 days'
  AND status = 'returned'
  AND total_amount >= 1000;

-- Exercise 2: EXPLAIN estimates only; EXPLAIN ANALYZE also executes and reports
-- actual timing and row counts. Use read-only SELECTs while learning ANALYZE.
EXPLAIN
SELECT c.country, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.country, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.country;

ROLLBACK;
