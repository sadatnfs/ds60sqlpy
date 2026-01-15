# Day 39 — Locks, Blocking, and Deadlocks (Companion Guide)

Learning objectives
- Inspect locks and blocking chains; understand lock types and modes
- Prevent and resolve deadlocks; order operations consistently
- Use lock timeouts, NOWAIT/SKIP LOCKED, and appropriate lock granularity

Why this matters
Contention is inevitable in multi-user systems. Knowing how Postgres locks rows/tables and how to debug blocking/deadlocks keeps systems healthy and avoids outages.

Core concepts and deep dive
- Locking model (high level)
  - Row-level locks: FOR UPDATE/SHARE; not visible in pg_locks as relation locks but as transaction locks; they block conflicting row locks
  - Table-level locks: AccessShare (reads), RowShare (SELECT FOR UPDATE), RowExclusive (INSERT/UPDATE/DELETE), Share/Exclusive variants for DDL
  - DDL takes stronger locks; avoid running schema changes in peak hours without care
- Detecting blocking
  - pg_stat_activity: wait_event_type, wait_event show waits (Lock, LWLock, IO)
  - pg_locks join to pg_class/pg_stat_activity to build a blocking tree
  - Example query: identify who is blocking whom and on what relation
- Deadlocks
  - Cycle of transactions each waiting on the other; Postgres detects and aborts one with error 40P01
  - Prevention: consistent lock acquisition order, keep transactions short, avoid user interaction inside a transaction
- Timeouts and options
  - SET lock_timeout='2s'; SET statement_timeout='30s' to fail fast
  - SELECT ... FOR UPDATE NOWAIT/ SKIP LOCKED for queues
  - NOWAIT raises immediately if locked; SKIP LOCKED skips locked rows — great for work queues

Operational playbook
- On-call triage: find head blockers (idle in transaction, long-running) and terminate if needed (pg_terminate_backend)
- Add instrumentation: log_lock_waits=on; deadlock_timeout='1s'; auto_explain for long statements
- Educate developers on transaction boundaries and lock order

Practice exercises
1) Create two sessions that lock rows in opposite order to force a deadlock; then fix by ordering consistently
2) Use FOR UPDATE SKIP LOCKED to implement a simple job queue consumer
3) Add lock_timeout and observe behavior when trying to ALTER TABLE during concurrent writes

Further reading
- Locks: https://www.postgresql.org/docs/current/explicit-locking.html
- Monitoring locks: https://wiki.postgresql.org/wiki/Lock_Monitoring
