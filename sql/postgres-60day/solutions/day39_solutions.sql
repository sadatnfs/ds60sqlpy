-- Day 39 solutions: locks and deadlocks
BEGIN;
SET search_path TO training, public;

-- Deadlocks require two concurrent sessions. The prevention rule is to lock
-- shared keys in a consistent order in every transaction.
WITH keys AS (
  SELECT order_id
  FROM orders
  ORDER BY order_id
  LIMIT 2
)
SELECT o.order_id
FROM orders o
JOIN keys k USING (order_id)
ORDER BY o.order_id
FOR UPDATE OF o;

-- Exercise 3: a runnable job-queue pattern.
CREATE TEMP TABLE solution_jobs (
  job_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  payload text NOT NULL,
  processed_at timestamptz
);
INSERT INTO solution_jobs(payload)
VALUES ('first'), ('second'), ('third'), ('fourth');

SELECT job_id, payload
FROM solution_jobs
WHERE processed_at IS NULL
ORDER BY job_id
FOR UPDATE SKIP LOCKED
LIMIT 2;

-- Transaction-scoped advisory locks release automatically at transaction end.
SELECT pg_try_advisory_xact_lock(3901) AS acquired_course_lock;

-- Manual deadlock reproduction:
-- A: BEGIN; UPDATE orders SET status=status WHERE order_id=1;
-- B: BEGIN; UPDATE orders SET status=status WHERE order_id=2;
-- A: UPDATE orders SET status=status WHERE order_id=2;
-- B: UPDATE orders SET status=status WHERE order_id=1; -- deadlock detected
-- Inspect pg_locks from a third session before issuing the final statement.

ROLLBACK;
