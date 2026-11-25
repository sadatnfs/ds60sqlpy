# Day 48: E-commerce Project, Part 3: Affinity and Attribution

## How to run this lesson

Open **sql-48** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and work in your copy at
`.learning/sql/sql-48/lesson/workspace/sql/postgres-60day/day48_project1_ecommerce_part3.sql`.
The lesson reads `order_items` and `products` for the basket half and `events`
plus `orders` for the attribution half, all in `advanced_sql_training`. The
script runs inside `BEGIN` ... `ROLLBACK`, so nothing it does persists. A clean
`psql` run prints the 50 most frequent product pairs, then a five-row
first-touch/last-touch table, then your exercise results. The fixture spaces
each customer's events and orders across that customer's lifetime, measured
from the moment you loaded it, so a few attribution counts can differ by a
handful from the numbers quoted here. Launcher and recovery steps are in the
[SQL study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom), and the
notebook option is in its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 47; cohort retention](day47_project1_ecommerce_part2.md) Day 47 gave you event and order timelines per customer; today you compare those timelines inside a seven-day window.
- **Artifacts:** [learner SQL](../day48_project1_ecommerce_part3.sql) ·
  [solution reasoning](../solutions/day48_solutions.md) ·
  [executable solution](../solutions/day48_solutions.sql)

## A beginner's mental model for this lesson

The lesson has two halves that share one discipline: decide what a single row
means before you count. In the basket half, one row of `items` is a distinct
(order, product) membership. Joining `items` to itself on `order_id` makes one
row per pair of products in the same order, and the condition
`a.product_id < b.product_id` keeps each unordered pair once, so product 14
with product 45 is never counted again as 45 with 14 or as 14 with itself. On
the course data `order_items` already has no repeated (order, product) lines,
13,085 lines across 4,362 orders, but the `GROUP BY` or `DISTINCT` step is what
protects the count when a future order lists a product twice.

In the attribution half the anchor is a `purchase` event, not an order. Every
customer has 40 events that rotate through five types, so there are exactly
4,000 purchase events. A touch is any other event by the same customer in the
half-open window `[purchase_time - 7 days, purchase_time)`, and its campaign
comes from `metadata ->> 'campaign'`. Because one purchase can have touches
from several campaigns, counting purchases per campaign double-counts, while
dividing one credit by the number of distinct campaigns makes the credits sum
back to the number of assisted purchases. Read each query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order),
naming the grain after every CTE.

## Two worked SQL examples

Both excerpts come from the learner script and run in order inside its
transaction.

### Example 1

```sql
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
```

**How to read it:** `items` collapses `order_items` to one row per (order, product). `pairs`
self-joins it within each order, keeps `a.product_id < b.product_id`, and
counts orders per pair in `together`. The outer query only swaps the two ids
for product names and keeps the 50 largest counts.

**Expected result/shape:** 50 rows of `product_a`, `product_b` and `together`. The largest count is 32,
and 255 of the 770 pairs share it, so the 50 rows you see are an arbitrary
slice of a large tie (Product 101 with Product 132 may appear on one run and
not the next). Adding `p1, p2` to the `ORDER BY` makes the slice repeatable.

### Example 2

```sql
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
```

**How to read it:** `ev` turns every event into (customer, time, campaign), with `none` as the
fallback label. `first_last` uses two ordered `ARRAY_AGG` calls per customer
and takes element `[1]` of each, so it keeps the earliest and the latest
campaign. The outer query counts customers per (first, last) combination.

**Expected result/shape:** Five rows of exactly 100 customers each, such as `winter` to `fall` and
`spring` to `none`. The fixture assigns campaigns by a formula on customer id
and event number, so each first touch always leads to the same last touch;
real data would spread across up to 25 combinations.

## Learning objectives

- Count each undirected basket pair once per order.
- Attribute a purchase event across distinct qualifying campaigns under an
  explicit lookback rule.

## Vocabulary and concepts

- **Market basket:** the distinct products associated with one order.
- **Attribution window:** the time interval in which a touch can qualify for
  conversion credit.
- **Fractional credit:** one conversion divided across several qualifying
  touches or campaigns.

## Worked example / walkthrough

Deduplicate products within each order, self-join with
`a.product_id < b.product_id`, and count orders per pair. For attribution,
deduplicate campaigns per purchase before dividing one credit by the distinct
campaign count; verify allocated credit sums to one for every assisted purchase.

## Exercises

Complete these in the [learner SQL](../day48_project1_ecommerce_part3.sql):

1. Calculate seven-day assisted conversions.
   **Inputs/evidence:** For sql-48 Exercise 1, take the 4,000 `purchase` events from `events` as conversions and join each one to the same customer's non-purchase events in the half-open window `[purchase_time - interval '7 days', purchase_time)`, reading `metadata ->> 'campaign'` (with `COALESCE(..., 'none')`) as the touch's campaign.
   **Expected result/shape:** For sql-48 Exercise 1, expected output: one row per campaign. The final columns are `campaign`, `assisted_conversions`, and `assisted_customers`. The final order is `assisted_conversions DESC, campaign`.
   **Verify:** For sql-48 Exercise 1, confirm 5 rows on our load (`none` and `summer` 264, `fall` 259, `spring` 253, `winter` 251), that `qualifying_touches` has 1,377 rows covering 702 distinct purchases, and that the five `assisted_conversions` add up to 1,291, the distinct (purchase, campaign) pairs, not 702. Then, in a transaction, add a customer whose `purchase` at 2026-01-08 10:00 has an `autumn` touch exactly 7 days earlier, two `summer` touches, and a `boundary` touch at the purchase timestamp; rerun and confirm a new `autumn` row with 1 and 1, `summer` rising to 265 and 35, no `boundary` row, and `ROLLBACK`.
   **Data check:** Touches are non-purchase events in the seven days before a purchase. Expect five rows, one per stored campaign value (`fall`, `none`, `spring`, `summer`, `winter`), each with roughly 250 to 265 assisted purchases and about 34 customers. The five conversion counts add up to well over the roughly 700 assisted purchases, because a purchase with three campaigns appears in three rows.
2. Allocate equal fractional multi-touch credit.
   **Inputs/evidence:** For sql-48 Exercise 2, start from the same purchases and seven-day non-purchase touches as Exercise 1, collapse them with `SELECT DISTINCT` to one row per (purchase, campaign) in `campaign_touches`, give each row `1.0 / COUNT(*) OVER (PARTITION BY purchase_event_id)`, and sum that credit by `campaign`.
   **Expected result/shape:** For sql-48 Exercise 2, expected output: one row per `campaign`. The final columns are `campaign`, `attributed_conversions`, and `touched_conversions`. The final order is `attributed_conversions DESC, campaign`.
   **Verify:** For sql-48 Exercise 2, confirm `attributed_conversions` of 148.5 for `summer`, 141.25 for `fall`, 140.25 for `none`, 139.25 for `spring`, and 132.75 for `winter` on our load, that they add up to 702.0000 (one credit per assisted purchase), and that `touched_conversions` equals Exercise 1's `assisted_conversions` for every campaign. Then repeat the Exercise 1 transaction: the new purchase has two distinct campaigns, so `autumn` gets 0.5, `summer` rises by 0.5 to 149.0000 even though it touched twice, and the total becomes 703 before `ROLLBACK`.
   **Data check:** Expect the same five campaigns. `touched_conversions` should match Exercise 1's assisted counts, while the five `attributed_conversions` values (around 133 to 149 each) must add up to the number of distinct assisted purchases, roughly 700. If the total is larger, a purchase is being credited per touch instead of per distinct campaign.
3. Predict repeated-campaign behavior at touch versus campaign grain.
   **Inputs/evidence:** For sql-48 Exercise 3, take `purchase` events as `purchases`, collect the distinct (`purchase_id`, `campaign`) pairs from the same customer's non-purchase events in the seven days before each purchase in `eligible_campaigns` (a missing campaign reads `(direct)`), and divide 1 by the number of campaigns in each purchase's partition.
   **Expected result/shape:** For sql-48 Exercise 3, expected output: one row per (`purchase_id`, `campaign`) pair, 1,291 rows over 702 purchases on our load, with columns `purchase_id`, `campaign`, and `campaign_credit`, ordered by `purchase_id, campaign`.
   **Verify:** For sql-48 Exercise 3, group the output by `purchase_id` and confirm every sum of `campaign_credit` is 1 and that summing it by `campaign` reproduces Exercise 2's `attributed_conversions`. Check purchase 8 by hand: its five touches are `none`, `summer`, `fall`, `winter`, and `none` again, so campaign grain gives 0.25 to each of four campaigns, while touch grain would give `none` 2/5 = 0.4 and the other three 0.2 each. Then check a one-campaign purchase, such as purchase 42 with `summer` alone, at credit 1 under both policies.
   **Data check:** Expect 1,291 rows on the reference load, one per (purchase, campaign) pair. Purchase 3 splits 0.5 and 0.5 between `none` and `winter`; purchase 8 splits 0.25 four ways. Grouping your output by `purchase_id` and summing `campaign_credit` should return 1 for every purchase.
4. Calculate product-pair support, bidirectional confidence, and lift.
   **Inputs/evidence:** For sql-48 Exercise 4, reduce `order_items` to distinct (`order_id`, `product_id`) baskets, count all 4,362 orders and each product's baskets, self-join baskets on `order_id` with `a.product_id < b.product_id` to count orders per pair, then compute support, both confidences, and lift from those counts.
   **Expected result/shape:** For sql-48 Exercise 4, expected output: 20 rows out of 770 product pairs, one per (`product_a`, `product_b`) with `product_a < product_b`, with columns `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`, ordered by `lift DESC, product_a, product_b`.
   **Verify:** For sql-48 Exercise 4, recompute the top row by hand: products 14 and 45 share 30 orders and appear in 45 and 46, so support is 30/4362 = 0.0069, confidences are 30/45 = 0.6667 and 30/46 = 0.6522, and lift is 30 * 4362 / (45 * 46) = 63.2174. Note that rows 9 to 20 are 12 of the 29 pairs tied at lift 62.5449, so the cap cuts through a tie that only `product_a, product_b` settles. Then, in a transaction, add a second product 14 line to an order that has both 14 and 45; confirm the pair count stays 30 with the `DISTINCT` baskets but becomes 31 without them, and `ROLLBACK`.
   **Data check:** Expect exactly 20 rows, one per product pair rather than per order line. The baskets are the 4,362 orders, and the top pairs, such as 14 with 45, appear together in 30 orders while each product appears in only 45 or 46, which is why lift reaches about 63. Check that `product_a < product_b` on every row.
5. Assign a touch only to the next purchase.
   **Inputs/evidence:** For sql-48 Exercise 5, start from all 20,000 `events` (every one carries a `campaign` key) and `LEFT JOIN LATERAL` a subquery over `orders` that keeps the same customer's orders after the touch and within 7 days, ordered by `order_date, order_id` with `LIMIT 1`, so each touch can reach only its next order.
   **Expected result/shape:** For sql-48 Exercise 5, expected output: 20,000 rows, one per `touch_id`, with columns `touch_id`, `campaign`, `order_id`, and `order_date`, ordered by `e.event_id`; 3,025 touches carry an order (2,182 distinct orders) and the rest show `NULL` order columns.
   **Verify:** For sql-48 Exercise 5, confirm 20,000 rows and 20,000 distinct `touch_id` values; then write the buggy plain `JOIN` of each event to every order within 7 days and confirm it returns 3,311 rows for the same 3,025 touches, with touch 10285 matching four orders (2245 to 2248). In a transaction, give a new customer one touch at 2026-01-01 10:00 and orders on 2026-01-02 and 2026-01-04; confirm the touch returns only the 2026-01-02 order, then `ROLLBACK`.
   **Data check:** Every one of the 20,000 events carries a `campaign` key, so expect one row per touch, 20,000 in total, ordered by `touch_id`. Only 3,025 touches have an order in the following seven days on our load; the rest keep `NULL` order columns because the `LATERAL` subquery is joined with `LEFT JOIN ... ON true`.
6. Add a direct bucket and reconcile credit to eligible purchases.
   **Inputs/evidence:** For sql-48 Exercise 6, start from all 4,362 `orders`, `LEFT JOIN LATERAL` the same customer's latest event with a `campaign` key in the seven days before `order_date` (ordered by `event_time DESC, event_id DESC` with `LIMIT 1`), and label orders with no such event `(direct)`.
   **Expected result/shape:** For sql-48 Exercise 6, expected output: one row per `attribution_bucket`, 6 rows on our load (`(direct)` 2,180, `winter` 440, `summer` 439, `spring` 438, `none` 434, `fall` 431), with columns `attribution_bucket` and `purchases`, ordered by `purchases DESC, attribution_bucket`.
   **Verify:** For sql-48 Exercise 6, confirm the six `purchases` values add up to 4,362, and recount `(direct)` independently as the orders with no event by the same customer in the previous seven days (`NOT EXISTS`, 2,180). Then, in a transaction, add an order for customer 1 dated 2020-01-01 and a new customer with `spring` and `winter` touches at the same timestamp followed by two orders; confirm `(direct)` becomes 2,181, `winter` becomes 442 because the higher `event_id` wins the tie, the total becomes 4,365, and `ROLLBACK`.
   **Data check:** Expect six rows: the five campaigns plus `(direct)`. The `purchases` column must add up to all 4,362 orders, because every order lands in exactly one bucket; on a fresh load about half of them are `(direct)` and the rest split almost evenly, around 430 to 440 per campaign.

Test touches exactly at both seven-day boundaries.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Enforce `product_id` ordering to avoid
  self-pairs and reversed duplicates. With `<>` instead of `<`, every pair
  appears twice, once in each direction, so the list has 1,540 rows instead
  of 770; with no condition at all, each product also pairs with itself.
- **Credits that add up to more than the assisted purchases:** you divided by
  the number of touches but grouped by campaign, or forgot `DISTINCT` on
  (purchase, campaign). Sum `fractional_credit` per `purchase_event_id`; every
  sum must be exactly 1.
- **A purchase credited to itself:** Exercise 3 has no event-type filter, so
  an upper bound of `<=` on `event_time` would let the purchase event count as
  its own touch. Keep the bound strict and test a touch exactly seven days
  before.
- **Orders missing from the direct bucket:** an inner `JOIN LATERAL` drops
  orders with no qualifying touch. Use `LEFT JOIN LATERAL ... ON true` and
  confirm the bucket total is 4,362.
- Generic recovery steps, including `psql` stopping on the first error, are
  in the [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Are reversed pairs, self-pairs, and repeat quantities excluded as intended?
- Does fractional credit reconcile to assisted conversions without implying
  causal impact?

## Next step

Continue to [Day 49; revenue forecasting](day49_project2_finance_part1.md).

## Deep dive and reference

## Project focus

- Form undirected market-basket product pairs.
- Count campaign-assisted purchase events in a seven-day lookback.
- Allocate equal fractional credit across distinct qualifying campaigns.

## How the learner script uses the current schema

The starter deduplicates products within each order and pairs them with
`a.product_id < b.product_id`. It also extracts campaign from
`events.metadata->>'campaign'` and demonstrates each customer's first and last
touch by `events.event_time`.

The setup provides event types `page_view`, `add_to_cart`, `checkout`,
`purchase`, and `support`. It has no separate sessions or experiment assignment
table.

## Practice map

Exercises 1, 2, 3 and 6 build attribution step by step: count assisted
purchases, split one credit across distinct campaigns, compare campaign grain
with touch grain, and finally give every order exactly one bucket. Exercise 4
returns to baskets with support, confidence and lift, and Exercise 5 shows how
`LATERAL ... LIMIT 1` stops one touch from claiming several orders. The
numbered list above is the contract, repeated unchanged in the learner SQL.

## Attribution reasoning

- The conversion anchor is a purchase event, not an order. State that definition
  before comparing results with order revenue.
- Assisted counts are not additive because one purchase can have several
  assisting campaigns.
- Equal credit for a qualifying purchase should sum to exactly one across its
  distinct campaigns.
- Decide whether missing campaign metadata, represented as `none`, should
  receive credit.

## Validation and limits

- Enforce `product_id` ordering to avoid self-pairs and reversed duplicates.
- The exercise does not establish causal marketing impact.
- The seven-day half-open window needs explicit boundary tests.
- Without session IDs, do not imply session-level journeys.

## Ask an AI tutor about this lesson

Attribution rules invite opinions, so a tutor can be a useful sparring
partner on first-touch versus split credit; the purchase counts still have to
come from your own runs. Paste this prompt if you want one, and see the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-48: E-Commerce Project, Part 3: Product Affinity and Attribution.

I have completed the direct catalog prerequisite: `sql-47`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day48_project1_ecommerce_part3.md
- Answer-free learner SQL: sql/postgres-60day/day48_project1_ecommerce_part3.sql

Key terms to teach in context: Market basket, Attribution window, Fractional credit. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Deduplicate products within each order, self-join with `a.product_id < b.product_id`, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-48/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
