# Day 38 — Transactions and Isolation Levels

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 37 — partitioning and sharding](day37_partitioning_sharding.md)
- **Artifacts:** [learner SQL](../day38_transactions_isolation.sql) ·
  [solution reasoning](../solutions/day38_solutions.md) ·
  [executable solution](../solutions/day38_solutions.sql)

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

2. Open **SQL-38 — Transactions Isolation** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-38/day38_transactions_isolation.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

The full learner file demonstrates the safe single-session part. For the manual concurrency prompts, open **two separate** `psql` terminals connected to `advanced_sql_training`, label them Session A and Session B, and follow the statement schedule exactly. Temporary tables are session-local, so use only the regular disposable table named by the exercise and clean it up when both sessions finish.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day38_transactions_isolation.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day38_transactions_isolation.sql
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
MVCC, Isolation level, Serialization failure. Its worked SQL reads or creates `txn_demo`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Open two disposable sessions and write down each statement before running it. Under READ COMMITTED, have session A read a count, session B commit a matching insert, and session A read again. Repeat at REPEATABLE READ and explain the snapshot difference; clean up the shared disposable table afterward.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day38_transactions_isolation.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TEMP TABLE txn_demo(id int PRIMARY KEY, qty int);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
INSERT INTO txn_demo VALUES (1, 10), (2, 20), (3, 30);
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Reproduce isolation behavior with an explicit two-session statement schedule.
- Treat serialization failures as a signal to retry the complete transaction.

## Vocabulary and concepts

- **MVCC:** multi-version concurrency control, which serves rows from
  transaction snapshots.
- **Isolation level:** the visibility and anomaly guarantees for a transaction.
- **Serialization failure:** SQLSTATE `40001`, requiring a whole-unit retry.

## Worked example / walkthrough

Open two disposable sessions and write down each statement before running it.
Under `READ COMMITTED`, have session A read a count, session B commit a matching
insert, and session A read again. Repeat at `REPEATABLE READ` and explain the
snapshot difference; clean up the shared disposable table afterward.

## Exercises

Complete these in the [learner SQL](../day38_transactions_isolation.sql):

1. Reproduce a non-repeatable read under `READ COMMITTED`.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. Reproduce a phantom with two counts and a concurrent insert.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Cause/retry a `SERIALIZABLE` failure.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. Predict savepoint state after `ROLLBACK TO SAVEPOINT`.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. Build an atomic checked transfer between two temp accounts.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
6. Recover after a unique-key error at a savepoint.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. Explain an isolation choice for a multi-query read-only report.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

Record exact two-session ordering and SQLSTATEs.

## Self-check

- Are you using a regular disposable table rather than a session-local
  temporary table for cross-session work?
- Would retry logic restart every read and write in the transaction?

## Next step

Continue to [Day 39 — locks and deadlocks](day39_locks_deadlocks.md).

## Deep dive and reference

## What you will learn

- Use transactions and savepoints for atomic, recoverable work.
- Reproduce non-repeatable reads and phantoms with two sessions.
- Observe and retry serialization failures.

## How the learner script works

The single-session portion shows the current isolation level, switches its
transaction to `REPEATABLE READ`, creates a temporary quantity table, and rolls
an update back to a savepoint.

PostgreSQL uses MVCC snapshots:

- `READ COMMITTED` takes a new snapshot for each statement.
- `REPEATABLE READ` keeps one transaction snapshot, so repeated reads do not see
  later commits; serialization anomalies can still occur.
- `SERIALIZABLE` adds conflict tracking and can abort a transaction with SQLSTATE
  `40001`; the application must retry the entire transaction.

## Practice — match the learner prompts exactly

1. In two sessions, reproduce a non-repeatable read under `READ COMMITTED`.
2. In two sessions, run `SELECT COUNT(*)`, commit a matching insert elsewhere,
   and run the count again to demonstrate a phantom under `READ COMMITTED`.
3. Run conflicting read/modify/write transactions at `SERIALIZABLE`; observe
   which transaction PostgreSQL aborts and retry it from `BEGIN`.

## Important two-session limitation

`txn_demo` is a temporary table and is visible only to the session that created
it. A second terminal cannot update it. For the manual exercises, create a
regular, uniquely named disposable table in `training`, use it from both
sessions, then drop it after both transactions end. Do not run the contention
demo against important shared rows.

## Pitfalls and validation

- Keep transactions short; old snapshots delay vacuum cleanup.
- A savepoint rolls back part of one transaction, not another session's commit.
- Retry the whole serializable unit of work, not only the statement that failed.
- Record the exact statement order in both terminals so the anomaly is
  reproducible.

## Expanded practice lab

Prompts 4–7 add single-session recovery patterns to the concurrency exercises.
After `ROLLBACK TO SAVEPOINT`, PostgreSQL keeps that savepoint available until
it is released or the transaction ends. This is why error recovery must first
return to a valid savepoint before more statements run.

For the transfer, lock/check/update both balances as one transaction and verify
that total money is unchanged. A multi-query read-only report can still need
`REPEATABLE READ` when all results must describe one consistent snapshot.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-38 — Transactions Isolation.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day38_transactions_isolation.md
- Answer-free learner SQL: sql/postgres-60day/day38_transactions_isolation.sql

The lesson concepts include MVCC, Isolation level, Serialization failure. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Open two disposable sessions and write down each statement before running it. Under READ COMMITTED, have session A read a count, session B commit a matching insert, and session A read again. Repeat at REPEATABLE READ and explain the snapshot difference; clean up the shared disposable table afterward.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-38/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
