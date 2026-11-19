-- Day 11: CASE expressions and conditional logic
-- BEGINNER WORKFLOW - sql-11: Case Expressions
-- Guide: sql/postgres-60day/companion-guides/day11_case_expressions.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-11.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
-- Assumptions: Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
-- Pitfall: Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
-- Predict row grain and NULL/order behavior before executing each example.
-- Label orders by size
SELECT
  o.order_id,
  o.total_amount,
  CASE WHEN o.total_amount >= 1000 THEN
    'XL'
  WHEN o.total_amount >= 300 THEN
    'L'
  WHEN o.total_amount >= 100 THEN
    'M'
  ELSE
    'S'
  END AS order_size
FROM
  orders o
ORDER BY
  o.total_amount DESC,
  o.order_id
LIMIT 50;

-- Conditional aggregation with CASE
SELECT
  p.category,
  SUM(
    CASE WHEN o.order_date >= now() - interval '30 days' THEN
      oi.quantity
    ELSE
      0
    END) AS qty_30d,
  SUM(
    CASE WHEN o.order_date >= now() - interval '90 days' THEN
      oi.quantity
    ELSE
      0
    END) AS qty_90d
FROM
  order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category
ORDER BY
  qty_30d DESC,
  p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Classify orders as small, medium, or large by total amount.
--    Hint: Validate boundaries and place the highest threshold first.
--    Inputs: For sql-11 Exercise 1, read from `orders` and label every order with a searched `CASE`: `large` when `total_amount >= 500`, `medium` when it is at least 100, otherwise `small`; no `GROUP BY` is needed.
--    Expected result/shape: For sql-11 Exercise 1, expected output: One row per order with exactly one size label. The final columns are `order_id`, `total_amount`, and `order_size`. The final order is `o.order_id`.
--    Verify: For sql-11 Exercise 1, confirm 4362 rows, one per `order_id`, and that counting the labels gives 2410 `large`, 1603 `medium`, and 349 `small`; then evaluate the same `CASE` on `VALUES (99.99), (100), (499.99), (500)` and expect `small`, `medium`, `medium`, and `large`.
--    Hint ladder, rung 1: For sql-11 Exercise 1, test the `CASE` on the four boundary values first; the highest threshold must come first because the first true branch wins.
-- 2. [Query writing] Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
--    Hint: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
--    Inputs: For sql-11 Exercise 2, read from `orders`. Compute `paid_like`, `open_orders`, `returned_orders`, and `all_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-11 Exercise 2, expected output: One summary row. The final columns are `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
--    Verify: For sql-11 Exercise 2, evaluate each of `open_orders`, `returned_orders`, and `all_orders` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-11 Exercise 2, count the input rows from `orders`, then run each aggregate `FILTER` predicate as its own count before combining the values into the one-row summary.
-- 3. [Query writing] Label missing customer segments separately from known segment values.
--    Hint: Test `IS NULL` before comparing text values.
--    Inputs: For sql-11 Exercise 3, read from `customers` and label each `segment` as `missing` when it is NULL, `premium` for `gold` or `platinum`, and `core` otherwise; return one row per customer.
--    Expected result/shape: For sql-11 Exercise 3, expected output: One row per customer with an explicit segment label. The final columns are `customer_id`, `segment`, and `segment_group`. The final order is `c.customer_id`.
--    Verify: For sql-11 Exercise 3, confirm 500 rows, one per `customer_id`; the seed gives 250 `premium` and 250 `core` rows and no `missing` row because every seeded customer has a segment. In a transaction you roll back, set one `segment` to NULL and confirm that customer becomes `missing`, not `core`.
--    Hint ladder, rung 1: For sql-11 Exercise 3, put the `IS NULL` branch first; `segment IN ('gold', 'platinum')` is unknown for NULL, so without that branch a NULL segment falls through to `ELSE`.
-- 4. [Prediction] Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
--    Hint: First-match wins, so specific/high thresholds must precede broader/lower ones.
--    Inputs: For sql-11 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `amount`, and `corrected_label`; keep `corrected_label` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-11 Exercise 4, expected output: A value of 500 is labeled high. The final columns are `amount`, and `corrected_label`. The final order is `amount`.
--    Verify: For sql-11 Exercise 4, reselect the returned keys directly from the source; require unique `corrected_label` where the expected grain is one row per key and confirm the projected `amount`, and `corrected_label` against the inline `VALUES` fixture. Add one source row with a new `corrected_label`; verify the result gains exactly one row carrying that `corrected_label` value.
--    Hint ladder, rung 1: For sql-11 Exercise 4, check `amount` before applying the row cap.
-- 5. [Debugging] Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
--    Hint: All result branches must resolve to a compatible PostgreSQL type.
--    Inputs: For sql-11 Exercise 5, read from the inline `VALUES` fixture. Build the answer toward `value`, and `value_state`; keep `value` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-11 Exercise 5, expected output: Three rows with text labels. The final columns are `value`, and `value_state`. The final order is `value NULLS FIRST`.
--    Verify: For sql-11 Exercise 5, reselect the returned keys directly from the source; require unique `value` where the expected grain is one row per key and confirm the projected `value`, and `value_state` against the inline `VALUES` fixture. Add one source row with a new `value`; verify the result gains exactly one row carrying that `value` value.
--    Hint ladder, rung 1: For sql-11 Exercise 5, check `value NULLS FIRST` before applying the row cap.
-- 6. [Extension] Create payment-method display labels and preserve unknown future methods with an explicit fallback.
--    Hint: A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
--    Inputs: For sql-11 Exercise 6, read from `payments`, group by `method`, count payments per method, and map each method to a display label with a simple `CASE p.method WHEN ... END` that keeps an `ELSE 'Other'` fallback.
--    Expected result/shape: For sql-11 Exercise 6, expected output: One row per payment method and display label. The final columns are `method`, `method_label`, and `payment_count`. The final order is `p.method`.
--    Verify: For sql-11 Exercise 6, confirm 4 rows (`bank` 886, `card` 860, `credit` 1050, `paypal` 1040) whose counts add up to `SELECT COUNT(*) FROM payments` (3836); then evaluate the same `CASE` on `VALUES ('crypto')` and confirm it returns `Other`, not NULL.
--    Hint ladder, rung 1: For sql-11 Exercise 6, group by `method` and count first; add the label `CASE` only after the counts add up to 3836.
ROLLBACK;
