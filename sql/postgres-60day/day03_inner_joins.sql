-- Day 3: INNER JOIN deep dive
-- BEGINNER WORKFLOW — sql-03: Inner Joins
-- Guide: sql/postgres-60day/companion-guides/day03_inner_joins.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-03/ copy, and prints the full
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
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
-- Assumptions: Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
-- Pitfall: A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
-- Predict row grain and NULL/order behavior before executing each example.

-- Example: Orders with customer and items (3-table join)
SELECT o.order_id, o.order_date, c.full_name, p.name AS product, oi.quantity, oi.unit_price
FROM orders o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p    ON p.product_id = oi.product_id
ORDER BY o.order_date DESC, o.order_id DESC, p.product_id
LIMIT 50;

-- Multiple joins with filters
SELECT o.order_id, c.country, SUM(oi.quantity) AS total_items
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, c.country
ORDER BY total_items DESC, o.order_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List orders with customer names and countries.
--    Hint: Join the order foreign key to the customer primary key and qualify every selected column.
--    Inputs: Use `orders`, `customers` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: List orders with customer names and countries” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Join the order foreign key to the customer primary key and qualify every selected column.
-- 2. [Query writing] Calculate each order item's net line revenue with the product name and category.
--    Hint: Remain at one row per order item; do not aggregate until the desired grain changes.
--    Inputs: Use `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Calculate each order item's net line revenue with the product name and category” at one row at one row per order item grain. Named evidence columns/objects: `evidence`, `line_revenue`, `oi`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row at one row per order item grain; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Remain at one row per order item; do not aggregate until the desired grain changes.
-- 3. [Query writing] List payments with order status and customer name.
--    Hint: Follow payments → orders → customers using each declared foreign key.
--    Inputs: Use `payments`, `orders`, `customers` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: List payments with order status and customer name” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `p`, `o`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `payments`, `orders`, `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Follow payments → orders → customers using each declared foreign key.
-- 4. [Prediction] Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
--    Hint: Aggregate items and payments separately to one row per order before joining those aggregates.
--    Inputs: Use `order_items`, `payments`, `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation”. Show both compared result shapes at one row per order before joining those aggregates, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `item_total`, `oi`, `paid_total`, `p`, `o`, `it`, `pt`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `order_items`, `payments`, `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate items and payments separately to one row per order before joining those aggregates.
-- 5. [Debugging] Repair a customer/order join whose `ON` clause compares unrelated IDs.
--    Hint: Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
--    Inputs: Use `orders`, `customers` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 requires a written prediction and the observed result for “Debugging: Repair a customer/order join whose ON clause compares unrelated IDs”. Show both compared result shapes at one row per customer or the customer grouping key named by the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `joined_rows`, `distinct_orders`, `o`, `c`.
--    Verify: For Exercise 5, run the two forms over the identical rows in `orders`, `customers`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Join orders.customerid to customers.customerid; verify output cannot exceed the order count for an inner many-to-one join.
-- 6. [Extension] Calculate net line revenue by customer country without double-counting order totals.
--    Hint: Start from line items, join through orders and customers, then aggregate at country grain.
--    Inputs: Use `order_items`, `orders`, `customers` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Calculate net line revenue by customer country without double-counting order totals” observable through the exact DDL/DML command tag plus one row at country grain; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `net_revenue`, `oi`, `o`, `c`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `net_revenue`, `oi`, `o`, `c`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Start from line items, join through orders and customers, then aggregate at country grain.

ROLLBACK;
