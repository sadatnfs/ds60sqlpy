# Day 39: Locks, Blocking, and Deadlocks

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 38; transactions and isolation](day38_transactions_isolation.md)
- **Artifacts:** [learner SQL](../day39_locks_deadlocks.sql) ·
  [solution reasoning](../solutions/day39_solutions.md) ·
  [executable solution](../solutions/day39_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-39**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-39/lesson/workspace/sql/postgres-60day/day39_locks_deadlocks.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-39
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

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

Continue to [Day 40; advanced analytic functions](day40_analytic_functions_advanced.md).

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
