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
--    Inputs: Use only the declared lesson objects (order_items, products, events) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Build multi-touch attribution with fractional credit using window functions.
--    Inputs: Use only the declared lesson objects (order_items, products, events) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: explain how repeated touches from the same campaign affect
--    touch-level versus campaign-level equal-credit attribution.
--    Inputs: Use only the declared lesson objects (order_items, products, events) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: calculate product-pair support, confidence in both
--    directions, and lift using distinct order baskets.
--    Inputs: Use only the declared lesson objects (order_items, products, events) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: prevent one event touch from being credited to several purchases
--    when the intended model assigns it only to the next purchase.
--    Inputs: Use only the declared lesson objects (order_items, products, events) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: place unattributed purchases in an explicit '(direct)' bucket
--    so total attributed credit reconciles to total eligible purchases.
--    Inputs: Use only the declared lesson objects (order_items, products, events) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
