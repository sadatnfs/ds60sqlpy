# Day 39 — Solutions: Locks and Deadlocks

Deadlocks and lock waits require concurrent sessions. A single sequential
solution file cannot fully execute these labs. Use two terminals for the
staged commands and a third terminal when observing a wait.

## Exercise 1 — Reproduce and observe a deadlock

Session A locks order 1:

```text
BEGIN;
SET LOCAL search_path TO training, public;
SELECT order_id FROM orders WHERE order_id = 1 FOR UPDATE;
```

Session B locks order 2:

```text
BEGIN;
SET LOCAL search_path TO training, public;
SELECT order_id FROM orders WHERE order_id = 2 FOR UPDATE;
```

Session A now waits for B:

```text
UPDATE training.orders
SET total_amount = total_amount
WHERE order_id = 2;
```

Before completing the cycle, run this safe diagnostic in a third session:

```sql
SELECT a.pid,
       a.state,
       l.locktype,
       l.relation::regclass AS relation,
       l.mode,
       l.granted,
       pg_blocking_pids(a.pid) AS blocking_pids
FROM pg_stat_activity a
JOIN pg_locks l ON l.pid = a.pid
WHERE cardinality(pg_blocking_pids(a.pid)) > 0
   OR NOT l.granted
ORDER BY a.pid, l.granted, l.locktype;
```

Then Session B completes the cycle:

```text
UPDATE training.orders
SET total_amount = total_amount
WHERE order_id = 1;
```

PostgreSQL detects the cycle and aborts one transaction with
`deadlock detected`; roll back both sessions afterward. The detector normally
resolves the deadlock quickly, so the diagnostic captures the lock wait before
the final cycle edge rather than promising to freeze a deadlock.

## Exercise 2 — Prevent the deadlock with consistent ordering

Every worker must acquire the same set of row locks in the same order:

```sql
BEGIN;
SET LOCAL search_path TO training, public;
SET LOCAL lock_timeout = '5s';

SELECT order_id,
       total_amount
FROM orders
WHERE order_id IN (1, 2)
ORDER BY order_id
FOR UPDATE;

ROLLBACK;
```

Run the same transaction in both sessions. One may wait, but neither can hold
order 2 while requesting order 1, so this pair does not form a cycle.

## Exercise 3 — Job-queue claiming with `SKIP LOCKED`

```sql
BEGIN;
SET LOCAL search_path TO training, public;

SELECT order_id,
       order_date,
       status
FROM orders
WHERE status = 'placed'
ORDER BY order_id
LIMIT 5
FOR UPDATE SKIP LOCKED;

ROLLBACK;
```

To see queue behavior, keep the first session open before `ROLLBACK` and run the
same `SELECT` in Session B. B skips A's locked rows and can claim a different
batch.

## Pitfalls

- `SKIP LOCKED` intentionally returns an inconsistent view and is appropriate
  for queues, not ordinary reports.
- `NOWAIT` fails immediately; `lock_timeout` bounds a wait; neither prevents a
  badly ordered locking design.
- Row locks are held until transaction end. Keep transactions short and never
  wait for user input while holding them.
- `total_amount = total_amount` is used only to request a write lock without
  changing course data; do not use no-op updates as a production lock pattern.

## Exercise 4 — Predict NOWAIT

`FOR UPDATE NOWAIT` raises SQLSTATE `55P03` immediately when a conflicting lock
already exists. The executable solution explains the two-session check without
blocking automated validation.

## Exercise 5 — Claim and update queue rows

The locking CTE selects up to five unprocessed jobs with `SKIP LOCKED`; the
UPDATE joins only those keys and `RETURNING` proves exactly what this worker
claimed.

## Exercise 6 — Preserve lock order

Keys and the final locking SELECT both order by the unique `order_id`. Every
writer must share that order for the pattern to prevent cycles.

## Exercise 7 — Prefer transaction advisory locks

`pg_try_advisory_xact_lock` is non-blocking and releases automatically when the
transaction ends. It works only if all cooperating applications derive the same
lock key.
