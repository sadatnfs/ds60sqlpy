# Day 37 — Partitioning and Sharding: Scale Out Strategically (Companion Guide)

Learning objectives
- Use native table partitioning to manage very large tables (by range/list/hash)
- Choose partition keys and prune effectively; understand global vs local indexes
- Distinguish partitioning (within a DB) vs sharding (across DBs/servers)

Why this matters
Large, time‑series‑like tables (events, orders) benefit from partitioning for faster scans, simpler retention, and maintenance. True sharding is an architectural decision with tradeoffs in joins and transactions.

Core concepts and deep dive (partitioning)
- Declarative partitioning
  - CREATE TABLE fact (...) PARTITION BY RANGE (order_date);
  - CREATE TABLE fact_2025_01 PARTITION OF fact FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
- Pruning
  - Planner eliminates partitions that don’t match constraints; ensure predicates reference the partition key
- Indexes
  - Local indexes exist per partition; global indexes are not supported; consider a covering index per hot partition
- Maintenance
  - ATTACH/DETACH partitions for rolling windows; drop old partitions instantly (DTRT for retention)
  - VACUUM/ANALYZE per partition; autovacuum runs per partition
- Partitioning methods
  - RANGE (time windows), LIST (country/tenant), HASH (even distribution when no natural range)

Sharding (overview)
- Horizontal split across servers/clusters (by tenant, region, hash)
- Pros: write/read scaling, isolation; Cons: cross‑shard joins/transactions are hard, added ops complexity
- Coordination approaches: application‑driven routing, FDWs, logical replication, proxies

Design patterns
- Time‑series events RANGE partitioned by day/month; keep last N partitions; archive or drop older ones
- Multi‑tenant LIST partitioning with per‑tenant isolation; attach/detach for migrations

Pitfalls
- Non‑sargable filters prevent partition pruning (e.g., WHERE date(order_ts)=...); use ranges
- Too many tiny partitions increase planning overhead; keep partition count reasonable (hundreds ok, thousands need care)

Practice exercises
1) Create a RANGE‑partitioned orders table by month; insert rows across months; verify pruning with EXPLAIN
2) Implement retention: detach and drop partitions older than 12 months
3) Add partition‑local indexes and compare plan/latency for key lookups

Further reading
- Partitioning: https://www.postgresql.org/docs/current/ddl-partitioning.html
- Sharding approaches: https://wiki.postgresql.org/wiki/Sharding
