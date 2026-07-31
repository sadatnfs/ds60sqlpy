-- Day 4: LEFT/RIGHT/FULL OUTER JOINs and NULL handling
-- BEGINNER WORKFLOW — sql-04: Outer Joins
-- Guide: sql/postgres-60day/companion-guides/day04_outer_joins.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-04/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, products, payments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
-- Assumptions: Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
-- Pitfall: A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
-- Predict row grain and NULL/order behavior before executing each example.

-- LEFT JOIN: customers without orders
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY orders ASC, c.customer_id
LIMIT 25;

-- RIGHT JOIN: products that appear in orders (or not)
SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity),0) AS sold_qty
FROM order_items oi
RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY sold_qty ASC, p.product_id
LIMIT 25;

-- FULL OUTER JOIN: payments vs orders.
-- A payment foreign key prevents an orphan payment in this dataset, while an
-- order may legitimately have no payment. Keep both keys visible when auditing.
SELECT o.order_id,
       p.payment_id,
       p.order_id AS payment_order_id,
       o.total_amount,
       p.amount AS payment_amount
FROM orders o
FULL OUTER JOIN payments p ON p.order_id = o.order_id
WHERE o.order_id IS NULL OR p.order_id IS NULL
ORDER BY COALESCE(o.order_id, p.order_id), p.payment_id; -- mismatches

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every customer with order count, including customers with zero orders.
--    Hint: Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: List every customer with order count, including customers with zero orders” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `order_count`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Start from customers, left join orders, and count the nullable order key rather than COUNT().
-- 2. [Query writing] Find products that have never appeared in an order item.
--    Hint: Left join and retain rows where the right-side primary key is NULL.
--    Inputs: Use `products`, `order_items` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Find products that have never appeared in an order item” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `p`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Left join and retain rows where the right-side primary key is NULL.
-- 3. [Query writing] Compare monthly budgets and expenses by category with a full outer join.
--    Hint: Aggregate each side to the same category/month grain before joining; preserve keys from either side.
--    Inputs: Use `expenses`, `budgets` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 requires a written prediction and the observed result for “Query writing: Compare monthly budgets and expenses by category with a full outer join”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `actual_amount`, `e`, `budget_amount`, `b`, `category`, `bm`, `em`.
--    Verify: For Exercise 3, run the two forms over the identical rows in `expenses`, `budgets`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate each side to the same category/month grain before joining; preserve keys from either side.
-- 4. [Prediction] Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
--    Hint: Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Preserve every customer while counting only delivered orders; compare a status predicate in ON with the same predicate in WHERE”. Show both compared result shapes at one row per customer or the customer grouping key named by the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `delivered_orders`, `c`, `o`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `customers`, `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Place o.status = 'delivered' in ON; WHERE would remove NULL-extended customers.
-- 5. [Debugging] Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
--    Hint: Count a non-nullable right-side key that becomes NULL for an unmatched row.
--    Inputs: Use `customers`, `orders` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Repair COUNT() in a left-join order count so customers without orders report zero rather than one” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `order_count`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Count a non-nullable right-side key that becomes NULL for an unmatched row.
-- 6. [Extension] Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
--    Hint: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
--    Inputs: Use `products`, `order_items` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys” observable through the exact DDL/DML command tag plus one row per product or product grouping requested; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `matched`, `evidence`, `matched_products`, `unsold_products`, `orphan_item_product_ids`, `p`, `oi`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `matched`, `evidence`, `matched_products`, `unsold_products`, `orphan_item_product_ids`, `p`, `oi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.

ROLLBACK;
