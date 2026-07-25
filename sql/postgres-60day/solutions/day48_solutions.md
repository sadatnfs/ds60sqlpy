# Day 48 Solutions — E-commerce Analytics, Part 3

The starter demonstrates market-basket pairs and first/last touch. The exercises
ask for seven-day assisted conversions and equal-credit multi-touch
attribution. The canonical file is
[`day48_solutions.sql`](day48_solutions.sql).

## Exercise 1 — Assisted conversions

```sql
SET search_path TO training, public;

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
```

Expected grain: one row per campaign. A purchase can appear under several
campaigns, so `assisted_conversions` is not additive across rows.

## Exercise 2 — Equal fractional multi-touch credit

```sql
SET search_path TO training, public;

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
```

For every purchase that has at least one qualifying campaign, credits across
its distinct campaigns sum to 1.

## Reasoning, safety, and pitfalls

- The conversion anchor here is a `purchase` event, not an order. State and test
  that business definition before comparing this result with order metrics.
- `DISTINCT` prevents repeated touches by the same campaign from receiving
  multiple shares.
- The half-open interval includes exactly seven days before the purchase but
  excludes the purchase timestamp itself.
- Campaign value `'none'` makes missing metadata visible; decide whether it
  should receive attribution in production.
