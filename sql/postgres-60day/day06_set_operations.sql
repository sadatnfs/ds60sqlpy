-- Day 6: UNION, UNION ALL, INTERSECT, EXCEPT
-- BEGINNER WORKFLOW — sql-06: Set Operations
-- Guide: sql/postgres-60day/companion-guides/day06_set_operations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-06/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
--    Inputs: Use `orders`, `events` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Return customer IDs that have either an order or a support event” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `e`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `events`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: UNION expresses set membership and removes duplicates across both sources.
-- 2. [Query writing] Return customer IDs that have both an order and a support event.
--    Hint: `INTERSECT` keeps keys present in both compatible sets.
--    Inputs: Use `orders`, `events` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Return customer IDs that have both an order and a support event” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `e`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `events`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: INTERSECT keeps keys present in both compatible sets.
-- 3. [Query writing] Return customers who have no orders.
--    Hint: `EXCEPT` subtracts the order-customer set from all customers.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Return customers who have no orders” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: EXCEPT subtracts the order-customer set from all customers.
-- 4. [Prediction] Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
--    Hint: `UNION ALL` preserves every input row; `UNION` returns distinct rows.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Compare row counts produced by UNION and UNION ALL for two overlapping status lists”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `o`, `operation`, `row_count`, `union`, `all`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: UNION ALL preserves every input row; UNION returns distinct rows.
-- 5. [Debugging] Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
--    Hint: Each branch below returns one text label and one numeric amount at the same report grain.
--    Inputs: Use `orders`, `expenses` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts” at one row at the same report grain. Named evidence columns/objects: `evidence`, `measure`, `amount`, `o`, `e`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row at the same report grain; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `expenses`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Each branch below returns one text label and one numeric amount at the same report grain.
-- 6. [Extension] Return the symmetric difference between customers with orders and customers with support events.
--    Hint: Subtract each set from the other, then union the two differences.
--    Inputs: Use `orders`, `events` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Return the symmetric difference between customers with orders and customers with support events” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `o`, `e`, `source`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `o`, `e`, `source`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Subtract each set from the other, then union the two differences.

ROLLBACK;
