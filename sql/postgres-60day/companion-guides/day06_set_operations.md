# Day 06 — Set Operations: UNION, INTERSECT, EXCEPT (Companion Guide)

Learning objectives
- Combine result sets with UNION/UNION ALL
- Compute set intersection and differences with INTERSECT/EXCEPT
- Understand duplicate handling and column alignment rules

Why this matters
Merging and comparing result sets is common in data reconciliation, feature flags, and A/B test cohorts.

Core concepts and deep dive
- UNION ALL concatenates rows and keeps duplicates; UNION removes duplicates (implies sort/unique).
- INTERSECT returns rows present in both queries; EXCEPT returns rows in left not in right.
- Column rules: Both queries must have same number of columns and compatible types; column names come from the first query.
- Performance: DISTINCT/UNION can be expensive; prefer UNION ALL followed by targeted dedup when appropriate.

Examples in your schema
- Active customers from two segments combined: SELECT id FROM ... WHERE segment='A' UNION ALL SELECT id FROM ... WHERE segment='B'.
- Orders present in system A but not in payments: SELECT order_id FROM orders EXCEPT SELECT order_id FROM payments.
- Common high-value customers across two periods with INTERSECT of customer_id sets.

Practice exercises
1) Build Q1 vs Q2 cohort sets and compute intersection and exclusive members.
2) Combine top sellers by category across two months using UNION ALL and then rank.
3) Find products present in catalog but not in any order_items.

Further reading
- Set operations: https://www.postgresql.org/docs/current/queries-union.html
