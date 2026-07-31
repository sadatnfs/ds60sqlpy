-- Day 07 executable solutions
-- SOLUTION READING MAP — sql-07: Week1 Project
-- Explanation: sql/postgres-60day/solutions/day07_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day07_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
-- Assumptions: Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
-- Pitfall: A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
-- Why: Aggregate orders at status grain and round only displayed monetary values.
-- Expected: One row per order status.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.status,
       COUNT(*) AS order_count,
       COUNT(DISTINCT o.customer_id) AS customer_count,
       ROUND(SUM(o.total_amount), 2) AS revenue,
       ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM orders AS o
GROUP BY o.status
ORDER BY revenue DESC, o.status;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Return the 20 products with the highest net line revenue.
-- Why: Aggregate order items by product before ranking; use product ID as tie-breaker.
-- Expected: At most 20 product rows.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
SELECT p.product_id,
       p.name,
       p.category,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue
FROM products AS p
JOIN order_items AS oi
  ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY net_revenue DESC, p.product_id
LIMIT 20;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Create a customer summary that retains customers with no orders.
-- Why: Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
-- Expected: One row per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       c.country,
       COUNT(o.order_id) AS order_count,
       COALESCE(ROUND(SUM(o.total_amount), 2), 0) AS stored_order_total
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.country
ORDER BY stored_order_total DESC, c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Debugging
-- Prompt: Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
-- Why: Aggregate each detail table to order grain first, then join the one-row-per-order relations.
-- Expected: One row per order with signed differences.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH item_totals AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_total
  FROM order_items AS oi
  GROUP BY oi.order_id
), payment_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_total
  FROM payments AS p
  GROUP BY p.order_id
)
SELECT o.order_id,
       o.status,
       ROUND(o.total_amount, 2) AS stored_total,
       ROUND(it.line_total, 2) AS line_total,
       ROUND(o.total_amount - it.line_total, 2) AS storage_difference,
       ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total,
       ROUND(o.total_amount - COALESCE(pt.paid_total, 0), 2) AS unpaid_balance
FROM orders AS o
JOIN item_totals AS it
  ON it.order_id = o.order_id
LEFT JOIN payment_totals AS pt
  ON pt.order_id = o.order_id
ORDER BY ABS(o.total_amount - it.line_total) DESC, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Prediction
-- Prompt: Build a monthly order trend and explain which months are absent rather than zero.
-- Why: Grouping observed orders alone cannot create empty calendar months.
-- Expected: One row per observed order month.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT date_trunc('month', o.order_date)::date AS order_month,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM orders AS o
GROUP BY date_trunc('month', o.order_date)
ORDER BY order_month;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Create a compact one-row audit of customer, order, item, and payment coverage.
-- Why: Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
-- Expected: Exactly one audit row.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
SELECT (SELECT COUNT(*) FROM customers) AS customer_rows,
       (SELECT COUNT(*) FROM orders) AS order_rows,
       (SELECT COUNT(*) FROM order_items) AS order_item_rows,
       (SELECT COUNT(*) FROM payments) AS payment_rows,
       (SELECT COUNT(*) FROM customers AS c
        WHERE NOT EXISTS (
          SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id
        )) AS customers_without_orders;

-- No course answer persists changes or temporary objects.
ROLLBACK;
