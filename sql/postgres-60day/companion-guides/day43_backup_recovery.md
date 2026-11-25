# Day 43: Logical Export, Staging, and Restore Checks

## How to run this lesson

In `./classroom`, choose PostgreSQL, open **sql-43** and run it with
**Whole SQL lesson (psql)** against `advanced_sql_training`. The script opens
`BEGIN`, creates an empty temporary `customers_stg` table shaped like
`customers`, prints a two-row count comparison and ends with `ROLLBACK`, so
nothing it builds outlives the run. Its file-copy lines are comments: a
server-side `COPY ... TO '/path'` fails for the course role, and a `\copy`
needs a path on the machine that runs `psql`. Your editable copy is
`.learning/sql/sql-43/lesson/workspace/sql/postgres-60day/day43_backup_recovery.sql`
in the Docker learning volume. In our private PostgreSQL 17 container the
transcript was `BEGIN`, `SET`, `CREATE TABLE`, the rows `customers 500` and
`customers_stg 0`, then `ROLLBACK`. Whole-lesson mode prints anything you add
as `COPY (query) TO STDOUT` straight into that transcript, which is how this
lesson exports without touching a file. It will not run an added `\copy`:
the classroom rejects any change to the file's psql meta-commands, so practice
that command in a `psql` terminal. Setup and resume live in the
[classroom launch steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom);
JupyterLab users can take the
[contributor notebook path](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
instead.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 42; data quality and validation](day42_data_quality_validation.md) Day 42's normalized-email duplicate report returns here as the `lower(trim(email))` key that decides which staged row wins before a merge.
- **Artifacts:** [learner SQL](../day43_backup_recovery.sql) ·
  [solution reasoning](../solutions/day43_solutions.md) ·
  [executable solution](../solutions/day43_solutions.sql)

## A beginner's mental model for this lesson

A restore has three stages, and this lesson gives each one a name. A
**Logical backup** stores rows as data records rather than disk pages: here,
the 63 US customers written as CSV lines with a header, one line per
`customer_id`. A **Staging table** is where those records land first, a private
copy you can count and inspect before any of it reaches `customers`. The
learner's `customers_stg` copies the full definition of `customers`, while the
solution's `customers_restore_stage` keeps six columns and drops
`customer_id`. An **Idempotent merge** loads the stage with a rule for rows
that already exist, so running it twice leaves the same table as running it
once. The solution's rule is `ON CONFLICT (email) DO UPDATE`: our second run
printed the same `INSERT 0 63`, and `customers` stayed at 500 rows.

Before writing anything, say what one row means at each stage: one customer in
the CSV, one customer in the stage, one customer in `customers` matched by
`email`. Every check in this lesson compares those three, by count first, then
by keys, then by values.

Read the queries inside the export and the checks in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
In `COPY (SELECT ... FROM customers WHERE country = 'US' ORDER BY
customer_id) TO STDOUT`, the inner query runs first (`FROM`, then `WHERE`,
then the seven selected columns, then `ORDER BY`), and `COPY` only formats the
finished result as CSV. In the final comparison, `FROM ... JOIN ... USING
(email)` pairs each staged row with its restored row (63 pairs) before `WHERE`
keeps the pairs that differ.

## Two worked SQL examples

Both excerpts come from `day43_backup_recovery.sql` and run between its
`BEGIN` and `ROLLBACK`, after `SET search_path TO training, public`, so
`customers` resolves to `training.customers` and the temporary stage lives in
your session's own `pg_temp` schema. Example 1 builds the empty landing table;
Example 2 is the first check to run after any import into it.

### Example 1: an empty stage with the target's shape

```sql
CREATE TEMP TABLE customers_stg (
  LIKE customers INCLUDING ALL
);
```

**How to read it:** `LIKE customers INCLUDING ALL` copies the column names and
types, `NOT NULL` rules, defaults, check constraints and indexes, including the
primary key and the unique index on `email`. It copies no rows. `TEMP` keeps the
stage private to this session, and the script's final `ROLLBACK` removes it.

**Expected result/shape:** the command tag `CREATE TABLE`. The copied default for
`customer_id` is still `nextval('customers_customer_id_seq')`, so inserting into
the stage without supplying `customer_id` consumes numbers from the real table's
sequence; a restore stage should carry the source keys explicitly.

### Example 2: compare base and stage counts

```sql
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
```

**How to read it:** each branch of `UNION ALL` returns one count row, and the
label column names which relation was counted. The first branch's aliases name
the result columns, `table` and `base_cnt`, for both rows.

**Expected result/shape:** two rows: `('customers', 500)` and
`('customers_stg', 0)`. After an import, the second count must equal the number
of data lines in the file; a difference means rows were rejected or the file
holds a different scope.

## Learning objectives

- Stage and validate a logical extract before merging it.
- Choose between server-side `COPY` and client-side `psql` `\copy`.

## Vocabulary and concepts

- **Logical backup:** a representation of database objects or rows as SQL or
  data records.
- **Staging table:** an isolated landing relation used for validation.
- **Idempotent merge:** a repeatable load with a defined conflict policy.

## Worked example / walkthrough

Use `\copy (SELECT ... WHERE ...) TO ...` from a path owned by the learner,
import into a staging table, and compare count, keys, types, and sample rows.
Only then merge inside `BEGIN`/`ROLLBACK` with an explicit email conflict
policy.

## Exercises

Complete these in the [learner SQL](../day43_backup_recovery.sql):

1. Export/import a filtered subset with `COPY (...)` or psql `\copy`.
   **Inputs/evidence:** For sql-43 Exercise 1, export the US subset of `training.customers` with `COPY (SELECT customer_id, full_name, email, country, created_at, segment, attributes FROM customers WHERE country = 'US' ORDER BY customer_id) TO STDOUT WITH (FORMAT csv, HEADER true)`, then model the later `\copy ... FROM` import by creating the temporary table `customers_restore_stage` from the same rows.
   **Expected result/shape:** For sql-43 Exercise 1, expected output: one CSV header line and 63 data lines streamed to the client, ordered by `customer_id`, then `SELECT 63` for the staging table.
   **Verify:** For sql-43 Exercise 1, confirm that `SELECT COUNT(*) FROM training.customers WHERE country = 'US'` and `SELECT COUNT(*) FROM customers_restore_stage` both return 63; then confirm that `COPY customers TO STDOUT WHERE country = 'US'` fails with SQLSTATE `42601` (`WHERE clause not allowed with COPY TO`), because only the query form can filter an export.
   **Data check:** In our container the export printed the header and 63 data lines for `customer_id` 1, 9, 17 and so on to 497, every eighth id. All 63 have segment `standard`, and the JSON in `attributes` arrives wrapped in double quotes with its inner quotes doubled, as in `"{""channel"": ""web"", ""referrer"": ""seo""}"`. The stage then reported `SELECT 63`, the tag `CREATE TABLE ... AS` prints. US is one of four countries with 63 customers (CA, DE and GB are the others; the remaining four have 62), so a count alone would not catch a wrong country. `COPY customers TO STDOUT WHERE country = 'US'` failed with `WHERE clause not allowed with COPY TO`.
2. Restore staged customers with deterministic conflict handling.
   **Inputs/evidence:** For sql-43 Exercise 2, mark one staged row as changed (`full_name || ' [restored]'` for `customer1@example.com`), then load `customers_restore_stage` into `customers` with `INSERT ... SELECT ... ON CONFLICT (email) DO UPDATE` inside the lesson transaction.
   **Expected result/shape:** For sql-43 Exercise 2, expected output: `UPDATE 1` for the staged change, then `INSERT 0 63`, because all 63 staged emails already exist and each conflicting row is updated; the `staged_rows` check returns 63, and `customers` still has 500 rows.
   **Verify:** For sql-43 Exercise 2, confirm that `SELECT full_name FROM customers WHERE email = 'customer1@example.com'` returns `Customer 1 [restored]` and `SELECT COUNT(*) FROM customers` returns 500 inside the transaction; rerun the same upsert and confirm it again reports `INSERT 0 63` with 500 rows and unchanged values, which is the idempotency evidence for the data, while `customers_customer_id_seq` still advances by 63 per run because each proposed row evaluates the `customer_id` default before the conflict is found.
   **Data check:** Our run printed `UPDATE 1`, `INSERT 0 63` and a `staged_rows` value of 63, and a second identical upsert printed `INSERT 0 63` again with `customers` still at 500 rows. One thing did not repeat: each run advanced `customers_customer_id_seq` by 63. `INSERT` evaluates the `customer_id` default for every proposed row before it finds the email conflict, and `ROLLBACK` does not give sequence numbers back, so gaps in future ids are expected.
3. Explain server-side `COPY` versus client-side `\copy`.
   **Inputs/evidence:** For sql-43 Exercise 3, compare server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` with psql's `\copy customers TO 'customers.csv'`, using the course role's privileges and the classroom layout as evidence.
   **Expected result/shape:** For sql-43 Exercise 3, expected output: a short written answer: `COPY ... TO 'file'` runs in the database server process and writes on the server's file system, which needs superuser or `pg_write_server_files`; `\copy` streams the rows to the `psql` client, which writes the file. In the classroom, `psql` runs in a Linux container, so `\copy` writes into the learning volume, not onto your desktop.
   **Verify:** For sql-43 Exercise 3, run the server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` as the course role (a non-superuser without `pg_write_server_files`) and confirm that it fails with SQLSTATE `42501` (`permission denied to COPY to a file`), while `COPY (SELECT 1) TO STDOUT` succeeds, because any role may copy to the client stream; a superuser session may be allowed to write the file, so it is not valid evidence.
   **Data check:** In our container we created a non-superuser role inside a rolled-back transaction and switched to it. `pg_has_role(current_user, 'pg_write_server_files', 'MEMBER')` returned `f`, the server-side `COPY` failed with `permission denied to COPY to a file`, and the server's own hint read "Anyone can COPY to stdout or from stdin. psql's \copy command also works for anyone." `COPY (SELECT 1) TO STDOUT` printed `1`. Run this check as the course role; a superuser may be allowed to write the file.
4. Build a deterministic row-count/key-range export manifest.
   **Inputs/evidence:** For sql-43 Exercise 4, summarize `customers` in one manifest row: `'training.customers' AS table_name`, `COUNT(*) AS row_count`, `MIN(customer_id) AS min_key`, `MAX(customer_id) AS max_key`, and `clock_timestamp() AS observed_at`.
   **Expected result/shape:** For sql-43 Exercise 4, expected output: exactly one row with columns `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`: `('training.customers', 500, 1, 500, <timestamp>)` on the course seed.
   **Verify:** For sql-43 Exercise 4, rerun the manifest and confirm that every column except `observed_at` is identical; then compare `row_count` with the number of data lines in an exported CSV of the same table (500).
   **Data check:** Our manifest row was `training.customers`, 500, 1, 500 and an `observed_at` with microseconds, and a rerun changed only `observed_at`. `max_key` stayed at 500 even after the upserts had pushed the sequence past it, because the merge updated rows rather than inserting them: the manifest describes the data, not the sequence.
5. Deduplicate staged emails with an explicit winner rule.
   **Inputs/evidence:** For sql-43 Exercise 5, rank `customers_restore_stage` rows with `ROW_NUMBER() OVER (PARTITION BY lower(trim(email)) ORDER BY created_at DESC, full_name, email)` and keep `winner_rank = 1`.
   **Expected result/shape:** For sql-43 Exercise 5, expected output: one row per normalized email with columns `full_name`, `email`, and `country`, ordered by `email`; the course stage has no duplicates, so all 63 rows survive.
   **Verify:** For sql-43 Exercise 5, add a second staged row for `customer1@example.com` with an older `created_at` and confirm that the result still has 63 rows and keeps the newer row; without this step, the Exercise 2 upsert fails with SQLSTATE `21000` (`ON CONFLICT DO UPDATE command cannot affect row a second time`).
   **Data check:** Our run listed 63 rows. The `Customer 1 [restored]` row came 14th, between `customer193@example.com` and `customer201@example.com`, and `customer9@example.com` came last: the `en_US.utf8` collation passes over the `@` and puts digits before letters. With a second `customer1@example.com` row dated one year earlier, the stage held 64 rows, the result still had 63, and the kept row carried the newer `created_at` (2026-10-08 23:00 UTC). The same duplicate sent straight to the second exercise's upsert failed with `ON CONFLICT DO UPDATE command cannot affect row a second time`.
6. Compare source/restored values with `IS DISTINCT FROM`.
   **Inputs/evidence:** For sql-43 Exercise 6, join `customers_restore_stage` to `customers` by `email` and keep rows where `full_name`, `country`, or `segment` differ according to `IS DISTINCT FROM`.
   **Expected result/shape:** For sql-43 Exercise 6, expected output: zero rows with columns `email`, `staged_name`, and `restored_name`, ordered by `s.email`, because the Exercise 2 upsert copied every staged value into `customers`.
   **Verify:** For sql-43 Exercise 6, after a savepoint, run `UPDATE customers SET segment = NULL WHERE email = 'customer9@example.com'`, rerun the comparison, and confirm that exactly one row appears; the same check written with `<>` returns no row, because a comparison with NULL is unknown.
   **Data check:** Our run returned zero rows. After a savepoint and `UPDATE customers SET segment = NULL WHERE email = 'customer9@example.com'`, it returned one row: `customer9@example.com`, `Customer 9`, `Customer 9`. Both names match because the difference is in `segment`, which the three output columns do not show. The `<>` version counted 0 rows.

Repeat the staged merge and prove it creates no duplicates.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** reading `INSERT 0 63` as 63 new
  customers. With `ON CONFLICT ... DO UPDATE` the tag counts rows inserted or
  updated; here all 63 emails already existed, every row was updated and
  `customers` stayed at 500. Check the table count, not the tag.
- **`WHERE clause not allowed with COPY TO`:** `COPY table` exports the whole
  table. Put the filter in a query, `COPY (SELECT ... WHERE country = 'US')
  TO STDOUT`, or use `\copy` with the same query in a `psql` terminal.
- **`permission denied to COPY to a file`:** a server-side path needs
  `pg_write_server_files`. Export to `STDOUT` or with `\copy`; do not ask for
  the role.
- **`ON CONFLICT DO UPDATE command cannot affect row a second time`:** the
  stage holds two rows for one email. Pick a winner with the fifth exercise's
  `ROW_NUMBER()` rule and load only `winner_rank = 1`.
- **A comparison that misses a `NULL`:** `<>` returns unknown when one side is
  `NULL`, so a value restored as `NULL` slips through. Use `IS DISTINCT FROM`.
- **Gaps in new `customer_id` values:** each upsert run consumed 63 sequence
  numbers even though it inserted nothing, and a rollback keeps them consumed.
  That is expected, not lost data.
- **`psql` stopped partway:** fix the first error and rerun the whole file
  from `BEGIN`; the
  [failure recovery checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  covers container and path problems.

## Self-check

- Is the file path interpreted on the intended client or database server?
- Are validation and conflict ownership defined before any persistent restore?

## Next step

Continue to [Day 44; monitoring and diagnostics](day44_monitoring_diagnostics.md).

## Deep dive and reference

## What you will learn

- Distinguish server-side `COPY` from client-side `psql` `\copy`.
- Restore through a staging table with explicit validation.
- Merge staged customers idempotently with `ON CONFLICT`.

## How the learner script works

The rollback-only SQL creates a temporary `customers_stg` table shaped like
`training.customers`, compares base and staging counts, and leaves file-copy
commands commented because paths and permissions are environment-owned.

`COPY table TO '/path'` reads or writes on the database server's file system and
requires superuser or the `pg_write_server_files` role; the course role gets
SQLSTATE `42501`. `\copy` is a `psql` command that reads or writes files on the
machine where `psql` runs. In the classroom, run `COPY (query) TO STDOUT` in
whole-lesson mode, which prints the rows in the transcript; the SQL pad's driver
cannot run `COPY`. Neither browser mode runs a `\copy` you add (the pad rejects
psql directives, and whole-lesson mode keeps the lesson's psql commands fixed),
so practice `\copy` in a psql terminal.

This lesson exports rows, not whole databases. A complete logical backup uses
`pg_dump -Fc`, and `pg_restore --list` shows what an archive contains before
anything is restored; [sql-ops-02](../../professional/companion-guides/sql_ops_02_backup_restore_recovery.md)
rehearses that workflow. PostgreSQL 17 also adds
`COPY ... FROM ... WITH (ON_ERROR ignore, LOG_VERBOSITY verbose)`, which skips
rows whose values cannot be converted to the column types and reports each
skipped row as a `NOTICE`; count the skipped rows before trusting the load.

## Practice map

The six numbered exercises above are the practice set, and four of them share
one stage. Build `customers_restore_stage` in the first exercise and keep it
for the second, fifth and sixth, all inside one `BEGIN`/`ROLLBACK` as the
solution does. The third is a written answer backed by two `COPY` statements,
and the fourth reads only `customers`. Several checks change data on purpose:
a duplicate staged email in the fifth, a `NULL` segment in the sixth. Put each
one after a `SAVEPOINT` and `ROLLBACK TO` it afterwards, so the later checks
still see 63 staged rows and an unchanged table.

## Environment and safety limits

- The browser modes do not run an added `\copy`. In a psql terminal, choose a
  path you own; directory creation and permissions belong to the machine that
  runs `psql`.
- Stage first; compare counts, keys, types, and representative rows before
  merging.
- Email is the schema's unique conflict key, but a real restore policy must
  decide which source wins for every column.
- Wrap the merge in `BEGIN`/`ROLLBACK` until the result is reconciled.

Logical export is not point-in-time recovery. Production PITR needs tested base
backups, WAL archiving, retention, encryption, and measured RPO/RTO outside this
SQL-only lesson.

## Expanded practice lab

Prompts 3 to 6 distinguish server-side `COPY` from client-side psql `\copy`.
`\copy` reads or writes files where `psql` runs (a psql terminal, not the
browser) and needs no database-server file access. A useful manifest records scope and counts;
cryptographic file checksums belong to the surrounding backup workflow.

Deduplicate a stage with an explicit winner rule before upsert. Compare restored
columns with `IS DISTINCT FROM`, which treats two NULLs as equal and one NULL as
different, exactly the behavior a reconciliation usually needs.

## Ask an AI tutor about this lesson

A tutor is optional; this guide, the learner file and PostgreSQL are enough
for Day 43. The
[tutor section of the study guide](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
lists what to share. The course data is clean, so the useful practice is with
messy imports: ask for a short invented CSV of customers with a repeated email
in different case, a missing email and a malformed date, and predict what the
stage, the winner rule and the upsert do with each line before checking. Ask it
this after your stage holds the 63 US rows:

```text
Tutor me through sql-43: Logical Export, Staging, and Restore Checks.

I have completed the direct catalog prerequisite: `sql-42`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day43_backup_recovery.md
- Answer-free learner SQL: sql/postgres-60day/day43_backup_recovery.sql

Key terms to teach in context: Logical backup, Staging table, Idempotent merge. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Use `\copy (SELECT ... WHERE ...) TO ...` from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside `BEGIN`/`ROLLBACK` with an explicit email conflict policy.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-43/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
