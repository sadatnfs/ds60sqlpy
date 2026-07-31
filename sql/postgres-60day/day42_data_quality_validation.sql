-- Day 42: Data Quality & Validation
-- BEGINNER WORKFLOW — sql-42: Data Quality Validation
-- Guide: sql/postgres-60day/companion-guides/day42_data_quality_validation.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-42/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, order_items, orders, payments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Null analysis and basic profiling
SELECT 'customers' AS table,
       COUNT(*) AS rows,
       SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_emails,
       SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) AS null_country
FROM customers;

-- Duplicate detection (emails should be unique ideally)
SELECT email, COUNT(*) AS cnt
FROM customers
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY cnt DESC;

-- Orphan checks (should be zero due to FK, but as validation queries)
SELECT oi.order_id
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_id IS NULL
LIMIT 10;

SELECT p.payment_id
FROM payments p
LEFT JOIN orders o ON o.order_id = p.order_id
WHERE o.order_id IS NULL
LIMIT 10;

-- Domain/constraint validation examples
SELECT * FROM orders WHERE total_amount < 0 LIMIT 10;
SELECT * FROM payments WHERE amount < 0 LIMIT 10;

-- Exercises
-- 1. Build a validation report summarizing nulls, duplicates, and constraint violations across core tables.
--    Inputs: Use only the declared lesson objects (customers, order_items, orders, payments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 2. Detect customers with invalid email patterns using regex.
--    Inputs: Use only the declared lesson objects (customers, order_items, orders, payments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 3. Prediction: explain why CHECK (amount >= 0) rejects negative values but,
--    without NOT NULL, would accept NULL under SQL's three-valued logic.
--    Inputs: Use only the declared lesson objects (customers, order_items, orders, payments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: reconcile each order's stored total_amount with calculated
--    line-item revenue and return only differences greater than one cent.
--    Inputs: Use only the declared lesson objects (customers, order_items, orders, payments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: repair a duplicate check that groups by lower(email) but reports
--    only the normalized value, losing the raw variants needed for diagnosis.
--    Inputs: Use only the declared lesson objects (customers, order_items, orders, payments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: detect overlapping promotion date ranges for the same product,
--    treating touching inclusive endpoints as an overlap.
--    Inputs: Use only the declared lesson objects (customers, order_items, orders, payments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.

ROLLBACK;
