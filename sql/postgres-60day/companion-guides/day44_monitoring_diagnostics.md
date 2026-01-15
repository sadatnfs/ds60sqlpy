# Day 44 — Monitoring and Diagnostics (Companion Guide)

Learning objectives
- Observe database health with pg_stat_* views and background process metrics
- Identify slow/expensive queries via pg_stat_statements and logs (auto_explain)
- Track bloat, vacuum activity, I/O pressure, and connection/session issues

Why this matters
Performance and reliability require continuous visibility. Knowing what to watch and how to interpret it lets you fix issues proactively and triage incidents quickly.

Core concepts and deep dive
- Sessions and waits
  - pg_stat_activity: state (active/idle/idle in transaction), query, xact_start, wait_event(_type)
  - Long‑running transactions block vacuum → bloat; kill or nudge offenders
- Top queries with pg_stat_statements (enable in postgresql.conf)
  - CREATE EXTENSION pg_stat_statements;
  - Columns: total_time, mean_time, calls, rows; normalize by calls to find outliers
  - Reset stats thoughtfully (SELECT pg_stat_statements_reset())
- Plans in logs with auto_explain
  - shared_preload_libraries='auto_explain'; auto_explain.log_min_duration='200ms'; auto_explain.log_analyze=on
  - Captures plans only for slow statements; inspect node time/loops and buffers
- Table/index stats
  - pg_stat_user_tables: seq_scan, idx_scan, n_tup_ins/upd/del, vacuum/analyze counts
  - pg_stat_user_indexes and pg_index: idx_scan usage, size via pg_relation_size
  - Bloat heuristics: compare relpages to expected; consider pgstattuple extension for accuracy
- I/O and caching (PG16+)
  - pg_stat_io shows read/write/wal I/O by backend type
  - EXPLAIN (ANALYZE, BUFFERS) to see shared/local read hits vs reads
- Vacuum and autovacuum
  - Monitor autovacuum activity; freeze age (400M) risk; tune autovacuum_vacuum_cost_limit/scale_factor
- Connections and pools
  - max_connections vs workload; prefer pgbouncer for pooling; check too many idle sessions

Operational playbook
- Daily dashboard: top queries (last 24h), slowest plans, vacuum lag, bloat candidates, blocked queries
- On incident: capture pg_stat_activity, lock tree, top pg_stat_statements; attach relevant logs
- Periodic hygiene: drop unused indexes (idx_scan=0), refresh stats, tune autovacuum per table

Practice exercises
1) Enable pg_stat_statements and list top 10 queries by total_time and mean_time
2) Turn on auto_explain and capture a slow plan; identify the dominant node
3) Compute a bloat candidate list and size the largest relations

Further reading
- pg_stat_statements: https://www.postgresql.org/docs/current/pgstatstatements.html
- Monitoring: https://www.postgresql.org/docs/current/monitoring-stats.html
- auto_explain: https://www.postgresql.org/docs/current/auto-explain.html
