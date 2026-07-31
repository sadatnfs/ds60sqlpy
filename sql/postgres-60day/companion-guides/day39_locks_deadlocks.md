# Day 39 — Locks, Blocking, and Deadlocks

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 38 — transactions and isolation](day38_transactions_isolation.md)
- **Artifacts:** [learner SQL](../day39_locks_deadlocks.sql) ·
  [solution reasoning](../solutions/day39_solutions.md) ·
  [executable solution](../solutions/day39_solutions.sql)

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

2. Open **SQL-39 — Locks Deadlocks** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-39/day39_locks_deadlocks.sql`. Save it, then run the notebook's
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
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day39_locks_deadlocks.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day39_locks_deadlocks.sql
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
Blocking, Deadlock, Advisory lock. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with 40P01. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day39_locks_deadlocks.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT pid, locktype, relation::regclass, mode, granted
FROM pg_locks
LEFT JOIN pg_class ON pg_locks.relation = pg_class.oid
ORDER BY granted DESC, relation;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH to_lock AS (
  SELECT order_id FROM orders WHERE total_amount > 900 ORDER BY order_id LIMIT 5
)
SELECT * FROM orders o
JOIN to_lock t ON t.order_id = o.order_id
FOR UPDATE;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Observe blocking and deadlock state without intervening blindly.
- Prevent a lock cycle with consistent acquisition order and design queue
  claiming with `SKIP LOCKED`.

## Vocabulary and concepts

- **Blocking:** one session waiting for an incompatible lock held elsewhere.
- **Deadlock:** a cycle of sessions each waiting for another in the cycle.
- **Advisory lock:** an application-defined coordination lock not tied to a row.

## Worked example / walkthrough

In two disposable sessions, lock test rows 1 and 2 in opposite orders and
inspect the wait before PostgreSQL aborts one participant with `40P01`. Roll
back, then repeat with both sessions ordering keys ascending to show the cycle
cannot form.

## Exercises

Complete these in the [learner SQL](../day39_locks_deadlocks.sql):

1. Reproduce a deadlock and inspect it with `pg_locks`.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Prevent it with consistent key ordering.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Demonstrate a `SKIP LOCKED` worker.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. Predict `NOWAIT` behavior when another session owns the lock.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. Atomically claim/update at most five queue rows.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Preserve deterministic key ordering through the locking SELECT.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. Test a transaction-level advisory lock.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Use a disposable queue and prove two workers claim different rows.

## Self-check

- Can you identify blocker, waiter, resource, and statement from evidence?
- Is `SKIP LOCKED` limited to queue-like work where an inconsistent view is
  acceptable?

## Next step

Continue to [Day 40 — advanced analytic functions](day40_analytic_functions_advanced.md).

## Deep dive and reference

## What you will learn

- Inspect locks with `pg_locks` and session state with `pg_stat_activity`.
- Reproduce a deadlock safely and prevent it with consistent lock order.
- Use `FOR UPDATE SKIP LOCKED` for competing queue workers.

## How the learner script uses the current schema

The script lists current locks, selects five high-value `orders` in ascending
`order_id`, and locks those same rows in a consistent order. It also introduces
transaction- and session-level advisory locks as application coordination
tools.

A deadlock is a cycle: session A waits for B while B waits for A. PostgreSQL
detects the cycle and aborts one transaction with SQLSTATE `40P01`. Consistent
key order, small transactions, and avoiding user pauses inside transactions
reduce risk.

## Practice — match the learner prompts exactly

1. In two disposable sessions, lock two test rows in opposite order, capture the
   waits in `pg_locks`, then let PostgreSQL detect the deadlock.
2. Repeat with both sessions acquiring rows in ascending key order.
3. Use a disposable job table and `SELECT ... FOR UPDATE SKIP LOCKED` so two
   workers claim different unprocessed rows.

## Operational safety

- Do not run the deliberate deadlock against production or important shared
  orders.
- `SKIP LOCKED` is appropriate for queue-like work; it gives an inconsistent
  view and is not a general reporting option.
- `NOWAIT` fails immediately, while `lock_timeout` allows a bounded wait.
- Investigate ownership and impact before canceling or terminating any backend.

## Validation

Record the two-session statement sequence, the blocked/aborted session, SQLSTATE,
and proof that the consistent-order version completes. Roll back or drop all
disposable queue/deadlock objects.

## Expanded practice lab

Prompts 4–7 compare waiting, immediate failure, cooperative queues, and advisory
coordination. `NOWAIT` raises an error instead of waiting; `SKIP LOCKED` omits
currently claimed rows, which is useful for workers but wrong for complete
reporting.

Claim and update queue rows in one transaction, with a deterministic key order.
Use `pg_try_advisory_xact_lock` for a non-blocking application lock that releases
automatically at transaction end. Advisory locks work only when every actor
follows the same key convention.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-39 — Locks Deadlocks.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day39_locks_deadlocks.md
- Answer-free learner SQL: sql/postgres-60day/day39_locks_deadlocks.sql

The lesson concepts include Blocking, Deadlock, Advisory lock. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with 40P01. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-39/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
