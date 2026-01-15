# Day 38 — Solutions (Transactions and Isolation)

We practice transactional control and explore PostgreSQL isolation levels with reproducible anomaly demos. We also cover lock modifiers (FOR UPDATE/SHARE), NOWAIT/SKIP LOCKED, and safe patterns for concurrent workers.

Setup
- ACID recap: Atomicity, Consistency, Isolation, Durability
- Default isolation in Postgres is READ COMMITTED; others: REPEATABLE READ, SERIALIZABLE
- Session commands: `BEGIN/COMMIT/ROLLBACK`, `SET TRANSACTION ISOLATION LEVEL ...`, `SHOW default_transaction_isolation`.

Exercise 1 — Explicit transaction blocks and error handling
```sql
BEGIN;
  -- 1) Insert an order and its lines atomically
  INSERT INTO orders(order_id, customer_id, order_date, total_amount)
  VALUES (90001, 123, now(), 0.00);

  INSERT INTO order_items(order_id, product_id, quantity, unit_price, discount)
  VALUES (90001, 501, 2, 19.99, 0.10);

  -- 2) Update order total from lines
  UPDATE orders o
  SET total_amount = (
    SELECT SUM(oi.quantity*oi.unit_price*(1-oi.discount)) FROM order_items oi WHERE oi.order_id = o.order_id
  )
  WHERE o.order_id = 90001;

  -- 3) Optional validation; RAISE EXCEPTION to trigger rollback in pl/pgSQL context
COMMIT;  -- or ROLLBACK on error
```
Notes
- Group multi-table changes in one transaction to prevent partial writes.

Exercise 2 — READ COMMITTED vs REPEATABLE READ (non-repeatable reads)
Open two sessions A and B.

Session A (repeatable read):
```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT SUM(total_amount) FROM orders WHERE order_date >= CURRENT_DATE - interval '1 day';  -- take snapshot
-- keep txn open
```
Session B (separate connection):
```sql
INSERT INTO orders(order_id, customer_id, order_date, total_amount)
VALUES (90002, 321, now(), 42.00);
COMMIT;
```
Back to Session A:
```sql
SELECT SUM(total_amount) FROM orders WHERE order_date >= CURRENT_DATE - interval '1 day';
COMMIT;
```
Observation
- Under REPEATABLE READ, A keeps a consistent snapshot; both sums in A are identical, ignoring B’s committed row. Under READ COMMITTED they would differ.

Exercise 3 — Phantom reads and predicate locks
```sql
-- In REPEATABLE READ, predicate locks prevent phantoms for certain queries
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM customers WHERE country='US';  -- snapshot established
-- In another session insert a new US customer and COMMIT
-- Back here, re-run the COUNT(*): still the same in RR; new row is invisible in this txn
COMMIT;
```
Takeaway
- REPEATABLE READ avoids non-repeatable reads and phantoms (via MVCC + predicate locking) in Postgres.

Exercise 4 — SERIALIZABLE and serialization failures
```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Run two concurrent txns that both read a total, compute a new value, and update
-- One may ROLLBACK with "could not serialize access due to read/write dependencies"
-- Pattern: catch and retry the whole transaction
COMMIT;
```
Pattern
- Use application-level retry for serialization failures; keep transactions short and deterministic.

Exercise 5 — Row locking, NOWAIT, SKIP LOCKED (worker queues)
```sql
-- Safely claim work items without blocking other workers
BEGIN;
WITH claimed AS (
  SELECT id
  FROM jobs
  WHERE status='queued'
  ORDER BY created_at
  FOR UPDATE SKIP LOCKED
  LIMIT 10
)
UPDATE jobs j
SET status='in_progress'
FROM claimed c
WHERE j.id=c.id
RETURNING j.*;
COMMIT;
```
Variants
- `FOR UPDATE NOWAIT` raises an error instead of waiting; handle and move on.
- `FOR SHARE` for read locks when updating related tables.

Tips
- Keep transactions short; avoid long-held locks.
- Use explicit isolation only when needed; default READ COMMITTED is fine for many OLTP workloads.
- Prefer SKIP LOCKED patterns for concurrent consumers.
