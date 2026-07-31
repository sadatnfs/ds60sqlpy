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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-39/lesson/workspace/sql/postgres-60day/day39_locks_deadlocks.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Blocking, Deadlock, Advisory lock. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with 40P01. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.
The first runnable example has a concrete contract: Example 1 returns one row per `pid` with columns `pid`, `locktype`, `regclass`, `mode`, and `granted` from `pg_locks`, and `pg_class`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `pid`, `locktype`, `regclass`, `mode`, and `granted`. Reselect the returned key columns from `pg_locks`, and `pg_class`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day39_locks_deadlocks.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT pid, locktype, relation::regclass, mode, granted
FROM pg_locks
LEFT JOIN pg_class ON pg_locks.relation = pg_class.oid
ORDER BY granted DESC, relation;
```

**How to read it:** Example 1: Start with `pg_locks`, and `pg_class` in `FROM`/`JOIN`. The final `SELECT` displays `pid`, `locktype`, `regclass`, `mode`, and `granted`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `pid` with columns `pid`, `locktype`, `regclass`, `mode`, and `granted` from `pg_locks`, and `pg_class`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH to_lock AS (
  SELECT order_id FROM orders WHERE total_amount > 900 ORDER BY order_id LIMIT 5
)
SELECT * FROM orders o
JOIN to_lock t ON t.order_id = o.order_id
FOR UPDATE;
```

**How to read it:** Example 2 is a data-changing CTE chain, not a displayed query result. The CTEs `to_lock` determine the affected rows before the final write to the columns written in the final `SELECT`. Read the command tag for the affected-row count, then use a separate `SELECT` to prove the lesson invariant; a successful command tag alone does not prove historical correctness.

**Expected result/shape:** Example 2 prints a DML command tag for `orders`. Capture the target key set at `order_id` grain before the write, compare it with affected/returned keys, and use a follow-up `SELECT` to prove the before/after invariant and transaction cleanup.

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
   **Inputs/evidence:** For sql-39 Exercise 1, read the target keys from `orders`, and `pg_locks` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-39 Exercise 1, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`.
   **Verify:** For sql-39 Exercise 1, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `pg_locks` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
2. Prevent it with consistent key ordering.
   **Inputs/evidence:** For sql-39 Exercise 2, read the target keys from `orders` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-39 Exercise 2, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`, and `total_amount`. The final order is `order_id FOR UPDATE`.
   **Verify:** For sql-39 Exercise 2, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
3. Demonstrate a `SKIP LOCKED` worker.
   **Inputs/evidence:** For sql-39 Exercise 3, read the target keys from `orders`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-39 Exercise 3, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`, `order_date`, and `status`. The final order is `order_id`.
   **Verify:** For sql-39 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
4. Predict `NOWAIT` behavior when another session owns the lock.
   **Inputs/evidence:** For sql-39 Exercise 4, run the underlying read-only query over `orders`, and `NOWAIT` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-39 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`.
   **Verify:** For sql-39 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
5. Atomically claim/update at most five queue rows.
   **Inputs/evidence:** For sql-39 Exercise 5, read the target keys from `solution_jobs`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-39 Exercise 5, expected output: up to five unprocessed jobs with `SKIP LOCKED`; the UPDATE joins only those keys and `RETURNING` proves exactly what this worker claimed. The final columns are `returning`.
   **Verify:** For sql-39 Exercise 5, materialize the intended `returning` target set first; require the command tag/`RETURNING` set to match it, then query `solution_jobs`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `returning` values in both cases.
6. Preserve deterministic key ordering through the locking SELECT.
   **Inputs/evidence:** For sql-39 Exercise 6, read the target keys from `orders`, `ordered_keys`, and `OF` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-39 Exercise 6, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`. The final order is `o.order_id FOR UPDATE OF o`.
   **Verify:** For sql-39 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, `ordered_keys`, and `OF` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
7. Test a transaction-level advisory lock.
   **Inputs/evidence:** For sql-39 Exercise 7, read from `pg_try_advisory_xact_lock`. Compute `ROLLBACK` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-39 Exercise 7, expected output: exactly one aggregate summary row. The final columns are `ROLLBACK`.
   **Verify:** For sql-39 Exercise 7, evaluate each of `row_count` in a separate control `SELECT` over `pg_try_advisory_xact_lock`; require one final row and compare every value. Add one source row with a new `ROLLBACK`; verify the result gains exactly one row carrying that `ROLLBACK` value.

Use a disposable queue and prove two workers claim different rows.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with 40P01. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.
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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

I have completed the direct catalog prerequisite: `sql-38`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day39_locks_deadlocks.md
- Answer-free learner SQL: sql/postgres-60day/day39_locks_deadlocks.sql

Key terms to teach in context: Blocking, Deadlock, Advisory lock. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with 40P01. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-39/ working copy. Never point setup, reset, DDL, or DML
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
