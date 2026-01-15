# Day 32 — Index Fundamentals: B‑tree, Covering, and Selectivity (Companion Guide)

Learning objectives
- Understand how B‑tree indexes work and when the planner uses them
- Create single- and multi-column indexes; choose column order
- Use covering (Index Only Scan) and partial/functional indexes
- Measure selectivity and plan changes with EXPLAIN

Why this matters
Indexes are the primary lever for performance on OLTP/OLAP queries. The right index turns seconds into milliseconds; the wrong one bloats storage and slows writes.

Core concepts and deep dive
- B‑tree basics
  - Balanced tree on sorted keys; supports =, <, >, BETWEEN, prefix LIKE, IN
  - Multi-column: leftmost prefix rule — (a,b) can serve predicates on a, or a+b; not on b alone
- Cardinality/selectivity
  - High selectivity (few rows) benefits most; low selectivity (many rows) may prefer Seq Scan
  - Use pg_stats (n_distinct, most_common_vals) to reason about selectivity
- Covering indexes
  - Index Only Scan if all needed columns are in the index and visibility map allows
  - INCLUDE clause (Postgres 11+) adds non-key columns only for covering
- Partial indexes
  - WHERE predicate stored in the index definition for hot subsets (e.g., status='active')
  - Smaller, faster; planner uses only when query implies predicate
- Functional/Expression indexes
  - Support computed predicates like LOWER(email) or (order_date::date)
  - Must match query expression or be derivable

Design patterns
- OLTP filters: (customer_id), (order_date DESC) with DESC ordering for recent-first queries
- Composite keys: (customer_id, order_date) for recent orders per customer
- Covering read-mostly: CREATE INDEX ... ON orders(customer_id) INCLUDE(total_amount, order_date)

Pitfalls
- Over-indexing hurts writes and vacuum; index only what queries use
- Wrong column order: put most selective and most commonly filtered columns first
- Functions on columns prevent index use; add functional index or store normalized value

Practice exercises
1) Add (order_date) and (customer_id, order_date) indexes; compare plans on date filter and customer-history queries.
2) Create LOWER(email) index and test case-insensitive search.
3) Build a partial index for orders WHERE status='completed' and measure size/speed vs full index.

Further reading
- Indexes: https://www.postgresql.org/docs/current/indexes.html
- INCLUDE: https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-INCLUDE
