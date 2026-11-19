# Day 43: Logical Export, Staging, and Restore Checks

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-43**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. The **Course database** panel above the code shows whether the course
   training tables are loaded. Missing tables load automatically before your
   first run (or choose **Load course tables**) and stay loaded for later
   lessons. **Reset training data** restores the original rows only when your
   own changes made results differ; it keeps your saved code and notes.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-43/lesson/workspace/sql/postgres-60day/day43_backup_recovery.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-43
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 42; data quality and validation](day42_data_quality_validation.md)
- **Artifacts:** [learner SQL](../day43_backup_recovery.sql) ·
  [solution reasoning](../solutions/day43_solutions.md) ·
  [executable solution](../solutions/day43_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Logical backup, Staging table, Idempotent merge. Its worked SQL reads or creates `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Use `\copy (SELECT ... WHERE ...) TO ...` from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside `BEGIN`/`ROLLBACK` with an explicit email conflict policy.
The learner script creates an empty staging table shaped like `customers` and
compares the two row counts: 500 against 0 until an import fills the stage.
That comparison is the first check of every restore; keys, types and sample
rows come next.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day43_backup_recovery.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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
2. Restore staged customers with deterministic conflict handling.
   **Inputs/evidence:** For sql-43 Exercise 2, mark one staged row as changed (`full_name || ' [restored]'` for `customer1@example.com`), then load `customers_restore_stage` into `customers` with `INSERT ... SELECT ... ON CONFLICT (email) DO UPDATE` inside the lesson transaction.
   **Expected result/shape:** For sql-43 Exercise 2, expected output: `UPDATE 1` for the staged change, then `INSERT 0 63`, because all 63 staged emails already exist and each conflicting row is updated; the `staged_rows` check returns 63, and `customers` still has 500 rows.
   **Verify:** For sql-43 Exercise 2, confirm that `SELECT full_name FROM customers WHERE email = 'customer1@example.com'` returns `Customer 1 [restored]` and `SELECT COUNT(*) FROM customers` returns 500 inside the transaction; rerun the same upsert and confirm that the row count and values do not change, which is the idempotency evidence.
3. Explain server-side `COPY` versus client-side `\copy`.
   **Inputs/evidence:** For sql-43 Exercise 3, compare server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` with psql's `\copy customers TO 'customers.csv'`, using the course role's privileges and the classroom layout as evidence.
   **Expected result/shape:** For sql-43 Exercise 3, expected output: a short written answer: `COPY ... TO 'file'` runs in the database server process and writes on the server's file system, which needs superuser or `pg_write_server_files`; `\copy` streams the rows to the `psql` client, which writes the file. In the classroom, `psql` runs in a Linux container, so `\copy` writes into the learning volume, not onto your desktop.
   **Verify:** For sql-43 Exercise 3, run the server-side `COPY customers TO '/var/lib/postgresql/customers.csv'` as the course role and confirm that it fails with SQLSTATE `42501` (`permission denied to COPY to a file`), while `COPY (SELECT 1) TO STDOUT` succeeds, because any role may copy to the client stream.
4. Build a deterministic row-count/key-range export manifest.
   **Inputs/evidence:** For sql-43 Exercise 4, summarize `customers` in one manifest row: `'training.customers' AS table_name`, `COUNT(*) AS row_count`, `MIN(customer_id) AS min_key`, `MAX(customer_id) AS max_key`, and `clock_timestamp() AS observed_at`.
   **Expected result/shape:** For sql-43 Exercise 4, expected output: exactly one row with columns `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`: `('training.customers', 500, 1, 500, <timestamp>)` on the course seed.
   **Verify:** For sql-43 Exercise 4, rerun the manifest and confirm that every column except `observed_at` is identical; then compare `row_count` with the number of data lines in an exported CSV of the same table (500).
5. Deduplicate staged emails with an explicit winner rule.
   **Inputs/evidence:** For sql-43 Exercise 5, rank `customers_restore_stage` rows with `ROW_NUMBER() OVER (PARTITION BY lower(trim(email)) ORDER BY created_at DESC, full_name, email)` and keep `winner_rank = 1`.
   **Expected result/shape:** For sql-43 Exercise 5, expected output: one row per normalized email with columns `full_name`, `email`, and `country`, ordered by `email`; the course stage has no duplicates, so all 63 rows survive.
   **Verify:** For sql-43 Exercise 5, add a second staged row for `customer1@example.com` with an older `created_at` and confirm that the result still has 63 rows and keeps the newer row; without this step, the Exercise 2 upsert fails with SQLSTATE `21000` (`ON CONFLICT DO UPDATE command cannot affect row a second time`).
6. Compare source/restored values with `IS DISTINCT FROM`.
   **Inputs/evidence:** For sql-43 Exercise 6, join `customers_restore_stage` to `customers` by `email` and keep rows where `full_name`, `country`, or `segment` differ according to `IS DISTINCT FROM`.
   **Expected result/shape:** For sql-43 Exercise 6, expected output: zero rows with columns `email`, `staged_name`, and `restored_name`, ordered by `s.email`, because the Exercise 2 upsert copied every staged value into `customers`.
   **Verify:** For sql-43 Exercise 6, after a savepoint, run `UPDATE customers SET segment = NULL WHERE email = 'customer9@example.com'`, rerun the comparison, and confirm that exactly one row appears; the same check written with `<>` returns no row, because a comparison with NULL is unknown.

Repeat the staged merge and prove it creates no duplicates.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Use `\copy (SELECT ... WHERE ...) TO ...` from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside `BEGIN`/`ROLLBACK` with an explicit email conflict policy.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

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

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
