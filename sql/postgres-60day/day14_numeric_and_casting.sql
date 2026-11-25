-- Day 14: Numeric functions & casting
-- BEGINNER WORKFLOW - sql-14: Numeric and Casting
-- Guide: sql/postgres-60day/companion-guides/day14_numeric_and_casting.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-14.
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
-- Focus: Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
-- Assumptions: Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
-- Pitfall: Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
-- Predict row grain and NULL/order behavior before executing each example.
-- Rounding and casting
SELECT
  order_id,
  total_amount,
  round(total_amount, 0) AS rounded,
  cast(total_amount AS int) AS as_int
FROM
  orders
ORDER BY
  total_amount DESC,
  order_id
LIMIT 50;

-- Safe division and null handling
SELECT
  p.category,
  SUM(oi.quantity) AS qty,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) / NULLIF (SUM(oi.quantity), 0), 2) AS avg_price
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category
ORDER BY
  avg_price DESC,
  p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
--    Hint: Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
--    Inputs: For sql-14 Exercise 1, compute `price - cost` and `ROUND((price - cost) / NULLIF(price, 0), 4)` for each of the 300 `products`; no fixture price is 0 or `NULL`.
--    Expected result/shape: For sql-14 Exercise 1, return 300 rows, one per product, led by seven products tied at a `margin_rate` of 0.6500 (40, 80, 120, 160, 200, 240, 280, in `product_id` order) and ending with product 83 at 0.2599. The final columns are `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`. The final order is `margin_rate DESC NULLS LAST, p.product_id`.
--    Verify: For sql-14 Exercise 1, confirm 300 distinct `product_id` values and that product 40 shows 24.80 - 8.68 = 16.12 and 16.12 / 24.80 = 0.6500. Inside a rolled-back transaction, set product 40's price to 0; the query must not raise a division error, product 40 must move to row 300 with `margin_amount` -8.68 and a `NULL` `margin_rate`, and product 80 must lead.
--    Hint ladder, rung 1: For sql-14 Exercise 1, check `margin_rate DESC NULLS LAST, p.product_id` before applying the row cap.
-- 2. [Query writing] Safely cast a set of text values to numeric only when they match a numeric grammar.
--    Hint: Validate with a regex before casting; otherwise return NULL.
--    Inputs: For sql-14 Exercise 2, test five inline `VALUES` strings (`'42'`, `' 3.14 '`, `'-0.5'`, `'many'`, and the empty string) against `'^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'` after `btrim`, casting to `numeric` only when the pattern matches.
--    Expected result/shape: For sql-14 Exercise 2, return 5 rows in `VALUES` order: 42, 3.14, -0.5, then `NULL` for `many` and `NULL` for the empty string; the query has no `ORDER BY`. The final columns are `raw_value`, and `parsed_numeric`.
--    Verify: For sql-14 Exercise 2, confirm 5 rows with exactly 2 `NULL` values in `parsed_numeric`. Run `SELECT 'many'::numeric` and `SELECT ''::numeric` on their own; both must fail with `invalid input syntax for type numeric`, which the guard avoids. Note that `'1e3'::numeric` succeeds (1000) but the pattern rejects it, so the guard is stricter than the cast.
--    Hint ladder, rung 1: For sql-14 Exercise 2, select `parsed_numeric` from the inline `VALUES` fixture before adding derived columns.
-- 3. [Query writing] Show order-item net revenue rounded only after summing.
--    Hint: Aggregate exact line expressions first; round the final display value.
--    Inputs: For sql-14 Exercise 3, sum `unit_price * quantity * (1 - discount)` over the 13,085 `order_items` rows per `order_id` and round each order total to 2 places.
--    Expected result/shape: For sql-14 Exercise 3, return 4,362 rows, one per order, starting with order 1 at 240.20 (two item lines) and order 2 at 417.94. The final columns are `order_id`, and `net_order_revenue`. The final order is `oi.order_id`.
--    Verify: For sql-14 Exercise 3, confirm 4,362 distinct `order_id` values, matching `SELECT COUNT(DISTINCT order_id) FROM order_items`, and 0 rows where `net_order_revenue` differs from `orders.total_amount` after joining on `order_id`; the returned values add up to 2355646.89, the same as `SELECT SUM(total_amount) FROM orders`.
--    Hint ladder, rung 1: For sql-14 Exercise 3, confirm the groups are `order_id`; then check `oi.order_id` before applying the row cap.
-- 4. [Prediction] Compare integer division with numeric division for 1 divided by 4.
--    Hint: At least one operand must be numeric to preserve the fraction.
--    Inputs: For sql-14 Exercise 4, evaluate the two constant expressions `1 / 4` and `1::numeric / 4` with no `FROM` clause; no table is read.
--    Expected result/shape: For sql-14 Exercise 4, return one row: `integer_division` 0 and `numeric_division` 0.25000000000000000000. The final columns are `integer_division`, and `numeric_division`.
--    Verify: For sql-14 Exercise 4, confirm one row with 0 and 0.25000000000000000000. Run `SELECT 7 / 2, -7 / 2, 1 / 4.0` and expect 3, -3, and 0.25000000000000000000, which shows integer division truncates toward zero; `SELECT 1 / 0` must fail with `division by zero`.
--    Hint ladder, rung 1: For sql-14 Exercise 4, select `order_id` from `orders`, `order_items`, and `products` before adding derived columns.
-- 5. [Debugging] Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
--    Hint: Aggregate payment amount and count distinct order IDs at one common scope.
--    Inputs: For sql-14 Exercise 5, read from `payments` and divide the total paid amount by the number of distinct paid orders, `SUM(amount) / NULLIF(COUNT(DISTINCT order_id), 0)`, rounded to 2 places.
--    Expected result/shape: For sql-14 Exercise 5, return one row, `average_paid_amount_per_order` 525.05. The final columns are `average_paid_amount_per_order`.
--    Verify: For sql-14 Exercise 5, confirm one row with 525.05, which is 1831900.81 divided by 3489 distinct paid orders; compare it with `ROUND(AVG(amount), 2)` (477.55), which divides by the 3836 payment rows instead.
--    Hint ladder, rung 1: For sql-14 Exercise 5, compute `COUNT(*)` and `COUNT(DISTINCT order_id)` from `payments` first; a per-order average needs the distinct count as its denominator.
-- 6. [Extension] Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
--    Hint: This diagnostic makes the consequence of early rounding visible.
--    Inputs: For sql-14 Exercise 6, read from `order_items` and compare the sum of line totals rounded per line, `SUM(ROUND(unit_price * quantity * (1 - discount), 2))`, with the exact sum rounded once, `ROUND(SUM(unit_price * quantity * (1 - discount)), 2)`.
--    Expected result/shape: For sql-14 Exercise 6, return one row: `sum_of_rounded_lines` 2355648.13, `rounded_exact_total` 2355647.12, and `rounding_difference` 1.01. The final columns are `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
--    Verify: For sql-14 Exercise 6, confirm one row with 2355648.13, 2355647.12, and a `rounding_difference` of 1.01; the difference is the per-line rounding accumulated over 13085 lines, so a report must state which rounding rule it uses.
--    Hint ladder, rung 1: For sql-14 Exercise 6, compute both totals in separate `SELECT` statements first; round inside the `SUM` for one and outside it for the other.
ROLLBACK;
