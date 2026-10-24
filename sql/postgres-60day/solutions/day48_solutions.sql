-- Day 48 solutions: attribution
-- SOLUTION READING MAP — sql-48: Project1 Ecommerce Part3
-- Explanation: sql/postgres-60day/solutions/day48_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day48_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
SET search_path TO training, public;

-- Exercise 1: campaign touches before a purchase event within seven days.
WITH purchases AS (
  SELECT event_id AS purchase_event_id,
         customer_id,
         event_time AS purchase_time
  FROM events
  WHERE event_type = 'purchase'
), qualifying_touches AS (
  SELECT p.purchase_event_id,
         p.customer_id,
         COALESCE(t.metadata->>'campaign', 'none') AS campaign
  FROM purchases p
  JOIN events t
    ON t.customer_id = p.customer_id
   AND t.event_type <> 'purchase'
   AND t.event_time >= p.purchase_time - interval '7 days'
   AND t.event_time < p.purchase_time
)
SELECT campaign,
       COUNT(DISTINCT purchase_event_id) AS assisted_conversions,
       COUNT(DISTINCT customer_id) AS assisted_customers
FROM qualifying_touches
GROUP BY campaign
ORDER BY assisted_conversions DESC, campaign;

-- Exercise 2: every qualifying campaign receives an equal fraction of one
-- conversion. Deduplicate repeated campaign touches before assigning credit.
WITH purchases AS (
  SELECT event_id AS purchase_event_id,
         customer_id,
         event_time AS purchase_time
  FROM events
  WHERE event_type = 'purchase'
), campaign_touches AS (
  SELECT DISTINCT
         p.purchase_event_id,
         p.customer_id,
         COALESCE(t.metadata->>'campaign', 'none') AS campaign
  FROM purchases p
  JOIN events t
    ON t.customer_id = p.customer_id
   AND t.event_type <> 'purchase'
   AND t.event_time >= p.purchase_time - interval '7 days'
   AND t.event_time < p.purchase_time
), credited AS (
  SELECT *,
         1.0 / COUNT(*) OVER (PARTITION BY purchase_event_id) AS fractional_credit
  FROM campaign_touches
)
SELECT campaign,
       ROUND(SUM(fractional_credit), 4) AS attributed_conversions,
       COUNT(DISTINCT purchase_event_id) AS touched_conversions
FROM credited
GROUP BY campaign
ORDER BY attributed_conversions DESC, campaign;

-- Exercise 3: collapse repeated touches to campaign grain before dividing when
-- policy grants equal credit per distinct campaign rather than per event.
WITH purchases AS (
  SELECT event_id AS purchase_id, customer_id, event_time AS purchased_at
  FROM events WHERE event_type = 'purchase'
), eligible_campaigns AS (
  SELECT DISTINCT p.purchase_id,
         COALESCE(e.metadata->>'campaign', '(direct)') AS campaign
  FROM purchases p
  JOIN events e
    ON e.customer_id = p.customer_id
   AND e.event_time >= p.purchased_at - interval '7 days'
   AND e.event_time < p.purchased_at
)
SELECT purchase_id, campaign,
       1.0 / COUNT(*) OVER (PARTITION BY purchase_id) AS campaign_credit
FROM eligible_campaigns
ORDER BY purchase_id, campaign;

-- Exercise 4: distinct baskets prevent duplicate lines from inflating support.
WITH baskets AS (
  SELECT DISTINCT order_id, product_id FROM order_items
), order_count AS (
  SELECT COUNT(DISTINCT order_id)::numeric AS n FROM baskets
), product_counts AS (
  SELECT product_id, COUNT(*)::numeric AS baskets FROM baskets GROUP BY product_id
), pairs AS (
  SELECT a.product_id AS product_a, b.product_id AS product_b,
         COUNT(*)::numeric AS together
  FROM baskets a JOIN baskets b
    ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p.product_a, p.product_b,
       ROUND(p.together / n, 4) AS support,
       ROUND(p.together / ca.baskets, 4) AS confidence_a_to_b,
       ROUND(p.together / cb.baskets, 4) AS confidence_b_to_a,
       ROUND((p.together * n) / NULLIF(ca.baskets * cb.baskets, 0), 4) AS lift
FROM pairs p
CROSS JOIN order_count
JOIN product_counts ca ON ca.product_id = p.product_a
JOIN product_counts cb ON cb.product_id = p.product_b
ORDER BY lift DESC, product_a, product_b
LIMIT 20;

-- Exercise 5: LATERAL chooses only the next purchase for each touch, preventing
-- one touch from being reused across several later purchases.
SELECT e.event_id AS touch_id,
       e.metadata->>'campaign' AS campaign,
       next_purchase.order_id,
       next_purchase.order_date
FROM events e
LEFT JOIN LATERAL (
  SELECT o.order_id, o.order_date
  FROM orders o
  WHERE o.customer_id = e.customer_id
    AND o.order_date > e.event_time
    AND o.order_date <= e.event_time + interval '7 days'
  ORDER BY o.order_date, o.order_id
  LIMIT 1
) next_purchase ON true
WHERE e.metadata ? 'campaign'
ORDER BY e.event_id;

-- Exercise 6: start from purchases and LEFT JOIN touches so every purchase
-- receives either a qualifying campaign or the explicit direct bucket.
SELECT COALESCE(t.campaign, '(direct)') AS attribution_bucket,
       COUNT(*) AS purchases
FROM orders o
LEFT JOIN LATERAL (
  SELECT e.metadata->>'campaign' AS campaign
  FROM events e
  WHERE e.customer_id = o.customer_id
    AND e.event_time >= o.order_date - interval '7 days'
    AND e.event_time < o.order_date
    AND e.metadata ? 'campaign'
  ORDER BY e.event_time DESC, e.event_id DESC
  LIMIT 1
) t ON true
GROUP BY COALESCE(t.campaign, '(direct)')
ORDER BY purchases DESC, attribution_bucket;
