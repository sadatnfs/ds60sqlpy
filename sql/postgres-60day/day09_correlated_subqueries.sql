-- Day 9: Correlated Subqueries, EXISTS/IN
-- BEGINNER WORKFLOW — sql-09: Correlated Subqueries
-- Guide: sql/postgres-60day/companion-guides/day09_correlated_subqueries.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-09/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
-- Assumptions: `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
-- Pitfall: A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
-- Predict row grain and NULL/order behavior before executing each example.

-- EXISTS: customers who purchased Electronics
SELECT c.*
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.customer_id = c.customer_id
    AND p.category = 'Electronics'
)
ORDER BY c.customer_id;

-- IN with correlated condition
SELECT p.product_id, p.name
FROM products p
WHERE p.product_id IN (
  SELECT DISTINCT oi.product_id
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_date >= now() - interval '30 days'
)
ORDER BY p.product_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return customers who have at least one delivered order.
--    Hint: `EXISTS` expresses the yes/no question without multiplying customer rows.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Return customers who have at least one delivered order” at one row at least one delivered order grain. Named evidence columns/objects: `evidence`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row at least one delivered order grain; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: EXISTS expresses the yes/no question without multiplying customer rows.
-- 2. [Query writing] Return products that have never been sold.
--    Hint: `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
--    Inputs: Use `products`, `order_items` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Return products that have never been sold” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `p`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: NOT EXISTS correlates on product ID and is not confused by NULL membership.
-- 3. [Query writing] Return each customer's orders that are above that customer's average order total.
--    Hint: Correlate the average to the current order's customer, not to the current order ID.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Return each customer's orders that are above that customer's average order total” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `peer`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Correlate the average to the current order's customer, not to the current order ID.
-- 4. [Prediction] Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
--    Hint: Correlate on the customer key; a matching row alone determines exclusion.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 needs the plan evidence for “Prediction: Explain and avoid the NOT IN plus NULL trap by finding customers without orders using NOT EXISTS”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `c`, `o`, `not`, `exists`.
--    Verify: For Exercise 4, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `customers`, `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
--    Hint ladder, rung 1: Start with the guide's first rung: Correlate on the customer key; a matching row alone determines exclusion.
-- 5. [Debugging] Return only each customer's most recent order without an arbitrary `LIMIT 1`.
--    Hint: Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Return only each customer's most recent order without an arbitrary LIMIT 1” at one row at that timestamp grain. Named evidence columns/objects: `evidence`, `o`, `candidate`, `limit`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row at that timestamp grain; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Compare to the correlated MAX(orderdate) and break timestamp ties with the maximum ID at that timestamp.
-- 6. [Extension] Return customers for whom every order has at least one payment, excluding customers with no orders.
--    Hint: Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
--    Inputs: Use `customers`, `orders`, `payments` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Return customers for whom every order has at least one payment, excluding customers with no orders” observable through the exact DDL/DML command tag plus one row at least one payment, excluding customers with no orders grain; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `c`, `any_order`, `o`, `p`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `c`, `any_order`, `o`, `p`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Require an order to exist, then prove no order lacks a payment using double NOT EXISTS.

ROLLBACK;
