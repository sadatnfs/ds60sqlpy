-- Day 26: CTEs with Window Functions
-- BEGINNER WORKFLOW — sql-26: CTEs with Windows
-- Guide: sql/postgres-60day/companion-guides/day26_ctes_with_windows.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-26/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
-- Assumptions: Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
-- Pitfall: Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
-- Predict row grain and NULL/order behavior before executing each example.

WITH line AS (
  SELECT o.order_id, o.customer_id, o.order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), ranked AS (
  SELECT line.*,
         RANK() OVER (
           PARTITION BY customer_id
           ORDER BY order_total DESC
         ) AS rnk
  FROM line
)
SELECT customer_id, order_id, order_date, order_total, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY customer_id, rnk, order_total DESC, order_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate monthly stored revenue and its prior-month value/change.
--    Hint: Aggregate to month in a CTE, then lag the monthly measure.
--    Inputs: For sql-26 Exercise 1, read from `orders`. Build the answer toward `month_start`, `revenue`, `previous_revenue`, and `change`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-26 Exercise 1, expected output: One row per observed month. The final columns are `month_start`, `revenue`, `previous_revenue`, and `change`. The final order is `month_start`.
--    Verify: For sql-26 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `month_start`, `revenue`, `previous_revenue`, and `change` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-26 Exercise 1, run `monthly`, and `compared` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 2. [Query writing] Rank product categories by net revenue within each UTC order month.
--    Hint: Aggregate month/category first, then rank the stable aggregate.
--    Inputs: For sql-26 Exercise 2, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `revenue_rank`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-26 Exercise 2, expected output: One row per observed month/category. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
--    Verify: For sql-26 Exercise 2, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, and `revenue_rank`, then verify output keys remain `category`. Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-26 Exercise 2, run `category_month` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 3. [Query writing] Return the top three category revenue levels per month.
--    Hint: Rank in one CTE and filter the window result outside.
--    Inputs: For sql-26 Exercise 3, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `revenue_rank`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-26 Exercise 3, expected output: Top three revenue ranks for each observed month. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
--    Verify: For sql-26 Exercise 3, project `category` plus the raw source columns from `orders`, `order_items`, and `products` at each join stage; record row count and distinct `category`, then assert the final `month_start`, `category`, `revenue`, and `revenue_rank` values match those staged rows without unintended fanout or loss. Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-26 Exercise 3, run `category_month`, and `ranked` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 4. [Prediction] Calculate each category's cumulative share of monthly revenue in descending contribution order.
--    Hint: Divide running category revenue by the full monthly total; use explicit frames.
--    Inputs: For sql-26 Exercise 4, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `cumulative_revenue_share`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-26 Exercise 4, expected output: One row per month/category with final share equal to one. The final columns are `month_start`, `category`, `revenue`, and `cumulative_revenue_share`. The final order is `month_start, revenue DESC, category`.
--    Verify: For sql-26 Exercise 4, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, and `cumulative_revenue_share`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-26 Exercise 4, run `category_month` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 5. [Debugging] Calculate a three-month moving average after building a dense month calendar.
--    Hint: Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
--    Inputs: For sql-26 Exercise 5, read from `orders`. Build the answer toward `month_start`, `revenue`, and `moving_3_month_average`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-26 Exercise 5, expected output: A continuous chronological month series. The final columns are `month_start`, `revenue`, and `moving_3_month_average`. The final order is `month_start`.
--    Verify: For sql-26 Exercise 5, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, and `moving_3_month_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-26 Exercise 5, run `bounds`, `calendar`, `monthly`, and `dense` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. [Extension] Reconcile the final cumulative monthly revenue with the independent order total.
--    Hint: Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
--    Inputs: For sql-26 Exercise 6, read from `orders`. Build the answer toward `final_cumulative`, `independent_total`, and `difference`; keep `cumulative_revenue` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-26 Exercise 6, expected output: One row with zero difference. The final columns are `final_cumulative`, `independent_total`, and `difference`.
--    Verify: For sql-26 Exercise 6, independently aggregate `orders` by `cumulative_revenue`; require one output row for every distinct `cumulative_revenue` tuple and compare `independent_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `independent_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-26 Exercise 6, run `monthly`, `running`, and `final` one at a time. Record each CTE's row count and `cumulative_revenue` uniqueness before the next stage uses it.

ROLLBACK;
