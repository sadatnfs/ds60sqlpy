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
--    Inputs: For sql-43 Exercise 1, read from `training.customers`. Build the answer toward `staged_rows`, and `customers_restore_stage`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-43 Exercise 1, expected output: CSV rows are streamed to the client, and `staged_rows` equals the number of US customers. A real import would create an explicit staging table and run `\copy customers_restore_stage FROM. The final columns are `staged_rows`, and `customers_restore_stage`.
--    Verify: For sql-43 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `staged_rows`, and `customers_restore_stage` against `training.customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-43 Exercise 1, inspect the source keys that survive `WHERE`.
-- 2. Restore customers from staged into base with conflict handling (ON CONFLICT DO UPDATE) in a transaction.
--    Inputs: For sql-43 Exercise 2, use `customers`, and `customers_restore_stage` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-43 Exercise 2, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `full_name`, `email`, `country`, `created_at`, `segment`, and `attributes`.
--    Verify: For sql-43 Exercise 2, restore into an isolated target and reconcile `customers`, and `customers_restore_stage` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-43 Exercise 2, restore into an isolated target and reconcile `customers`, and `customers_restore_stage` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 3. Prediction: decide whether COPY TO '/server/path' or psql \copy writes on
--    the database server. Explain which is usually appropriate for a learner PC.
--    Inputs: For sql-43 Exercise 3, complete the explain server-side copy versus client-side copy written analysis and support its claims with read-only evidence from `customers`, `customers_stg`, and `customers_restore_stage`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-43 Exercise 3, expected output: a completed the explain server-side copy versus client-side copy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `copy`.
--    Verify: For sql-43 Exercise 3, check the explain server-side copy versus client-side copy written analysis against `copy`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-43 Exercise 3, check the explain server-side copy versus client-side copy written analysis against `copy`.
-- 4. Construction: generate a deterministic manifest with table name, row
--    count, minimum key, maximum key, and export timestamp.
--    Inputs: For sql-43 Exercise 4, read from `customers`. Build the answer toward `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-43 Exercise 4, expected output: one row per `customer_id`. The final columns are `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`.
--    Verify: For sql-43 Exercise 4, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-43 Exercise 4, select `customer_id` from `customers` before adding derived columns.
-- 5. Debugging: stage duplicate emails and make the restore deterministic
--    before ON CONFLICT, rather than letting one arbitrary duplicate win.
--    Inputs: For sql-43 Exercise 5, read from `customers_restore_stage`. Build the answer toward `full_name`, `email`, and `country`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-43 Exercise 5, expected output: one row per `country`. The final columns are `full_name`, `email`, and `country`. The final order is `email`.
--    Verify: For sql-43 Exercise 5, run an anti-check that counts rows where NOT ((winner_rank = 1)); require unique `country` where the expected grain is one row per key and confirm the projected `full_name`, `email`, and `country` against `customers_restore_stage`. Add duplicate source candidates for `country`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-43 Exercise 5, run `staged_duplicates` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 6. Edge case: compare source and restored rows with IS DISTINCT FROM so NULL
--    values are compared safely.
--    Inputs: For sql-43 Exercise 6, use `customers_restore_stage`, `customers`, `c.country`, and `c.segment` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-43 Exercise 6, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `email`, `staged_name`, and `restored_name`. The final order is `s.email`.
--    Verify: For sql-43 Exercise 6, restore into an isolated target and reconcile `customers_restore_stage`, `customers`, `c.country`, and `c.segment` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-43 Exercise 6, start with the first relation in `customers_restore_stage`, `customers`, `c.country`, and `c.segment`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.

ROLLBACK;
