-- Day 48: Project 1 - E-commerce Analytics (Part 3)
-- BEGINNER WORKFLOW — sql-48: Project1 Ecommerce Part3
-- Guide: sql/postgres-60day/companion-guides/day48_project1_ecommerce_part3.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-48/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, events.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
-- 1. Compute assisted conversions: campaigns that appear before purchase within 7 days.
--    Inputs: For sql-48 Exercise 1, read from `events`. Build the answer toward `campaign`, `assisted_conversions`, and `assisted_customers`; keep `campaign` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-48 Exercise 1, expected output: one row per campaign. The final columns are `campaign`, `assisted_conversions`, and `assisted_customers`. The final order is `assisted_conversions DESC, campaign`.
--    Verify: For sql-48 Exercise 1, independently aggregate `events` by `campaign`; require one output row for every distinct `campaign` tuple and compare `assisted_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `assisted_customers` for the existing `campaign` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-48 Exercise 1, run `purchases`, and `qualifying_touches` one at a time. Record each CTE's row count and `campaign` uniqueness before the next stage uses it.
-- 2. Build multi-touch attribution with fractional credit using window functions.
--    Inputs: For sql-48 Exercise 2, read from `events`. Build the answer toward `campaign`, `attributed_conversions`, and `touched_conversions`; keep `campaign` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-48 Exercise 2, expected output: one row per `campaign`. The final columns are `campaign`, `attributed_conversions`, and `touched_conversions`. The final order is `attributed_conversions DESC, campaign`.
--    Verify: For sql-48 Exercise 2, independently aggregate `events` by `campaign`; require one output row for every distinct `campaign` tuple and compare `attributed_conversions`, and `touched_conversions` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `attributed_conversions`, and `touched_conversions` for the existing `campaign` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-48 Exercise 2, run `purchases`, `campaign_touches`, and `credited` one at a time. Record each CTE's row count and `campaign` uniqueness before the next stage uses it.
-- 3. Prediction: explain how repeated touches from the same campaign affect
--    touch-level versus campaign-level equal-credit attribution.
--    Inputs: For sql-48 Exercise 3, read from `events`. Build the answer toward `purchase_id`, `campaign`, and `campaign_credit`; keep `purchase_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-48 Exercise 3, expected output: one row per `purchase_id`. The final columns are `purchase_id`, `campaign`, and `campaign_credit`. The final order is `purchase_id, campaign`.
--    Verify: For sql-48 Exercise 3, choose one complete partition from `events`; hand-calculate its first, middle, and final window values for `campaign`, and `campaign_credit`, then verify output keys remain `purchase_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-48 Exercise 3, run `purchases`, and `eligible_campaigns` one at a time. Record each CTE's row count and `purchase_id` uniqueness before the next stage uses it.
-- 4. Construction: calculate product-pair support, confidence in both
--    directions, and lift using distinct order baskets.
--    Inputs: For sql-48 Exercise 4, read from `order_items`. Build the answer toward `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`; keep `order_item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-48 Exercise 4, expected output: at most 20 rows keyed by `order_item_id`. The final columns are `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`. The final order is `lift DESC, product_a, product_b`.
--    Verify: For sql-48 Exercise 4, assert no more than 20 rows, no duplicate `order_item_id`, and no adjacent pair that violates `lift DESC, product_a, product_b`. Rejoin the returned keys to `order_items` to confirm `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, product_a, product_b`.
--    Hint ladder, rung 1: For sql-48 Exercise 4, run `baskets`, `order_count`, `product_counts`, and `pairs` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
-- 5. Debugging: prevent one event touch from being credited to several purchases
--    when the intended model assigns it only to the next purchase.
--    Inputs: For sql-48 Exercise 5, read from `events`, and `orders`. Build the answer toward `touch_id`, `campaign`, `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-48 Exercise 5, expected output: one row per `order_id`. The final columns are `touch_id`, `campaign`, `order_id`, and `order_date`. The final order is `e.event_id`.
--    Verify: For sql-48 Exercise 5, project `order_id` plus the raw source columns from `events`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `touch_id`, `campaign`, `order_id`, and `order_date` values match those staged rows without unintended fanout or loss. Add one row for which `(e.metadata ? 'campaign')` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-48 Exercise 5, start with the first relation in `events`, and `orders`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 6. Edge case: place unattributed purchases in an explicit '(direct)' bucket
--    so total attributed credit reconciles to total eligible purchases.
--    Inputs: For sql-48 Exercise 6, read from `orders`, and `events`. Build the answer toward `attribution_bucket`, and `purchases`; keep `attribution_bucket`, and `purchases` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-48 Exercise 6, expected output: one row per `attribution_bucket`, and `purchases`. The final columns are `attribution_bucket`, and `purchases`. The final order is `purchases DESC, attribution_bucket`.
--    Verify: For sql-48 Exercise 6, independently aggregate `orders`, and `events` by `attribution_bucket`, and `purchases`; require one output row for every distinct `attribution_bucket`, and `purchases` tuple and compare `row_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-48 Exercise 6, start with the first relation in `orders`, and `events`; after each join, record total rows and distinct `attribution_bucket`, and `purchases` so the exact fanout or loss is visible.

ROLLBACK;
