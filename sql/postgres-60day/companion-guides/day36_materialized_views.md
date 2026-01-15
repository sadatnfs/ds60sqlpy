# Day 36 — Materialized Views: Caching Expensive Results (Companion Guide)

Learning objectives
- Create and refresh materialized views to cache heavy query results
- Decide between VIEW vs MATERIALIZED VIEW; REFRESH options (CONCURRENTLY)
- Use indexes on materialized views and schedule refreshes safely

Why this matters
Long-running aggregations and joins can be precomputed into a materialized view (MV) to accelerate dashboards and downstream queries while keeping logic centralized.

Core concepts and deep dive
- VIEW vs MATERIALIZED VIEW
  - VIEW is just a stored query; runs every time
  - MATERIALIZED VIEW stores the result set; must be refreshed to reflect source changes
- REFRESH MATERIALIZED VIEW
  - REFRESH MATERIALIZED VIEW mv; (blocking, atomically replaces contents)
  - REFRESH MATERIALIZED VIEW CONCURRENTLY mv; (non-blocking reads) requires a unique index on the MV covering all rows
- Indexing MVs
  - Create indexes on columns used by consumers (filters/joins/order)
- Dependency management
  - MVs depend on base tables; use COMMENT ON and naming to document lineage
- Incremental refresh patterns (concept)
  - Native incremental refresh not built-in; emulate with partitioned MVs or staging delta tables

Patterns
- Precompute monthly/category revenue with dimensions joined; index (month, category)
- Build a search-friendly MV with denormalized text for full-text search

Pitfalls
- Forgetting the unique index prevents CONCURRENTLY refresh
- Stale data: document freshness and add a last_refreshed timestamp column
- Refresh storms: schedule refresh during off-peak; consider REFRESH only changed partitions

Practice exercises
1) Create an MV for monthly revenue by country and category; index (month, country, category)
2) Compare query latency against the raw query; measure with EXPLAIN (ANALYZE)
3) Add a scheduler (cron/systemd) to refresh nightly; log refresh duration

Further reading
- Materialized views: https://www.postgresql.org/docs/current/sql-creatematerializedview.html
- Concurrent refresh: https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html
