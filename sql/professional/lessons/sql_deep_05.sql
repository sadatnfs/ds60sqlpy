-- sql-deep-05: Predicate Proof, Partial Indexes, and Conditional Mutation Contracts
-- Guide: sql/professional/companion-guides/sql_deep_05.md
-- Use the complete file in the disposable advanced_sql_training database.

BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE deep5_jobs(job_id integer PRIMARY KEY,tenant_id integer NOT NULL,status text,priority integer NOT NULL,attempts integer NOT NULL,version integer NOT NULL) ON COMMIT DROP;
INSERT INTO deep5_jobs VALUES (1,1,'ready',10,0,1),(2,1,'done',50,2,4),(3,1,'ready',5,1,2),(4,2,'ready',99,0,1),(5,1,'blocked',100,0,3),(6,1,'ready',5,0,1),(7,1,NULL,1000,0,1);
CREATE INDEX deep5_ready_idx ON deep5_jobs(tenant_id,priority DESC,job_id) WHERE status='ready';
CREATE TEMP TABLE deep5_requests(request_key text PRIMARY KEY,job_id integer NOT NULL,delta integer NOT NULL) ON COMMIT DROP;

-- Worked example 1
SELECT job_id,status,(status='ready') AS ready_predicate,(status<>'done') AS broad_predicate
FROM deep5_jobs WHERE job_id IN(1,5,7) ORDER BY job_id;

-- Worked example 2
SELECT job_id,priority FROM deep5_jobs
WHERE tenant_id=1 AND status='ready'
ORDER BY priority DESC,job_id;

-- Exercises
-- Write attempts in your ignored working copy before the final ROLLBACK.

-- 1. State the exact eligible queue predicate
-- Inputs/evidence: For sql-deep-05 Exercise 1, Return job_id, priority for tenant 1 jobs whose status equals ready, ordered by priority descending then job_id ascending. Preserve the three eligible job identities and exclude another tenant, blocked, done and unknown statuses.
-- Expected result/shape: For sql-deep-05 Exercise 1, Rows are(1,10),(3,5),(6,5). The tie between 3 and 6 follows job identity, not unspecified physical row order.
-- Verify: For sql-deep-05 Exercise 1, list eligible queue IDs from the status and attempt conditions, including the NULL-attempt case, before considering whether an index could support the predicate.

-- 2. Produce a counterexample to an invalid predicate rewrite
-- Inputs/evidence: For sql-deep-05 Exercise 2, Return job_id, status for tenant 1 rows selected by status<>done but not satisfying status=ready under a known nonready value. One row represents one counterexample, ordered by job_id. Explain why the ready-only partial index cannot cover the broader query.
-- Expected result/shape: For sql-deep-05 Exercise 2, Only job 5 with status blocked is returned. Unknown status is not selected by ordinary inequality and is not silently classified as ready.
-- Verify: For sql-deep-05 Exercise 2, project both the original and rewritten predicates on the same rows; retain the counterexample where their truth values differ instead of relying on coincidentally equal counts.

-- 3. Inspect index existence without inventing a plan guarantee
-- Inputs/evidence: For sql-deep-05 Exercise 3, Return one row with index_name, is_partial, key_columns, ready_rows for the temporary deep 5_ready_idx. Use pg_index and pg_class to verify a predicate exists and there are three key attributes; count ready source rows separately. Do not assert that the planner must choose this index.
-- Expected result/shape: For sql-deep-05 Exercise 3, The row is deep 5_ready_idx, true,3,4. The ready count includes tenant 2 job 4 because the index predicate restricts status, not tenant.
-- Verify: For sql-deep-05 Exercise 3, inspect the catalog index name, definition and predicate; confirm existence separately from planner choice, which would require actual EXPLAIN evidence.

-- 4. Apply a version-checked mutation and inspect its receipt
-- Inputs/evidence: For sql-deep-05 Exercise 4, Within the exercise savepoint, increment attempts and version for job 1 only when tenant 1, status ready and expected version 1 still match. Capture ROW_COUNT and return action, affected, job_id, attempts, version in one row. Roll back after checking.
-- Expected result/shape: For sql-deep-05 Exercise 4, action first, affected 1, job_id1, attempts 1, version 2. A read followed by an unguarded update is not an acceptable substitute for the combined predicate.
-- Verify: For sql-deep-05 Exercise 4, read the original value and version before writing, inspect the RETURNING receipt, and verify the committed-in-transaction state equals one increment with one version increase.

-- 5. Reject a stale replay without a second increment
-- Inputs/evidence: For sql-deep-05 Exercise 5, Starting from the original fixture, perform the same expected-version 1 update twice and capture first/stale receipts. Return action, affected, attempts, version for both receipts ordered by action. Both rows report final stored state; this is a sequential stale-version model, not a multi-session timing proof.
-- Expected result/shape: For sql-deep-05 Exercise 5, first affected 1 and stale affected 0; both show final attempts 1, version 2. The second attempt must not raise attempts to 2.
-- Verify: For sql-deep-05 Exercise 5, apply the stale version a second time and inspect its empty RETURNING receipt; compare the final value and version with the first successful update to prove no second increment.

-- 6. Make retry identity distinct from payload identity
-- Inputs/evidence: For sql-deep-05 Exercise 6, Implement a temporary apply_request function that stores request_key, job_id, a positive delta and applies a tenant 1 ready-job increment only on a new key. Replay the same key/payload without applying again, then reject the same key with a changed delta using SQLSTATE 22023. Return one row with request_key, first_applied, replay_applied, conflict_rejected, attempts, version, request_count.
-- Expected result/shape: For sql-deep-05 Exercise 6, request-a, true, false, true,1,2,1. The changed-payload attempt is caught as an expected error and must not change the job or create another request row.
-- Verify: For sql-deep-05 Exercise 6, perform an identical idempotent retry and then a conflicting payload under the same key; verify one stored receipt row and one increment, while the conflicting request raises the declared error.

ROLLBACK;
