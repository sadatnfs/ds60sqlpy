# Day 31 — EXPLAIN and EXPLAIN ANALYZE: Reading Query Plans (Companion Guide)

Learning objectives
- Generate query plans with EXPLAIN and EXPLAIN ANALYZE
- Interpret nodes (Seq Scan, Index Scan/Only, Bitmap Heap/Index Scan, Hash/Sort/Merge Join)
- Understand cost estimates vs actuals; rows, loops, width
- Identify selectivity, join order, and bottlenecks; iterate toward faster plans

Why this matters
Performance work starts with visibility. Plans reveal how the optimizer will execute your SQL and why it’s slow. You’ll learn to form hypotheses and fix root causes instead of guessing.

Core concepts and deep dive
- EXPLAIN vs EXPLAIN ANALYZE
  - EXPLAIN shows the planned operations with estimated costs and rows.
  - EXPLAIN ANALYZE executes the query and adds actual time and rows for each node; use LIMIT or representative filters to keep safe.
- Anatomy of a plan node
  - Node type, relation name, filter conditions, startup/total cost, rows, width; for ANALYZE: actual time, rows, loops.
  - Rows and loops show cardinality; big mismatches (est vs act) indicate poor statistics or skew.
- Join strategies
  - Nested Loop (good for small inner); Hash Join (build hash of smaller input); Merge Join (requires sorted inputs).
- Scan types
  - Seq Scan (table scan), Index Scan (uses btree), Index Only Scan (all columns from index), Bitmap scans (efficient for many scattered rows).
- Common issues discovered via plans
  - Missing/unused index; wrong join order; unselective predicates; heavy sorts/aggregates; repeated function calls preventing index use.

Walkthrough of the day’s script
- Baseline plan for a filter on orders.total_amount > 500 and limited output; compare EXPLAIN vs EXPLAIN ANALYZE outputs.
- Multi-join with a WHERE on last 90 days shows whether indexes on (order_date) and join keys are used; track how GROUP BY feeds into ORDER BY.
- Guidance to rerun plans after creating indexes (Day 32) to observe improvements.

Tactics
- Add FILTER (WHERE ...) to aggregates to avoid extra joins; reduce plan nodes.
- Push selective predicates as early as possible; avoid functions on columns (cast/store normalized instead or use functional index).
- Use SET enable_seqscan = off temporarily to test index viability (for exploration only).

Pitfalls
- EXPLAIN ANALYZE runs the query; don’t use on destructive DML in production. Wrap in a transaction and ROLLBACK.
- Chasing micro-optimizations before fixing cardinality (stats) or schema (indexes).

Practice exercises
1) Compare plans before/after adding an index on orders(order_date) and customers(country).
2) Force Hash vs Merge vs Nested Loop joins by adjusting work_mem, enable_* GUCs; note differences.
3) Use EXPLAIN (ANALYZE, BUFFERS) to inspect I/O and cache effects.

Further reading
- EXPLAIN: https://www.postgresql.org/docs/current/using-explain.html
- Understanding plans: https://explain.depesz.com and https://tatiyants.com/pev/
