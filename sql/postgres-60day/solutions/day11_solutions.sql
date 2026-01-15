-- Day 11 - Solutions: CASE Expressions and Conditional Logic
-- Assumes: orders, order_items, products, customers

/*
Exercise 1) Bucket orders by amount into tiers and compute counts per tier.
Why: Searched CASE allows flexible thresholds; do all bucketing in a single pass.
*/
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

/*
Exercise 2) Create priority rules combining country, segment, and recent activity.
Why: CASE encodes business rules; order matters (first match wins).
*/
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

-- End of Day 11 solutions
