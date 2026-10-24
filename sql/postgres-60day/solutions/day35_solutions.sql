-- Day 35 solutions: avoiding common query pitfalls
-- SOLUTION READING MAP — sql-35: Avoiding Pitfalls
-- Explanation: sql/postgres-60day/solutions/day35_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day35_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
BEGIN;
SET search_path TO training, public;

-- Exercise 1: three sargable rewrites.
-- 1a. Range bounds instead of date_trunc(order_date).
SELECT COUNT(*)
FROM orders
WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP)
  AND order_date < date_trunc('month', CURRENT_TIMESTAMP) + interval '1 month';

-- 1b. Exact comparison can use the unique email B-tree.
SELECT customer_id
FROM customers
WHERE email = 'customer100@example.com';

-- 1c. country is NOT NULL, so COALESCE is unnecessary.
SELECT COUNT(*)
FROM customers
WHERE country = 'US';

-- Exercise 2: replace a per-customer correlated aggregate with one grouped CTE.
WITH order_totals AS (
  SELECT customer_id,
         COUNT(*) AS orders,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id,
       c.full_name,
       COALESCE(ot.orders, 0) AS orders,
       COALESCE(ot.revenue, 0) AS revenue
FROM customers c
LEFT JOIN order_totals ot USING (customer_id)
ORDER BY revenue DESC, c.customer_id;

-- Exercise 3: a prefix has a searchable starting point; a leading wildcard
-- generally cannot seek into a normal B-tree text index.
EXPLAIN SELECT customer_id FROM customers WHERE full_name LIKE 'A%';
EXPLAIN SELECT customer_id FROM customers WHERE full_name LIKE '%A%';

-- Exercise 4: keyset paging starts strictly after the final tuple from the
-- previous page and repeats the identical deterministic ordering.
WITH boundary AS (
  SELECT order_date, order_id
  FROM orders
  ORDER BY order_date DESC, order_id DESC
  OFFSET 19 LIMIT 1
)
SELECT o.order_id, o.order_date
FROM orders o
CROSS JOIN boundary b
WHERE (o.order_date, o.order_id) < (b.order_date, b.order_id)
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 20;

-- Exercise 5: independent pre-aggregations prevent payment/item fanout.
WITH paid AS (
  SELECT order_id, SUM(amount) AS paid FROM payments GROUP BY order_id
), sold AS (
  SELECT order_id, SUM(quantity * unit_price * (1 - discount)) AS sold
  FROM order_items GROUP BY order_id
)
SELECT o.order_id, p.paid, s.sold
FROM orders o
LEFT JOIN paid p USING (order_id)
LEFT JOIN sold s USING (order_id)
ORDER BY o.order_id
LIMIT 20;

-- Exercise 6: COUNT(expression) intentionally ignores NULL expression values.
SELECT COUNT(*) AS customer_rows,
       COUNT(email) AS customers_with_email,
       COUNT(*) - COUNT(email) AS customers_without_email
FROM customers;

ROLLBACK;
