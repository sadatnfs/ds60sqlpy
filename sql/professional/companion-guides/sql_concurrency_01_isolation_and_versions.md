# SQL-CONCURRENCY-01: Isolation Traces and Optimistic Concurrency

## How to run this lesson

Use only the local disposable `advanced_sql_training` database on PostgreSQL
16 or newer. The lesson page is a readable preview. In the private course
portal, choose **Create/open guided SQL notebook**, run readiness, acknowledge
only the explicitly offered course reset if needed, and edit the notebook's
ignored `.learning/sql/sql-concurrency-01/` SQL copy. Its exact path is
`.learning/sql/sql-concurrency-01/lesson/workspace/sql/professional/lessons/sql_concurrency_01_isolation_and_versions.sql`. Save the copy and run its complete-script
cell. Output appears below that cell as a full `psql` transcript. A successful
run ends in `ROLLBACK`, exits 0, and has the example identities stated below.
The setup uses temporary tables and no external data or extension.

If using VS Code directly, run from the repository root. These fallbacks work
in terminals after PostgreSQL setup:

```powershell
# Windows PowerShell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_concurrency_01_isolation_and_versions.sql"
```

```bash
# macOS/Linux
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_concurrency_01_isolation_and_versions.sql
```

Keep `-X` to ignore personal client startup changes and `ON_ERROR_STOP` to
stop at the first unexpected error. If `psql` is missing, return to the
operating-system setup and `scripts/course.py doctor`. An authentication
failure needs the local setup workflow, never a password pasted into a lesson.
If the database-name guard rejects the run, inspect your target instead of
removing the guard. After an unexpected transaction error, fix that first
error and rerun the whole file in a fresh connection. To try an exercise, put
its SQL before the final `ROLLBACK` in your private copy; temporary tables
exist only in that connection and transaction. Running this official learner
file demonstrates the examples; exercises remain answer-free until you add an
attempt. Do not edit the separate official solutions while studying.

## Level and prerequisites

- **Level:** advanced
- **Direct catalog prerequisites:** [`sql-39`](../../postgres-60day/companion-guides/day39_locks_deadlocks.md), [`sql-test-01`](sql_test_01_contracts_migrations.md)
- **Artifacts:** [learner SQL](../lessons/sql_concurrency_01_isolation_and_versions.sql), [solution reasoning](../solutions/sql_concurrency_01_isolation_and_versions_solutions.md), [executable solution](../solutions/sql_concurrency_01_isolation_and_versions_solutions.sql).

Direct prerequisites name the required boundary. The fixture setup is supplied; do not mistake its table-definition syntax for extra unstated prerequisite work.

## Learning objectives

- Express a single-row write precondition in an atomic UPDATE predicate.
- Distinguish stale versions, insufficient capacity, and successful writes from returned evidence.
- Record actual two-session visibility and serialize observations without mistaking a model for live concurrency.

## Vocabulary and concepts

A user reads stock 5 at version 1, then thinks for a moment. Another user can
change that row before the first user sends an update. The old reading is
evidence about an earlier view, not a lock on the future. A write should state
its assumption where PostgreSQL can test it atomically. Optimistic concurrency
includes the expected version in the UPDATE condition and interprets the
returned row count as part of the result, instead of assuming a successful
network round trip means the business action happened.



- **Optimistic version:** An optimistic version is an application-managed number changed on every
successful guarded update. 

- **Compare-and-set:** A compare-and-set operation updates only when
the current state matches a supplied expectation. 

- **Precondition:** A precondition is the
condition that must still hold when a write occurs. 

- **Stale write:** A stale write uses an
expectation that no longer matches current state. 

- **Schedule:** A schedule is an ordered
list of actions by named transactions. 

- **Visibility trace:** A visibility trace records what
each session actually observed under its isolation level and action order.

The default lesson is a deterministic single-session model. It proves the
behavior of version and capacity predicates, including negative controls.
It cannot prove a race, blocking, deadlock, or snapshot anomaly. The optional
lab supplies a separately owned committed schema so two real sessions can
observe one row. Its exact preparation and cleanup are explicit below.
Neither a modeled schedule nor a selected isolation setting counts as an
observed concurrent execution. Preserve session labels, statements, returned
rows, commit order, and errors when claiming that evidence.

## Syntax anatomy and query reasoning

`UPDATE concurrency_stock SET available = available - 2, version = version + 1
WHERE sku = 'A' AND version = 1 AND available >= 2 RETURNING sku, available,
version` combines three checks. The key selects the intended item, the version
tests the caller's earlier observation, and capacity prevents negative stock.
RETURNING exposes the committed candidate state to the caller inside the
current transaction. A zero-row result is a failed precondition, not a SQL
exception. The caller must distinguish that outcome and decide whether to
reread, reject, or retry under the product's rules.

Always increment the version in every write path, including administrative
changes that invalidate an old observation. A version cannot protect against
writers that bypass it. Keep the read and its associated expected version
together. An unconditional assignment derived from an old value can overwrite
someone else's work even when both statements execute successfully. For simple
capacity changes an arithmetic guarded UPDATE can avoid a separate read, but
multi-row invariants may require stronger coordination or serializable retries.
A single-row version predicate does not prove a cross-row business invariant.

At READ COMMITTED a statement normally sees a new snapshot when it begins;
at REPEATABLE READ a transaction retains its established view. Competing writes
under stronger isolation can raise a serialization failure rather than simply
returning zero rows. Retrying requires a new transaction and a fresh read,
not replaying only the final statement in an aborted transaction. A successful
UPDATE is also provisional until COMMIT. Losing the commit acknowledgement
creates an unknown outcome that needs an idempotency contract, covered in the
bridge and replication tracks, rather than an unconditional retry.

## Worked example / walkthrough

Run these in the complete learner file so the temporary fixture and transaction are present. The fixture values are fixed; the examples never depend on the current clock. Predict each result before running it.

### Example 1: Guard an update and inspect its result

```sql
SAVEPOINT worked_success;
UPDATE concurrency_stock
SET available=available-2,version=version+1
WHERE sku='A' AND version=1 AND available>=2
RETURNING sku,available,version;
ROLLBACK TO SAVEPOINT worked_success;
RELEASE SAVEPOINT worked_success;
```

The returned row is A with stock 3 and version 2. The savepoint is a local experiment boundary; rolling back to it restores A to stock 5 and version 1 for later examples. The output grain is one successfully updated SKU. No returned row means no row met all preconditions. This demonstration is deterministic and does not involve another connection.

**Expected:** One updated row, columns sku, available, version: (A,3,2). After rollback the fixture is (A,5,1).

### Example 2: A stale expectation does not write

```sql
UPDATE concurrency_stock
SET available=available-1,version=version+1
WHERE sku='A' AND version=99 AND available>=1
RETURNING sku,available,version;
SELECT sku,available,version FROM concurrency_stock WHERE sku='A';
```

No row matches version 99, so PostgreSQL reports UPDATE 0 and RETURNING contains no rows. The following SELECT proves the stock and version stayed unchanged. An application that reports success merely because the statement raised no exception would mislead the user. Do not immediately remove the version condition to make the update succeed; that deletes the protection instead of handling the conflict.

**Expected:** Zero updated rows, then one inspected row (A,5,1), columns sku, available, version.

## Exercises

Attempt these in order in the ignored working copy, before its final rollback. Write the output grain and a prediction before execution. Compare the actual identities and values with each contract. A query merely running is not sufficient evidence. Hints are optional and leave the answer construction to you.

1. **Perform a guarded reservation.**

   **Inputs/evidence:** For sql-concurrency-01 Exercise 1, Inside a savepoint, reserve two A units using expected version 1 and a nonnegative-capacity predicate. Return sku, available, version, then roll back the attempt.

   **Expected result/shape:** For sql-concurrency-01 Exercise 1, One updated SKU row, columns sku, available, version: (A,3,2). After savepoint rollback, A is (A,5,1). No final ORDER BY is needed for the unique sku update.

   **Verify:** For sql-concurrency-01 Exercise 1, Inspect RETURNING (A,3,2), then inspect restored A state (5,1) after savepoint rollback. A successful command tag alone does not establish the version and capacity outcome.

   **Progressive hint:** Put version and capacity conditions in WHERE, not only in an earlier SELECT.

2. **Reject a stale expected version.**

   **Inputs/evidence:** For sql-concurrency-01 Exercise 2, Try reserving one A unit with expected version 99. Return sku, available, version for any successful update and inspect the row afterward.

   **Expected result/shape:** For sql-concurrency-01 Exercise 2, Zero returned rows with columns sku, available, version. A remains available 5 and version 1; SQL execution itself succeeds with UPDATE 0.

   **Verify:** For sql-concurrency-01 Exercise 2, Require zero RETURNING rows and unchanged A state available=5,version=1. Removing the version condition would discard the requested stale-write protection.

   **Progressive hint:** A failed precondition is an ordinary zero-row outcome.

3. **Reject insufficient capacity independently.**

   **Inputs/evidence:** For sql-concurrency-01 Exercise 3, Try reserving two B units with correct expected version 1. Return sku, available, version on success and inspect B afterward.

   **Expected result/shape:** For sql-concurrency-01 Exercise 3, Zero returned rows, columns sku, available, version. B remains (B,1,1), proving the capacity condition can fail even with a current version.

   **Verify:** For sql-concurrency-01 Exercise 3, Require zero RETURNING rows and unchanged B state available=1,version=1. The current version and failed capacity distinguish this outcome from the stale-version case.

   **Progressive hint:** Use a boundary that differs from the stale-version example.

4. **Model two callers sharing an old version.**

   **Inputs/evidence:** For sql-concurrency-01 Exercise 4, Inside one savepoint, apply caller One reserving two A units at version 1, then caller Two reserving one A unit with the same old version. Return caller, affected_rows from both attempts.

   **Expected result/shape:** For sql-concurrency-01 Exercise 4, Two model-trace rows keyed by caller, columns caller, affected_rows; final ORDER BY caller: One affects 1, Two affects 0. A is temporarily (A,3,2), then rollback restores the fixture. This is a sequential model, not a concurrent trace.

   **Verify:** For sql-concurrency-01 Exercise 4, Inspect trace One=1 affected row and Two=0, plus temporary A state (3,2). Rollback restores (5,1). Label the result a sequential model rather than a concurrent execution trace.

   **Progressive hint:** Execute the two writes in distinct statements and save their actual returned counts.

5. **Verify a no-change read result.**

   **Inputs/evidence:** For sql-concurrency-01 Exercise 5, Return sku, available, version for both initial stock rows, ordered by sku. State what a single-session read proves and what a two-session isolation claim additionally needs.

   **Expected result/shape:** For sql-concurrency-01 Exercise 5, Two SKU rows, columns sku, available, version; final ORDER BY sku: (A,5,1),(B,1,1). A genuine isolation trace also needs session names, isolation level, ordered statements, commit boundary, and observations.

   **Verify:** For sql-concurrency-01 Exercise 5, Inspect initial rows (A,5,1),(B,1,1). A separate isolation claim requires actual A-session reads, B-session write/commit order, and the selected isolation level from the optional lab.

   **Progressive hint:** The SELECT verifies current fixture state, not the visibility of another transaction.

6. **Transfer the guard to an atomic replenishment.**

   **Inputs/evidence:** For sql-concurrency-01 Exercise 6, Inside a savepoint, add three B units using expected version 1, increment version, and return sku, available, version. Then retry the same old expectation and prove it affects zero rows.

   **Expected result/shape:** For sql-concurrency-01 Exercise 6, One initial updated SKU row, columns sku, available, version: (B,4,2). A second attempt using version 1 returns zero rows. Rollback leaves B at (B,1,1).

   **Verify:** For sql-concurrency-01 Exercise 6, Inspect initial RETURNING (B,4,2), then require zero rows for repeating old version 1, and inspect restored (B,1,1) after rollback. This tests stale-write protection, not unknown-commit recovery.

   **Progressive hint:** Every mutation path must advance the same version contract, including replenishment.

## Optional observed two-session lab

The default file above is a model. To observe visibility, this optional lab
commits exactly one table in the course-owned `sql_concurrency_live` schema.
It uses two terminals connected to the same local disposable database, needs
no extension or superuser role, and must finish with the explicit cleanup.
The preparation refuses to replace an existing schema. Stop if another learner
is already using that schema; do not erase their work.

Run from the repository root, in PowerShell or a macOS/Linux terminal:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/concurrency/prepare.sql
```

Open **Terminal A** and **Terminal B**, each with:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training
```

In A, establish a view and leave the transaction open:

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL statement_timeout = '10s';
SELECT sku,available,version FROM sql_concurrency_live.stock WHERE sku='A';
```

Expect `(A,5,1)`. In B, make and commit one guarded write:

```sql
BEGIN;
SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '10s';
UPDATE sql_concurrency_live.stock
SET available=available-1,version=version+1
WHERE sku='A' AND version=1 AND available>=1
RETURNING sku,available,version;
COMMIT;
```

B returns `(A,4,2)`. In A, run the same SELECT again, then `ROLLBACK`.
The second READ COMMITTED statement now shows `(A,4,2)`. Record session,
isolation, action order, both A results, and B's commit. This transcript is
visibility evidence; the single-session default script is not.

For a contrasting run, reset only the fixture row in B using the following
statement when both previous transactions have ended:

```sql
UPDATE sql_concurrency_live.stock SET available=5,version=1 WHERE sku='A';
```

This reset is fixture preparation only. It deliberately resets the version
and must never be copied into an application write path. Repeat A's sequence
with `BEGIN ISOLATION LEVEL REPEATABLE READ;`. Run A's first SELECT before
B updates and commits. A's second SELECT remains `(A,5,1)` within that
transaction; after A rolls back, a new SELECT shows `(A,4,2)`. If A had not
established its first snapshot before B's commit, it could instead establish
the later view, which is why action order belongs in the evidence. This lab
observes reads; it does not reproduce a serialization failure or deadlock.
Do not add timing sleeps to substitute for the explicit checkpoints.

Finally issue `ROLLBACK;` in both terminals to release any forgotten
transaction, quit both with `\q`, and run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/fixtures/concurrency/cleanup.sql
```

Cleanup drops the known table and then its empty course schema without CASCADE;
unexpected extra objects cause a visible failure instead of silent deletion.
`verify_cleanup.sql` can confirm the schema is absent. If a client disconnects
mid-experiment, its uncommitted transaction is rolled back, but the explicitly
committed fixture still needs this cleanup. Nothing here changes server
configuration, roles, extensions, replication, or another database.

## Self-check

- Why is a successful SQL execution different from a successful reservation?
- Which concurrency claims cannot be made from this deterministic model?
- Why must a replenishment advance the same version used by a reservation?

Keep your actual query and transcript. Explain one incorrect alternative and the exact fixture row that exposes it. A passing worked example does not prove an unattempted exercise. Revisit a failed prediction after taking a break, then answer the retrieval questions without looking at the code.

## Common pitfalls

- If UPDATE 0 is treated as success, inspect RETURNING or affected-row count before debugging connection code.

- If a stale reader still succeeds, audit every write path for an unconditional update or missing version increment.

- If two terminals cannot see each other's fixture, check whether you used temporary tables or uncommitted setup. Use only the explicit optional shared fixture below.

## Next step

Transfer these contracts to the integrated bridge capstone after checking its direct prerequisites.

Concrete next target: [Integrated evidence capstone](../../../bridge/professional/companion-guides/bridge_capstone_01_evidence_review.md).

## Reference

The course works offline after setup. These optional official references describe the PostgreSQL semantics used here:

- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/transaction-iso.html)

## Ask Codex about this lesson

The lesson and expected observations are sufficient offline. For optional coaching, copy:

```text
Tutor me through sql-concurrency-01: Isolation Traces and Optimistic Concurrency using the checked-in $guide-ds60sqlpy-learning skill.
Guide: sql/professional/companion-guides/sql_concurrency_01_isolation_and_versions.md
Answer-free learner: sql/professional/lessons/sql_concurrency_01_isolation_and_versions.sql
Direct prerequisite boundary: sql-39, sql-test-01.
Teach at the advanced level, defining each new term before relying on it.
Focus on Express a single-row write precondition in an atomic UPDATE predicate. Distinguish stale versions, insufficient capacity, and successful writes from returned evidence.
Use the guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval loop.
Keep solutions/ closed until I ask after an honest attempt. Do not read, quote,
or summarize the official solution before that boundary.
Prefer Create/open guided SQL notebook and its ignored .learning/sql/sql-concurrency-01/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
