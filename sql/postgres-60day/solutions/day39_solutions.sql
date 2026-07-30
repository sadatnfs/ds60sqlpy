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

-- Exercise 4: NOWAIT uses the same row-lock semantics but raises SQLSTATE 55P03
-- immediately if another session owns a conflicting lock. EXPLAIN verifies the
-- runnable shape without requiring/blocking a second connection here.
EXPLAIN
SELECT order_id FROM orders WHERE order_id = 1 FOR UPDATE NOWAIT;

-- Exercise 5: select and update claimed jobs in one statement. SKIP LOCKED lets
-- concurrent workers choose different available rows.
WITH claimed AS (
  SELECT job_id
  FROM solution_jobs
  WHERE processed_at IS NULL
  ORDER BY job_id
  FOR UPDATE SKIP LOCKED
  LIMIT 5
)
UPDATE solution_jobs j
SET processed_at = clock_timestamp()
FROM claimed c
WHERE j.job_id = c.job_id
RETURNING j.job_id, j.payload, j.processed_at;

-- Exercise 6: both selection and locking retain the same unique order_id order;
-- every competing transaction must follow that contract.
WITH ordered_keys AS MATERIALIZED (
  SELECT order_id
  FROM orders
  WHERE total_amount > 900
  ORDER BY order_id
  LIMIT 5
)
SELECT o.order_id
FROM ordered_keys k
JOIN orders o USING (order_id)
ORDER BY o.order_id
FOR UPDATE OF o;

-- Exercise 7: transaction-scoped advisory locks cannot be forgotten after
-- COMMIT/ROLLBACK. The second attempt in this transaction remains successful
-- because this backend already owns the same lock.
SELECT pg_try_advisory_xact_lock(3902) AS first_attempt;
SELECT pg_try_advisory_xact_lock(3902) AS same_owner_attempt;

ROLLBACK;
