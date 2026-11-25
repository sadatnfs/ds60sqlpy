-- Day 48: Project 1 - E-commerce Analytics (Part 3)
-- BEGINNER WORKFLOW - sql-48: Project 1 Ecommerce Part 3
-- Guide: sql/postgres-60day/companion-guides/day48_project1_ecommerce_part3.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-48.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    order_id,
    product_id
  FROM
    order_items
  GROUP BY
    order_id,
    product_id
),
pairs AS (
  SELECT
    a.product_id AS p1,
    b.product_id AS p2,
    COUNT(*) AS together
  FROM
    items a
    JOIN items b ON a.order_id = b.order_id
      AND a.product_id < b.product_id
  GROUP BY
    a.product_id,
    b.product_id
)
SELECT
  p1.name AS product_a,
  p2.name AS product_b,
  together
FROM
  pairs
  JOIN products p1 ON p1.product_id = pairs.p1
  JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY
  together DESC
LIMIT 50;

-- Attribution: first touch vs last touch (by event campaign)
WITH ev AS (
  SELECT
    e.customer_id,
    e.event_time,
    coalesce(e.metadata ->> 'campaign', 'none') AS campaign
  FROM
    events e
),
first_last AS (
  SELECT
    customer_id,
    (ARRAY_AGG(campaign ORDER BY event_time ASC))[1] AS first_touch,
    (ARRAY_AGG(campaign ORDER BY event_time DESC))[1] AS last_touch
  FROM
    ev
  GROUP BY
    customer_id
)
SELECT
  first_touch,
  last_touch,
  COUNT(*)
FROM
  first_last
GROUP BY
  first_touch,
  last_touch
ORDER BY
  COUNT(*) DESC
LIMIT 50;

-- Exercises
-- 1. Compute assisted conversions: campaigns that appear before purchase within 7 days.
--    Inputs: For sql-48 Exercise 1, take the 4,000 `purchase` events from `events` as conversions and join each one to the same customer's non-purchase events in the half-open window `[purchase_time - interval '7 days', purchase_time)`, reading `metadata ->> 'campaign'` (with `COALESCE(..., 'none')`) as the touch's campaign.
--    Expected result/shape: For sql-48 Exercise 1, expected output: one row per campaign. The final columns are `campaign`, `assisted_conversions`, and `assisted_customers`. The final order is `assisted_conversions DESC, campaign`.
--    Verify: For sql-48 Exercise 1, confirm 5 rows on our load (`none` and `summer` 264, `fall` 259, `spring` 253, `winter` 251), that `qualifying_touches` has 1,377 rows covering 702 distinct purchases, and that the five `assisted_conversions` add up to 1,291, the distinct (purchase, campaign) pairs, not 702. Then, in a transaction, add a customer whose `purchase` at 2026-01-08 10:00 has an `autumn` touch exactly 7 days earlier, two `summer` touches, and a `boundary` touch at the purchase timestamp; rerun and confirm a new `autumn` row with 1 and 1, `summer` rising to 265 and 35, no `boundary` row, and `ROLLBACK`.
--    Hint ladder, rung 1: For sql-48 Exercise 1, run `purchases` (4,000 rows) and then `qualifying_touches` (1,377 rows on our load) on their own; count distinct `purchase_event_id` in the touches (702) before you group by `campaign`, so you know how much one purchase can repeat across campaigns.
-- 2. Build multi-touch attribution with fractional credit using window functions.
--    Inputs: For sql-48 Exercise 2, start from the same purchases and seven-day non-purchase touches as Exercise 1, collapse them with `SELECT DISTINCT` to one row per (purchase, campaign) in `campaign_touches`, give each row `1.0 / COUNT(*) OVER (PARTITION BY purchase_event_id)`, and sum that credit by `campaign`.
--    Expected result/shape: For sql-48 Exercise 2, expected output: one row per `campaign`. The final columns are `campaign`, `attributed_conversions`, and `touched_conversions`. The final order is `attributed_conversions DESC, campaign`.
--    Verify: For sql-48 Exercise 2, confirm `attributed_conversions` of 148.5 for `summer`, 141.25 for `fall`, 140.25 for `none`, 139.25 for `spring`, and 132.75 for `winter` on our load, that they add up to 702.0000 (one credit per assisted purchase), and that `touched_conversions` equals Exercise 1's `assisted_conversions` for every campaign. Then repeat the Exercise 1 transaction: the new purchase has two distinct campaigns, so `autumn` gets 0.5, `summer` rises by 0.5 to 149.0000 even though it touched twice, and the total becomes 703 before `ROLLBACK`.
--    Hint ladder, rung 1: For sql-48 Exercise 2, run `campaign_touches` alone (1,291 rows on our load) and check that (`purchase_event_id`, `campaign`) is unique; then group `credited` by `purchase_event_id` and confirm every purchase's `fractional_credit` sums to exactly 1 before you aggregate by `campaign`.
-- 3. Prediction: explain how repeated touches from the same campaign affect
--    touch-level versus campaign-level equal-credit attribution.
--    Inputs: For sql-48 Exercise 3, take `purchase` events as `purchases`, collect the distinct (`purchase_id`, `campaign`) pairs from the same customer's non-purchase events in the seven days before each purchase in `eligible_campaigns` (a missing campaign reads `(direct)`), and divide 1 by the number of campaigns in each purchase's partition.
--    Expected result/shape: For sql-48 Exercise 3, expected output: one row per (`purchase_id`, `campaign`) pair, 1,291 rows over 702 purchases on our load, with columns `purchase_id`, `campaign`, and `campaign_credit`, ordered by `purchase_id, campaign`.
--    Verify: For sql-48 Exercise 3, group the output by `purchase_id` and confirm every sum of `campaign_credit` is 1 and that summing it by `campaign` reproduces Exercise 2's `attributed_conversions`. Check purchase 8 by hand: its five touches are `none`, `summer`, `fall`, `winter`, and `none` again, so campaign grain gives 0.25 to each of four campaigns, while touch grain would give `none` 2/5 = 0.4 and the other three 0.2 each. Then check a one-campaign purchase, such as purchase 42 with `summer` alone, at credit 1 under both policies.
--    Hint ladder, rung 1: For sql-48 Exercise 3, run `eligible_campaigns` alone and check that (`purchase_id`, `campaign`) is unique; then list purchase 8's raw touches without `DISTINCT` (five rows) beside its campaign rows (four rows) and predict both credit splits before you add the window.
-- 4. Construction: calculate product-pair support, confidence in both
--    directions, and lift using distinct order baskets.
--    Inputs: For sql-48 Exercise 4, reduce `order_items` to distinct (`order_id`, `product_id`) baskets, count all 4,362 orders and each product's baskets, self-join baskets on `order_id` with `a.product_id < b.product_id` to count orders per pair, then compute support, both confidences, and lift from those counts.
--    Expected result/shape: For sql-48 Exercise 4, expected output: 20 rows out of 770 product pairs, one per (`product_a`, `product_b`) with `product_a < product_b`, with columns `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`, ordered by `lift DESC, product_a, product_b`.
--    Verify: For sql-48 Exercise 4, recompute the top row by hand: products 14 and 45 share 30 orders and appear in 45 and 46, so support is 30/4362 = 0.0069, confidences are 30/45 = 0.6667 and 30/46 = 0.6522, and lift is 30 * 4362 / (45 * 46) = 63.2174. Note that rows 9 to 20 are 12 of the 29 pairs tied at lift 62.5449, so the cap cuts through a tie that only `product_a, product_b` settles. Then, in a transaction, add a second product 14 line to an order that has both 14 and 45; confirm the pair count stays 30 with the `DISTINCT` baskets but becomes 31 without them, and `ROLLBACK`.
--    Hint ladder, rung 1: For sql-48 Exercise 4, run `baskets` (13,085 rows, unique on (`order_id`, `product_id`)), `order_count` (4,362), `product_counts` (275 products), and `pairs` (770 rows) one at a time, and check that the 14 with 45 pair has `together = 30` before you compute any ratio.
-- 5. Debugging: prevent one event touch from being credited to several purchases
--    when the intended model assigns it only to the next purchase.
--    Inputs: For sql-48 Exercise 5, start from all 20,000 `events` (every one carries a `campaign` key) and `LEFT JOIN LATERAL` a subquery over `orders` that keeps the same customer's orders after the touch and within 7 days, ordered by `order_date, order_id` with `LIMIT 1`, so each touch can reach only its next order.
--    Expected result/shape: For sql-48 Exercise 5, expected output: 20,000 rows, one per `touch_id`, with columns `touch_id`, `campaign`, `order_id`, and `order_date`, ordered by `e.event_id`; 3,025 touches carry an order (2,182 distinct orders) and the rest show `NULL` order columns.
--    Verify: For sql-48 Exercise 5, confirm 20,000 rows and 20,000 distinct `touch_id` values; then write the buggy plain `JOIN` of each event to every order within 7 days and confirm it returns 3,311 rows for the same 3,025 touches, with touch 10285 matching four orders (2245 to 2248). In a transaction, give a new customer one touch at 2026-01-01 10:00 and orders on 2026-01-02 and 2026-01-04; confirm the touch returns only the 2026-01-02 order, then `ROLLBACK`.
--    Hint ladder, rung 1: For sql-48 Exercise 5, first write the plain `JOIN` from `events` to `orders` within 7 days and count rows (3,311) against distinct touches (3,025); the difference is the double credit, and touch 10285 with four orders shows it. Then move the order lookup into a `LATERAL` subquery with `LIMIT 1`.
-- 6. Edge case: place unattributed purchases in an explicit '(direct)' bucket
--    so total attributed credit reconciles to total eligible purchases.
--    Inputs: For sql-48 Exercise 6, start from all 4,362 `orders`, `LEFT JOIN LATERAL` the same customer's latest event with a `campaign` key in the seven days before `order_date` (ordered by `event_time DESC, event_id DESC` with `LIMIT 1`), and label orders with no such event `(direct)`.
--    Expected result/shape: For sql-48 Exercise 6, expected output: one row per `attribution_bucket`, 6 rows on our load (`(direct)` 2,180, `winter` 440, `summer` 439, `spring` 438, `none` 434, `fall` 431), with columns `attribution_bucket` and `purchases`, ordered by `purchases DESC, attribution_bucket`.
--    Verify: For sql-48 Exercise 6, confirm the six `purchases` values add up to 4,362, and recount `(direct)` independently as the orders with no event by the same customer in the previous seven days (`NOT EXISTS`, 2,180). Then, in a transaction, add an order for customer 1 dated 2020-01-01 and a new customer with `spring` and `winter` touches at the same timestamp followed by two orders; confirm `(direct)` becomes 2,181, `winter` becomes 442 because the higher `event_id` wins the tie, the total becomes 4,365, and `ROLLBACK`.
--    Hint ladder, rung 1: For sql-48 Exercise 6, run the query without `GROUP BY` and confirm it still has 4,362 rows, one per order, so the `LATERAL ... LIMIT 1` adds no fanout; then count the `NULL` campaigns (2,180) before wrapping them in `COALESCE(..., '(direct)')`.
ROLLBACK;
