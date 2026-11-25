-- Day 43: Backup & Recovery Scenarios (conceptual + SQL helpers)
-- BEGINNER WORKFLOW - sql-43: Backup Recovery
-- Guide: sql/postgres-60day/companion-guides/day43_backup_recovery.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-43.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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

-- Logical export/import. Server-side COPY TO a file needs superuser or the
-- pg_write_server_files role; the course role gets SQLSTATE 42501. Export
-- through the client instead: COPY (query) TO STDOUT (whole-lesson mode prints
-- the rows; the SQL pad cannot run COPY), or psql's \copy in a psql terminal,
-- which reads and writes files on the machine where psql runs.
-- Import into staging tables (demo only)
CREATE TEMP TABLE customers_stg (
  LIKE customers INCLUDING ALL
);

-- A client-side import would be: \copy customers_stg FROM 'customers.csv' WITH (FORMAT csv, HEADER true)
-- Verify counts between base and staged
SELECT
  'customers' AS table,
  COUNT(*) AS base_cnt
FROM
  customers
UNION ALL
SELECT
  'customers_stg',
  COUNT(*)
FROM
  customers_stg;

-- Point-in-time concepts (notes):
-- - Use WAL archiving and base backups for PITR (outside SQL scope)
-- - For ad-hoc recovery, restore into a separate DB and compare using EXCEPT/INTERSECT
-- Exercises
-- 1. Export/import a subset. COPY table has no WHERE clause; use
--    COPY (SELECT ... WHERE ...) TO STDOUT or client-side \copy in psql.
--    Inputs: For sql-43 Exercise 1, export the US subset of `training.customers` with `COPY (SELECT customer_id, full_name, email, country, created_at, segment, attributes FROM customers WHERE country = 'US' ORDER BY customer_id) TO STDOUT WITH (FORMAT csv, HEADER true)`, then model the later `\copy ... FROM` import by creating the temporary table `customers_restore_stage` from the same rows.
--    Expected result/shape: For sql-43 Exercise 1, expected output: one CSV header line and 63 data lines streamed to the client, ordered by `customer_id`, then `SELECT 63` for the staging table.
--    Verify: For sql-43 Exercise 1, confirm that `SELECT COUNT(*) FROM training.customers WHERE country = 'US'` and `SELECT COUNT(*) FROM customers_restore_stage` both return 63; then confirm that `COPY customers TO STDOUT WHERE country = 'US'` fails with SQLSTATE `42601` (`WHERE clause not allowed with COPY TO`), because only the query form can filter an export.
--    Hint ladder, rung 1: For sql-43 Exercise 1, `COPY (query) TO STDOUT` sends rows to the client connection; `\copy` is the psql command that writes that stream to a client-side file.
-- 2. Restore customers from staged into base with conflict handling (ON CONFLICT DO UPDATE) in a transaction.
--    Inputs: For sql-43 Exercise 2, mark one staged row as changed (`full_name || ' [restored]'` for `customer1@example.com`), then load `customers_restore_stage` into `customers` with `INSERT ... SELECT ... ON CONFLICT (email) DO UPDATE` inside the lesson transaction.
--    Expected result/shape: For sql-43 Exercise 2, expected output: `UPDATE 1` for the staged change, then `INSERT 0 63`, because all 63 staged emails already exist and each conflicting row is updated; the `staged_rows` check returns 63, and `customers` still has 500 rows.
--    Verify: For sql-43 Exercise 2, confirm that `SELECT full_name FROM customers WHERE email = 'customer1@example.com'` returns `Customer 1 [restored]` and `SELECT COUNT(*) FROM customers` returns 500 inside the transaction; rerun the same upsert and confirm it again reports `INSERT 0 63` with 500 rows and unchanged values, which is the idempotency evidence for the data, while `customers_customer_id_seq` still advances by 63 per run because each proposed row evaluates the `customer_id` default before the conflict is found.
--    Hint ladder, rung 1: For sql-43 Exercise 2, the conflict target must be the unique key that identifies the same customer in both copies; here that is `email`.
-- 3. Prediction: decide whether COPY TO '/server/path' or psql \copy writes on
--    the database server. Explain which is usually appropriate for a learner PC.
--    Inputs: For sql-43 Exercise 3, compare server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` with psql's `\copy customers TO 'customers.csv'`, using the course role's privileges and the classroom layout as evidence.
--    Expected result/shape: For sql-43 Exercise 3, expected output: a short written answer: `COPY ... TO 'file'` runs in the database server process and writes on the server's file system, which needs superuser or `pg_write_server_files`; `\copy` streams the rows to the `psql` client, which writes the file. In the classroom, `psql` runs in a Linux container, so `\copy` writes into the learning volume, not onto your desktop.
--    Verify: For sql-43 Exercise 3, run the server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` as the course role (a non-superuser without `pg_write_server_files`) and confirm that it fails with SQLSTATE `42501` (`permission denied to COPY to a file`), while `COPY (SELECT 1) TO STDOUT` succeeds, because any role may copy to the client stream; a superuser session may be allowed to write the file, so it is not valid evidence.
--    Hint ladder, rung 1: For sql-43 Exercise 3, ask which process opens the file: the database server, or the `psql` client you are typing into.
-- 4. Construction: generate a deterministic manifest with table name, row
--    count, minimum key, maximum key, and export timestamp.
--    Inputs: For sql-43 Exercise 4, summarize `customers` in one manifest row: `'training.customers' AS table_name`, `COUNT(*) AS row_count`, `MIN(customer_id) AS min_key`, `MAX(customer_id) AS max_key`, and `clock_timestamp() AS observed_at`.
--    Expected result/shape: For sql-43 Exercise 4, expected output: exactly one row with columns `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`: `('training.customers', 500, 1, 500, <timestamp>)` on the course seed.
--    Verify: For sql-43 Exercise 4, rerun the manifest and confirm that every column except `observed_at` is identical; then compare `row_count` with the number of data lines in an exported CSV of the same table (500).
--    Hint ladder, rung 1: For sql-43 Exercise 4, a manifest is one aggregate row; every value except the timestamp must be reproducible from the same snapshot.
-- 5. Debugging: stage duplicate emails and make the restore deterministic
--    before ON CONFLICT, rather than letting one arbitrary duplicate win.
--    Inputs: For sql-43 Exercise 5, rank `customers_restore_stage` rows with `ROW_NUMBER() OVER (PARTITION BY lower(trim(email)) ORDER BY created_at DESC, full_name, email)` and keep `winner_rank = 1`.
--    Expected result/shape: For sql-43 Exercise 5, expected output: one row per normalized email with columns `full_name`, `email`, and `country`, ordered by `email`; the course stage has no duplicates, so all 63 rows survive.
--    Verify: For sql-43 Exercise 5, add a second staged row for `customer1@example.com` with an older `created_at` and confirm that the result still has 63 rows and keeps the newer row; without this step, the Exercise 2 upsert fails with SQLSTATE `21000` (`ON CONFLICT DO UPDATE command cannot affect row a second time`).
--    Hint ladder, rung 1: For sql-43 Exercise 5, decide which duplicate should win before loading; `ON CONFLICT` cannot choose between two staged rows for the same key.
-- 6. Edge case: compare source and restored rows with IS DISTINCT FROM so NULL
--    values are compared safely.
--    Inputs: For sql-43 Exercise 6, join `customers_restore_stage` to `customers` by `email` and keep rows where `full_name`, `country`, or `segment` differ according to `IS DISTINCT FROM`.
--    Expected result/shape: For sql-43 Exercise 6, expected output: zero rows with columns `email`, `staged_name`, and `restored_name`, ordered by `s.email`, because the Exercise 2 upsert copied every staged value into `customers`.
--    Verify: For sql-43 Exercise 6, after a savepoint, run `UPDATE customers SET segment = NULL WHERE email = 'customer9@example.com'`, rerun the comparison, and confirm that exactly one row appears; the same check written with `<>` returns no row, because a comparison with NULL is unknown.
--    Hint ladder, rung 1: For sql-43 Exercise 6, `a IS DISTINCT FROM b` treats two NULLs as equal and one NULL as different, so it never returns unknown.
ROLLBACK;
