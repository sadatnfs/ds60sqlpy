-- Day 43: Backup & Recovery Scenarios (conceptual + SQL helpers)
-- BEGINNER WORKFLOW — sql-43: Backup Recovery
-- Guide: sql/postgres-60day/companion-guides/day43_backup_recovery.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-43/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Logical export/import examples with COPY (server must have file access; adjust paths)
-- Export:
-- COPY customers TO '/tmp/customers.csv' CSV HEADER;
-- COPY orders    TO '/tmp/orders.csv'    CSV HEADER;

-- Import into staging tables (demo only)
CREATE TEMP TABLE customers_stg (LIKE customers INCLUDING ALL);
-- COPY customers_stg FROM '/tmp/customers.csv' CSV HEADER; -- example only

-- Verify counts between base and staged
SELECT 'customers' AS table, COUNT(*) AS base_cnt FROM customers
UNION ALL
SELECT 'customers_stg', COUNT(*) FROM customers_stg;

-- Point-in-time concepts (notes):
-- - Use WAL archiving and base backups for PITR (outside SQL scope)
-- - For ad-hoc recovery, restore into a separate DB and compare using EXCEPT/INTERSECT

-- Exercises
-- 1. Export/import a subset. COPY table has no WHERE clause; use
--    COPY (SELECT ... WHERE ...) TO STDOUT or client-side \copy in psql.
--    Inputs: Use only the declared lesson objects (customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 2. Restore customers from staged into base with conflict handling (ON CONFLICT DO UPDATE) in a transaction.
--    Inputs: Use only the declared lesson objects (customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: decide whether COPY TO '/server/path' or psql \copy writes on
--    the database server. Explain which is usually appropriate for a learner PC.
--    Inputs: Use only the declared lesson objects (customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: generate a deterministic manifest with table name, row
--    count, minimum key, maximum key, and export timestamp.
--    Inputs: Use only the declared lesson objects (customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Debugging: stage duplicate emails and make the restore deterministic
--    before ON CONFLICT, rather than letting one arbitrary duplicate win.
--    Inputs: Use only the declared lesson objects (customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: compare source and restored rows with IS DISTINCT FROM so NULL
--    values are compared safely.
--    Inputs: Use only the declared lesson objects (customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
