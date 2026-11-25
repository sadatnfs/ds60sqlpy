# Day 48 Solutions: E-commerce Analytics, Part 3


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day48_solutions.sql
```

The solution only reads course tables. Check the per-purchase credit sum, the
4,362-order bucket total and the 20-row cap before comparing campaign figures;
the [solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Read each query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Two clauses carry this lesson. The join condition sets the grain: within one
order for baskets, and a seven-day half-open time window per customer for
touches. The second is the step that removes repeats before dividing or
counting: `DISTINCT` on (order, product) or (purchase, campaign), and
`COUNT(DISTINCT purchase_event_id)` when a purchase can reach a campaign
through several touches. When you see `LATERAL ... LIMIT 1`, read it as "pick
one row per outer row" and check its `ORDER BY` for a tie-breaker.

The starter demonstrates market-basket pairs and first/last touch. The
exercises add seven-day assisted conversions, equal-credit multi-touch
attribution at campaign grain, basket support, confidence and lift,
next-purchase assignment and a reconciled direct bucket. The canonical file is
[`day48_solutions.sql`](day48_solutions.sql).

## Exercise 1: Assisted conversions

```sql
SET search_path TO training, public;

WITH purchases AS (
  SELECT
    event_id AS purchase_event_id,
    customer_id,
    event_time AS purchase_time
  FROM
    events
  WHERE
    event_type = 'purchase'
),
qualifying_touches AS (
  SELECT
    p.purchase_event_id,
    p.customer_id,
    COALESCE(t.metadata ->> 'campaign', 'none') AS campaign
  FROM
    purchases p
    JOIN events t ON t.customer_id = p.customer_id
      AND t.event_type <> 'purchase'
      AND t.event_time >= p.purchase_time - interval '7 days'
      AND t.event_time < p.purchase_time
)
  SELECT
    campaign,
    COUNT(DISTINCT purchase_event_id) AS assisted_conversions,
    COUNT(DISTINCT customer_id) AS assisted_customers
  FROM
    qualifying_touches
GROUP BY
  campaign
ORDER BY
  assisted_conversions DESC,
  campaign;
```

Expected grain: one row per campaign. A purchase can appear under several
campaigns, so `assisted_conversions` is not additive across rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 1, take the 4,000 `purchase` events from `events` as conversions and join each one to the same customer's non-purchase events in the half-open window `[purchase_time - interval '7 days', purchase_time)`, reading `metadata ->> 'campaign'` (with `COALESCE(..., 'none')`) as the touch's campaign.
- **Expected result/shape:** For sql-48 Exercise 1, expected output: one row per campaign. The final columns are `campaign`, `assisted_conversions`, and `assisted_customers`. The final order is `assisted_conversions DESC, campaign`.
- **Independent verification:** For sql-48 Exercise 1, confirm 5 rows on our load (`none` and `summer` 264, `fall` 259, `spring` 253, `winter` 251), that `qualifying_touches` has 1,377 rows covering 702 distinct purchases, and that the five `assisted_conversions` add up to 1,291, the distinct (purchase, campaign) pairs, not 702. Then, in a transaction, add a customer whose `purchase` at 2026-01-08 10:00 has an `autumn` touch exactly 7 days earlier, two `summer` touches, and a `boundary` touch at the purchase timestamp; rerun and confirm a new `autumn` row with 1 and 1, `summer` rising to 265 and 35, no `boundary` row, and `ROLLBACK`.
- **Intermediate relation check:** `purchases` has 4,000 rows, one per purchase event. `qualifying_touches` has one row per (purchase, touch), so a purchase with four earlier events in its window appears four times; that is why the final `SELECT` counts `DISTINCT purchase_event_id` and `DISTINCT customer_id` instead of rows.
- **Clause check:** The join is the whole rule: same customer, a non-purchase event, and `event_time` in `[purchase_time - 7 days, purchase_time)`. `GROUP BY campaign` then collapses touches into five rows, and the `ORDER BY` puts the most assisted campaign first with the name as tie-breaker (`none` and `summer` tie at the top on the reference load).
- **Alternative/trade-off:** An `EXISTS` subquery per (purchase, campaign) would avoid the touch-level fan-out entirely, but you would first have to list the campaigns; the join plus `COUNT(DISTINCT ...)` is easier to inspect one CTE at a time.
- **Edge case:** Move one touch to exactly seven days before its purchase and it still counts; move it one second earlier and it drops out. A touch at the same instant as the purchase never counts because the upper bound is strict.

## Exercise 2: Equal fractional multi-touch credit

```sql
SET search_path TO training, public;

WITH purchases AS (
  SELECT
    event_id AS purchase_event_id,
    customer_id,
    event_time AS purchase_time
  FROM
    events
  WHERE
    event_type = 'purchase'
),
campaign_touches AS (
  SELECT DISTINCT
    p.purchase_event_id,
    p.customer_id,
    COALESCE(t.metadata ->> 'campaign', 'none') AS campaign
  FROM
    purchases p
    JOIN events t ON t.customer_id = p.customer_id
      AND t.event_type <> 'purchase'
      AND t.event_time >= p.purchase_time - interval '7 days'
      AND t.event_time < p.purchase_time
),
credited AS (
  SELECT
    *,
    1.0 / COUNT(*) OVER (PARTITION BY purchase_event_id) AS fractional_credit
FROM
  campaign_touches
)
SELECT
  campaign,
  ROUND(SUM(fractional_credit), 4) AS attributed_conversions,
  COUNT(DISTINCT purchase_event_id) AS touched_conversions
FROM
  credited
GROUP BY
  campaign
ORDER BY
  attributed_conversions DESC,
  campaign;
```

For every purchase that has at least one qualifying campaign, credits across
its distinct campaigns sum to 1.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 2, start from the same purchases and seven-day non-purchase touches as Exercise 1, collapse them with `SELECT DISTINCT` to one row per (purchase, campaign) in `campaign_touches`, give each row `1.0 / COUNT(*) OVER (PARTITION BY purchase_event_id)`, and sum that credit by `campaign`.
- **Expected result/shape:** For sql-48 Exercise 2, expected output: one row per `campaign`. The final columns are `campaign`, `attributed_conversions`, and `touched_conversions`. The final order is `attributed_conversions DESC, campaign`.
- **Independent verification:** For sql-48 Exercise 2, confirm `attributed_conversions` of 148.5 for `summer`, 141.25 for `fall`, 140.25 for `none`, 139.25 for `spring`, and 132.75 for `winter` on our load, that they add up to 702.0000 (one credit per assisted purchase), and that `touched_conversions` equals Exercise 1's `assisted_conversions` for every campaign. Then repeat the Exercise 1 transaction: the new purchase has two distinct campaigns, so `autumn` gets 0.5, `summer` rises by 0.5 to 149.0000 even though it touched twice, and the total becomes 703 before `ROLLBACK`.
- **Intermediate relation check:** `campaign_touches` is `SELECT DISTINCT` on (purchase, customer, campaign), so a purchase reached twice by `summer` keeps one `summer` row. `credited` keeps that row count and adds `fractional_credit`, which is 1 divided by the number of distinct campaigns for that purchase. Summing it per purchase must give 1, and summing it over all rows must give the number of distinct assisted purchases, roughly 700 on the reference load, the same purchases that Exercise 1 counted once per campaign.
- **Clause check:** `COUNT(*) OVER (PARTITION BY purchase_event_id)` counts the campaign rows of each purchase without collapsing them, so each row can carry its own share. `ROUND(SUM(fractional_credit), 4)` happens only after grouping by campaign, which keeps rounding error out of the per-purchase division.
- **Alternative/trade-off:** Computing the campaign count in a separate grouped CTE and joining it back gives identical numbers; the window version saves a join and keeps the division next to the rows it splits.
- **Edge case:** If a purchase had only `none` touches, it would still receive one full credit under `none`. Excluding `none` would leave that purchase uncredited, so decide the policy before comparing the total with Exercise 1.

## Reasoning, safety, and pitfalls

- The conversion anchor here is a `purchase` event, not an order. State and test
  that business definition before comparing this result with order metrics.
- `DISTINCT` prevents repeated touches by the same campaign from receiving
  multiple shares.
- The half-open interval includes exactly seven days before the purchase but
  excludes the purchase timestamp itself.
- Campaign value `'none'` makes missing metadata visible; decide whether it
  should receive attribution in production.

## Exercise 3: Credit distinct campaigns

The solution collapses repeated touches to `(purchase, campaign)` before
dividing. That implements equal credit per distinct campaign rather than per
event.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 3, take `purchase` events as `purchases`, collect the distinct (`purchase_id`, `campaign`) pairs from the same customer's non-purchase events in the seven days before each purchase in `eligible_campaigns` (a missing campaign reads `(direct)`), and divide 1 by the number of campaigns in each purchase's partition.
- **Expected result/shape:** For sql-48 Exercise 3, expected output: one row per (`purchase_id`, `campaign`) pair, 1,291 rows over 702 purchases on our load, with columns `purchase_id`, `campaign`, and `campaign_credit`, ordered by `purchase_id, campaign`.
- **Independent verification:** For sql-48 Exercise 3, group the output by `purchase_id` and confirm every sum of `campaign_credit` is 1 and that summing it by `campaign` reproduces Exercise 2's `attributed_conversions`. Check purchase 8 by hand: its five touches are `none`, `summer`, `fall`, `winter`, and `none` again, so campaign grain gives 0.25 to each of four campaigns, while touch grain would give `none` 2/5 = 0.4 and the other three 0.2 each. Then check a one-campaign purchase, such as purchase 42 with `summer` alone, at credit 1 under both policies.
- **Intermediate relation check:** `purchases` renames the purchase event to `purchase_id`. `eligible_campaigns` is one row per (purchase, campaign), 1,291 rows across 702 purchases on the reference load, because `SELECT DISTINCT` drops repeated touches from the same campaign. Like Exercises 1 and 2, the join excludes other purchase events with `e.event_type <> 'purchase'`, so these are the same pairs as Exercise 2's `campaign_touches`; a missing campaign would read `(direct)`.
- **Clause check:** There is no `GROUP BY`. The window `COUNT(*) OVER (PARTITION BY purchase_id)` gives each campaign row its share, so purchase 3 with two campaigns gets 0.5 on each row and purchase 8 with four gets 0.25. The output keeps one row per (purchase, campaign).
- **Alternative/trade-off:** Dividing at touch grain instead (no `DISTINCT`) would give a campaign that touched a purchase three times three shares. That is a different policy, credit per touch, and it rewards repeated exposure; the exercise asks you to predict both and keep the campaign-grain version.
- **Edge case:** A purchase with a single eligible campaign forms a one-row partition and receives credit 1. One with three campaigns must show three rows of one third each, and the three must still sum to 1 after any rounding you add.

## Exercise 4: Compute basket association metrics

Distinct order/product membership defines baskets. Pair counts feed support;
single-product basket counts feed directional confidence; lift compares the
observed pair rate with independence.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 4, reduce `order_items` to distinct (`order_id`, `product_id`) baskets, count all 4,362 orders and each product's baskets, self-join baskets on `order_id` with `a.product_id < b.product_id` to count orders per pair, then compute support, both confidences, and lift from those counts.
- **Expected result/shape:** For sql-48 Exercise 4, expected output: 20 rows out of 770 product pairs, one per (`product_a`, `product_b`) with `product_a < product_b`, with columns `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`, ordered by `lift DESC, product_a, product_b`.
- **Independent verification:** For sql-48 Exercise 4, recompute the top row by hand: products 14 and 45 share 30 orders and appear in 45 and 46, so support is 30/4362 = 0.0069, confidences are 30/45 = 0.6667 and 30/46 = 0.6522, and lift is 30 * 4362 / (45 * 46) = 63.2174. Note that rows 9 to 20 are 12 of the 29 pairs tied at lift 62.5449, so the cap cuts through a tie that only `product_a, product_b` settles. Then, in a transaction, add a second product 14 line to an order that has both 14 and 45; confirm the pair count stays 30 with the `DISTINCT` baskets but becomes 31 without them, and `ROLLBACK`.
- **Intermediate relation check:** `baskets` is one row per (order, product), 13,085 rows; `order_count` is a single number, 4,362; `product_counts` gives each product's basket count; `pairs` has one row per unordered product pair, 770 in total. None of these is keyed by `order_item_id`, despite the contract wording; the output key is (`product_a`, `product_b`).
- **Clause check:** Support is `together / n`, confidence divides `together` by the basket count of one side, and lift is `together * n / (count_a * count_b)`, with `NULLIF` guarding the division. `CROSS JOIN order_count` makes `n` available on every pair row, and `LIMIT 20` comes last, after the lift sort, so the cap never changes which pairs qualify, only how many are shown.
- **Alternative/trade-off:** Computing confidence once, as a single directional metric, would hide that 14 to 45 (0.6667) and 45 to 14 (0.6522) differ. Showing both directions makes the asymmetry visible, while lift stays symmetric by definition.
- **Edge case:** Products 14 and 45 share 30 orders but appear in only 45 and 46 baskets each, so their lift of about 63 rests on very small counts. Several pairs tie on that lift, which is why `product_a, product_b` follow `lift DESC` before the `LIMIT`.

## Exercise 5: Assign a touch only once

A LATERAL subquery chooses the earliest qualifying purchase after each touch.
`ORDER BY order_date, order_id LIMIT 1` prevents reuse and makes ties stable.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 5, start from all 20,000 `events` (every one carries a `campaign` key) and `LEFT JOIN LATERAL` a subquery over `orders` that keeps the same customer's orders after the touch and within 7 days, ordered by `order_date, order_id` with `LIMIT 1`, so each touch can reach only its next order.
- **Expected result/shape:** For sql-48 Exercise 5, expected output: 20,000 rows, one per `touch_id`, with columns `touch_id`, `campaign`, `order_id`, and `order_date`, ordered by `e.event_id`; 3,025 touches carry an order (2,182 distinct orders) and the rest show `NULL` order columns.
- **Independent verification:** For sql-48 Exercise 5, confirm 20,000 rows and 20,000 distinct `touch_id` values; then write the buggy plain `JOIN` of each event to every order within 7 days and confirm it returns 3,311 rows for the same 3,025 touches, with touch 10285 matching four orders (2245 to 2248). In a transaction, give a new customer one touch at 2026-01-01 10:00 and orders on 2026-01-02 and 2026-01-04; confirm the touch returns only the 2026-01-02 order, then `ROLLBACK`.
- **Intermediate relation check:** There is no CTE. Start with `SELECT count(*) FROM events WHERE metadata ? 'campaign'` and confirm it is 20,000, the size of the output. Then run the `LATERAL` subquery for one `event_id` by hand to see that it returns at most one order.
- **Clause check:** The `LEFT JOIN LATERAL (... LIMIT 1) ... ON true` evaluates the subquery once per touch, using that touch's customer and time. Its `ORDER BY o.order_date, o.order_id` picks the earliest order in the next seven days, so a touch can never be assigned to two orders, and touches with no order keep `NULL`.
- **Alternative/trade-off:** `ROW_NUMBER()` over (touch) ordered by order date, filtered to 1, gives the same assignment but first builds every (touch, order) pair in the window; `LATERAL` with `LIMIT 1` expresses "the next one" directly.
- **Edge case:** The output has one row per touch, 20,000 rows, and 3,025 of them carry an order on our load. Two orders at the same timestamp would be resolved by the lower `order_id`.

## Exercise 6: Reconcile direct purchases

The query starts from every order and left-joins its most recent qualifying
touch. Missing touches become `(direct)`, so bucket counts sum to purchases.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 6, start from all 4,362 `orders`, `LEFT JOIN LATERAL` the same customer's latest event with a `campaign` key in the seven days before `order_date` (ordered by `event_time DESC, event_id DESC` with `LIMIT 1`), and label orders with no such event `(direct)`.
- **Expected result/shape:** For sql-48 Exercise 6, expected output: one row per `attribution_bucket`, 6 rows on our load (`(direct)` 2,180, `winter` 440, `summer` 439, `spring` 438, `none` 434, `fall` 431), with columns `attribution_bucket` and `purchases`, ordered by `purchases DESC, attribution_bucket`.
- **Independent verification:** For sql-48 Exercise 6, confirm the six `purchases` values add up to 4,362, and recount `(direct)` independently as the orders with no event by the same customer in the previous seven days (`NOT EXISTS`, 2,180). Then, in a transaction, add an order for customer 1 dated 2020-01-01 and a new customer with `spring` and `winter` touches at the same timestamp followed by two orders; confirm `(direct)` becomes 2,181, `winter` becomes 442 because the higher `event_id` wins the tie, the total becomes 4,365, and `ROLLBACK`.
- **Intermediate relation check:** Start from `orders`: 4,362 rows. The `LATERAL` subquery returns at most one campaign per order, so the row count stays at 4,362 before grouping, and the six bucket counts must add back to it. Note that this exercise anchors on `orders`, not on purchase events, so its totals are not comparable with the 4,000 purchase events used in Exercises 1 to 3.
- **Clause check:** Inside the `LATERAL`, the window is `[order_date - 7 days, order_date)` and `ORDER BY e.event_time DESC, e.event_id DESC LIMIT 1` keeps the latest touch, a last-touch rule. `COALESCE(t.campaign, '(direct)')` appears in both `SELECT` and `GROUP BY`, so orders with no touch form their own bucket.
- **Alternative/trade-off:** Joining every touch in the window and then picking the latest with `DISTINCT ON (order_id)` works too, but it multiplies rows first; the `LATERAL` form never holds more than one touch per order.
- **Edge case:** An order whose only touch is exactly seven days earlier still gets that campaign, while a touch at the same instant as the order does not. Compare the `purchases` column bucket by bucket with the `NOT EXISTS` recount of `(direct)`.