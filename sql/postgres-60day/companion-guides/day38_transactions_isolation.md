# Day 38: Transactions and Isolation Levels

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-38**. The
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
   `.learning/sql/sql-38/lesson/workspace/sql/postgres-60day/day38_transactions_isolation.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-38
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
- **Prerequisites:** [Day 37; partitioning and sharding](day37_partitioning_sharding.md)
- **Artifacts:** [learner SQL](../day38_transactions_isolation.sql) ·
  [solution reasoning](../solutions/day38_solutions.md) ·
  [executable solution](../solutions/day38_solutions.sql)

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

The worked walkthrough's lesson-specific task is: Open two disposable sessions and write down each statement before running it. Under `READ COMMITTED`, have session A read a count, session B commit a matching insert, and session A read again. Repeat at `REPEATABLE READ` and explain the snapshot difference; clean up the shared disposable table afterward.
The first worked example is a single-session savepoint: it proves that part of a
transaction can be undone while the rest continues. The second is a two-terminal
schedule, because isolation is only observable when another session commits
between two of your statements.

## Two worked SQL examples

Example 1 comes from `sql/postgres-60day/day38_transactions_isolation.sql`; Example 2 is a manual two-terminal schedule. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1: undo part of one transaction with a savepoint

```sql
SAVEPOINT sp1;

UPDATE
  txn_demo
SET
  qty = qty + 100
WHERE
  id = 1;

SELECT
  *
FROM
  txn_demo
WHERE
  id = 1;

ROLLBACK TO SAVEPOINT sp1;
```

**How to read it:** `SAVEPOINT sp1` marks a point inside the open lesson
transaction. The `UPDATE` changes one row of the session-private `txn_demo`
table, and `ROLLBACK TO SAVEPOINT sp1` undoes only the work done after the
mark. The surrounding transaction stays open and usable.

**Expected result/shape:** the `SELECT` inside the savepoint returns one row with
columns `id` and `qty`: `(1, 110)`. The learner script's next `SELECT` after the
rollback returns `(1, 10)` again, and the final `ROLLBACK` removes `txn_demo`
entirely.

### Example 2: a non-repeatable read needs two sessions

This schedule is not part of the learner file, because one `psql` script runs
in one session. Run it by hand in two terminals after the lab setup described
under "Important two-session limitation" below.

```text
-- Session A
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT qty FROM training.isolation_lab WHERE id = 1;   -- 10

-- Session B
BEGIN;
UPDATE training.isolation_lab SET qty = 15 WHERE id = 1;
COMMIT;

-- Session A
SELECT qty FROM training.isolation_lab WHERE id = 1;   -- 15
ROLLBACK;
```

**How to read it:** under `READ COMMITTED`, each statement in Session A takes a
new snapshot, so its second read sees Session B's committed change. Replace the
first line with `BEGIN ISOLATION LEVEL REPEATABLE READ;` (after resetting
`qty` to `10`) and the second read returns `10`, because the whole transaction
keeps the snapshot taken by its first query.

**Expected result/shape:** each `SELECT` returns one row with one `qty` column.
The pair of values is `10` then `15` under `READ COMMITTED`, and `10` then `10`
under `REPEATABLE READ`.

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
   **Inputs/evidence:** For sql-38 Exercise 1, use two terminals and the committed lab table `training.isolation_lab` from the lab setup, seeded with rows `(1, 10)` and `(2, 20)`; Session B changes only the row with `id = 1`.
   **Expected result/shape:** For sql-38 Exercise 1, expected output: under `READ COMMITTED`, Session A's two `SELECT qty FROM training.isolation_lab WHERE id = 1` statements return one row each, `10` and then `15`, because Session B commits `qty = 15` between them; under `REPEATABLE READ` the second read still returns `10`.
   **Verify:** For sql-38 Exercise 1, record both `qty` values, the commit order, and each session's level from `SHOW transaction_isolation`; after both sessions end, `SELECT id, qty FROM training.isolation_lab ORDER BY id` returns `(1, 15)` and `(2, 20)`. Reset `id = 1` to `10` before repeating the schedule at `REPEATABLE READ`.
2. Reproduce a phantom under `READ COMMITTED`, then show that `REPEATABLE READ`
   prevents it.
   **Inputs/evidence:** For sql-38 Exercise 2, start from `training.isolation_lab` with no row whose `id >= 3`; Session A counts rows matching `qty >= 20` twice while Session B inserts and commits `(3, 30)` between the two counts.
   **Expected result/shape:** For sql-38 Exercise 2, expected output: under `READ COMMITTED`, Session A's two one-row `count` results are `1` and then `2`, because the committed row `(3, 30)` is a phantom; under `REPEATABLE READ`, both counts are `1` until Session A ends.
   **Verify:** For sql-38 Exercise 2, record both `count` values and the commit order at each isolation level; after each run, `SELECT COUNT(*) FROM training.isolation_lab WHERE id = 3` returns `1`, proving Session B's insert was committed. Delete the row with `id = 3` before repeating the schedule.
3. Cause/retry a `SERIALIZABLE` failure.
   **Inputs/evidence:** For sql-38 Exercise 3, reset `training.isolation_lab` to `(1, 10)` and `(2, 20)`, then open two `SERIALIZABLE` transactions that both read `SUM(qty)` before Session A updates the row with `id = 1` and Session B updates the row with `id = 2`.
   **Expected result/shape:** For sql-38 Exercise 3, expected output: both sums are `30`; Session A's `COMMIT` succeeds and Session B's `COMMIT` fails with SQLSTATE `40001` (`could not serialize access due to read/write dependencies among transactions`), leaving committed rows `(1, 11)` and `(2, 20)`.
   **Verify:** For sql-38 Exercise 3, capture the error text and SQLSTATE (for example after `\set VERBOSITY verbose`), confirm the committed rows with `SELECT id, qty FROM training.isolation_lab ORDER BY id`, then rerun Session B's whole transaction from `BEGIN ISOLATION LEVEL SERIALIZABLE` and confirm the rows `(1, 11)` and `(2, 21)`.
4. Predict savepoint state after `ROLLBACK TO SAVEPOINT`.
   **Inputs/evidence:** For sql-38 Exercise 4, use the temporary `isolation_solution` rows `(1, 10)` and `(2, 20)` inside the lesson transaction; set a savepoint, add `1` to `quantity` for `id = 2`, roll back to the savepoint, then release it.
   **Expected result/shape:** For sql-38 Exercise 4, expected output: `RELEASE SAVEPOINT` succeeds because `ROLLBACK TO SAVEPOINT` keeps the savepoint, and the final `SELECT` returns two rows ordered by `id` with columns `id` and `quantity`: `(1, 10)` and `(2, 20)`.
   **Verify:** For sql-38 Exercise 4, compare the row with `id = 2` before the savepoint and after the rollback (both `20`); in a scratch transaction, a second `RELEASE SAVEPOINT reusable_point` fails with SQLSTATE `3B001` (`savepoint "reusable_point" does not exist`), which proves the first `RELEASE` removed it.
5. Build an atomic checked transfer between two temp accounts.
   **Inputs/evidence:** For sql-38 Exercise 5, create the temporary `transfer_accounts` table with rows `(1, 100.00)` and `(2, 40.00)` and `CHECK (balance >= 0)`; move `25.00` from account 1 to account 2 after locking and checking the debit row.
   **Expected result/shape:** For sql-38 Exercise 5, expected output: one `conserved_total` row equal to `140.00`; the account rows become `(1, 75.00)` and `(2, 65.00)`.
   **Verify:** For sql-38 Exercise 5, list `account_id` and `balance` before and after the transfer and compare their sums; then attempt a `200.00` transfer after a savepoint, confirm the `insufficient balance` exception with SQLSTATE `P0001`, roll back to the savepoint, and confirm both balances are unchanged.
6. Recover after a unique-key error at a savepoint.
   **Inputs/evidence:** For sql-38 Exercise 6, insert a duplicate `id = 1` into the temporary `isolation_solution` table inside a protected PL/pgSQL block (or after a savepoint), so the unique violation with SQLSTATE `23505` is caught or rolled back to the savepoint.
   **Expected result/shape:** For sql-38 Exercise 6, expected output: a notice that the duplicate was rejected, then one `still_usable` row whose value is `2`, the number of rows in `isolation_solution`.
   **Verify:** For sql-38 Exercise 6, in a scratch transaction, repeat the duplicate insert without protection and confirm that the next statement fails with SQLSTATE `25P02` (`current transaction is aborted`); the savepoint recovery is what avoids that state.
7. Explain an isolation choice for a multi-query read-only report.
   **Inputs/evidence:** For sql-38 Exercise 7, consider a report that runs two statements over `training.isolation_lab`, a `COUNT(*)` and a `SUM(qty)`, while another session may commit changes between them.
   **Expected result/shape:** For sql-38 Exercise 7, expected output: a short written answer that chooses `REPEATABLE READ` (optionally `READ ONLY`) when both results must describe one snapshot, and `READ COMMITTED` when each statement may show the latest committed data.
   **Verify:** For sql-38 Exercise 7, test the claim with the Exercise 2 schedule: under `READ COMMITTED`, a `SUM(qty)` run after Session B commits includes the new row that the earlier `COUNT(*)` did not count; under `REPEATABLE READ`, both values describe the first snapshot.

Record exact two-session ordering and SQLSTATEs.

## Self-check

- Are you using a regular disposable table rather than a session-local
  temporary table for cross-session work?
- Would retry logic restart every read and write in the transaction?

## Next step

Continue to [Day 39; locks and deadlocks](day39_locks_deadlocks.md).

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
- `REPEATABLE READ` keeps one snapshot: repeated reads see neither later commits
  nor phantom rows. Updating or locking a row that a concurrent transaction
  changed and committed fails with SQLSTATE `40001`, so this level also needs
  whole-transaction retry. Write skew between different rows is still possible.
- `SERIALIZABLE` also tracks read/write dependencies and can abort with `40001`
  when no single row conflicts (write skew). Retry the entire transaction.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Important two-session limitation

`txn_demo` is a temporary table, created inside an uncommitted transaction, and
is visible only to the session that created it. A second terminal cannot read
or update it. For the manual Exercises 1 to 3, create this committed,
course-owned table once from either terminal, outside any open transaction:

```sql
SET search_path TO training, public;

DROP TABLE IF EXISTS isolation_lab;

CREATE TABLE isolation_lab (
  id int PRIMARY KEY,
  qty int NOT NULL
);

INSERT INTO isolation_lab
VALUES
  (1, 10),
  (2, 20);
```

Use it from both sessions, then run `DROP TABLE training.isolation_lab;` after
both transactions end. Do not run the contention demo against important shared
rows.

## Pitfalls and validation

- Keep transactions short; old snapshots delay vacuum cleanup.
- A savepoint rolls back part of one transaction, not another session's commit.
- Retry the whole serializable unit of work, not only the statement that failed.
- Record the exact statement order in both terminals so the anomaly is
  reproducible.

## Expanded practice lab

Prompts 4-7 add single-session recovery patterns to the concurrency exercises.
After `ROLLBACK TO SAVEPOINT`, PostgreSQL keeps that savepoint available until
it is released or the transaction ends. This is why error recovery must first
return to a valid savepoint before more statements run.

For the transfer, lock/check/update both balances as one transaction and verify
that total money is unchanged. A multi-query read-only report can still need
`REPEATABLE READ` when all results must describe one consistent snapshot.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-38: Transactions and Isolation Levels.

I have completed the direct catalog prerequisite: `sql-37`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day38_transactions_isolation.md
- Answer-free learner SQL: sql/postgres-60day/day38_transactions_isolation.sql

Key terms to teach in context: MVCC, Isolation level, Serialization failure. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Open two disposable sessions and write down each statement before running it. Under `READ COMMITTED`, have session A read a count, session B commit a matching insert, and session A read again. Repeat at `REPEATABLE READ` and explain the snapshot difference; clean up the shared disposable table afterward.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
