# Day 43 — Logical Backup and Recovery Patterns

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 42 — data quality and validation](day42_data_quality_validation.md)
- **Artifacts:** [learner SQL](../day43_backup_recovery.sql) ·
  [solution reasoning](../solutions/day43_solutions.md) ·
  [executable solution](../solutions/day43_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-43 — Backup Recovery** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-43/lesson/workspace/sql/postgres-60day/day43_backup_recovery.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Backup/restore commands are capability-sensitive and are not hidden inside a transaction. Use only the lesson's isolated dump/rehearsal targets, inspect every path first, and treat a successful restore plus verification queries—not merely a created file—as success.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day43_backup_recovery.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day43_backup_recovery.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

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

The worked walkthrough's lesson-specific task is: Use \copy (SELECT ... WHERE ...) TO ... from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside BEGIN/ROLLBACK with an explicit email conflict policy.
The first runnable example has a concrete contract: Example 1 must complete through `psql` with its documented command tag or notice for the lesson evidence named below. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup. Its final projection is the columns written in the final `SELECT`. Reselect the returned key columns from the columns written in the final `SELECT`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day43_backup_recovery.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TEMP TABLE customers_stg (LIKE customers INCLUDING ALL);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must complete through `psql` with its documented command tag or notice for the lesson evidence named below. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

### Example 2

```sql
SELECT 'customers' AS table, COUNT(*) AS base_cnt FROM customers
UNION ALL
SELECT 'customers_stg', COUNT(*) FROM customers_stg;
```

**How to read it:** Example 2: Start with `customers`, and `customers_stg` in `FROM`/`JOIN`; append branches with `UNION ALL` (duplicates are retained). The final `SELECT` displays the columns written in the final `SELECT`. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns exactly one summary row with columns `base_cnt` from `customers`, and `customers_stg`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-43 Exercise 1, read from `training.customers`. Build the answer toward `staged_rows`, and `customers_restore_stage`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-43 Exercise 1, expected output: CSV rows are streamed to the client, and `staged_rows` equals the number of US customers. A real import would create an explicit staging table and run `\copy customers_restore_stage FROM. The final columns are `staged_rows`, and `customers_restore_stage`.
   **Verify:** For sql-43 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `staged_rows`, and `customers_restore_stage` against `training.customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
2. Restore staged customers with deterministic conflict handling.
   **Inputs/evidence:** For sql-43 Exercise 2, use `customers`, and `customers_restore_stage` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-43 Exercise 2, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `full_name`, `email`, `country`, `created_at`, `segment`, and `attributes`.
   **Verify:** For sql-43 Exercise 2, restore into an isolated target and reconcile `customers`, and `customers_restore_stage` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
3. Explain server-side `COPY` versus client-side `\copy`.
   **Inputs/evidence:** For sql-43 Exercise 3, complete the explain server-side copy versus client-side copy written analysis and support its claims with read-only evidence from `customers`, `customers_stg`, and `customers_restore_stage`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-43 Exercise 3, expected output: a completed the explain server-side copy versus client-side copy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `copy`.
   **Verify:** For sql-43 Exercise 3, check the explain server-side copy versus client-side copy written analysis against `copy`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
4. Build a deterministic row-count/key-range export manifest.
   **Inputs/evidence:** For sql-43 Exercise 4, read from `customers`. Build the answer toward `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-43 Exercise 4, expected output: one row per `customer_id`. The final columns are `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`.
   **Verify:** For sql-43 Exercise 4, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
5. Deduplicate staged emails with an explicit winner rule.
   **Inputs/evidence:** For sql-43 Exercise 5, read from `customers_restore_stage`. Build the answer toward `full_name`, `email`, and `country`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-43 Exercise 5, expected output: one row per `country`. The final columns are `full_name`, `email`, and `country`. The final order is `email`.
   **Verify:** For sql-43 Exercise 5, run an anti-check that counts rows where NOT ((winner_rank = 1)); require unique `country` where the expected grain is one row per key and confirm the projected `full_name`, `email`, and `country` against `customers_restore_stage`. Add duplicate source candidates for `country`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
6. Compare source/restored values with `IS DISTINCT FROM`.
   **Inputs/evidence:** For sql-43 Exercise 6, use `customers_restore_stage`, `customers`, `c.country`, and `c.segment` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-43 Exercise 6, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `email`, `staged_name`, and `restored_name`. The final order is `s.email`.
   **Verify:** For sql-43 Exercise 6, restore into an isolated target and reconcile `customers_restore_stage`, `customers`, `c.country`, and `c.segment` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

Repeat the staged merge and prove it creates no duplicates.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Use \copy (SELECT ... WHERE ...) TO ... from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside BEGIN/ROLLBACK with an explicit email conflict policy.
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

Continue to [Day 44 — monitoring and diagnostics](day44_monitoring_diagnostics.md).

## Deep dive and reference

## What you will learn

- Distinguish server-side `COPY` from client-side `psql` `\copy`.
- Restore through a staging table with explicit validation.
- Merge staged customers idempotently with `ON CONFLICT`.

## How the learner script works

The rollback-only SQL creates a temporary `customers_stg` table shaped like
`training.customers`, compares base and staging counts, and leaves file-copy
commands commented because paths and permissions are environment-owned.

`COPY table TO '/path'` reads or writes on the database server and commonly
requires elevated privileges. `\copy` is a `psql` command that reads or writes
on the learner's Windows, macOS, or Linux client.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Environment and safety limits

- The learner must choose a path they own. Windows drive/path syntax, directory
  creation, and permissions cannot be prescribed by the repository.
- Stage first; compare counts, keys, types, and representative rows before
  merging.
- Email is the schema's unique conflict key, but a real restore policy must
  decide which source wins for every column.
- Wrap the merge in `BEGIN`/`ROLLBACK` until the result is reconciled.

Logical export is not point-in-time recovery. Production PITR needs tested base
backups, WAL archiving, retention, encryption, and measured RPO/RTO outside this
SQL-only lesson.

## Expanded practice lab

Prompts 3–6 distinguish server-side `COPY` from client-side psql `\copy`.
`\copy` reads or writes on the learner's machine and normally avoids needing
database-server filesystem access. A useful manifest records scope and counts;
cryptographic file checksums belong to the surrounding backup workflow.

Deduplicate a stage with an explicit winner rule before upsert. Compare restored
columns with `IS DISTINCT FROM`, which treats two NULLs as equal and one NULL as
different—exactly the behavior a reconciliation usually needs.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-43 — Backup Recovery.

I have completed the direct catalog prerequisite: `sql-42`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day43_backup_recovery.md
- Answer-free learner SQL: sql/postgres-60day/day43_backup_recovery.sql

Key terms to teach in context: Logical backup, Staging table, Idempotent merge. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Use \copy (SELECT ... WHERE ...) TO ... from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside BEGIN/ROLLBACK with an explicit email conflict policy.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
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
