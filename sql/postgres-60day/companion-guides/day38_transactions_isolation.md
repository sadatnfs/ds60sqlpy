# Day 38 — Transactions and Isolation Levels

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 37 — partitioning and sharding](day37_partitioning_sharding.md)
- **Artifacts:** [learner SQL](../day38_transactions_isolation.sql) ·
  [solution reasoning](../solutions/day38_solutions.md) ·
  [executable solution](../solutions/day38_solutions.sql)

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

Complete the prompts in the [learner SQL](../day38_transactions_isolation.sql)
and the documented two-session exercises. Record exact ordering and SQLSTATEs.

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
