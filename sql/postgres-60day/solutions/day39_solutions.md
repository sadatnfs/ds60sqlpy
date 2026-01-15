# Day 39 — Solutions (Locks and Deadlocks)

We explore PostgreSQL lock types, how to inspect blocking, reproduce a deadlock, and apply timeouts/ordering to avoid them. We also cover advisory locks for application‑level coordination.

Setup
- Inspect locks: `SELECT * FROM pg_locks JOIN pg_stat_activity USING (pid);`
- Helpful settings: `SET lock_timeout = '3s';` `SET statement_timeout = '30s';`
- Lock modes (row level): FOR UPDATE/SHARE + NOWAIT/SKIP LOCKED. Table locks: ACCESS SHARE/EXCLUSIVE etc.

Exercise 1 — Identify blockers and waiters
```sql
-- Who is blocking whom?
SELECT bl.pid        AS waiting_pid,
       a_us.usename  AS waiting_user,
       bl.locktype, bl.mode, bl.relation::regclass AS rel,
       now() - a_bl.query_start AS waiting_for,
       a_bl.query      AS waiting_query,
       a_gr.pid       AS blocking_pid,
       a_gr.query     AS blocking_query
FROM pg_locks bl
JOIN pg_stat_activity a_bl ON a_bl.pid = bl.pid AND NOT bl.granted
JOIN pg_locks gr ON gr.locktype = bl.locktype AND gr.relation = bl.relation AND gr.granted
JOIN pg_stat_activity a_gr ON a_gr.pid = gr.pid
JOIN pg_stat_activity a_us ON a_us.pid = bl.pid
WHERE bl.pid <> gr.pid;
```
Notes
- Join pg_locks to pg_stat_activity to see SQL text and durations. Add filters for a specific relation.

Exercise 2 — Reproduce a simple deadlock (two sessions A/B)
Session A:
```sql
BEGIN;
UPDATE customers SET segment='gold' WHERE customer_id=1;  -- locks row 1
-- keep txn open
```
Session B:
```sql
BEGIN;
UPDATE customers SET segment='silver' WHERE customer_id=2;  -- locks row 2
-- keep txn open
```
Now, still in A:
```sql
UPDATE customers SET segment='gold' WHERE customer_id=2;  -- waits on B
```
Still in B:
```sql
UPDATE customers SET segment='silver' WHERE customer_id=1; -- deadlock; one txn will ROLLBACK
```
Takeaway
- Always update rows in a consistent key order (e.g., ascending customer_id) across code paths to avoid cycles.

Exercise 3 — Row‑level locking options
```sql
-- Avoid waiting indefinitely
SELECT *
FROM jobs
WHERE status='queued'
FOR UPDATE NOWAIT;  -- error immediately if locked by another txn

-- Nonblocking worker queue pattern
WITH take AS (
  SELECT id FROM jobs WHERE status='queued' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 10
)
UPDATE jobs j
SET status='in_progress'
FROM take t
WHERE j.id=t.id
RETURNING j.*;
```
When to use
- NOWAIT for fast‑fail UX; SKIP LOCKED for high‑throughput worker fleets.

Exercise 4 — Advisory locks for coarse‑grained coordination
```sql
-- App‑level critical section keyed by a bigint
SELECT pg_try_advisory_lock(42);   -- returns true if acquired
-- do protected work
SELECT pg_advisory_unlock(42);
```
Notes
- Advisory locks are independent of data rows; choose a hashable key. Prefer try_ variants; avoid global bottlenecks.

Exercise 5 — Timeouts and safe defaults
```sql
SET lock_timeout = '3s';       -- give up waiting on locks quickly
SET statement_timeout = '30s'; -- prevent runaway queries
```
Guidance
- Keep transactions short; hold locks only as long as needed.
- Access rows in deterministic order to avoid deadlocks.
- Prefer SKIP LOCKED queues for concurrency, and use monitoring queries to alert on blocking chains.
