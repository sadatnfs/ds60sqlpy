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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-43/day43_backup_recovery.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Logical backup, Staging table, Idempotent merge. Its worked SQL reads or creates `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Use \copy (SELECT ... WHERE ...) TO ... from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside BEGIN/ROLLBACK with an explicit email conflict policy.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day43_backup_recovery.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TEMP TABLE customers_stg (LIKE customers INCLUDING ALL);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT 'customers' AS table, COUNT(*) AS base_cnt FROM customers
UNION ALL
SELECT 'customers_stg', COUNT(*) FROM customers_stg;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Restore staged customers with deterministic conflict handling.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Explain server-side `COPY` versus client-side `\copy`.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Build a deterministic row-count/key-range export manifest.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Deduplicate staged emails with an explicit winner rule.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Compare source/restored values with `IS DISTINCT FROM`.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

Repeat the staged merge and prove it creates no duplicates.

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

## Practice — match the learner prompts exactly

1. Export and import a filtered customer subset. A SQL `COPY table` cannot add a
   `WHERE` clause, so use `\copy (SELECT ...) TO ...` and the corresponding
   staged import.
2. In a transaction, restore staged customers into `training.customers` and use
   `ON CONFLICT (email) DO UPDATE` for the reviewed attributes.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day43_backup_recovery.md
- Answer-free learner SQL: sql/postgres-60day/day43_backup_recovery.sql

The lesson concepts include Logical backup, Staging table, Idempotent merge. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Use \copy (SELECT ... WHERE ...) TO ... from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside BEGIN/ROLLBACK with an explicit email conflict policy.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-43/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
