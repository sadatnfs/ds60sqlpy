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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-38/lesson/workspace/sql/postgres-60day/day38_transactions_isolation.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is MVCC, Isolation level, Serialization failure. Its worked SQL reads or creates `txn_demo`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Open two disposable sessions and write down each statement before running it. Under READ COMMITTED, have session A read a count, session B commit a matching insert, and session A read again. Repeat at REPEATABLE READ and explain the snapshot difference; clean up the shared disposable table afterward.
The first runnable example has a concrete contract: Example 1 must complete through `psql` with its documented command tag or notice for the lesson evidence named below. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup. Its final projection is the columns written in the final `SELECT`. Reselect the returned key columns from the columns written in the final `SELECT`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day38_transactions_isolation.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TEMP TABLE txn_demo(id int PRIMARY KEY, qty int);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must complete through `psql` with its documented command tag or notice for the lesson evidence named below. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

### Example 2

```sql
INSERT INTO txn_demo VALUES (1, 10), (2, 20), (3, 30);
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** Example 2 must complete through `psql` with its documented command tag or notice for `txn_demo`. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

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
   **Inputs/evidence:** For sql-38 Exercise 1, read from `isolation_lab`. Build the answer toward `qty`; keep `qty` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-38 Exercise 1, expected output: one row per `qty`. The final columns are `qty`.
   **Verify:** For sql-38 Exercise 1, run an anti-check that counts rows where NOT ((id = 1)); require unique `qty` where the expected grain is one row per key and confirm the projected `qty` against `isolation_lab`. Add one row for which `(id = 1)` is true and one for which it is false; verify only the matching `qty` value is returned.
2. Reproduce a phantom with two counts and a concurrent insert.
   **Inputs/evidence:** For sql-38 Exercise 2, read the target keys from `training.isolation_lab` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-38 Exercise 2, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
   **Verify:** For sql-38 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `training.isolation_lab` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
3. Cause/retry a `SERIALIZABLE` failure.
   **Inputs/evidence:** For sql-38 Exercise 3, read from `training.isolation_lab`. Build the answer toward `serializable`; keep `serializable` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-38 Exercise 3, expected output: one row per `serializable`. The final columns are `serializable`.
   **Verify:** For sql-38 Exercise 3, run an anti-check that counts rows where NOT ((id = 1) OR (id = 2) OR (id >= 3)); require unique `serializable` where the expected grain is one row per key and confirm the projected `serializable` against `training.isolation_lab`. Add one row for which `(id = 1) OR (id = 2) OR (id >= 3)` is true and one for which it is false; verify only the matching `serializable` value is returned.
4. Predict savepoint state after `ROLLBACK TO SAVEPOINT`.
   **Inputs/evidence:** For sql-38 Exercise 4, read from `isolation_solution`. Build the answer toward `release`; keep `release` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-38 Exercise 4, expected output: one row per `release`. The final columns are `release`. The final order is `id`.
   **Verify:** For sql-38 Exercise 4, run an anti-check that counts rows where NOT ((id = 2)); require unique `release` where the expected grain is one row per key and confirm the projected `release` against `isolation_solution`. Add one row for which `(id = 2)` is true and one for which it is false; verify only the matching `release` value is returned.
5. Build an atomic checked transfer between two temp accounts.
   **Inputs/evidence:** For sql-38 Exercise 5, read from `transfer_accounts`. Build the answer toward `available`; keep `available` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-38 Exercise 5, expected output: one row per `available`. The final columns are `available`.
   **Verify:** For sql-38 Exercise 5, run an anti-check that counts rows where NOT ((account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)); require unique `available` where the expected grain is one row per key and confirm the projected `available` against `transfer_accounts`. Add one row for which `(account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)` is true and one for which it is false; verify only the matching `available` value is returned.
6. Recover after a unique-key error at a savepoint.
   **Inputs/evidence:** For sql-38 Exercise 6, read from `isolation_solution`. Build the answer toward `still_usable`; keep `still_usable` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-38 Exercise 6, expected output: one row per `still_usable`. The final columns are `still_usable`.
   **Verify:** For sql-38 Exercise 6, reselect the returned keys directly from the source; require unique `still_usable` where the expected grain is one row per key and confirm the projected `still_usable` against `isolation_solution`. Add duplicate source candidates for `still_usable`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
7. Explain an isolation choice for a multi-query read-only report.
   **Inputs/evidence:** For sql-38 Exercise 7, use two labeled terminals and only `txn_demo`, `isolation_solution`, and `transfer_accounts`. Write the statement order, expected wait/SQLSTATE, and cleanup step before opening either transaction.
   **Expected result/shape:** For sql-38 Exercise 7, expected output: a statement-by-statement Session A/Session B transcript followed by the committed fixture state and cleanup evidence. The final columns are `session`, `statement_number`, `outcome`, and `sqlstate`.
   **Verify:** For sql-38 Exercise 7, compare every observed value, wait, and SQLSTATE with the written schedule; query `txn_demo`, `isolation_solution`, and `transfer_accounts` after each commit/rollback and finish with both sessions idle and the fixture reset. Repeat the exact interleaving after cleanup and confirm the same wait, SQLSTATE, and committed final rows.

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

I have completed the direct catalog prerequisite: `sql-37`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day38_transactions_isolation.md
- Answer-free learner SQL: sql/postgres-60day/day38_transactions_isolation.sql

Key terms to teach in context: MVCC, Isolation level, Serialization failure. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Open two disposable sessions and write down each statement before running it. Under READ COMMITTED, have session A read a count, session B commit a matching insert, and session A read again. Repeat at REPEATABLE READ and explain the snapshot difference; clean up the shared disposable table afterward.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-38/ working copy. Never point setup, reset, DDL, or DML
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
