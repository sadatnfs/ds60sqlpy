-- Day 33 solutions: index optimization strategies
-- SOLUTION READING MAP — sql-33: Index Optimization Strategies
-- Explanation: sql/postgres-60day/solutions/day33_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day33_solutions.sql
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

-- Exercise 1: equality first, range second in a composite index.
CREATE INDEX idx_products_category_created_solution
  ON products(category, created_at);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, created_at
FROM products
WHERE category = 'Home'
  AND created_at >= CURRENT_TIMESTAMP - interval '1 year'
ORDER BY created_at;

-- Exercise 2: a compact partial index for only high-value orders.
CREATE INDEX idx_orders_high_value_solution
  ON orders(total_amount, order_date)
  WHERE total_amount > 1000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM orders
WHERE total_amount > 1000
  AND order_date >= CURRENT_TIMESTAMP - interval '90 days'
ORDER BY total_amount DESC;

-- Exercise 3: without the leftmost category equality, created_at alone cannot
-- use the full composite search prefix as efficiently.
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, created_at
FROM products
WHERE created_at >= CURRENT_TIMESTAMP - interval '1 year';

-- Exercise 4: customer/date are search keys; status and total are payload that
-- may permit an index-only scan once visibility-map state allows it.
CREATE INDEX idx_orders_history_cover_solution
  ON orders(customer_id, order_date DESC)
  INCLUDE (status, total_amount);
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, status, total_amount
FROM orders
WHERE customer_id = 1
ORDER BY order_date DESC;

-- Exercise 5: only the first predicate implies total_amount > 1000. The second
-- query is correct but is not eligible for the partial index.
EXPLAIN SELECT order_id FROM orders WHERE total_amount > 1200;
EXPLAIN SELECT order_id FROM orders WHERE total_amount > 500;

-- Exercise 6: measure the candidate subset before paying for another index.
SELECT COUNT(*) AS all_customers,
       COUNT(*) FILTER (WHERE segment IS NULL) AS null_segments
FROM customers;
CREATE INDEX idx_customers_null_segment_solution
  ON customers(customer_id)
  WHERE segment IS NULL;
EXPLAIN SELECT customer_id FROM customers WHERE segment IS NULL;

ROLLBACK;
