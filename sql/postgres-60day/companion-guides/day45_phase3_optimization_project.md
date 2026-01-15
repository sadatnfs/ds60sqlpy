# Day 45 — Phase 3 Optimization Project (Companion Guide)

Goal
- Apply the last two weeks’ performance topics (plans, indexes, partitioning, materialized views, transactions/locks, monitoring) to measurably speed up a realistic workload.

What you’ll deliver
- A baseline report: representative queries, timings (EXPLAIN ANALYZE), buffer usage, and current indexes
- Targeted improvements with rationale (schema/indexing/SQL rewrites/partitioning/MV)
- Before/after measurements and a short write‑up of tradeoffs and operating guidance

Recommended workflow
1) Inventory and baseline
   - Choose 5–8 queries that represent critical paths (daily KPIs, weekly reports, top endpoints)
   - Record EXPLAIN (ANALYZE, BUFFERS) for each; snapshot pg_stat_statements entries (total_time, mean_time, calls)
2) Quick wins first
   - Projection pruning (drop SELECT *), add missing selective indexes, fix sargability (remove function‑wrapped predicates)
   - Push selective WHERE predicates earlier (CTEs/subqueries), pre‑aggregate many‑to‑many joins
3) Structure for scale
   - Add composite or covering indexes to remove Sort or enable Index Only Scan
   - Consider RANGE partitioning for large time‑series facts; verify pruning with EXPLAIN
   - Create a materialized view for expensive monthly rollups; add unique index to allow CONCURRENT refresh
4) Concurrency safety
   - Review transaction scopes; ensure no long‑running idle‑in‑transaction sessions
   - Add lock timeouts (statement_timeout, lock_timeout) and NOWAIT/SKIP LOCKED where appropriate
5) Monitor and iterate
   - Enable pg_stat_statements and auto_explain (dev) to spot regressions; document ongoing hygiene (vacuum, index bloat checks)

Quality bar
- Each improvement shows a meaningful reduction in total time or I/O (buffers) under the same plan inputs
- No correctness regressions (identical row counts/keys) and acceptable write overhead from added indexes
- Documentation explains when to refresh MVs, how partition retention works, and any retry logic for SERIALIZABLE

Stretch goals
- Add row‑level security (RLS) policies for BI users and measure impact
- Prototype BRIN on very large append‑only tables and compare to B‑tree
- Build a simple validation suite that runs post‑load and fails the pipeline on threshold breaches
