# Day 48 — Solutions (Project 1: E‑commerce Analytics, Part 3)

Today covers product affinity (market basket) and campaign attribution. We’ll solve assisted conversions and a simple multi‑touch fractional attribution.

Reference (annotated)
```sql
-- Distinct items per order
WITH items AS (
  SELECT order_id, product_id
  FROM order_items
  GROUP BY order_id, product_id
), pairs AS (
  SELECT a.product_id AS p1,
         b.product_id AS p2,
         COUNT(*) AS together
  FROM items a
  JOIN items b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p1.name AS product_a, p2.name AS product_b, together
FROM pairs
JOIN products p1 ON p1.product_id = pairs.p1
JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY together DESC
LIMIT 50;
```
Notes
- Ensure a.product_id < b.product_id to avoid duplicates and self‑pairs.
- GROUP BY on the distinct items ensures one count per order pair.

Exercise 1 — Assisted conversions: campaigns appearing within 7 days before purchase
Goal
- Count customers for whom a campaign touch occurred in the 7 days leading up to first purchase.

Solution (first‑touch window)
```sql
WITH first_purchase AS (
  SELECT o.customer_id, MIN(o.order_date) AS first_buy
  FROM orders o
  GROUP BY o.customer_id
), touch AS (
  SELECT e.customer_id,
         e.event_time,
         COALESCE(e.metadata->>'campaign','none') AS campaign
  FROM events e
)
SELECT t.campaign,
       COUNT(DISTINCT t.customer_id) AS assisted_customers
FROM touch t
JOIN first_purchase fp ON fp.customer_id = t.customer_id
WHERE t.event_time BETWEEN fp.first_buy - interval '7 days' AND fp.first_buy
GROUP BY t.campaign
ORDER BY assisted_customers DESC;
```
Line‑by‑line notes
- first_purchase: define the conversion anchor per customer.
- touch: extract campaign from JSON metadata, defaulting to 'none'.
- WHERE clause: inclusive window of 7 days before first_buy.
- COUNT DISTINCT: count customers, not touches.

Variation: consider any purchase, not just first
- Replace first_purchase with purchases (all orders), then COUNT DISTINCT customer_id across any assisted order window.

Exercise 2 — Multi‑touch attribution with fractional credit
Goal
- Distribute credit equally across all campaigns a customer interacted with within 7 days prior to their first purchase.

Solution (equal split)
```sql
WITH first_purchase AS (
  SELECT o.customer_id, MIN(o.order_date) AS first_buy
  FROM orders o
  GROUP BY o.customer_id
), touches AS (
  SELECT e.customer_id,
         e.event_time,
         COALESCE(e.metadata->>'campaign','none') AS campaign
  FROM events e
), windowed AS (
  SELECT t.customer_id,
         t.campaign
  FROM touches t
  JOIN first_purchase fp ON fp.customer_id = t.customer_id
  WHERE t.event_time BETWEEN fp.first_buy - interval '7 days' AND fp.first_buy
), credits AS (
  SELECT customer_id,
         campaign,
         1.0 / NULLIF(COUNT(*) OVER (PARTITION BY customer_id), 0) AS credit
  FROM (
    SELECT DISTINCT customer_id, campaign FROM windowed
  ) u
)
SELECT campaign,
       ROUND(SUM(credit), 4) AS total_credit
FROM credits
GROUP BY campaign
ORDER BY total_credit DESC;
```
Line‑by‑line notes
- windowed: keep only touches inside the pre‑conversion window.
- DISTINCT in credits: one campaign per customer; otherwise multiple touches by same campaign would overweight.
- COUNT(*) OVER (PARTITION BY customer_id): number of unique campaigns for that customer.
- Credit = 1 / (#campaigns). Sum over customers per campaign to get total credit.

Going further
- Time‑decay weighting: use exp(−lambda * hours_to_conversion) to weight more recent touches.
- Position‑based models: allocate 40/40/20 to first/last/middle touches using window functions.
