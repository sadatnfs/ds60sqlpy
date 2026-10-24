-- Day 46: Project 1 - E-commerce Analytics (Part 1)
-- BEGINNER WORKFLOW — sql-46: Project1 Ecommerce Part1
-- Guide: sql/postgres-60day/companion-guides/day46_project1_ecommerce_part1.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-46/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Topics: Customer segmentation by lifetime value, cohort setup
BEGIN;
SET search_path TO training, public;

-- Lifetime Value (LTV)
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, ROUND(SUM(order_value),2) AS ltv
  FROM order_values
  GROUP BY customer_id
)
SELECT c.customer_id, c.country, c.segment, l.ltv,
       NTILE(4) OVER (ORDER BY l.ltv DESC) AS ltv_quartile
FROM customers c
JOIN ltv l ON l.customer_id = c.customer_id
ORDER BY l.ltv DESC
LIMIT 100;

-- Cohort setup by signup month
SELECT date_trunc('month', created_at)::date AS cohort_month,
       COUNT(*) AS new_customers
FROM customers
GROUP BY 1
ORDER BY cohort_month DESC;

-- Exercises
-- 1. Create LTV segments (gold/silver/bronze) based on thresholds and analyze by country.
--    Inputs: For sql-46 Exercise 1, read from `customers`, and `orders`. Build the answer toward `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`; keep `country`, and `ltv_segment` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-46 Exercise 1, expected output: one row per `(country, ltv_segment)`. The final columns are `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`. The final order is `country, avg_ltv DESC`.
--    Verify: For sql-46 Exercise 1, independently aggregate `customers`, and `orders` by `country`, and `ltv_segment`; require one output row for every distinct `country`, and `ltv_segment` tuple and compare `customers`, `avg_ltv`, and `total_ltv` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customers`, `avg_ltv`, and `total_ltv` for the existing `country`, and `ltv_segment` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-46 Exercise 1, run `lifetime`, and `segmented` one at a time. Record each CTE's row count and `country`, and `ltv_segment` uniqueness before the next stage uses it.
-- 2. Compute revenue per cohort month at month offsets 0..12.
--    Inputs: For sql-46 Exercise 2, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, and `revenue`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-46 Exercise 2, expected output: one row per cohort and lifecycle month. The final columns are `cohort_month`, `month_offset`, and `revenue`. The final order is `cohort_month DESC, month_offset`.
--    Verify: For sql-46 Exercise 2, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, and `revenue` values match those staged rows without unintended fanout or loss. Add one row for which `(month_offset BETWEEN 0 AND 12)` is true and one for which it is false; verify only the matching `cohort_month` value is returned.
--    Hint ladder, rung 1: For sql-46 Exercise 2, run `cohorts`, `monthly_customer`, and `cohort_revenue` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 3. Prediction: compare NTILE(4) with fixed monetary thresholds. Explain why a
--    customer's label can change under NTILE when unrelated customers arrive.
--    Inputs: For sql-46 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-46 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`. The final order is `ltv DESC, customer_id`.
--    Verify: For sql-46 Exercise 3, choose one complete partition from `customers`, and `orders`; hand-calculate its first, middle, and final window values for `ltv`, `population_quartile`, and `fixed_segment`, then verify output keys remain `customer_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-46 Exercise 3, run `lifetime` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 4. Construction: calculate customer LTV, order count, average order value, and
--    days since last order in one customer-grain result.
--    Inputs: For sql-46 Exercise 4, read from `orders`, and `customers`. Build the answer toward `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-46 Exercise 4, expected output: one row per `customer_id`. The final columns are `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`. The final order is `ltv DESC, c.customer_id`.
--    Verify: For sql-46 Exercise 4, project `customer_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `customer_id`, then assert the final `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-46 Exercise 4, run `behavior` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 5. Debugging: repair an LTV query that joins payments and order_items at raw
--    grain and therefore multiplies revenue.
--    Inputs: For sql-46 Exercise 5, read from `orders`, and `order_items`. Build the answer toward `customer_id`, and `line_ltv`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-46 Exercise 5, expected output: one row per order before it becomes customer LTV. The final columns are `customer_id`, and `line_ltv`. The final order is `line_ltv DESC, customer_id`.
--    Verify: For sql-46 Exercise 5, independently aggregate `orders`, and `order_items` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `line_ltv` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `line_ltv` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-46 Exercise 5, run `order_value` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 6. Edge case: retain customers with no orders, assign zero LTV, and explain
--    where COALESCE belongs so the LEFT JOIN remains outer.
--    Inputs: For sql-46 Exercise 6, read from `customers`, and `orders`. Build the answer toward `customer_id`, `ltv`, and `activity_status`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-46 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_id`, `ltv`, and `activity_status`. The final order is `c.customer_id`.
--    Verify: For sql-46 Exercise 6, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `ltv`, and `activity_status` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `ltv`, and `activity_status` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-46 Exercise 6, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.

ROLLBACK;
