# Day 25 — Multiple CTEs and Hierarchies in One Query (Companion Guide)

Learning objectives
- Chain multiple CTEs to express stepwise logic clearly
- Mix recursive and non-recursive CTEs for hierarchical problems
- Reuse earlier CTE outputs to avoid recomputation

Why this matters
Complex reports often need staging, filtering, enrichment, and aggregation in stages. Multiple CTEs provide a declarative pipeline that remains readable and testable.

Core concepts and deep dive
- Ordering of CTEs: later CTEs can reference earlier ones. Think of each as a named subquery stage.
- Mixed recursion: WITH RECURSIVE tree AS (...), leaves AS (...) SELECT ... FROM tree JOIN leaves ...
- Performance: since Postgres 12, non-recursive CTEs may be inlined. Force MATERIALIZED for expensive reused CTEs.

Patterns
- Stage raw lines -> enrich with dims -> filter -> aggregate -> final select.
- Build a hierarchy CTE (org tree) and join to an aggregated facts CTE (sales by manager).

Pitfalls
- Circular references between CTEs are invalid.
- Excessive staging for trivial logic harms readability; strike a balance.

Practice exercises
1) Create a 4-stage CTE pipeline from order_items to a country-category monthly summary.
2) Build an employee tree with depth, then join monthly revenue per employee’s accounts to compute team totals by level.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html
