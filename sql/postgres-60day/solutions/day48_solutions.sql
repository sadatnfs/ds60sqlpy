-- Day 48 solutions: attribution
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
