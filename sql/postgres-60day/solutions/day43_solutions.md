# Day 43 Solutions: Logical Backup and Recovery


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day43_solutions.sql
```

In our container `psql` printed `BEGIN`, `SET`, a CSV header and 63 data
lines, `SELECT 63` for the stage, `UPDATE 1`, `INSERT 0 63`, a `staged_rows`
value of 63, the one-row manifest, 63 deduplicated rows, an empty comparison
and `ROLLBACK`. That last empty result is the success signal: after the merge,
no staged value differs from `customers`. Your manifest timestamp will differ.
The [solution reading notes](../../STUDY-GUIDE.md#read-a-solution) describe how
to compare your attempt.

## Clause-by-clause reading map

The whole file is one transaction. Read each query in
[logical order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order) and
note what row each step carries:

- The export is `COPY (query) TO STDOUT WITH (FORMAT csv, HEADER true)`. Its
  inner `SELECT` filters `customers` to the 63 US rows and orders them by
  `customer_id`; `COPY` formats that result for the client.
- `CREATE TEMP TABLE customers_restore_stage AS SELECT ...` stands in for the
  later `\copy ... FROM` import. It keeps six columns and drops
  `customer_id`, so `email` is the only key left to match on.
- `UPDATE` marks `customer1@example.com` as changed, giving the merge one real
  difference to restore.
- `INSERT ... SELECT ... ON CONFLICT (email) DO UPDATE` sets `full_name`,
  `country`, `segment` and `attributes` from `EXCLUDED`, the proposed row. It
  leaves `created_at` alone, so a restore does not rewrite signup dates.
- Four reads follow: a stage count, a one-row manifest over `customers`, the
  `staged_duplicates` CTE that ranks each normalized email, and the
  `IS DISTINCT FROM` comparison of the stage with `customers`.

`ROLLBACK` then undoes the stage and the merge; only the consumed sequence
numbers remain.

This day distinguishes client-side export from database recovery logic. The
answer uses `COPY ... TO STDOUT` so it works through the current connection and
models a restore with a temporary staging table. See
[`day43_solutions.sql`](day43_solutions.sql).

## Exercise 1: Export and stage a subset

In interactive `psql`, `\copy` writes on the client machine:

```text
\copy (SELECT * FROM training.customers WHERE country = 'US' ORDER BY customer_id) TO 'customers_us.csv' WITH (FORMAT csv, HEADER true)
```

Replace that filename with a path the learner owns and run the command in a psql
terminal; the classroom's browser modes do not run an added `\copy`. Path
syntax, directory creation, and write permission depend on the machine that runs
psql, so the repository cannot choose or create that destination safely.

The executable solution uses SQL-standard server output instead:

```sql
BEGIN;
SET search_path TO training, public;

COPY (
  SELECT
    customer_id,
    full_name,
    email,
    country,
    created_at,
    segment,
    attributes
  FROM
    customers
  WHERE
    country = 'US'
  ORDER BY
    customer_id)
  TO STDOUT WITH (
    FORMAT csv,
    HEADER true);

CREATE TEMP TABLE customers_restore_stage AS
SELECT
  full_name,
  email,
  country,
  created_at,
  segment,
  attributes
FROM
  customers
WHERE
  country = 'US';

SELECT
  COUNT(*) AS staged_rows
FROM
  customers_restore_stage;

ROLLBACK;
```

Expected shape: CSV rows are streamed to the client, and `staged_rows` equals
the number of US customers. A real import would create an explicit staging
table and run `\copy customers_restore_stage FROM ...`.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 1, export the US subset of `training.customers` with `COPY (SELECT customer_id, full_name, email, country, created_at, segment, attributes FROM customers WHERE country = 'US' ORDER BY customer_id) TO STDOUT WITH (FORMAT csv, HEADER true)`, then model the later `\copy ... FROM` import by creating the temporary table `customers_restore_stage` from the same rows.
- **Expected result/shape:** For sql-43 Exercise 1, expected output: one CSV header line and 63 data lines streamed to the client, ordered by `customer_id`, then `SELECT 63` for the staging table.
- **Independent verification:** For sql-43 Exercise 1, confirm that `SELECT COUNT(*) FROM training.customers WHERE country = 'US'` and `SELECT COUNT(*) FROM customers_restore_stage` both return 63; then confirm that `COPY customers TO STDOUT WHERE country = 'US'` fails with SQLSTATE `42601` (`WHERE clause not allowed with COPY TO`), because only the query form can filter an export.
- **Intermediate relation check:** For sql-43 Exercise 1, run the inner `SELECT ... WHERE country = 'US'` alone and confirm 63 rows before wrapping it in `COPY`.
- **Clause check:** For sql-43 Exercise 1, the solution uses `COPY (SELECT ... WHERE country = 'US' ORDER BY customer_id) TO STDOUT WITH (FORMAT csv, HEADER true)` and `CREATE TEMP TABLE customers_restore_stage AS SELECT ...`.
- **Alternative/trade-off:** For sql-43 Exercise 1, `pg_dump --table=training.customers` exports a whole table with its definition, but it cannot select a row subset; a filtered `COPY` exports data only.
- **Edge case:** The `attributes` JSONB column is quoted in CSV because it contains commas and double quotes; a CSV reader must honour that quoting to import it again.

## Exercise 2: Idempotent restore with conflict handling

Email is the current schema's unique business key for this exercise.

```sql
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE customers_restore_stage AS
SELECT
  full_name,
  email,
  country,
  created_at,
  segment,
  attributes
FROM
  customers
WHERE
  country = 'US';

UPDATE
  customers_restore_stage
SET
  full_name = full_name || ' [restored]'
WHERE
  email = 'customer1@example.com';

INSERT INTO customers (full_name, email, country, created_at, segment, attributes)
SELECT
  full_name,
  email,
  country,
  created_at,
  segment,
  attributes
FROM
  customers_restore_stage
ON CONFLICT (email)
  DO UPDATE SET
    full_name = EXCLUDED.full_name,
    country = EXCLUDED.country,
    segment = EXCLUDED.segment,
    attributes = EXCLUDED.attributes;

ROLLBACK;
```

The transaction proves both insert and update paths while leaving the course
data unchanged.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 2, mark one staged row as changed (`full_name || ' [restored]'` for `customer1@example.com`), then load `customers_restore_stage` into `customers` with `INSERT ... SELECT ... ON CONFLICT (email) DO UPDATE` inside the lesson transaction.
- **Expected result/shape:** For sql-43 Exercise 2, expected output: `UPDATE 1` for the staged change, then `INSERT 0 63`, because all 63 staged emails already exist and each conflicting row is updated; the `staged_rows` check returns 63, and `customers` still has 500 rows.
- **Independent verification:** For sql-43 Exercise 2, confirm that `SELECT full_name FROM customers WHERE email = 'customer1@example.com'` returns `Customer 1 [restored]` and `SELECT COUNT(*) FROM customers` returns 500 inside the transaction; rerun the same upsert and confirm it again reports `INSERT 0 63` with 500 rows and unchanged values, which is the idempotency evidence for the data, while `customers_customer_id_seq` still advances by 63 per run because each proposed row evaluates the `customer_id` default before the conflict is found.
- **Intermediate relation check:** For sql-43 Exercise 2, `SELECT COUNT(*) FROM customers_restore_stage s JOIN customers c USING (email)` returns 63 before the load, which predicts that every staged row will update rather than insert.
- **Clause check:** For sql-43 Exercise 2, the solution uses one `UPDATE customers_restore_stage ...` and one `INSERT INTO customers (...) SELECT ... FROM customers_restore_stage ON CONFLICT (email) DO UPDATE SET ... = EXCLUDED....`.
- **Alternative/trade-off:** For sql-43 Exercise 2, `MERGE INTO customers USING customers_restore_stage ON ... WHEN MATCHED THEN UPDATE WHEN NOT MATCHED THEN INSERT` expresses the same restore and can also handle deletions, but it does not use `ON CONFLICT`'s arbiter index.
- **Edge case:** A staged row whose email is NULL never conflicts, because NULLs are distinct for a `UNIQUE` constraint, so it is inserted as a new customer; filter or reject NULL keys before loading.

## Reasoning, safety, and pitfalls

- `COPY ... TO '/path'` reads or writes on the database server and usually needs
  elevated privileges. `\copy` reads or writes on the `psql` client.
- Restore into staging first; validate counts, keys, types, and representative
  rows before merging into the base table.
- `ON CONFLICT` is idempotent only when the conflict key represents the intended
  entity and update policy.
- Logical export is not point-in-time recovery. Production PITR requires base
  backups plus WAL archiving, which is outside this SQL-only exercise.

## Exercise 3: Choose COPY or backslash-copy

Server-side `COPY` accesses the database server's filesystem. psql `\copy`
streams through the client, which is usually the appropriate learner-machine
workflow.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 3, compare server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` with psql's `\copy customers TO 'customers.csv'`, using the course role's privileges and the classroom layout as evidence.
- **Expected result/shape:** For sql-43 Exercise 3, expected output: a short written answer: `COPY ... TO 'file'` runs in the database server process and writes on the server's file system, which needs superuser or `pg_write_server_files`; `\copy` streams the rows to the `psql` client, which writes the file. In the classroom, `psql` runs in a Linux container, so `\copy` writes into the learning volume, not onto your desktop.
- **Independent verification:** For sql-43 Exercise 3, run the server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` as the course role (a non-superuser without `pg_write_server_files`) and confirm that it fails with SQLSTATE `42501` (`permission denied to COPY to a file`), while `COPY (SELECT 1) TO STDOUT` succeeds, because any role may copy to the client stream; a superuser session may be allowed to write the file, so it is not valid evidence.
- **Intermediate relation check:** For sql-43 Exercise 3, `SELECT pg_has_role(current_user, 'pg_write_server_files', 'MEMBER')` returns `false` for the course role, which predicts the permission error.
- **Clause check:** For sql-43 Exercise 3, the evidence is the same `COPY` statement aimed at a server path and at `STDOUT`; the answer itself is written prose.
- **Alternative/trade-off:** For sql-43 Exercise 3, granting `pg_write_server_files` would let the server write files, but it gives a role access to the server's file system; `\copy` keeps the file on the client side without that privilege.
- **Edge case:** `\copy` paths are resolved on the machine that runs `psql`, so the same path can work in one terminal and fail in another; the classroom's browser modes do not run an added `\copy` at all.

## Exercise 4: Build a manifest

The manifest records table, count, key range, and observation time. Production
automation should also hash the exported file outside SQL.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 4, summarize `customers` in one manifest row: `'training.customers' AS table_name`, `COUNT(*) AS row_count`, `MIN(customer_id) AS min_key`, `MAX(customer_id) AS max_key`, and `clock_timestamp() AS observed_at`.
- **Expected result/shape:** For sql-43 Exercise 4, expected output: exactly one row with columns `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`: `('training.customers', 500, 1, 500, <timestamp>)` on the course seed.
- **Independent verification:** For sql-43 Exercise 4, rerun the manifest and confirm that every column except `observed_at` is identical; then compare `row_count` with the number of data lines in an exported CSV of the same table (500).
- **Intermediate relation check:** For sql-43 Exercise 4, `SELECT COUNT(DISTINCT customer_id) FROM customers` also returns 500, so `min_key` and `max_key` bound a gap-free key range on this seed.
- **Clause check:** For sql-43 Exercise 4, the solution uses one aggregate `SELECT` with `COUNT(*)`, `MIN(customer_id)`, `MAX(customer_id)`, and `clock_timestamp()`, and no `GROUP BY`.
- **Alternative/trade-off:** For sql-43 Exercise 4, adding `md5(string_agg(customer_id::text, ',' ORDER BY customer_id))` gives a content fingerprint of the key set, which detects swapped keys that the minimum and maximum cannot.
- **Edge case:** `clock_timestamp()` changes between calls even inside one transaction; use `now()` when the manifest must record the transaction's start time instead.

## Exercise 5: Deduplicate deterministically

`ROW_NUMBER` partitions by normalized email and orders by an explicit newest/
tie-break policy. Upsert never receives arbitrary duplicate winners.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 5, rank `customers_restore_stage` rows with `ROW_NUMBER() OVER (PARTITION BY lower(trim(email)) ORDER BY created_at DESC, full_name, email)` and keep `winner_rank = 1`.
- **Expected result/shape:** For sql-43 Exercise 5, expected output: one row per normalized email with columns `full_name`, `email`, and `country`, ordered by `email`; the course stage has no duplicates, so all 63 rows survive.
- **Independent verification:** For sql-43 Exercise 5, add a second staged row for `customer1@example.com` with an older `created_at` and confirm that the result still has 63 rows and keeps the newer row; without this step, the Exercise 2 upsert fails with SQLSTATE `21000` (`ON CONFLICT DO UPDATE command cannot affect row a second time`).
- **Intermediate relation check:** For sql-43 Exercise 5, `SELECT lower(trim(email)), COUNT(*) FROM customers_restore_stage GROUP BY 1 HAVING COUNT(*) > 1` lists the duplicate keys before ranking; it is empty on the course stage.
- **Clause check:** For sql-43 Exercise 5, the solution uses a `staged_duplicates` CTE with `ROW_NUMBER() OVER (PARTITION BY lower(trim(email)) ORDER BY created_at DESC, full_name, email)`, an outer `WHERE winner_rank = 1`, and `ORDER BY email`.
- **Alternative/trade-off:** For sql-43 Exercise 5, `SELECT DISTINCT ON (lower(trim(email))) ... ORDER BY lower(trim(email)), created_at DESC, full_name, email` keeps the same winners in PostgreSQL-specific syntax.
- **Edge case:** The `email` sort order follows the database collation (`en_US.utf8`), so `customer105@example.com` sorts before `customer17@example.com`; add `COLLATE "C"` when byte order matters.

## Exercise 6: Compare NULL safely

`IS DISTINCT FROM` treats two NULLs as equal and one NULL as different. It
therefore reports real source/restore differences without UNKNOWN results.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 6, join `customers_restore_stage` to `customers` by `email` and keep rows where `full_name`, `country`, or `segment` differ according to `IS DISTINCT FROM`.
- **Expected result/shape:** For sql-43 Exercise 6, expected output: zero rows with columns `email`, `staged_name`, and `restored_name`, ordered by `s.email`, because the Exercise 2 upsert copied every staged value into `customers`.
- **Independent verification:** For sql-43 Exercise 6, after a savepoint, run `UPDATE customers SET segment = NULL WHERE email = 'customer9@example.com'`, rerun the comparison, and confirm that exactly one row appears; the same check written with `<>` returns no row, because a comparison with NULL is unknown.
- **Intermediate relation check:** For sql-43 Exercise 6, the join alone returns 63 rows, one per staged email; the `WHERE` clause then keeps only the rows with a real difference.
- **Clause check:** For sql-43 Exercise 6, the solution uses `FROM customers_restore_stage s JOIN customers c USING (email)`, a `WHERE` with three `IS DISTINCT FROM` comparisons joined by `OR`, and `ORDER BY s.email`.
- **Alternative/trade-off:** For sql-43 Exercise 6, `(SELECT full_name, email, country, segment FROM customers_restore_stage) EXCEPT (SELECT full_name, email, country, segment FROM customers)` also treats NULLs as equal, but it reports only the staged side of each difference.
- **Edge case:** A staged email that is missing from `customers` disappears from this inner join; reconcile missing keys separately with a `LEFT JOIN ... WHERE c.email IS NULL`.
