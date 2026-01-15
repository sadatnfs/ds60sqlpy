# Day 33 — Index Optimization Strategies (Companion Guide)

Learning objectives
- Choose the right index type and shape (btree vs GIN/GiST/BRIN) for your workload
- Design composite, partial, covering, and functional indexes; pick effective column order
- Maintain healthy indexes: analyze, vacuum, reindex concurrently; watch bloat and visibility

Why this matters
Indexes are not one-size-fits-all. Careful design and maintenance improve plan quality and latency while controlling write overhead and storage.

Core concepts and deep dive
- B‑tree vs GIN/GiST/BRIN
  - B‑tree: general purpose for equality/range/prefix LIKE
  - GIN: inverted index for arrays, jsonb containment, full-text search
  - GiST: geometric/range types, KNN searches
  - BRIN: block-range index for very large, naturally ordered tables (time-series), tiny footprint
- Composite indexes and order
  - Leftmost prefix rule: (a,b,c) can satisfy predicates on (a), (a,b), (a,b,c)
  - Column order: most selective and most common filter first; consider sort order to enable ORDER BY without extra Sort
- Covering indexes (INCLUDE)
  - CREATE INDEX ... ON t(a) INCLUDE (b,c) to enable Index Only Scan when visibility map permits
- Partial indexes
  - CREATE INDEX ... ON orders(order_date) WHERE status='completed' — smaller, faster; planner uses when predicate is implied
- Functional/Expression indexes
  - CREATE INDEX ... ON customers(LOWER(email)); query must use the same expression (or be provably equivalent)
- Fillfactor and clustering
  - ALTER INDEX ... SET (fillfactor=80) to reduce page splits for heavy updates
  - CLUSTER t USING idx to physically reorder table; persists until table changes; consider for range scans
- Stats and bloat
  - Adjust default_statistics_target per column for skewed data
  - Monitor pg_stat_user_indexes, pg_class relpages, pg_stat_all_indexes idx_scan; reindex concurrently to avoid locks

Tuning workflow
1) Identify slow queries (pg_stat_statements) and read plans (EXPLAIN ANALYZE)
2) Propose index candidates from predicates/join keys/sort keys
3) Validate with plans; watch index size and write overhead
4) Drop unused or redundant indexes (idx_scan=0 over long window)

Practice exercises
1) For a top-N query with ORDER BY order_date DESC WHERE customer_id=?, create a composite index that avoids a Sort.
2) Add a partial index for active products (active=true) and show plan change vs full-table index.
3) Compare BRIN vs B‑tree on a 100M‑row time-series table; measure size and query latency.

Further reading
- Indexes and types: https://www.postgresql.org/docs/current/indexes-types.html
- BRIN: https://www.postgresql.org/docs/current/brin.html
- GIN/GiST: https://www.postgresql.org/docs/current/gin.html, https://www.postgresql.org/docs/current/gist.html
