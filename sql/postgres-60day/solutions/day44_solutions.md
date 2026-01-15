# Day 44 — Solutions (Monitoring and Diagnostics)

We set up query/instance monitoring, inspect live activity, and capture slow plans automatically. Tools include pg_stat_statements, auto_explain, pg_stat_activity/pg_locks, and log settings.

Setup
- Enable pg_stat_statements (in postgresql.conf + shared_preload_libraries)
```conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```
Create extension and reset when needed:
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT pg_stat_statements_reset();
```

Exercise 1 — Top queries by total/mean time and calls
```sql
SELECT queryid,
       calls,
       round(total_exec_time/1000,2) AS total_s,
       round(mean_exec_time ,2)      AS mean_ms,
       rows,
       left(query,120) AS sample
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```
Interpretation
- Focus on highest total time or highest mean time (after filtering utility statements). Combine with table sizes and indexes.

Exercise 2 — Live sessions, blockers, wait events
```sql
-- Active sessions
SELECT pid, usename, state, wait_event_type, wait_event,
       now()-query_start AS running, left(query,120) AS qry
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY running DESC
LIMIT 30;

-- Blocking chains
SELECT bl.pid AS waiting_pid, gr.pid AS blocking_pid,
       a1.query AS waiting_q, a2.query AS blocking_q
FROM pg_locks bl
JOIN pg_locks gr ON (bl.locktype, bl.relation, bl.page, bl.tuple, bl.classid, bl.objid, bl.objsubid) IS NOT DISTINCT FROM
                   (gr.locktype, gr.relation, gr.page, gr.tuple, gr.classid, gr.objid, gr.objsubid)
JOIN pg_stat_activity a1 ON a1.pid=bl.pid
JOIN pg_stat_activity a2 ON a2.pid=gr.pid
WHERE NOT bl.granted AND gr.granted AND bl.pid<>gr.pid
LIMIT 20;
```

Exercise 3 — Auto-explain slow plans to logs
postgresql.conf:
```conf
shared_preload_libraries = 'auto_explain,pg_stat_statements'
auto_explain.log_min_duration = '200ms'   # log plans slower than 200ms
auto_explain.log_analyze = on
auto_explain.log_buffers = on
auto_explain.log_triggers = on
auto_explain.log_verbose = on
```
Why
- Captures full plans for slow queries in server logs without changing application code. Tune thresholds per environment.

Exercise 4 — Server log hygiene
```conf
log_min_duration_statement = 500ms
log_checkpoints = on
log_autovacuum_min_duration = 0
log_lock_waits = on
log_temp_files = 0
log_statement = 'none'  # keep low in prod; escalate on demand
```
Tips
- Use a log shipper (e.g., fluent-bit) to centralize logs; add dashboards/alerts for spikes.

Exercise 5 — I/O and vacuum stats
```sql
-- PG16+: pg_stat_io for detailed I/O; earlier PG: pg_statio_* views
SELECT * FROM pg_stat_bgwriter;
SELECT relname, n_dead_tup, vacuum_count, autovacuum_count
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
```
Actions
- Bump autovacuum scale factors/thresholds on hot tables; schedule manual VACUUM (VERBOSE, ANALYZE) if needed.

Runbook
- When latency spikes: check active sessions, blocking, long-running queries, recent deploys, and resource saturation. Capture plans (auto_explain) and top pg_stat_statements. Open a ticket with plan/regressions attached.
