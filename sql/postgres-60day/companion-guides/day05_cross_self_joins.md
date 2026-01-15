# Day 05 — CROSS and SELF JOINs: Combinatorics and Relationships to Self (Companion Guide)

Learning objectives
- Use CROSS JOIN to form Cartesian products intentionally
- Write self-joins to compare rows within the same table
- Generate pairs and ensure de-duplication (i<j pattern)

Why this matters
Some analyses require pairing rows (A/B comparisons, before/after, customer-customer similarity). Self-joins and controlled Cartesian products enable these.

Core concepts and deep dive
- CROSS JOIN: every row on left with every row on right; use only with small sets or with subsequent filters.
- SELF JOIN: join a table to itself (aliasing required) to compare peers (e.g., orders on consecutive days per customer).
- Pair generation patterns:
  - Symmetric pairs once: JOIN with key ordering (a.id < b.id) to avoid duplicates and self-pairs.
  - Time adjacency: JOIN on same key and abs(date_a - date_b) <= interval '1 day'.

Walkthrough mapping
- Product substitution pairs within a category (p1.category=p2.category AND p1.product_id<p2.product_id) for bundling analysis.
- Employee hierarchy: employees e LEFT JOIN employees m ON e.manager_id=m.id to get manager names (a self-join).

Performance notes
- CROSS JOIN blows up quickly; reduce with filters immediately after.
- Consider generating sequences with generate_series for small domains rather than CROSS of large tables.

Practice exercises
1) For each customer, find the closest two orders in time.
2) Generate all unique pairs of products within each category and count co-purchases.
3) Join employees to themselves to produce (employee, manager) and (manager, director) chains.

Further reading
- Self-joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOINS
