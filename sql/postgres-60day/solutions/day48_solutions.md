# Day 48 Solutions — E-commerce Analytics, Part 3


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day48_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day48_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Market basket, Attribution window, Fractional credit. Its worked-model focus is:
Deduplicate products within each order, self-join with a.productid < b.productid, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 1, read from `events`. Build the answer toward `campaign`, `assisted_conversions`, and `assisted_customers`; keep `campaign` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-48 Exercise 1, expected output: one row per campaign. The final columns are `campaign`, `assisted_conversions`, and `assisted_customers`. The final order is `assisted_conversions DESC, campaign`.
- **Independent verification:** For sql-48 Exercise 1, independently aggregate `events` by `campaign`; require one output row for every distinct `campaign` tuple and compare `assisted_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `assisted_customers` for the existing `campaign` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-48 Exercise 1, run `purchases`, and `qualifying_touches` one at a time. Record each CTE's row count and `campaign` uniqueness before the next stage uses it.
- **Clause check:** For sql-48 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `campaign`, and finish with `campaign`, `assisted_conversions`, and `assisted_customers` ordered by `assisted_conversions DESC, campaign`.
- **Alternative/trade-off:** For sql-48 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected grain: one row per campaign. Evaluate another form against the concrete expected result (one row per campaign) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `assisted_customers` for the existing `campaign` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 2, read from `events`. Build the answer toward `campaign`, `attributed_conversions`, and `touched_conversions`; keep `campaign` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-48 Exercise 2, expected output: one row per `campaign`. The final columns are `campaign`, `attributed_conversions`, and `touched_conversions`. The final order is `attributed_conversions DESC, campaign`.
- **Independent verification:** For sql-48 Exercise 2, independently aggregate `events` by `campaign`; require one output row for every distinct `campaign` tuple and compare `attributed_conversions`, and `touched_conversions` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `attributed_conversions`, and `touched_conversions` for the existing `campaign` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-48 Exercise 2, run `purchases`, `campaign_touches`, and `credited` one at a time. Record each CTE's row count and `campaign` uniqueness before the next stage uses it.
- **Clause check:** For sql-48 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `campaign`, and finish with `campaign`, `attributed_conversions`, and `touched_conversions` ordered by `attributed_conversions DESC, campaign`.
- **Alternative/trade-off:** For sql-48 Exercise 2, the chosen form is justified by this lesson-specific rationale: For every purchase that has at least one qualifying campaign, credits across its distinct campaigns sum to 1. Evaluate another form against the concrete expected result (one row per `campaign`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `attributed_conversions`, and `touched_conversions` for the existing `campaign` tuple and verify the new tuple appears exactly once.

## Reasoning, safety, and pitfalls

- The conversion anchor here is a `purchase` event, not an order. State and test
  that business definition before comparing this result with order metrics.
- `DISTINCT` prevents repeated touches by the same campaign from receiving
  multiple shares.
- The half-open interval includes exactly seven days before the purchase but
  excludes the purchase timestamp itself.
- Campaign value `'none'` makes missing metadata visible; decide whether it
  should receive attribution in production.

## Exercise 3 — Credit distinct campaigns

The solution collapses repeated touches to `(purchase, campaign)` before
dividing. That implements equal credit per distinct campaign rather than per
event.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 3, read from `events`. Build the answer toward `purchase_id`, `campaign`, and `campaign_credit`; keep `purchase_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-48 Exercise 3, expected output: one row per `purchase_id`. The final columns are `purchase_id`, `campaign`, and `campaign_credit`. The final order is `purchase_id, campaign`.
- **Independent verification:** For sql-48 Exercise 3, choose one complete partition from `events`; hand-calculate its first, middle, and final window values for `campaign`, and `campaign_credit`, then verify output keys remain `purchase_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-48 Exercise 3, run `purchases`, and `eligible_campaigns` one at a time. Record each CTE's row count and `purchase_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-48 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `purchase_id`, and finish with `purchase_id`, `campaign`, and `campaign_credit` ordered by `purchase_id, campaign`.
- **Alternative/trade-off:** For sql-48 Exercise 3, the chosen form is justified by this lesson-specific rationale: The solution collapses repeated touches to `(purchase, campaign)` before dividing. Evaluate another form against the concrete expected result (one row per `purchase_id`) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Compute basket association metrics

Distinct order/product membership defines baskets. Pair counts feed support;
single-product basket counts feed directional confidence; lift compares the
observed pair rate with independence.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 4, read from `order_items`. Build the answer toward `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`; keep `order_item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-48 Exercise 4, expected output: at most 20 rows keyed by `order_item_id`. The final columns are `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`. The final order is `lift DESC, product_a, product_b`.
- **Independent verification:** For sql-48 Exercise 4, assert no more than 20 rows, no duplicate `order_item_id`, and no adjacent pair that violates `lift DESC, product_a, product_b`. Rejoin the returned keys to `order_items` to confirm `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, product_a, product_b`.
- **Intermediate relation check:** For sql-48 Exercise 4, run `baskets`, `order_count`, `product_counts`, and `pairs` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-48 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `order_items`, preserve one row per `order_item_id`, and finish with `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift` ordered by `lift DESC, product_a, product_b`.
- **Alternative/trade-off:** For sql-48 Exercise 4, the chosen form is justified by this lesson-specific rationale: Distinct order/product membership defines baskets. Evaluate another form against the concrete expected result (at most 20 rows keyed by `order_item_id`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, product_a, product_b`.

## Exercise 5 — Assign a touch only once

A LATERAL subquery chooses the earliest qualifying purchase after each touch.
`ORDER BY order_date, order_id LIMIT 1` prevents reuse and makes ties stable.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 5, read from `events`, and `orders`. Build the answer toward `touch_id`, `campaign`, `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-48 Exercise 5, expected output: one row per `order_id`. The final columns are `touch_id`, `campaign`, `order_id`, and `order_date`. The final order is `e.event_id`.
- **Independent verification:** For sql-48 Exercise 5, project `order_id` plus the raw source columns from `events`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `touch_id`, `campaign`, `order_id`, and `order_date` values match those staged rows without unintended fanout or loss. Add one row for which `(e.metadata ? 'campaign')` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-48 Exercise 5, start with the first relation in `events`, and `orders`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-48 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `events`, and `orders`, preserve one row per `order_id`, and finish with `touch_id`, `campaign`, `order_id`, and `order_date` ordered by `e.event_id`.
- **Alternative/trade-off:** For sql-48 Exercise 5, the chosen form is justified by this lesson-specific rationale: A LATERAL subquery chooses the earliest qualifying purchase after each touch. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one row for which `(e.metadata ? 'campaign')` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 6 — Reconcile direct purchases

The query starts from every order and left-joins its most recent qualifying
touch. Missing touches become `(direct)`, so bucket counts sum to purchases.

### Reasoning and verification

- **Inputs/evidence:** For sql-48 Exercise 6, read from `orders`, and `events`. Build the answer toward `attribution_bucket`, and `purchases`; keep `attribution_bucket`, and `purchases` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-48 Exercise 6, expected output: one row per `attribution_bucket`, and `purchases`. The final columns are `attribution_bucket`, and `purchases`. The final order is `purchases DESC, attribution_bucket`.
- **Independent verification:** For sql-48 Exercise 6, independently aggregate `orders`, and `events` by `attribution_bucket`, and `purchases`; require one output row for every distinct `attribution_bucket`, and `purchases` tuple and compare `row_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-48 Exercise 6, start with the first relation in `orders`, and `events`; after each join, record total rows and distinct `attribution_bucket`, and `purchases` so the exact fanout or loss is visible.
- **Clause check:** For sql-48 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, and `events`, preserve one row per `attribution_bucket`, and `purchases`, and finish with `attribution_bucket`, and `purchases` ordered by `purchases DESC, attribution_bucket`.
- **Alternative/trade-off:** For sql-48 Exercise 6, the chosen form is justified by this lesson-specific rationale: The query starts from every order and left-joins its most recent qualifying touch. Evaluate another form against the concrete expected result (one row per `attribution_bucket`, and `purchases`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.
