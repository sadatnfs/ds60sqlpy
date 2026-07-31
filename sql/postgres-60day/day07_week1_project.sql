-- Day 7: Week 1 Mini-Project
-- BEGINNER WORKFLOW — sql-07: Week1 Project
-- Guide: sql/postgres-60day/companion-guides/day07_week1_project.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-07/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Build a comprehensive report combining joins, aggregates, set ops
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
-- Assumptions: Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
-- Pitfall: A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
-- Predict row grain and NULL/order behavior before executing each example.

-- Customer revenue by country and category (last 90 days)
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= now() - interval '90 days'
), line AS (
  SELECT ro.order_id, ro.customer_id, c.country, p.category,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
  FROM recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category,
       ROUND(SUM(line_revenue),2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers,
       ROUND(SUM(line_revenue)/NULLIF(COUNT(DISTINCT customer_id),0),2) AS rev_per_buyer
FROM line
GROUP BY country, category
ORDER BY revenue DESC, country, category
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
--    Hint: Aggregate orders at status grain and round only displayed monetary values.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 must make “Query writing: Build an order KPI table by status with order count, revenue, average order value, and distinct customers” observable through the exact DDL/DML command tag plus one row at status grain; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_count`, `customer_count`, `revenue`, `average_order_value`, `o`, `kpi`.
--    Verify: For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_count`, `customer_count`, `revenue`, `average_order_value`, `o`, `kpi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate orders at status grain and round only displayed monetary values.
-- 2. [Query writing] Return the 20 products with the highest net line revenue.
--    Hint: Aggregate order items by product before ranking; use product ID as tie-breaker.
--    Inputs: Use `products`, `order_items` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Return the 20 products with the highest net line revenue” at one row per product or product grouping requested. Named evidence columns/objects: `tie`, `evidence`, `net_revenue`, `p`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate order items by product before ranking; use product ID as tie-breaker.
-- 3. [Query writing] Create a customer summary that retains customers with no orders.
--    Hint: Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 must make “Query writing: Create a customer summary that retains customers with no orders” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_count`, `stored_order_total`, `c`, `o`.
--    Verify: For Exercise 3, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_count`, `stored_order_total`, `c`, `o`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Left join from customers and count/order-sum nullable matches with COALESCE only where zero has clear meaning.
-- 4. [Debugging] Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
--    Hint: Aggregate each detail table to order grain first, then join the one-row-per-order relations.
--    Inputs: Use `order_items`, `payments`, `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 returns a table-shaped answer to “Debugging: Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `p`, `stored_total`, `storage_difference`, `unpaid_balance`, `o`, `it`, `pt`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 4, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, `payments`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate each detail table to order grain first, then join the one-row-per-order relations.
-- 5. [Prediction] Build a monthly order trend and explain which months are absent rather than zero.
--    Hint: Grouping observed orders alone cannot create empty calendar months.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 needs the plan evidence for “Prediction: Build a monthly order trend and explain which months are absent rather than zero”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `order_month`, `order_count`, `stored_revenue`, `o`.
--    Verify: For Exercise 5, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
--    Hint ladder, rung 1: Start with the guide's first rung: Grouping observed orders alone cannot create empty calendar months.
-- 6. [Extension] Create a compact one-row audit of customer, order, item, and payment coverage.
--    Hint: Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
--    Inputs: Use `customers`, `orders`, `order_items`, `payments` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Create a compact one-row audit of customer, order, item, and payment coverage” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, `c`, `o`, `customers_without_orders`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, `c`, `o`, `customers_without_orders`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Use scalar subqueries for independent counts; this avoids accidental cross multiplication.

ROLLBACK;
