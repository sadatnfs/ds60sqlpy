# Day 38: Transactions and Isolation Levels

## How to run this lesson

Start `./classroom`, pick **sql-38** and run **Whole SQL lesson (psql)**.
That runs the single-session half of the lesson: it reports the starting
isolation level, builds a temporary `txn_demo` table, rolls one update back
to a savepoint and ends with `ROLLBACK`. Edit your copy at
`.learning/sql/sql-38/lesson/workspace/sql/postgres-60day/day38_transactions_isolation.sql`;
it runs against `advanced_sql_training`. See
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom)
for launch details.

The other half needs two live connections. Exercises 1 to 3 are schedules
you type by hand into two `psql` terminals against a committed
`training.isolation_lab` table, described under "Important two-session
limitation" below. A whole-file run is one session, so it can never show
another transaction's commit landing between two of its reads.

### Optional contributor notebook route

A notebook holds one connection, so it suits the savepoint half; keep two
terminals for the schedules
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-38
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 37; partitioning and sharding](day37_partitioning_sharding.md)
- **Artifacts:** [learner SQL](../day38_transactions_isolation.sql) ·
  [solution reasoning](../solutions/day38_solutions.md) ·
  [executable solution](../solutions/day38_solutions.sql)

## A beginner's mental model for this lesson

A transaction groups statements so they commit or vanish together. Under
**MVCC**, PostgreSQL never overwrites a row in place for readers; it keeps
old versions so each transaction can read from a snapshot. The
**isolation level** decides how often that snapshot is taken.
`READ COMMITTED`, the default the learner file reports first, takes a
fresh one for every statement. `REPEATABLE READ` takes one at the first
query and keeps it until the transaction ends.

That timing explains an ordering rule in the learner file.
`SET TRANSACTION ISOLATION LEVEL REPEATABLE READ` comes after `SHOW` but
before the first `SELECT`. `SHOW` reads a setting and takes no snapshot,
so the switch is still allowed; put it after the `SELECT` and PostgreSQL
answers `SET TRANSACTION ISOLATION LEVEL must be called before any query`.

The `txn_demo` rows are `(1, 10)`, `(2, 20)` and `(3, 30)`. A savepoint is
a bookmark inside one transaction: adding 100 to row 1 shows `110`, and
`ROLLBACK TO SAVEPOINT sp1` puts it back to `10` while the transaction
stays open. A **serialization failure** is the opposite case: PostgreSQL
cannot keep the promise of the level, aborts the whole transaction with
SQLSTATE `40001`, and the only correct response is to run all of it
again.

## Two worked SQL examples

Example 1 is copied from the learner file and runs inside its transaction. Example 2 is the first hand-typed schedule: type each `Session A` line in one terminal and each `Session B` line in the other, in the order shown.

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

The prompts split cleanly. The first three are two-terminal schedules on
`isolation_lab`, so reset `qty` to `10` and `20` between attempts and write
your predicted values before Session B commits. The last four run in one
session against temporary tables: a savepoint reused and released, a
`25.00` transfer that must keep the two balances summing to `140.00`, a
duplicate key caught without aborting the transaction, and a written choice
of isolation level for a two-statement report.

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

A tutor can play Session B for you: it names the statement it would
commit next, and you predict what your Session A read returns at each
level before running it. Setup is in the
[AI tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional); start
with this prompt:

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
