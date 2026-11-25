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
--    Expected result/shape: For sql-11 Exercise 1, return 4,362 rows, one per order, each with exactly one label; order 1 (240.20) is `medium`, order 3 (601.73) is `large`, and order 5 (105.84) is `medium`. The final columns are `order_id`, `total_amount`, and `order_size`. The final order is `o.order_id`.
--    Verify: For sql-11 Exercise 1, confirm 4362 rows, one per `order_id`, and that counting the labels gives 2410 `large`, 1603 `medium`, and 349 `small`; then evaluate the same `CASE` on `VALUES (99.99), (100), (499.99), (500)` and expect `small`, `medium`, `medium`, and `large`.
--    Hint ladder, rung 1: For sql-11 Exercise 1, test the `CASE` on the four boundary values first; the highest threshold must come first because the first true branch wins.
-- 2. [Query writing] Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
--    Hint: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
--    Inputs: For sql-11 Exercise 2, count the 4,362 `orders` rows four ways in one pass with `COUNT(*) FILTER (WHERE ...)`: `paid`, `shipped`, or `delivered` as `paid_like`, `placed` as `open_orders`, `returned` as `returned_orders`, and all rows as `all_orders`.
--    Expected result/shape: For sql-11 Exercise 2, return one row: `paid_like` 2617, `open_orders` 873, `returned_orders` 872, and `all_orders` 4362. The final columns are `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
--    Verify: For sql-11 Exercise 2, confirm `GROUP BY status` returns shipped 873, paid 872, and delivered 872 (adding up to 2617), placed 873, and returned 872, and that the three filtered counts add up to `all_orders`. Inside a rolled-back transaction, set order 1 from `paid` to `cancelled`; `paid_like` must drop to 2616 while `all_orders` stays 4362.
--    Hint ladder, rung 1: For sql-11 Exercise 2, count the input rows from `orders`, then run each aggregate `FILTER` predicate as its own count before combining the values into the one-row summary.
-- 3. [Query writing] Label missing customer segments separately from known segment values.
--    Hint: Test `IS NULL` before comparing text values.
--    Inputs: For sql-11 Exercise 3, read from `customers` and label each `segment` as `missing` when it is NULL, `premium` for `gold` or `platinum`, and `core` otherwise; return one row per customer.
--    Expected result/shape: For sql-11 Exercise 3, return 500 rows, one per customer: customer 1 (`standard`) and customer 2 (`silver`) map to `core`, customer 3 (`gold`) and customer 4 (`platinum`) map to `premium`. The final columns are `customer_id`, `segment`, and `segment_group`. The final order is `c.customer_id`.
--    Verify: For sql-11 Exercise 3, confirm 500 rows, one per `customer_id`; the seed gives 250 `premium` and 250 `core` rows and no `missing` row because every seeded customer has a segment. In a transaction you roll back, set one `segment` to NULL and confirm that customer becomes `missing`, not `core`.
--    Hint ladder, rung 1: For sql-11 Exercise 3, put the `IS NULL` branch first; `segment IN ('gold', 'platinum')` is unknown for NULL, so without that branch a NULL segment falls through to `ELSE`.
-- 4. [Prediction] Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
--    Hint: First-match wins, so specific/high thresholds must precede broader/lower ones.
--    Inputs: For sql-11 Exercise 4, label the three amounts in the inline `VALUES (50), (100), (500)` fixture with a searched `CASE` that tests `amount >= 500` before `amount >= 100`, so the first matching branch is the most specific.
--    Expected result/shape: For sql-11 Exercise 4, return 3 rows: 50 is `low`, 100 is `medium`, and 500 is `high`. The final columns are `amount`, and `corrected_label`. The final order is `amount`.
--    Verify: For sql-11 Exercise 4, confirm the 3 labels above, then swap the two `WHEN` branches so `amount >= 100` is tested first; 500 must come back as `medium`, which is the bug being corrected. Add `499.99` and `99.99` to the fixture; the corrected `CASE` must return `medium` and `low`.
--    Hint ladder, rung 1: For sql-11 Exercise 4, check `amount` before applying the row cap.
-- 5. [Debugging] Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
--    Hint: All result branches must resolve to a compatible PostgreSQL type.
--    Inputs: For sql-11 Exercise 5, classify the three values in the inline `VALUES (NULL::integer), (0), (2)` fixture with a `CASE` whose first branch is `value IS NULL`.
--    Expected result/shape: For sql-11 Exercise 5, return 3 rows: `NULL` is `missing`, 0 is `zero`, and 2 is `nonzero`, with the `NULL` row first. The final columns are `value`, and `value_state`. The final order is `value NULLS FIRST`.
--    Verify: For sql-11 Exercise 5, confirm 3 rows with three different `value_state` labels. Remove the `IS NULL` branch and the `NULL` row must fall through to `ELSE` as `nonzero`, because `NULL = 0` is unknown rather than true; drop `NULLS FIRST` and the `NULL` row must sort last.
--    Hint ladder, rung 1: For sql-11 Exercise 5, check `value NULLS FIRST` before applying the row cap.
-- 6. [Extension] Create payment-method display labels and preserve unknown future methods with an explicit fallback.
--    Hint: A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
--    Inputs: For sql-11 Exercise 6, read from `payments`, group by `method`, count payments per method, and map each method to a display label with a simple `CASE p.method WHEN ... END` that keeps an `ELSE 'Other'` fallback.
--    Expected result/shape: For sql-11 Exercise 6, return 4 rows, one per payment method: `bank` as `Bank transfer` (886), `card` as `Card` (860), `credit` as `Store credit` (1050), and `paypal` as `PayPal` (1040). The final columns are `method`, `method_label`, and `payment_count`. The final order is `p.method`.
--    Verify: For sql-11 Exercise 6, confirm 4 rows (`bank` 886, `card` 860, `credit` 1050, `paypal` 1040) whose counts add up to `SELECT COUNT(*) FROM payments` (3836); then evaluate the same `CASE` on `VALUES ('crypto')` and confirm it returns `Other`, not NULL.
--    Hint ladder, rung 1: For sql-11 Exercise 6, group by `method` and count first; add the label `CASE` only after the counts add up to 3836.
ROLLBACK;
