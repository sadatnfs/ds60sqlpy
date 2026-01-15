# Day 34 — Query Optimization: From Hypothesis to Faster SQL (Companion Guide)

Learning objectives
- Build a disciplined optimization loop: observe → hypothesize → change → measure
- Eliminate unnecessary work (rows, columns, joins, sorts)
- Push predicates, choose join orders, avoid function-wrapped predicates
- Use appropriate indexes and rewrite queries for sargability

Why this matters
Most slow queries do too much work. Optimization is about reducing work while preserving semantics. Small rewrites and proper indexing often yield order‑of‑magnitude gains.

Optimization loop
1) Get a baseline with EXPLAIN (ANALYZE, BUFFERS)
2) Identify dominant nodes (big time/rows/loops)
3) Hypothesize root cause (missing index, poor join order, huge sort, low selectivity)
4) Try a targeted change (index, predicate pushdown, rewrite)
5) Measure again; keep changes that reduce total time and I/O

Tactics and patterns
- Projection pruning: SELECT only needed columns; avoid SELECT * in joins and aggregates
- Predicate pushdown: Filter early in CTEs/subqueries; move filters into ON for outer joins carefully
- Sargability: WHERE date_col >= '2025-01-01' instead of WHERE date(date_col) >= '2025-01-01'
  - Add functional indexes only when needed (LOWER(email))
- Join order: Join most selective relations first; pre-aggregate many‑to‑many before joining to avoid fanout
- Aggregation: Prefer FILTER and CASE in one pass; avoid correlated subqueries computing aggregates per row
- Sorting: Ensure ORDER BY matches an index where possible; avoid unnecessary ORDER BY in subqueries
- De‑dup: Distinct often hides fanout; fix join logic or pre-aggregate rather than slapping DISTINCT
- Data volume: Pre-aggregate to day/month before windows; sample representative partitions for experimentation

Instrumentation
- EXPLAIN options: ANALYZE, BUFFERS, TIMING, VERBOSE; track shared/local read vs hit
- pg_stat_statements: find top queries by total_time and mean_time
- Auto_explain: log slow plans in dev

Practice exercises
1) Rewrite a query using date_trunc(date_col) in WHERE to a sargable range and compare plans
2) Replace a correlated subquery with a join on a pre-aggregated CTE; measure speedup
3) Remove unnecessary DISTINCT by fixing join cardinality; validate counts stay correct

Further reading
- Using EXPLAIN: https://www.postgresql.org/docs/current/using-explain.html
- Query planning: https://www.postgresql.org/docs/current/runtime-config-query.html
