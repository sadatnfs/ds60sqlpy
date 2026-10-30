# SQL-CONCURRENCY-01: solution reasoning

Use this after an honest attempt at the [guide](../companion-guides/sql_concurrency_01_isolation_and_versions.md)
and [learner script](../lessons/sql_concurrency_01_isolation_and_versions.sql). The separate
[executable solution](sql_concurrency_01_isolation_and_versions_solutions.sql) runs all six answers and independent
fail-fast checks with `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_concurrency_01_isolation_and_versions_solutions.sql`.
It uses only temporary fixtures, starts a transaction, and ends in rollback.
It must exit 0 with no contract failures. Each answer has a savepoint so an
experiment cannot silently change a later exercise's starting conditions.
The assertion helper treats false and unknown as failures, rather than allowing
a NULL assertion to pass accidentally. Keep the original fixture unchanged
when comparing your work so the stated identities remain a reliable oracle.

The code below is the answer for each numbered prompt, followed by its
reasoning. Inspect the first discrepancy in your own transcript before reading
a different answer. A solution is one defensible implementation of this contract;
an alternative is valid if its identities, values, missingness, ordering, and
transaction behavior match. Tests constrain the actual returned relation,
rather than assuming a familiar-looking query must be right.

## Exercise solutions

## Exercise 1: Perform a guarded reservation

```sql
UPDATE
  concurrency_stock
SET
  available = available - 2,
  version = version + 1
WHERE
  sku = 'A'
  AND version = 1
  AND available >= 2
RETURNING
  sku,
  available,
  version;
```

The UPDATE selects a unique SKU and checks both expectations in the same statement that changes the values. It increments the version so an earlier reader cannot reuse version 1 after this reservation succeeds. RETURNING supplies direct evidence of the row that changed. The exercise wrapper uses a savepoint so subsequent independent questions start from the same fixture. The assertion checks the returned state and the script separately confirms rollback restoration. A preceding SELECT without a guarded write would leave a time gap during which its observation could become stale. No timing claim follows here because this is still a single-session operation.

**Inputs/evidence:** For sql-concurrency-01 Exercise 1, Inside a savepoint, reserve two A units using expected version 1 and a nonnegative-capacity predicate. Return sku, available, version, then roll back the attempt.

**Expected result/shape:** For sql-concurrency-01 Exercise 1, One updated SKU row, columns sku, available, version: (A,3,2). After savepoint rollback, A is (A,5,1). No final ORDER BY is needed for the unique sku update.

**Verify:** For sql-concurrency-01 Exercise 1, Inspect RETURNING (A,3,2), then inspect restored A state (5,1) after savepoint rollback. A successful command tag alone does not establish the version and capacity outcome.

## Exercise 2: Reject a stale expected version

```sql
UPDATE
  concurrency_stock
SET
  available = available - 1,
  version = version + 1
WHERE
  sku = 'A'
  AND version = 99
  AND available >= 1
RETURNING
  sku,
  available,
  version;
```

Version 99 does not match the current row, so no mutation occurs. This is intentionally a successful SQL statement with an unsuccessful business precondition. Keep those two outcomes distinct in application code and learner evidence. The assertion checks both the empty RETURNING relation and the unchanged stored state. Removing the version condition would make the statement affect a row while destroying the protection the caller requested. A caller can reread to investigate, but must decide whether the original business intent remains valid before retrying. Under actual concurrent stronger-isolation execution an exception may be another possible outcome; this deterministic stale-version example makes no claim that all conflicts are reported as zero rows.

**Inputs/evidence:** For sql-concurrency-01 Exercise 2, Try reserving one A unit with expected version 99. Return sku, available, version for any successful update and inspect the row afterward.

**Expected result/shape:** For sql-concurrency-01 Exercise 2, Zero returned rows with columns sku, available, version. A remains available 5 and version 1; SQL execution itself succeeds with UPDATE 0.

**Verify:** For sql-concurrency-01 Exercise 2, Require zero RETURNING rows and unchanged A state available=5,version=1. Removing the version condition would discard the requested stale-write protection.

## Exercise 3: Reject insufficient capacity independently

```sql
UPDATE
  concurrency_stock
SET
  available = available - 2,
  version = version + 1
WHERE
  sku = 'B'
  AND version = 1
  AND available >= 2
RETURNING
  sku,
  available,
  version;
```

The version precondition is satisfied, but available >= 2 is false for B's one unit. Both predicates belong to the atomic update condition, so stock never becomes negative and the version does not advance. The CHECK constraint is an additional invariant guard; the ordinary business shortage should be handled without intentionally violating it. The assertion verifies an empty result and the unchanged B row. A zero-row outcome alone does not identify which precondition failed, so the caller may need an explicit follow-up read and a conflict policy. Keep that diagnostic read separate from a claim that the earlier attempt succeeded.

**Inputs/evidence:** For sql-concurrency-01 Exercise 3, Try reserving two B units with correct expected version 1. Return sku, available, version on success and inspect B afterward.

**Expected result/shape:** For sql-concurrency-01 Exercise 3, Zero returned rows, columns sku, available, version. B remains (B,1,1), proving the capacity condition can fail even with a current version.

**Verify:** For sql-concurrency-01 Exercise 3, Require zero RETURNING rows and unchanged B state available=1,version=1. The current version and failed capacity distinguish this outcome from the stale-version case.

## Exercise 4: Model two callers sharing an old version

```sql
CREATE TEMP TABLE model_trace (
  caller text PRIMARY KEY,
  affected_rows bigint
) ON COMMIT DROP;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 2,
    version = version + 1
  WHERE
    sku = 'A'
    AND version = 1
    AND available >= 2
  RETURNING
    sku)
INSERT INTO model_trace
SELECT
  'One',
  count(*)
FROM
  changed;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 1,
    version = version + 1
  WHERE
    sku = 'A'
    AND version = 1
    AND available >= 1
  RETURNING
    sku)
INSERT INTO model_trace
SELECT
  'Two',
  count(*)
FROM
  changed;

SELECT
  caller,
  affected_rows
FROM
  model_trace
ORDER BY
  caller;
```

The first caller's successful write advances version 1 to 2. A distinct second statement with the old version then finds no matching row. The solution executes two statements and captures their RETURNING counts into a temporary trace table, avoiding ambiguous attempts to update the same row twice inside one SQL statement. The assertion expects One to affect one row and Two none. This models the conflict contract but does not reproduce simultaneous transactions or show how long a writer waits. The optional lab is the source of actual multi-session evidence. Rollback to the surrounding savepoint removes both the modeled mutation and trace objects before the next exercise.

**Inputs/evidence:** For sql-concurrency-01 Exercise 4, Inside one savepoint, apply caller One reserving two A units at version 1, then caller Two reserving one A unit with the same old version. Return caller, affected_rows from both attempts.

**Expected result/shape:** For sql-concurrency-01 Exercise 4, Two model-trace rows keyed by caller, columns caller, affected_rows; final ORDER BY caller: One affects 1, Two affects 0. A is temporarily (A,3,2), then rollback restores the fixture. This is a sequential model, not a concurrent trace.

**Verify:** For sql-concurrency-01 Exercise 4, Inspect trace One=1 affected row and Two=0, plus temporary A state (3,2). Rollback restores (5,1). Label the result a sequential model rather than a concurrent execution trace.

## Exercise 5: Verify a no-change read result

```sql
SELECT
  sku,
  available,
  version
FROM
  concurrency_stock
ORDER BY
  sku;
```

This read confirms that the independent exercise wrappers restored the local fixture to its initial state. It does not show whether another session could see the row before or after a commit. The assertion checks both rows and their versions so accidental persistence from a previous exercise becomes visible. To make an isolation claim, run the optional two-session sequence and preserve the actual SELECT output before and after the other session commits. Merely selecting current_setting for an isolation level would show a configuration, not an observed anomaly or consistency guarantee. Keep those evidence tiers separate when explaining your result to another engineer.

**Inputs/evidence:** For sql-concurrency-01 Exercise 5, Return sku, available, version for both initial stock rows, ordered by sku. State what a single-session read proves and what a two-session isolation claim additionally needs.

**Expected result/shape:** For sql-concurrency-01 Exercise 5, Two SKU rows, columns sku, available, version; final ORDER BY sku: (A,5,1),(B,1,1). A genuine isolation trace also needs session names, isolation level, ordered statements, commit boundary, and observations.

**Verify:** For sql-concurrency-01 Exercise 5, Inspect initial rows (A,5,1),(B,1,1). A separate isolation claim requires actual A-session reads, B-session write/commit order, and the selected isolation level from the optional lab.

## Exercise 6: Transfer the guard to an atomic replenishment

```sql
UPDATE
  concurrency_stock
SET
  available = available + 3,
  version = version + 1
WHERE
  sku = 'B'
  AND version = 1
RETURNING
  sku,
  available,
  version;
```

Replenishment changes the state just as reservation does, so it must advance the version. Otherwise an old reader could still act on the former version while using outdated capacity information. The first update returns B with four units and version 2. Repeating the old version precondition affects no rows. The solution captures that second RETURNING count as a negative control before rolling back the exercise. This does not make arbitrary retries idempotent after an unknown commit result: a retried caller needs a durable operation identity to know whether the first intent already committed. The version guard prevents a stale conditional write, while idempotency solves a related but different recovery question.

**Inputs/evidence:** For sql-concurrency-01 Exercise 6, Inside a savepoint, add three B units using expected version 1, increment version, and return sku, available, version. Then retry the same old expectation and prove it affects zero rows.

**Expected result/shape:** For sql-concurrency-01 Exercise 6, One initial updated SKU row, columns sku, available, version: (B,4,2). A second attempt using version 1 returns zero rows. Rollback leaves B at (B,1,1).

**Verify:** For sql-concurrency-01 Exercise 6, Inspect initial RETURNING (B,4,2), then require zero rows for repeating old version 1, and inspect restored (B,1,1) after rollback. This tests stale-write protection, not unknown-commit recovery.

## Cleanup and evidence boundary

The final rollback removes every temporary table, helper function, index, and modeled change. Running this file twice starts from the same fixture and should produce the same logical evidence. No extension, external dataset, current timestamp, or administrator capability is required. For the optional two-session concurrency lab, use its separate explicit cleanup because that fixture is deliberately committed; the default script never prepares that shared state. A static content check can validate contracts and file structure, while only a live PostgreSQL transcript validates SQL execution. Retain that distinction when reporting completion.
