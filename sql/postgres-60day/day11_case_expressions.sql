-- Day 11: CASE expressions and conditional logic
-- BEGINNER WORKFLOW — sql-11: Case Expressions
-- Guide: sql/postgres-60day/companion-guides/day11_case_expressions.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-11/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
SELECT o.order_id, o.total_amount,
  CASE
    WHEN o.total_amount >= 1000 THEN 'XL'
    WHEN o.total_amount >= 300 THEN 'L'
    WHEN o.total_amount >= 100 THEN 'M'
    ELSE 'S'
  END AS order_size
FROM orders o
ORDER BY o.total_amount DESC, o.order_id
LIMIT 50;

-- Conditional aggregation with CASE
SELECT p.category,
  SUM(CASE WHEN o.order_date >= now() - interval '30 days' THEN oi.quantity ELSE 0 END) AS qty_30d,
  SUM(CASE WHEN o.order_date >= now() - interval '90 days' THEN oi.quantity ELSE 0 END) AS qty_90d
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY qty_30d DESC, p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Classify orders as small, medium, or large by total amount.
--    Hint: Validate boundaries and place the highest threshold first.
--    Inputs: For sql-11 Exercise 1, read from `orders`. Compute `order_id`, `total_amount`, and `order_size` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-11 Exercise 1, expected output: One row per order with exactly one size label. The final columns are `order_id`, `total_amount`, and `order_size`. The final order is `o.order_id`.
--    Verify: For sql-11 Exercise 1, evaluate each of `total_amount`, and `order_size` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-11 Exercise 1, check `o.order_id` before applying the row cap.
-- 2. [Query writing] Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
--    Hint: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
--    Inputs: For sql-11 Exercise 2, read from `orders`. Compute `paid_like`, `open_orders`, `returned_orders`, and `all_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-11 Exercise 2, expected output: One summary row. The final columns are `paid_like`, `open_orders`, `returned_orders`, and `all_orders`.
--    Verify: For sql-11 Exercise 2, evaluate each of `open_orders`, `returned_orders`, and `all_orders` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-11 Exercise 2, count the input rows from `orders`, then run each aggregate `FILTER` predicate as its own count before combining the values into the one-row summary.
-- 3. [Query writing] Label missing customer segments separately from known segment values.
--    Hint: Test `IS NULL` before comparing text values.
--    Inputs: For sql-11 Exercise 3, read from `customers`. Compute `customer_id`, `segment`, and `segment_group` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-11 Exercise 3, expected output: One row per customer with an explicit segment label. The final columns are `customer_id`, `segment`, and `segment_group`. The final order is `c.customer_id`.
--    Verify: For sql-11 Exercise 3, evaluate each of `segment`, and `segment_group` in a separate control `SELECT` over `customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-11 Exercise 3, check `c.customer_id` before applying the row cap.
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
--    Inputs: For sql-11 Exercise 6, read from `payments`. Compute `method`, `method_label`, and `payment_count` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-11 Exercise 6, expected output: One row per payment method and display label. The final columns are `method`, `method_label`, and `payment_count`. The final order is `p.method`.
--    Verify: For sql-11 Exercise 6, evaluate each of `payment_count` in a separate control `SELECT` over `payments`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `payment_count` for the existing `method` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-11 Exercise 6, confirm the groups are `method`; then check `p.method` before applying the row cap.

ROLLBACK;
