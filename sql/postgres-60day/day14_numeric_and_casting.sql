-- Day 14: Numeric functions & casting
-- BEGINNER WORKFLOW — sql-14: Numeric and Casting
-- Guide: sql/postgres-60day/companion-guides/day14_numeric_and_casting.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-14/ copy, and prints the full
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
-- Focus: Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
-- Assumptions: Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
-- Pitfall: Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
-- Predict row grain and NULL/order behavior before executing each example.

-- Rounding and casting
SELECT order_id,
       total_amount,
       round(total_amount, 0) AS rounded,
       cast(total_amount AS int) AS as_int
FROM orders
ORDER BY total_amount DESC, order_id
LIMIT 50;

-- Safe division and null handling
SELECT p.category,
       SUM(oi.quantity) AS qty,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)) / NULLIF(SUM(oi.quantity),0), 2) AS avg_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY avg_price DESC, p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
--    Hint: Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
--    Inputs: For sql-14 Exercise 1, read from `products`. Build the answer toward `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-14 Exercise 1, expected output: One row per product. The final columns are `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`. The final order is `margin_rate DESC NULLS LAST, p.product_id`.
--    Verify: For sql-14 Exercise 1, reselect the returned keys directly from the source; require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate` against `products`. Repeat with `NULL` in `product_id`, and `price` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-14 Exercise 1, check `margin_rate DESC NULLS LAST, p.product_id` before applying the row cap.
-- 2. [Query writing] Safely cast a set of text values to numeric only when they match a numeric grammar.
--    Hint: Validate with a regex before casting; otherwise return NULL.
--    Inputs: For sql-14 Exercise 2, read from the inline `VALUES` fixture. Build the answer toward `raw_value`, and `parsed_numeric`; keep `parsed_numeric` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-14 Exercise 2, expected output: One row per sample text. The final columns are `raw_value`, and `parsed_numeric`.
--    Verify: For sql-14 Exercise 2, reselect the returned keys directly from the source; require unique `parsed_numeric` where the expected grain is one row per key and confirm the projected `raw_value`, and `parsed_numeric` against the inline `VALUES` fixture. Add one source row with a new `parsed_numeric`; verify the result gains exactly one row carrying that `parsed_numeric` value.
--    Hint ladder, rung 1: For sql-14 Exercise 2, select `parsed_numeric` from the inline `VALUES` fixture before adding derived columns.
-- 3. [Query writing] Show order-item net revenue rounded only after summing.
--    Hint: Aggregate exact line expressions first; round the final display value.
--    Inputs: For sql-14 Exercise 3, read from `order_items`. Build the answer toward `order_id`, and `net_order_revenue`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-14 Exercise 3, expected output: One row per order. The final columns are `order_id`, and `net_order_revenue`. The final order is `oi.order_id`.
--    Verify: For sql-14 Exercise 3, independently aggregate `order_items` by `order_id`; require one output row for every distinct `order_id` tuple and compare `net_order_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_order_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-14 Exercise 3, confirm the groups are `order_id`; then check `oi.order_id` before applying the row cap.
-- 4. [Prediction] Compare integer division with numeric division for 1 divided by 4.
--    Hint: At least one operand must be numeric to preserve the fraction.
--    Inputs: For sql-14 Exercise 4, read from `orders`, `order_items`, and `products`. Compute `integer_division`, and `numeric_division` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-14 Exercise 4, expected output: One row showing 0 and 0.25. The final columns are `integer_division`, and `numeric_division`.
--    Verify: For sql-14 Exercise 4, evaluate each of `integer_division`, and `numeric_division` in a separate control `SELECT` over `orders`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-14 Exercise 4, select `order_id` from `orders`, `order_items`, and `products` before adding derived columns.
-- 5. [Debugging] Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
--    Hint: Aggregate payment amount and count distinct order IDs at one common scope.
--    Inputs: For sql-14 Exercise 5, read from `payments`. Build the answer toward `average_paid_amount_per_order`; keep `payment_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-14 Exercise 5, expected output: Exactly one summary row. The final columns are `average_paid_amount_per_order`.
--    Verify: For sql-14 Exercise 5, reselect the returned keys directly from the source; require unique `payment_id` where the expected grain is one row per key and confirm the projected `average_paid_amount_per_order` against `payments`. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
--    Hint ladder, rung 1: For sql-14 Exercise 5, select `payment_id` from `payments` before adding derived columns.
-- 6. [Extension] Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
--    Hint: This diagnostic makes the consequence of early rounding visible.
--    Inputs: For sql-14 Exercise 6, read from `order_items`. Build the answer toward `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`; keep `order_item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-14 Exercise 6, expected output: One row with two totals and their signed difference. The final columns are `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
--    Verify: For sql-14 Exercise 6, reselect the returned keys directly from the source; require unique `order_item_id` where the expected grain is one row per key and confirm the projected `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference` against `order_items`. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
--    Hint ladder, rung 1: For sql-14 Exercise 6, select `order_item_id` from `order_items` before adding derived columns.

ROLLBACK;
