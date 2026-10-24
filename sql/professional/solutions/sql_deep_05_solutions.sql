-- sql-deep-05: complete reference queries and exact result assertions

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

CREATE FUNCTION pg_temp.assert_true(ok boolean, message text)
RETURNS void LANGUAGE plpgsql AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$;

-- Exercises

-- 1. State the exact eligible queue predicate
SAVEPOINT exercise_1;
CREATE TEMP TABLE answer_1 ON COMMIT DROP AS
SELECT job_id,priority FROM deep5_jobs WHERE tenant_id=1 AND status='ready'
ORDER BY priority DESC,job_id;
SELECT job_id,priority FROM answer_1 ORDER BY priority DESC,job_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_1) ORDER BY priority DESC,job_id),'[]'::jsonb) FROM answer_1) = '[{"job_id": 1, "priority": 10}, {"job_id": 3, "priority": 5}, {"job_id": 6, "priority": 5}]'::jsonb,'sql-deep-05 exercise 1');
ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;

-- 2. Produce a counterexample to an invalid predicate rewrite
SAVEPOINT exercise_2;
CREATE TEMP TABLE answer_2 ON COMMIT DROP AS
SELECT job_id,status FROM deep5_jobs
WHERE tenant_id=1 AND status<>'done' AND status IS DISTINCT FROM 'ready'
ORDER BY job_id;
SELECT job_id,status FROM answer_2 ORDER BY job_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_2) ORDER BY job_id),'[]'::jsonb) FROM answer_2) = '[{"job_id": 5, "status": "blocked"}]'::jsonb,'sql-deep-05 exercise 2');
ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;

-- 3. Inspect index existence without inventing a plan guarantee
SAVEPOINT exercise_3;
CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
SELECT c.relname AS index_name,i.indpred IS NOT NULL AS is_partial,
 i.indnkeyatts AS key_columns,
 (SELECT count(*) FROM deep5_jobs WHERE status='ready') AS ready_rows
FROM pg_index AS i JOIN pg_class AS c ON c.oid=i.indexrelid
WHERE i.indexrelid='pg_temp.deep5_ready_idx'::regclass;
SELECT index_name,is_partial,key_columns,ready_rows FROM answer_3 ORDER BY index_name;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_3) ORDER BY index_name),'[]'::jsonb) FROM answer_3) = '[{"index_name": "deep5_ready_idx", "is_partial": true, "key_columns": 3, "ready_rows": 4}]'::jsonb,'sql-deep-05 exercise 3');
ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;

-- 4. Apply a version-checked mutation and inspect its receipt
SAVEPOINT exercise_4;
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
CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
SELECT r.action,r.affected,j.job_id,j.attempts,j.version
FROM deep5_receipt AS r CROSS JOIN deep5_jobs AS j WHERE j.job_id=1 ORDER BY r.action;
SELECT action,affected,job_id,attempts,version FROM answer_4 ORDER BY action;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_4) ORDER BY action),'[]'::jsonb) FROM answer_4) = '[{"action": "first", "affected": 1, "job_id": 1, "attempts": 1, "version": 2}]'::jsonb,'sql-deep-05 exercise 4');
ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;

-- 5. Reject a stale replay without a second increment
SAVEPOINT exercise_5;
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
CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
SELECT r.action,r.affected,j.attempts,j.version FROM deep5_receipt AS r
CROSS JOIN deep5_jobs AS j WHERE j.job_id=1 ORDER BY r.action;
SELECT action,affected,attempts,version FROM answer_5 ORDER BY action;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_5) ORDER BY action),'[]'::jsonb) FROM answer_5) = '[{"action": "first", "affected": 1, "attempts": 1, "version": 2}, {"action": "stale", "affected": 0, "attempts": 1, "version": 2}]'::jsonb,'sql-deep-05 exercise 5');
ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;

-- 6. Make retry identity distinct from payload identity
SAVEPOINT exercise_6;
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
CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
SELECT 'request-a' AS request_key,
 (SELECT applied FROM deep5_apply_receipt WHERE call_id=1) AS first_applied,
 (SELECT applied FROM deep5_apply_receipt WHERE call_id=2) AS replay_applied,
 (SELECT conflict_rejected FROM deep5_apply_receipt WHERE call_id=3) AS conflict_rejected,
 j.attempts,j.version,(SELECT count(*) FROM deep5_requests) AS request_count
FROM deep5_jobs AS j WHERE j.job_id=1;
SELECT request_key,first_applied,replay_applied,conflict_rejected,attempts,version,request_count FROM answer_6 ORDER BY request_key;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_6) ORDER BY request_key),'[]'::jsonb) FROM answer_6) = '[{"request_key": "request-a", "first_applied": true, "replay_applied": false, "conflict_rejected": true, "attempts": 1, "version": 2, "request_count": 1}]'::jsonb,'sql-deep-05 exercise 6');
ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;

ROLLBACK;
