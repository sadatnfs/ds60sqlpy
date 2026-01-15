# Day 38 — Transactions and Isolation Levels (Companion Guide)

Learning objectives
- Use explicit transactions (BEGIN/COMMIT/ROLLBACK) and SAVEPOINT for multi-step changes
- Understand ACID, MVCC, and Postgres isolation levels; identify anomalies each level permits
- Implement safe retry logic for serialization failures; choose appropriate level per workload

Why this matters
Transactions are the unit of correctness. Getting isolation wrong yields phantom reads, double charges, or lost updates. Getting it right safely enables concurrency without corruption.

Core concepts and deep dive
- ACID and MVCC
  - Atomicity, Consistency, Isolation, Durability. Postgres uses MVCC (multi-version concurrency control) — readers don’t block writers and vice versa (mostly). Each transaction sees a consistent snapshot.
- Transaction control
  - BEGIN/COMMIT/ROLLBACK. Use SAVEPOINT sp; ROLLBACK TO SAVEPOINT sp; for partial undo.
  - SET TRANSACTION ISOLATION LEVEL ... within a transaction to override default.
- Isolation levels (Postgres)
  - READ COMMITTED (default): each statement sees a new snapshot; prevents dirty reads; allows non-repeatable reads and phantoms
  - REPEATABLE READ: one snapshot per transaction; prevents non-repeatable reads and phantoms in many cases due to predicate locking behavior
  - SERIALIZABLE: true serializable semantics via SSI; may abort with serialization errors under conflicts; requires retry
- Anomalies
  - Lost update: two writers overwrite; avoid with SELECT FOR UPDATE or appropriate isolation
  - Non-repeatable read: value changes between statements (allowed in READ COMMITTED)
  - Phantom read: row set changes between statements (in READ COMMITTED)
- Locking reads and writes
  - SELECT ... FOR UPDATE/SHARE/SKIP LOCKED/NO WAIT; UPDATE/DELETE acquire row locks; understand lock strength

Patterns
- Idempotent upsert with unique constraint and ON CONFLICT DO UPDATE wrapped in a transaction
- Dequeue worker: SELECT ... FOR UPDATE SKIP LOCKED LIMIT 1, process, then COMMIT
- Safe transfer: verify source balance, insert payment, update balances atomically; roll back on failure

Pitfalls
- Long transactions bloat tables (VACUUM can’t clean old versions); keep transactions short
- SERIALIZABLE without retries causes user-visible errors; implement retry with backoff on SQLSTATE '40001'
- Overusing table locks; prefer row-level locks and precise WHERE clauses

Practice exercises
1) Simulate a lost update at READ COMMITTED and then fix with FOR UPDATE or higher isolation
2) Implement a retry loop for a SERIALIZABLE transaction that occasionally conflicts
3) Use SAVEPOINT to partially roll back a multi-statement ETL step

Further reading
- Transaction isolation: https://www.postgresql.org/docs/current/transaction-iso.html
- MVCC: https://www.postgresql.org/docs/current/mvcc.html
