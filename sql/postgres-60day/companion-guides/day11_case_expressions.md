# Day 11 — CASE Expressions and Conditional Logic (Companion Guide)

Learning objectives
- Write simple and searched CASE expressions in SELECT and ORDER BY
- Use CASE within aggregates for conditional sums/counts
- Understand evaluation order and NULL handling in CASE

Core concepts and deep dive
- Simple CASE: CASE expr WHEN val1 THEN ... WHEN val2 THEN ... ELSE ... END
- Searched CASE: CASE WHEN cond1 THEN ... WHEN cond2 THEN ... ELSE ... END — more flexible; prefer for predicates.
- CASE is an expression; can be nested and used anywhere expressions are allowed.
- Use CASE to implement bucketing, flags, and conditional aggregation without extra joins.

Examples
- Segment labels: CASE WHEN ltv>=1000 THEN 'gold' WHEN ltv>=300 THEN 'silver' ELSE 'bronze' END.
- Conditional aggregate: SUM(CASE WHEN status='refunded' THEN amount ELSE 0 END) AS refunded.

Pitfalls
- Overlapping conditions in searched CASE; first match wins. Order matters.
- Returning mixed types; ensure consistent result types across branches.

Practice exercises
1) Bucket orders by amount into tiers and compute counts per tier.
2) Create priority rules combining country, segment, and recent activity.

Further reading
- CASE: https://www.postgresql.org/docs/current/functions-conditional.html
