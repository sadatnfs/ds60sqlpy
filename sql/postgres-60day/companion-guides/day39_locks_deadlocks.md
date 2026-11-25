# Day 39: Locks, Blocking, and Deadlocks

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-39**. The
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

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 38; transactions and isolation](day38_transactions_isolation.md)
- **Artifacts:** [learner SQL](../day39_locks_deadlocks.sql) ·
  [solution reasoning](../solutions/day39_solutions.md) ·
  [executable solution](../solutions/day39_solutions.sql)

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

The worked walkthrough's lesson-specific task is: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with `40P01`. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.
The first worked example lists the locks your own session holds, so you can read
`pg_locks` before any contention exists. The second locks five rows in a fixed
key order, which is the habit that prevents deadlocks when several sessions
lock the same rows.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day39_locks_deadlocks.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1: read the lock table

```sql
SELECT
  pid,
  locktype,
  relation::regclass,
  mode,
  granted
FROM
  pg_locks
  LEFT JOIN pg_class ON pg_locks.relation = pg_class.oid
ORDER BY
  granted DESC,
  relation;
```

**How to read it:** `pg_locks` has one row per lock held or awaited, so one
`pid` usually appears several times. `relation::regclass` turns a table or
index OID into its name; locks that are not on a relation, such as the
`virtualxid` lock every transaction holds, show `NULL` there. `granted = false`
marks a lock that is still being waited for.

**Expected result/shape:** in a fresh single session the result shows only your
own `pid` (compare with `SELECT pg_backend_pid()`): `AccessShareLock` rows on
`pg_locks`, `pg_class` and its indexes, plus one `virtualxid` `ExclusiveLock`,
all with `granted = true`. A row with `granted = false` appears only when
another session holds a conflicting lock.

### Example 2: lock rows in a consistent key order

```sql
SELECT
  o.order_id,
  o.total_amount
FROM
  orders AS o
WHERE
  o.total_amount > 900
ORDER BY
  o.order_id
LIMIT 5
FOR UPDATE;
```

**How to read it:** `FOR UPDATE` locks every returned row until the transaction
ends. Because `ORDER BY` is part of the locking `SELECT`, the plan is `Limit`
above `LockRows` above an ordered scan, so the rows are locked in ascending
`order_id` order. If every transaction that touches these rows uses the same
order, two transactions can make each other wait but cannot form a cycle.

**Expected result/shape:** five rows with columns `order_id` and
`total_amount`; on the course seed the keys are `4`, `8`, `12`, `19`, and `24`.
The locks disappear at the script's final `ROLLBACK`.

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
   **Inputs/evidence:** For sql-39 Exercise 1, use two terminals on the seeded `training.orders` rows with `order_id` 1 and 2: Session A locks row 1 then row 2, Session B locks row 2 then row 1 (with `SELECT ... FOR UPDATE` or a no-op `UPDATE ... SET total_amount = total_amount`), and a third terminal reads `pg_locks` while a session waits.
   **Expected result/shape:** For sql-39 Exercise 1, expected output: while Session A's second lock request waits, the third terminal shows one ungranted `transactionid` row (`mode = ShareLock`, `granted = false`) for Session A's `pid`; when Session B's second lock request closes the cycle, about one second later (`deadlock_timeout`) Session B fails with SQLSTATE `40P01` (`deadlock detected`) and Session A's waiting statement completes.
   **Verify:** For sql-39 Exercise 1, record each session's `pg_backend_pid()`, the waiting `pid` from `pg_locks`, and the two `DETAIL` lines (`Process ... waits for ShareLock on transaction ...`); end both transactions with `ROLLBACK` and confirm that `SELECT order_id, status, total_amount FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id` returns the same values as before the experiment.
2. Prevent it with consistent key ordering.
   **Inputs/evidence:** For sql-39 Exercise 2, repeat the Exercise 1 schedule, but let both sessions lock `order_id` 1 and 2 in ascending order with one statement such as `SELECT order_id FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id FOR UPDATE`.
   **Expected result/shape:** For sql-39 Exercise 2, expected output: Session A's locking `SELECT` returns two rows, `order_id` 1 and 2; Session B's identical statement waits instead of deadlocking and returns the same two rows after Session A ends. No session receives SQLSTATE `40P01`.
   **Verify:** For sql-39 Exercise 2, while Session B waits, confirm in a third terminal that `SELECT locktype, mode FROM pg_locks WHERE NOT granted` returns exactly one row, a `transactionid` `ShareLock`; then rerun the opposite-order schedule from Exercise 1 to show that only the lock order changed.
3. Demonstrate a `SKIP LOCKED` worker.
   **Inputs/evidence:** For sql-39 Exercise 3, create the temporary `solution_jobs` queue with four unprocessed jobs (`first` to `fourth`), then select the oldest two unprocessed jobs with `ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 2`.
   **Expected result/shape:** For sql-39 Exercise 3, expected output: two rows with columns `job_id` and `payload`: `(1, first)` and `(2, second)`, now locked by this transaction.
   **Verify:** For sql-39 Exercise 3, recreate the queue as a committed disposable table, run the same claim in a second session while the first session still holds its locks, and confirm that the second session returns jobs `3` and `4` immediately instead of waiting; a temporary table cannot show this, because only its creating session can read it.
4. Predict `NOWAIT` behavior when another session owns the lock.
   **Inputs/evidence:** For sql-39 Exercise 4, lock `order_id = 1` with `SELECT order_id FROM training.orders WHERE order_id = 1 FOR UPDATE` in Session A, then run the same statement in Session B once without and once with `NOWAIT`; the single-session script only plans the `NOWAIT` form with `EXPLAIN`.
   **Expected result/shape:** For sql-39 Exercise 4, expected output: without `NOWAIT`, Session B waits until Session A ends; with `NOWAIT`, it fails at once with SQLSTATE `55P03` (`could not obtain lock on row in relation "orders"`). The script's `EXPLAIN` shows a `LockRows` node above an index scan on `orders_pkey`.
   **Verify:** For sql-39 Exercise 4, record both outcomes and their SQLSTATE; then run `SET lock_timeout = '2s'` in Session B and confirm that the ordinary `FOR UPDATE` fails after about two seconds with SQLSTATE `55P03` (`canceling statement due to lock timeout`).
5. Atomically claim/update at most five queue rows.
   **Inputs/evidence:** For sql-39 Exercise 5, claim at most five unprocessed `solution_jobs` rows in one statement: a `claimed` CTE with `ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 5`, joined by an `UPDATE` that sets `processed_at` and returns `job_id`, `payload`, and `processed_at`.
   **Expected result/shape:** For sql-39 Exercise 5, expected output: four rows, `job_id` 1 to 4 with their `payload` and a non-NULL `processed_at`, and the command tag `UPDATE 4`. Jobs 1 and 2 are not skipped even though Exercise 3 locked them, because `SKIP LOCKED` skips only rows locked by other transactions.
   **Verify:** For sql-39 Exercise 5, count `SELECT COUNT(*) FROM solution_jobs WHERE processed_at IS NULL` before (`4`) and after (`0`) the claim and compare the difference with `UPDATE 4` and the four returned `job_id` values; a second claim in the same transaction returns zero rows.
6. Preserve deterministic key ordering through the locking SELECT.
   **Inputs/evidence:** For sql-39 Exercise 6, compare a locking query whose only `ORDER BY` is inside a CTE with the repaired form that keeps `ORDER BY o.order_id` in the locking `SELECT ... FOR UPDATE OF o`, over orders with `total_amount > 900`.
   **Expected result/shape:** For sql-39 Exercise 6, expected output: five rows with one column, `order_id`: `4`, `8`, `12`, `19`, and `24` on the course seed, returned and locked in ascending order.
   **Verify:** For sql-39 Exercise 6, run `EXPLAIN (COSTS OFF)` on both forms: in the repaired form the rows reach `LockRows` already in `order_id` order (on PostgreSQL 17, a nested loop driven by the ordered CTE scan), while the CTE-only form has no outer `ORDER BY`, so its lock order follows whatever join method the planner picks. Confirm that `SELECT COUNT(*) FROM training.orders WHERE total_amount > 900` returns `605`, so the five-row limit is reached.
7. Test a transaction-level advisory lock.
   **Inputs/evidence:** For sql-39 Exercise 7, call `pg_try_advisory_xact_lock(3902)` twice inside the lesson transaction, then once from a second session while the first transaction is still open.
   **Expected result/shape:** For sql-39 Exercise 7, expected output: two one-row results, `first_attempt = true` and `same_owner_attempt = true`, because the owning backend may take the same lock again; the second session's call returns `false` until the first transaction ends.
   **Verify:** For sql-39 Exercise 7, while the first transaction is open, `SELECT locktype, objid, mode, granted FROM pg_locks WHERE locktype = 'advisory'` shows one row with `objid = 3902` and `ExclusiveLock`; after `ROLLBACK`, that query returns no row and the second session's call returns `true`, without any `pg_advisory_unlock`.

Use a disposable queue and prove two workers claim different rows.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with `40P01`. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.
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

The script lists current locks, then selects and locks five high-value
`orders` with `ORDER BY o.order_id` inside the locking `SELECT`, so the rows are
locked in ascending key order. It also introduces
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

Prompts 4-7 compare waiting, immediate failure, cooperative queues, and advisory
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
Tutor me through sql-39: Locks, Blocking, and Deadlocks.

I have completed the direct catalog prerequisite: `sql-38`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day39_locks_deadlocks.md
- Answer-free learner SQL: sql/postgres-60day/day39_locks_deadlocks.sql

Key terms to teach in context: Blocking, Deadlock, Advisory lock. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with `40P01`. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.

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
