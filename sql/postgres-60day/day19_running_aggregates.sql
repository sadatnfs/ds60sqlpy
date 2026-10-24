-- Day 19: Running Aggregates with Window Functions
-- BEGINNER WORKFLOW — sql-19: Running Aggregates
-- Guide: sql/postgres-60day/companion-guides/day19_running_aggregates.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-19/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
-- Assumptions: Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
-- Pitfall: Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
-- Predict row grain and NULL/order behavior before executing each example.

-- Running total per customer by order date
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 200;

-- Moving average across seven observed UTC dates. Densify the calendar first
-- if the business meaning requires exactly seven consecutive calendar dates.
WITH daily AS (
  SELECT (order_date AT TIME ZONE 'UTC')::date AS d_utc,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY d_utc
)
SELECT d_utc,
       revenue,
       ROUND(AVG(revenue) OVER (
         ORDER BY d_utc
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ),2) AS ma7
FROM daily
ORDER BY d_utc DESC
LIMIT 40;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate cumulative stored revenue across all orders.
--    Hint: Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.
--    Inputs: For sql-19 Exercise 1, read from `orders`. Build the answer toward `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-19 Exercise 1, expected output: One row per order with nondecreasing cumulative revenue. The final columns are `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`. The final order is `o.order_date, o.order_id`.
--    Verify: For sql-19 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, `total_amount`, and `cumulative_revenue`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-19 Exercise 1, inspect one window partition before projecting; then check `o.order_date, o.order_id` before applying the row cap.
-- 2. [Query writing] Calculate each customer's cumulative stored spend.
--    Hint: Partition by customer and reset the explicit row frame for every customer.
--    Inputs: For sql-19 Exercise 2, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-19 Exercise 2, expected output: One row per order. The final columns are `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-19 Exercise 2, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, `total_amount`, and `customer_cumulative_spend`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-19 Exercise 2, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 3. [Query writing] Calculate a trailing seven-order average within each customer.
--    Hint: A seven-row frame is based on observations, not seven calendar days.
--    Inputs: For sql-19 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-19 Exercise 3, expected output: One row per order with up to seven observations in its frame. The final columns are `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-19 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, and `trailing_7_order_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-19 Exercise 3, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 4. [Prediction] Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
--    Hint: `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
--    Inputs: For sql-19 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`; keep `row_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-19 Exercise 4, expected output: Three rows making the peer difference visible. The final columns are `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`. The final order is `row_id`.
--    Verify: For sql-19 Exercise 4, hand-calculate all three peer rows from the inline fixture: `rows_sum` must be `(10, 30, 35)` while `range_sum` must be `(30, 30, 35)` in `row_id` order. Require three unique `row_id` values and explain why the two rows tied at `sort_value = 1` advance separately under `ROWS` but together under `RANGE`.
--    Hint ladder, rung 1: For sql-19 Exercise 4, inspect one window partition before projecting; then check `row_id` before applying the row cap.
-- 5. [Debugging] Reset a running expense total at each category and month.
--    Hint: Partition by both reset keys and order by date plus expense ID.
--    Inputs: For sql-19 Exercise 5, read from `expenses`. Build the answer toward `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`; keep `expense_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-19 Exercise 5, expected output: One row per expense. The final columns are `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`. The final order is `e.category, e.expense_date, e.expense_id`.
--    Verify: For sql-19 Exercise 5, choose one complete partition from `expenses`; hand-calculate its first, middle, and final window values for `amount`, then verify output keys remain `expense_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-19 Exercise 5, inspect one window partition before projecting; then check `e.category, e.expense_date, e.expense_id` before applying the row cap.
-- 6. [Extension] Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
--    Hint: Select the last ordered cumulative value and compare it with an independent aggregate.
--    Inputs: For sql-19 Exercise 6, read from `orders`. Build the answer toward `final_cumulative`, `aggregate_total`, and `difference`; keep `cumulative_revenue` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-19 Exercise 6, expected output: One row with zero difference. The final columns are `final_cumulative`, `aggregate_total`, and `difference`.
--    Verify: For sql-19 Exercise 6, independently aggregate `orders` by `cumulative_revenue`; require one output row for every distinct `cumulative_revenue` tuple and compare `aggregate_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `aggregate_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-19 Exercise 6, run `running`, and `final_running` one at a time. Record each CTE's row count and `cumulative_revenue` uniqueness before the next stage uses it.

ROLLBACK;
