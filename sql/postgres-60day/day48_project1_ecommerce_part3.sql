-- Day 48: Project 1 - E-commerce Analytics (Part 3)
-- Topics: Product affinity and attribution analysis
BEGIN;
SET search_path TO training, public;

-- Product affinity (market-basket pairs by order)
WITH items AS (
  SELECT order_id, product_id FROM order_items GROUP BY order_id, product_id
), pairs AS (
  SELECT a.product_id AS p1, b.product_id AS p2, COUNT(*) AS together
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

-- Attribution: first touch vs last touch (by event campaign)
WITH ev AS (
  SELECT e.customer_id, e.event_time, coalesce(e.metadata->>'campaign','none') AS campaign
  FROM events e
), first_last AS (
  SELECT customer_id,
         (ARRAY_AGG(campaign ORDER BY event_time ASC))[1] AS first_touch,
         (ARRAY_AGG(campaign ORDER BY event_time DESC))[1] AS last_touch
  FROM ev
  GROUP BY customer_id
)
SELECT first_touch, last_touch, COUNT(*)
FROM first_last
GROUP BY first_touch, last_touch
ORDER BY COUNT(*) DESC
LIMIT 50;

-- Exercises
-- 1) Compute assisted conversions: campaigns that appear before purchase within 7 days.
-- 2) Build multi-touch attribution with fractional credit using window functions.

ROLLBACK;
