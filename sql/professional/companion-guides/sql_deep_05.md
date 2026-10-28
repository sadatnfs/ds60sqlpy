# Predicate Proof, Partial Indexes, and Conditional Mutation Contracts

**Stable ID:** `sql-deep-05`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-deep-05**. The
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
   `.learning/sql/sql-deep-05/lesson/workspace/sql/professional/lessons/sql_deep_05.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-deep-05
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced. The guide defines each new mechanism before relying on it.
- **Prerequisites:** [`sql-ops-01`](sql_ops_01_indexes_statistics_maintenance.md), [`sql-concurrency-01`](sql_concurrency_01_isolation_and_versions.md).
- **Artifacts:** [Learner SQL](../lessons/sql_deep_05.sql), [explained reference](../solutions/sql_deep_05_solutions.md), and [executable reference](../solutions/sql_deep_05_solutions.sql). Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

- State the output grain and identity before writing a query, including the NULL and duplicate policies.
- Explain the new SQL mechanism, produce each exact projected result and expose the listed counterexample.
- Verify rollback-safe behavior from inspected result rows and assertions without relying on a final success message.

## Vocabulary and concepts

- **Predicate implication:** The requirement that a query condition guarantees an index predicate before a partial index can supply all needed rows.

- **Optimistic version:** A stored revision checked in the same UPDATE that changes a row, rejecting a write based on an obsolete revision.

- **Affected-row receipt:** The actual number of rows changed by a statement, which must be interpreted before claiming a write succeeded.

- **Idempotency key:** An operation identity stored with its intended payload so a retry can be recognized without repeating the mutation.

A partial index contains only rows satisfying its predicate. A query can use it as a complete source only when its condition implies that predicate, and the planner must be able to establish the implication. status='ready' implies a ready-only index predicate. status<>'done' does not, because blocked rows also satisfy it. NULL behavior must be included in this reasoning rather than assumed away.

Semantic eligibility is different from plan selection. On a seven-row teaching table PostgreSQL may correctly choose a sequential scan even when a partial index is applicable. Inspect the index definition and the query condition, then use EXPLAIN on representative data to assess cost. Do not force an index and claim universal speed. Parameterized predicates and generic plans can also limit what the planner can prove at planning time.

A deterministic queue query needs an identity tie break after priority. An index on tenant_id, priority DESC, job_id can support that ordering for eligible ready rows, but ordering alone does not claim or mutate a job. The read and the later write must have their own concurrency contract. This lesson builds on the earlier locking and isolation modules rather than launching a multi-session workload.

Optimistic mutation puts the expected version in the UPDATE predicate and increments the version in the same statement. A client that read version 1 can change the row only while that version remains current. A later retry with version 1 changes zero rows after the first write succeeds. Zero affected rows can also mean the row is absent, in another tenant or no longer eligible, so classify the outcome rather than interpreting every zero as the same conflict.

Idempotency solves a different retry problem. If a response is lost after a successful mutation, repeating an unguarded increment applies the change twice. Store a request identity and payload in the same transaction as the mutation, enforce key uniqueness and return whether this request was newly applied. Reusing a key for a different payload must be rejected rather than treated as a harmless replay.

The executable reference uses temporary tables and single-session sequences to verify exact predicates, receipts and replay behavior. It does not claim to simulate every concurrent interleaving, crash boundary or distributed delivery scenario. Database atomicity and constraints provide mechanisms; a production service must also preserve transaction boundaries, authorization scope and durable request identity across retries.

## Worked example / walkthrough

### Example 1

```sql
SELECT job_id,status,(status='ready') AS ready_predicate,(status<>'done') AS broad_predicate
FROM deep5_jobs WHERE job_id IN(1,5,7) ORDER BY job_id;
```

One row per job_id projects both predicates. Ready job 1 satisfies both, blocked job 5 satisfies only the broad predicate, and unknown-status job 7 yields NULL for both comparisons. The blocked row disproves the claim that not-done implies ready, independently of any physical query plan.

### Example 2

```sql
SELECT job_id,priority FROM deep5_jobs
WHERE tenant_id=1 AND status='ready'
ORDER BY priority DESC,job_id;
```

The result grain is one eligible job with columns job_id and priority. IDs 1,3,6 appear with priorities 10,5,5; job_id resolves the equal-priority tie. This is a read-only ordered candidate list, not a claim that these jobs were locked or assigned to a worker.

## Exercises

1. **State the exact eligible queue predicate.** Return job_id, priority for tenant 1 jobs whose status equals ready, ordered by priority descending then job_id ascending. Preserve the three eligible job identities and exclude another tenant, blocked, done and unknown statuses.

**Inputs/evidence:** For sql-deep-05 Exercise 1, Return job_id, priority for tenant 1 jobs whose status equals ready, ordered by priority descending then job_id ascending. Preserve the three eligible job identities and exclude another tenant, blocked, done and unknown statuses.

**Expected result/shape:** For sql-deep-05 Exercise 1, Rows are(1,10),(3,5),(6,5). The tie between 3 and 6 follows job identity, not unspecified physical row order.

**Verify:** For sql-deep-05 Exercise 1, list eligible queue IDs from the status and attempt conditions, including the NULL-attempt case, before considering whether an index could support the predicate.

2. **Produce a counterexample to an invalid predicate rewrite.** Return job_id, status for tenant 1 rows selected by status<>done but not satisfying status=ready under a known nonready value. One row represents one counterexample, ordered by job_id. Explain why the ready-only partial index cannot cover the broader query.

**Inputs/evidence:** For sql-deep-05 Exercise 2, Return job_id, status for tenant 1 rows selected by status<>done but not satisfying status=ready under a known nonready value. One row represents one counterexample, ordered by job_id. Explain why the ready-only partial index cannot cover the broader query.

**Expected result/shape:** For sql-deep-05 Exercise 2, Only job 5 with status blocked is returned. Unknown status is not selected by ordinary inequality and is not silently classified as ready.

**Verify:** For sql-deep-05 Exercise 2, project both the original and rewritten predicates on the same rows; retain the counterexample where their truth values differ instead of relying on coincidentally equal counts.

3. **Inspect index existence without inventing a plan guarantee.** Return one row with index_name, is_partial, key_columns, ready_rows for the temporary `deep5_ready_idx`. Use pg_index and pg_class to verify a predicate exists and there are three key attributes; count ready source rows separately. Do not assert that the planner must choose this index.

**Inputs/evidence:** For sql-deep-05 Exercise 3, Return one row with index_name, is_partial, key_columns, ready_rows for the temporary `deep5_ready_idx`. Use pg_index and pg_class to verify a predicate exists and there are three key attributes; count ready source rows separately. Do not assert that the planner must choose this index.

**Expected result/shape:** For sql-deep-05 Exercise 3, The row is `deep5_ready_idx`, true,3,4. The ready count includes tenant 2 job 4 because the index predicate restricts status, not tenant.

**Verify:** For sql-deep-05 Exercise 3, inspect the catalog index name, definition and predicate; confirm existence separately from planner choice, which would require actual EXPLAIN evidence.

4. **Apply a version-checked mutation and inspect its receipt.** Within the exercise savepoint, increment attempts and version for job 1 only when tenant 1, status ready and expected version 1 still match. Capture ROW_COUNT and return action, affected, job_id, attempts, version in one row. Roll back after checking.

**Inputs/evidence:** For sql-deep-05 Exercise 4, Within the exercise savepoint, increment attempts and version for job 1 only when tenant 1, status ready and expected version 1 still match. Capture ROW_COUNT and return action, affected, job_id, attempts, version in one row. Roll back after checking.

**Expected result/shape:** For sql-deep-05 Exercise 4, action first, affected 1, job_id1, attempts 1, version 2. A read followed by an unguarded update is not an acceptable substitute for the combined predicate.

**Verify:** For sql-deep-05 Exercise 4, read the original value and version before writing, inspect the RETURNING receipt, and verify the committed-in-transaction state equals one increment with one version increase.

5. **Reject a stale replay without a second increment.** Starting from the original fixture, perform the same expected-version 1 update twice and capture first/stale receipts. Return action, affected, attempts, version for both receipts ordered by action. Both rows report final stored state; this is a sequential stale-version model, not a multi-session timing proof.

**Inputs/evidence:** For sql-deep-05 Exercise 5, Starting from the original fixture, perform the same expected-version 1 update twice and capture first/stale receipts. Return action, affected, attempts, version for both receipts ordered by action. Both rows report final stored state; this is a sequential stale-version model, not a multi-session timing proof.

**Expected result/shape:** For sql-deep-05 Exercise 5, first affected 1 and stale affected 0; both show final attempts 1, version 2. The second attempt must not raise attempts to 2.

**Verify:** For sql-deep-05 Exercise 5, apply the stale version a second time and inspect its empty RETURNING receipt; compare the final value and version with the first successful update to prove no second increment.

6. **Make retry identity distinct from payload identity.** Implement a temporary apply_request function that stores request_key, job_id, a positive delta and applies a tenant 1 ready-job increment only on a new key. Replay the same key/payload without applying again, then reject the same key with a changed delta using SQLSTATE 22023. Return one row with request_key, first_applied, replay_applied, conflict_rejected, attempts, version, request_count.

**Inputs/evidence:** For sql-deep-05 Exercise 6, Implement a temporary apply_request function that stores request_key, job_id, a positive delta and applies a tenant 1 ready-job increment only on a new key. Replay the same key/payload without applying again, then reject the same key with a changed delta using SQLSTATE 22023. Return one row with request_key, first_applied, replay_applied, conflict_rejected, attempts, version, request_count.

**Expected result/shape:** For sql-deep-05 Exercise 6, request-a, true, false, true,1,2,1. The changed-payload attempt is caught as an expected error and must not change the job or create another request row.

**Verify:** For sql-deep-05 Exercise 6, perform an identical idempotent retry and then a conflicting payload under the same key; verify one stored receipt row and one increment, while the conflicting request raises the declared error.

## Common mistakes and diagnosis

If a partial index seems unused, separate predicate implication from cost selection before changing planner settings. If a rewritten predicate admits blocked jobs, fix semantics before benchmarking. If a write changes zero rows, inspect identity, tenant, eligibility and version rather than retrying an unguarded update. If retries increment twice, distinguish stale-version protection from durable request identity. If an idempotency key accepts a changed payload, preserve and compare the original payload. Keep temporary training functions and tables inside the rollback boundary; no live queue or production state belongs in this lesson.

## Self-check

- Explain the row grain after each FROM, JOIN, filter, grouping or window step. Name the identity columns that prove rows were neither lost nor multiplied.
- Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next step

Transfer the same reasoning to a new small fixture before using it on larger data, then continue with [the next deepening lesson](sql_deep_06.md). Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) provides the wider route.

## Primary sources and official APIs

- [PostgreSQL17 partial indexes and predicate implication](https://www.postgresql.org/docs/17/indexes-partial.html).

- [PostgreSQL17 UPDATE and RETURNING](https://www.postgresql.org/docs/17/sql-update.html).

- [PostgreSQL17 INSERT ON CONFLICT](https://www.postgresql.org/docs/17/sql-insert.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-05: Predicate Proof, Partial Indexes, and Conditional Mutation Contracts.
Read sql/professional/companion-guides/sql_deep_05.md and sql/professional/lessons/sql_deep_05.sql. Direct prerequisites: sql-ops-01, sql-concurrency-01.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
