# Day 35 — Avoiding SQL Pitfalls: Correctness and Performance (Companion Guide)

Learning objectives
- Recognize common correctness bugs (NULL logic, join fanout, implicit casts)
- Avoid performance anti-patterns (SELECT *, function-wrapped predicates, DISTINCT-as-bandaid)
- Write robust, maintainable SQL with explicit semantics

Why this matters
Small mistakes can silently skew metrics or explode runtime. Developing a checklist of pitfalls prevents costly outages and bad decisions.

Correctness pitfalls and fixes
- NULL semantics and three-valued logic
  - WHERE col = 'X' excludes NULLs; use IS [NOT] NULL explicitly when intended
  - COALESCE for grouping labels; beware of conflating unknown with zero
- Join fanout and double counting
  - Joining two facts (orders × payments) multiplies rows; pre-aggregate each to 1 row per key before joining
  - Validate with COUNT(*) vs COUNT(DISTINCT key) at each stage
- Implicit type casts
  - Comparing text to numeric or timestamp to text triggers runtime casts and can block indexes; cast once up front
- Time zone mismatch
  - TIMESTAMPTZ vs TIMESTAMP; convert to UTC on ingest; display only at the edge
- Using NOT IN with NULLs
  - NOT IN (subq) returns UNKNOWN if subq contains NULL; use NOT EXISTS correlated subquery instead

Performance anti-patterns
- SELECT *
  - Increases I/O and blocks Index Only Scans; select only needed columns
- Function-wrapped predicates
  - WHERE date(order_ts) = '2025-01-01' prevents index use; rewrite as range WHERE order_ts >= '2025-01-01' AND order_ts < '2025-01-02'
- DISTINCT to “fix” duplicates
  - Often hides join bugs; fix join cardinality or pre-aggregate instead
- Large OFFSET pagination
  - OFFSET 100000 is O(n); use keyset pagination (WHERE (t, id) < (...))
- Over-normalizing optional attributes into EAV tables
  - Hard to index and validate; prefer JSONB with GIN for sparse attributes

Reliability practices
- Guard rails with CHECK/UNIQUE/FOREIGN KEY constraints (deferred when necessary)
- Use generated columns for canonical forms (e.g., lower_email) with unique indexes
- Add comments on tables/columns (COMMENT ON ...) for shared understanding

Practice exercises
1) Refactor a query that uses DISTINCT to remove dupes by fixing join logic; show identical result set without DISTINCT
2) Rewrite function-wrapped date filters to sargable ranges; compare plans
3) Demonstrate NOT IN vs NOT EXISTS with a NULL in the subquery

Further reading
- pitfalls: https://wiki.postgresql.org/wiki/Don%27t_Do_This
- sargable predicates: https://use-the-index-luke.com
