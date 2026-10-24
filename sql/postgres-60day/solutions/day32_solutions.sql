-- Day 32 solutions: index fundamentals
-- SOLUTION READING MAP — sql-32: Index Fundamentals
-- Explanation: sql/postgres-60day/solutions/day32_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day32_solutions.sql
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

-- Exercise 1: create and test an index on products(category).
CREATE INDEX idx_products_category_solution ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

-- Exercise 2: compare the plan without and with the course-owned index.
DROP INDEX idx_products_category_solution;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

CREATE INDEX idx_products_category_solution ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

-- On a 300-row table PostgreSQL may rationally choose a sequential scan.
-- Exercise 3: frequency supplies the selectivity evidence behind that choice.
SELECT category, COUNT(*) AS products
FROM products
GROUP BY category
ORDER BY products DESC, category;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id FROM products WHERE category = 'Electronics';

-- Exercise 4: B-tree indexes support bounded range predicates. Half-open
-- bounds avoid double-counting a timestamp at an adjacent window boundary.
CREATE INDEX idx_payments_date_solution ON payments(payment_date);
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, amount
FROM payments
WHERE payment_date >= CURRENT_TIMESTAMP - interval '180 days'
  AND payment_date < CURRENT_TIMESTAMP;

-- Exercise 5: lower(country) needs an index on that same expression.
CREATE INDEX idx_customers_lower_country_solution ON customers(lower(country));
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id FROM customers WHERE lower(country) = 'us';

-- Exercise 6: only the second query promises order. The first is intentionally
-- a control whose apparent order must not be treated as an API contract.
SELECT customer_id, country FROM customers LIMIT 10;
SELECT customer_id, country
FROM customers
ORDER BY country, customer_id
LIMIT 10;

ROLLBACK;
