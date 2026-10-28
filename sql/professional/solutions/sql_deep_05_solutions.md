# sql-deep-05: Explained reference solutions

Read [Predicate Proof, Partial Indexes, and Conditional Mutation Contracts](../companion-guides/sql_deep_05.md) and attempt its six queries before comparing. The [complete reference script](sql_deep_05_solutions.sql) recreates the same temporary fixture, runs every answer inside its own savepoint, compares exact JSON row sets with fail-fast assertions, then rolls back. No permanent table, role or service is changed.

## Exercises and reasoning

## Exercise 1: State the exact eligible queue predicate

Return job_id, priority for tenant 1 jobs whose status equals ready, ordered by priority descending then job_id ascending. Preserve the three eligible job identities and exclude another tenant, blocked, done and unknown statuses.

**Inputs/evidence:** For sql-deep-05 Exercise 1, Return job_id, priority for tenant 1 jobs whose status equals ready, ordered by priority descending then job_id ascending. Preserve the three eligible job identities and exclude another tenant, blocked, done and unknown statuses.

**Expected result/shape:** For sql-deep-05 Exercise 1, Rows are(1,10),(3,5),(6,5). The tie between 3 and 6 follows job identity, not unspecified physical row order.

**Verify:** For sql-deep-05 Exercise 1, list eligible queue IDs from the status and attempt conditions, including the NULL-attempt case, before considering whether an index could support the predicate.

```sql
SELECT job_id,priority FROM deep5_jobs WHERE tenant_id=1 AND status='ready'
ORDER BY priority DESC,job_id;
```

The predicate states both authorization-like tenant scope and operational eligibility. Equality to ready also implies the partial-index predicate, although the planner may still choose another access method. The outer ordering includes job_id so equal priorities have a deterministic presentation. Replacing the status condition with not-done would change semantics before it changed performance.

## Exercise 2: Produce a counterexample to an invalid predicate rewrite

Return job_id, status for tenant 1 rows selected by status<>done but not satisfying status=ready under a known nonready value. One row represents one counterexample, ordered by job_id. Explain why the ready-only partial index cannot cover the broader query.

**Inputs/evidence:** For sql-deep-05 Exercise 2, Return job_id, status for tenant 1 rows selected by status<>done but not satisfying status=ready under a known nonready value. One row represents one counterexample, ordered by job_id. Explain why the ready-only partial index cannot cover the broader query.

**Expected result/shape:** For sql-deep-05 Exercise 2, Only job 5 with status blocked is returned. Unknown status is not selected by ordinary inequality and is not silently classified as ready.

**Verify:** For sql-deep-05 Exercise 2, project both the original and rewritten predicates on the same rows; retain the counterexample where their truth values differ instead of relying on coincidentally equal counts.

```sql
SELECT job_id,status FROM deep5_jobs
WHERE tenant_id=1 AND status<>'done' AND status IS DISTINCT FROM 'ready'
ORDER BY job_id;
```

A single admitted blocked row disproves implication, so a ready-only index cannot supply every row of the broader predicate. The NULL-status row does not pass status<>done because that comparison is unknown. Using an explicit counterexample query is often clearer than arguing from a plan screenshot: it tests semantic equivalence before considering cost or index availability.

## Exercise 3: Inspect index existence without inventing a plan guarantee

Return one row with index_name, is_partial, key_columns, ready_rows for the temporary `deep5_ready_idx`. Use pg_index and pg_class to verify a predicate exists and there are three key attributes; count ready source rows separately. Do not assert that the planner must choose this index.

**Inputs/evidence:** For sql-deep-05 Exercise 3, Return one row with index_name, is_partial, key_columns, ready_rows for the temporary `deep5_ready_idx`. Use pg_index and pg_class to verify a predicate exists and there are three key attributes; count ready source rows separately. Do not assert that the planner must choose this index.

**Expected result/shape:** For sql-deep-05 Exercise 3, The row is `deep5_ready_idx`, true,3,4. The ready count includes tenant 2 job 4 because the index predicate restricts status, not tenant.

**Verify:** For sql-deep-05 Exercise 3, inspect the catalog index name, definition and predicate; confirm existence separately from planner choice, which would require actual EXPLAIN evidence.

```sql
SELECT c.relname AS index_name,i.indpred IS NOT NULL AS is_partial,
 i.indnkeyatts AS key_columns,
 (SELECT count(*) FROM deep5_jobs WHERE status='ready') AS ready_rows
FROM pg_index AS i JOIN pg_class AS c ON c.oid=i.indexrelid
WHERE i.indexrelid='pg_temp.deep5_ready_idx'::regclass;
```

The catalog query verifies an actual index object in the current temporary namespace rather than inferring it from source text. indpred distinguishes a partial index, and indnkeyatts counts key attributes independently of included columns. The source-row count explains the predicate population. None of these facts establishes a latency improvement or a chosen execution plan on a larger workload.

## Exercise 4: Apply a version-checked mutation and inspect its receipt

Within the exercise savepoint, increment attempts and version for job 1 only when tenant 1, status ready and expected version 1 still match. Capture ROW_COUNT and return action, affected, job_id, attempts, version in one row. Roll back after checking.

**Inputs/evidence:** For sql-deep-05 Exercise 4, Within the exercise savepoint, increment attempts and version for job 1 only when tenant 1, status ready and expected version 1 still match. Capture ROW_COUNT and return action, affected, job_id, attempts, version in one row. Roll back after checking.

**Expected result/shape:** For sql-deep-05 Exercise 4, action first, affected 1, job_id1, attempts 1, version 2. A read followed by an unguarded update is not an acceptable substitute for the combined predicate.

**Verify:** For sql-deep-05 Exercise 4, read the original value and version before writing, inspect the RETURNING receipt, and verify the committed-in-transaction state equals one increment with one version increase.

```sql
CREATE TEMP TABLE deep5_receipt(action text,affected integer) ON COMMIT DROP;
DO $write$
DECLARE changed integer;
BEGIN
 UPDATE deep5_jobs SET attempts=attempts+1,version=version+1
 WHERE job_id=1 AND tenant_id=1 AND status='ready' AND version=1;
 GET DIAGNOSTICS changed=ROW_COUNT;
 INSERT INTO deep5_receipt VALUES('first',changed);
END
$write$;
SELECT r.action,r.affected,j.job_id,j.attempts,j.version
FROM deep5_receipt AS r CROSS JOIN deep5_jobs AS j WHERE j.job_id=1 ORDER BY r.action;
```

The version and eligibility checks occur in the same UPDATE that changes the row, eliminating a separate check-then-write gap in this contract. GET DIAGNOSTICS captures the actual row count immediately after that statement. The result then verifies both the receipt and stored state. A printed UPDATE command tag alone would not establish which job changed or whether its version advanced correctly.

## Exercise 5: Reject a stale replay without a second increment

Starting from the original fixture, perform the same expected-version 1 update twice and capture first/stale receipts. Return action, affected, attempts, version for both receipts ordered by action. Both rows report final stored state; this is a sequential stale-version model, not a multi-session timing proof.

**Inputs/evidence:** For sql-deep-05 Exercise 5, Starting from the original fixture, perform the same expected-version 1 update twice and capture first/stale receipts. Return action, affected, attempts, version for both receipts ordered by action. Both rows report final stored state; this is a sequential stale-version model, not a multi-session timing proof.

**Expected result/shape:** For sql-deep-05 Exercise 5, first affected 1 and stale affected 0; both show final attempts 1, version 2. The second attempt must not raise attempts to 2.

**Verify:** For sql-deep-05 Exercise 5, apply the stale version a second time and inspect its empty RETURNING receipt; compare the final value and version with the first successful update to prove no second increment.

```sql
CREATE TEMP TABLE deep5_receipt(action text,affected integer) ON COMMIT DROP;
DO $writes$
DECLARE changed integer;
BEGIN
 UPDATE deep5_jobs SET attempts=attempts+1,version=version+1 WHERE job_id=1 AND tenant_id=1 AND status='ready' AND version=1;
 GET DIAGNOSTICS changed=ROW_COUNT; INSERT INTO deep5_receipt VALUES('first',changed);
 UPDATE deep5_jobs SET attempts=attempts+1,version=version+1 WHERE job_id=1 AND tenant_id=1 AND status='ready' AND version=1;
 GET DIAGNOSTICS changed=ROW_COUNT; INSERT INTO deep5_receipt VALUES('stale',changed);
END
$writes$;
SELECT r.action,r.affected,j.attempts,j.version FROM deep5_receipt AS r
CROSS JOIN deep5_jobs AS j WHERE j.job_id=1 ORDER BY r.action;
```

The first mutation changes the version to two, so the identical second predicate no longer matches. Zero affected rows is the expected conflict signal for this fixture, while other real cases could involve missing identity or changed eligibility. The single-session sequence verifies the state predicate and prevents an accidental double increment. It does not establish all lock, isolation or network-response behavior of a concurrent application.

## Exercise 6: Make retry identity distinct from payload identity

Implement a temporary apply_request function that stores request_key, job_id, a positive delta and applies a tenant 1 ready-job increment only on a new key. Replay the same key/payload without applying again, then reject the same key with a changed delta using SQLSTATE 22023. Return one row with request_key, first_applied, replay_applied, conflict_rejected, attempts, version, request_count.

**Inputs/evidence:** For sql-deep-05 Exercise 6, Implement a temporary apply_request function that stores request_key, job_id, a positive delta and applies a tenant 1 ready-job increment only on a new key. Replay the same key/payload without applying again, then reject the same key with a changed delta using SQLSTATE 22023. Return one row with request_key, first_applied, replay_applied, conflict_rejected, attempts, version, request_count.

**Expected result/shape:** For sql-deep-05 Exercise 6, request-a, true, false, true,1,2,1. The changed-payload attempt is caught as an expected error and must not change the job or create another request row.

**Verify:** For sql-deep-05 Exercise 6, perform an identical idempotent retry and then a conflicting payload under the same key; verify one stored receipt row and one increment, while the conflicting request raises the declared error.

```sql
CREATE FUNCTION pg_temp.apply_request(p_key text,p_job integer,p_delta integer)
RETURNS boolean LANGUAGE plpgsql AS $apply$
DECLARE inserted integer; existing deep5_requests%ROWTYPE;
BEGIN
 IF p_key IS NULL OR btrim(p_key)='' OR p_delta IS NULL OR p_delta<=0 THEN
  RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='Request identity and positive delta are required';
 END IF;
 INSERT INTO deep5_requests(request_key,job_id,delta) VALUES(p_key,p_job,p_delta) ON CONFLICT(request_key) DO NOTHING;
 GET DIAGNOSTICS inserted=ROW_COUNT;
 IF inserted=0 THEN
  SELECT * INTO existing FROM deep5_requests WHERE request_key=p_key;
  IF existing.job_id IS DISTINCT FROM p_job OR existing.delta IS DISTINCT FROM p_delta THEN
   RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='Idempotency key reused with a different payload';
  END IF;
  RETURN false;
 END IF;
 UPDATE deep5_jobs SET attempts=attempts+p_delta,version=version+1 WHERE job_id=p_job AND tenant_id=1 AND status='ready';
 IF NOT FOUND THEN RAISE EXCEPTION 'Eligible job was not found'; END IF;
 RETURN true;
END
$apply$;
CREATE TEMP TABLE deep5_apply_receipt(call_id integer,applied boolean,conflict_rejected boolean) ON COMMIT DROP;
INSERT INTO deep5_apply_receipt VALUES(1,pg_temp.apply_request('request-a',1,1),false);
INSERT INTO deep5_apply_receipt VALUES(2,pg_temp.apply_request('request-a',1,1),false);
DO $conflict$
BEGIN
 BEGIN
  PERFORM pg_temp.apply_request('request-a',1,2);
  RAISE EXCEPTION 'Expected a changed-payload rejection';
 EXCEPTION WHEN invalid_parameter_value THEN
  INSERT INTO deep5_apply_receipt VALUES(3,NULL,true);
 END;
END
$conflict$;
SELECT 'request-a' AS request_key,
 (SELECT applied FROM deep5_apply_receipt WHERE call_id=1) AS first_applied,
 (SELECT applied FROM deep5_apply_receipt WHERE call_id=2) AS replay_applied,
 (SELECT conflict_rejected FROM deep5_apply_receipt WHERE call_id=3) AS conflict_rejected,
 j.attempts,j.version,(SELECT count(*) FROM deep5_requests) AS request_count
FROM deep5_jobs AS j WHERE j.job_id=1;
```

The request-key constraint decides whether this operation is new, while stored payload fields distinguish a replay from a conflicting reuse. The request insert and job mutation share the transaction, so a failed eligible-job update cannot publish a successful request independently. The changed-payload test catches only the designated SQLSTATE; its own missing-error assertion has a different error class and cannot falsely pass. This teaches an atomic database boundary without claiming end-to-end distributed exactly-once delivery.

## Verification and transaction boundary

Every answer is materialized into a temporary answer table and compared with a literal expected row set, including column names, NULL values and deterministic order. The assertion function rejects both false and unknown Boolean results, so a NULL comparison cannot silently pass. Each exercise rolls back to its own savepoint, ensuring mutations used for one boundary case do not alter the next. The final ROLLBACK removes the full fixture. Read the first error if a contract fails; a later row count or command tag cannot repair an earlier failed assertion.
