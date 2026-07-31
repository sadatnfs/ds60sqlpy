-- Day 56: Project 4 - Complex BI (Part 2)
-- BEGINNER WORKFLOW — sql-56: Project4 BI Part2
-- Guide: sql/postgres-60day/companion-guides/day56_project4_bi_part2.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-56/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Ranking and percentile reporting, multi-dimensional splits
BEGIN;
SET search_path TO training, public;

-- Percentile distribution of order values per country-month
WITH orders_m AS (
  SELECT c.country,
         date_trunc('month', o.order_date)::date AS month,
         o.total_amount AS amt
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
)
SELECT country,
       month,
       PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM orders_m
GROUP BY country, month
ORDER BY month DESC, country
LIMIT 200;

-- Top-N per dimension (category) within country using window rank
WITH prod_rev AS (
  SELECT c.country,
         p.category,
         p.product_id,
         p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk_country,
            RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk_in_cat
  FROM prod_rev
)
SELECT * FROM ranked
WHERE rnk_in_cat <= 5
ORDER BY country, category, rnk_in_cat;

-- CUBE for multi-dimensional subtotals across country, category
WITH line AS (
  SELECT c.country, p.category,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category, ROUND(SUM(revenue),2) AS revenue,
       GROUPING(country) AS g_country, GROUPING(category) AS g_cat
FROM line
GROUP BY CUBE (country, category)
ORDER BY country NULLS FIRST, category NULLS FIRST;

-- Exercises
-- 1. Add payment method to the CUBE and measure row count increase.
--    Inputs: For sql-56 Exercise 1, read from `payments`, `orders`, `customers`, `order_items`, and `products`. Compute `two_dimension_rows`, and `three_dimension_rows` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-56 Exercise 1, expected output: one row; `three_dimension_rows` should be larger. The final columns are `two_dimension_rows`, and `three_dimension_rows`.
--    Verify: For sql-56 Exercise 1, evaluate each of `two_dimension_rows`, and `three_dimension_rows` in a separate control `SELECT` over `payments`, `orders`, `customers`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
--    Hint ladder, rung 1: For sql-56 Exercise 1, run `payment_by_method`, `ranked_payment`, `primary_payment`, `line`, `cube_two`, and `cube_three` one at a time. Record each CTE's row count and `payment_id` uniqueness before the next stage uses it.
-- 2. Compute p50/p90 of order values per category-month.
--    Inputs: For sql-56 Exercise 2, read from `orders`, `order_items`, and `products`. Build the answer toward `month`, `category`, `p50_order_value`, and `p90_order_value`; keep `month`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-56 Exercise 2, expected output: one row per represented `(month, category)`. The final columns are `month`, `category`, `p50_order_value`, and `p90_order_value`. The final order is `month DESC, category`.
--    Verify: For sql-56 Exercise 2, independently aggregate `orders`, `order_items`, and `products` by `month`, and `category`; require one output row for every distinct `month`, and `category` tuple and compare `p50_order_value`, and `p90_order_value` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `p50_order_value`, and `p90_order_value` for the existing `month`, and `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-56 Exercise 2, run `category_orders` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
-- 3. Prediction: explain why joining raw payments to raw order_items multiplies
--    revenue when an order has several rows in both tables.
--    Inputs: For sql-56 Exercise 3, read from `orders`, `order_items`, and `payments`. Build the answer toward `raw_join_rows`, `distinct_items`, and `distinct_payments`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-56 Exercise 3, expected output: one row per `order_id`. The final columns are `raw_join_rows`, `distinct_items`, and `distinct_payments`.
--    Verify: For sql-56 Exercise 3, project `order_id` plus the raw source columns from `orders`, `order_items`, and `payments` at each join stage; record row count and distinct `order_id`, then assert the final `raw_join_rows`, `distinct_items`, and `distinct_payments` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-56 Exercise 3, start with the first relation in `orders`, `order_items`, and `payments`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 4. Construction: pre-aggregate payment methods at order grain before joining
--    line revenue, and reconcile the result to total line revenue.
--    Inputs: For sql-56 Exercise 4, read from `payments`, and `order_items`. Build the answer toward `reporting_method`, `revenue`, and `reconciled_total`; keep `payment_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-56 Exercise 4, expected output: one row per `payment_id`. The final columns are `reporting_method`, `revenue`, and `reconciled_total`. The final order is `reporting_method`.
--    Verify: For sql-56 Exercise 4, choose one complete partition from `payments`, and `order_items`; hand-calculate its first, middle, and final window values for `revenue`, and `reconciled_total`, then verify output keys remain `payment_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-56 Exercise 4, run `method`, `lines`, and `attributed` one at a time. Record each CTE's row count and `payment_id` uniqueness before the next stage uses it.
-- 5. Debugging: correct a percentile query that calculates percentiles over
--    line items when the metric definition says order value.
--    Inputs: For sql-56 Exercise 5, read from `orders`, `order_items`, and `products`. Build the answer toward `category`, `observations`, and `p50`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-56 Exercise 5, expected output: one row per `category`. The final columns are `category`, `observations`, and `p50`. The final order is `category`.
--    Verify: For sql-56 Exercise 5, independently aggregate `orders`, `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `p50` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `p50` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-56 Exercise 5, run `category_order` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 6. Edge case: compare percentile_cont and percentile_disc for a category-month
--    with an even number of orders and explain which output is an observed value.
--    Inputs: For sql-56 Exercise 6, read from `orders`, `order_items`, and `products`. Build the answer toward `category`, `observations`, `continuous_p50`, and `discrete_p50`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-56 Exercise 6, expected output: one row per `category`. The final columns are `category`, `observations`, `continuous_p50`, and `discrete_p50`. The final order is `category`.
--    Verify: For sql-56 Exercise 6, independently aggregate `orders`, `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `continuous_p50`, and `discrete_p50` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `continuous_p50`, and `discrete_p50` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-56 Exercise 6, run `category_order` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.

ROLLBACK;
