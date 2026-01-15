# Day 11 — Solutions (CASE Expressions and Conditional Logic)

We implement searched CASE expressions to encode business rules, create buckets, and combine multiple signals. Includes reasoning, line-by-line notes, and pitfalls.

Setup
- Schema: training; tables: orders, order_items, products, customers
- Rule: Order of CASE branches matters — the first match wins; add an ELSE for completeness

Exercise 1 — Bucket orders by amount into tiers and count per tier
```sql
WITH bucketed AS (
  SELECT o.order_id,
         o.total_amount,
         CASE
           WHEN o.total_amount >= 500 THEN 'tier_500_plus'
           WHEN o.total_amount >= 200 THEN 'tier_200_499'
           WHEN o.total_amount >= 50  THEN 'tier_50_199'
           ELSE 'tier_under_50'
         END AS amount_tier
  FROM orders o
)
SELECT amount_tier, COUNT(*) AS orders
FROM bucketed
GROUP BY amount_tier
ORDER BY orders DESC;
```
Line-by-line
- CASE searched form compares boolean predicates in order; the first true branch returns the label. Non-overlapping ranges prevent ambiguity.
- ELSE catches all values < 50 (and NULLs, if total_amount can be NULL). Consider adding explicit `WHEN o.total_amount IS NULL THEN 'tier_unknown'` if you want to separate NULLs.
- GROUP BY amount_tier then counts rows per bucket.
Pitfalls
- Overlapping ranges or missing ELSE leading to NULL labels that later break GROUP BY expectations.

Exercise 2 — Priority rules combining country, segment, recent activity
```sql
SELECT c.customer_id,
       c.country,
       COALESCE(c.segment,'standard') AS segment,
       MAX(o.order_date) AS last_order,
       CASE
         WHEN c.country IN ('US','CA') AND COALESCE(c.segment,'') = 'gold' THEN 'P1'
         WHEN c.country IN ('GB','DE','FR') AND COALESCE(c.segment,'') IN ('gold','silver') THEN 'P2'
         WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '30 days' THEN 'P2'
         ELSE 'P3'
       END AS priority
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.country, COALESCE(c.segment,'standard')
ORDER BY priority, last_order DESC NULLS LAST;
```
Explanation
- COALESCE(segment,'standard'): normalizes NULL segments to a default before grouping; the same expression appears in GROUP BY.
- MAX(o.order_date): we need the most recent activity signal; because we aggregate, the CASE must reference the aggregate as well. Postgres allows aggregates in a SELECT alongside GROUP BY keys.
- Priority rules: The order matters; P1 supersedes others. The third WHEN uses recent activity alone to promote to P2.
Pitfalls and tips
- If you reference MAX(o.order_date) in CASE, ensure it’s computed in the same SELECT scope (as shown). Alternatively, compute last_order in a CTE and use it in a non-aggregated SELECT.
- If you later filter by priority, consider wrapping this statement as a CTE to avoid duplicating CASE logic.
