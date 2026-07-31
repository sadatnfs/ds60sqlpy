-- Day 55: Project 4 - Complex BI (Part 1)
-- BEGINNER WORKFLOW — sql-55: Project4 BI Part1
-- Guide: sql/postgres-60day/companion-guides/day55_project4_bi_part1.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-55/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: payments, orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Multi-dimensional analysis (drill-down capability)
BEGIN;
SET search_path TO training, public;

-- Use GROUPING SETS/ROLLUP/CUBE for flexible drilldowns.
-- Dimensions: country, category, primary payment method, month.
-- An order can have split payments, so first choose one reporting label:
-- the method with the greatest paid amount (method name breaks ties).
WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS method_amount
  FROM payments
  GROUP BY order_id, method
), primary_payment_method AS (
  SELECT order_id, method
  FROM (
    SELECT order_id,
           method,
           ROW_NUMBER() OVER (
             PARTITION BY order_id
             ORDER BY method_amount DESC, method
           ) AS method_rank
    FROM payment_by_method
  ) ranked_methods
  WHERE method_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(pm.method, 'unpaid') AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue,
         oi.quantity AS qty
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN primary_payment_method pm ON pm.order_id = o.order_id
)
SELECT country,
       category,
       payment_method,
       month,
       ROUND(SUM(revenue),2) AS revenue,
       SUM(qty) AS units,
       GROUPING(country)        AS g_country,
       GROUPING(category)       AS g_category,
       GROUPING(payment_method) AS g_method,
       GROUPING(month)          AS g_month
FROM line
GROUP BY ROLLUP (country, category, payment_method, month)
ORDER BY country NULLS FIRST, category NULLS FIRST, payment_method NULLS FIRST, month NULLS FIRST;

-- Drill-down example: country -> category -> product (top-N per level)
WITH prod_rev AS (
  SELECT c.country, p.category, p.product_id, p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *,
         RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT * FROM ranked WHERE rnk <= 5
ORDER BY country, category, rnk;

-- Exercises
-- 1. Replace ROLLUP with CUBE to get all subtotal combinations and compare row counts.
--    Inputs: For sql-55 Exercise 1, read from `orders`, `customers`, `order_items`, and `products`. Compute `rollup_row_count`, and `cube_row_count` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-55 Exercise 1, expected output: one comparison row. `CUBE(country, category)` adds category-only subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count is greater on this seed. The final columns are `rollup_row_count`, and `cube_row_count`.
--    Verify: For sql-55 Exercise 1, evaluate each of `rollup_row_count`, and `cube_row_count` in a separate control `SELECT` over `orders`, `customers`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-55 Exercise 1, run `line`, `rollup_rows`, and `cube_rows` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 2. Add a dimension for order status and re-run the drill-down with top-5.
--    Inputs: For sql-55 Exercise 2, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-55 Exercise 2, expected output: up to five rows per `(country, category, status)`. The final columns are `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank`. The final order is `country, category, status, product_rank`.
--    Verify: For sql-55 Exercise 2, project `product_id` plus the raw source columns from `orders`, `customers`, `order_items`, and `products` at each join stage; record row count and distinct `product_id`, then assert the final `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank` values match those staged rows without unintended fanout or loss. Give two rows the same `country` value and different `product_rank` values; verify `country, category, status, product_rank` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-55 Exercise 2, run `line`, `product_revenue`, and `ranked` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
-- 3. Prediction: list the grouping sets produced by ROLLUP(country, category,
--    month) and contrast them with CUBE before running either query.
--    Inputs: For sql-55 Exercise 3, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `revenue`, and `grouping_mask`; keep `country`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-55 Exercise 3, expected output: one row per `country`, and `category`. The final columns are `country`, `category`, `revenue`, and `grouping_mask`. The final order is `grouping_mask, country, category`.
--    Verify: For sql-55 Exercise 3, independently aggregate `orders`, `customers`, `order_items`, and `products` by `country`, and `category`; require one output row for every distinct `country`, and `category` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-55 Exercise 3, run `line` one at a time. Record each CTE's row count and `country`, and `category` uniqueness before the next stage uses it.
-- 4. Construction: use PostgreSQL's GROUPING(country, category) bit mask to
--    assign stable detail/subtotal/grand-total labels without mistaking stored
--    NULLs for subtotal markers.
--    Inputs: For sql-55 Exercise 4, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `level_id`, `level_name`, `country`, `category`, and `revenue`; keep `level_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-55 Exercise 4, expected output: one row per `level_id`. The final columns are `level_id`, `level_name`, `country`, `category`, and `revenue`. The final order is `level_id, country, category`.
--    Verify: For sql-55 Exercise 4, independently aggregate `orders`, `customers`, `order_items`, and `products` by `level_id`; require one output row for every distinct `level_id` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `level_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-55 Exercise 4, run `line` one at a time. Record each CTE's row count and `level_id` uniqueness before the next stage uses it.
-- 5. Debugging: replace RANK with ROW_NUMBER plus a deterministic tie-breaker
--    when the dashboard must show exactly five products per group.
--    Inputs: For sql-55 Exercise 5, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-55 Exercise 5, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`. The final order is `country, position`.
--    Verify: For sql-55 Exercise 5, project `order_id` plus the raw source columns from `orders`, `customers`, `order_items`, and `products` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one row for which `(position <= 5)` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-55 Exercise 5, run `revenue`, and `ranked` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. Edge case: preserve a real '(unknown)' country member separately from the
--    ALL-countries subtotal in both machine-readable and display columns.
--    Inputs: For sql-55 Exercise 6, read from `customers`. Build the answer toward `display_country`, `is_generated_total`, and `customers`; keep `display_country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-55 Exercise 6, expected output: one row per `display_country`. The final columns are `display_country`, `is_generated_total`, and `customers`. The final order is `is_generated_total, display_country`.
--    Verify: For sql-55 Exercise 6, independently aggregate `customers` by `display_country`; require one output row for every distinct `display_country` tuple and compare `is_generated_total`, and `customers` tuple by tuple. Repeat with `NULL` in `display_country`, and `is_generated_total` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-55 Exercise 6, confirm the groups are `display_country`; then check `is_generated_total, display_country` before applying the row cap.

ROLLBACK;
