-- Day 43: Backup & Recovery Scenarios (conceptual + SQL helpers)
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
-- 2. Restore customers from staged into base with conflict handling (ON CONFLICT DO UPDATE) in a transaction.
-- 3. Prediction: decide whether COPY TO '/server/path' or psql \copy writes on
--    the database server. Explain which is usually appropriate for a learner PC.
-- 4. Construction: generate a deterministic manifest with table name, row
--    count, minimum key, maximum key, and export timestamp.
-- 5. Debugging: stage duplicate emails and make the restore deterministic
--    before ON CONFLICT, rather than letting one arbitrary duplicate win.
-- 6. Edge case: compare source and restored rows with IS DISTINCT FROM so NULL
--    values are compared safely.

ROLLBACK;
