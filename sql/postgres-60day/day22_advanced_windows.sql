-- Day 22: Advanced Window Function Scenarios
-- BEGINNER WORKFLOW — sql-22: Advanced Windows
-- Guide: sql/postgres-60day/companion-guides/day22_advanced_windows.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-22/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
-- Assumptions: Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
-- Pitfall: Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
-- Predict row grain and NULL/order behavior before executing each example.

-- Multi-level analysis: rank within partition, then across all
WITH prod_rev AS (
  SELECT p.product_id,
         p.name,
         p.category,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.product_id, p.name, p.category
)
SELECT *,
  RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
  RANK() OVER (ORDER BY revenue DESC) AS rank_overall
FROM prod_rev
ORDER BY category, rank_in_category, revenue DESC, product_id
LIMIT 100;

-- Combine multiple windows in one query
SELECT o.customer_id,
       o.order_id,
       o.total_amount,
       AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS avg_per_customer,
       SUM(o.total_amount) OVER () AS total_revenue_all,
       RANK() OVER (PARTITION BY o.customer_id ORDER BY o.total_amount DESC) AS order_value_rank
FROM orders o
ORDER BY o.customer_id,
         order_value_rank,
         o.total_amount DESC,
         o.order_id
LIMIT 100;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Use a named window to show each order with customer count, average, first date, and last date.
--    Hint: Name a full-partition customer window once and reuse it.
--    Inputs: For sql-22 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-22 Exercise 1, expected output: One row per order. The final columns are `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-22 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date` against `orders`. Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-22 Exercise 1, check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 2. [Query writing] Compare each employee salary with the average of other employees in the department.
--    Hint: Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.
--    Inputs: For sql-22 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, and `other_employee_average`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-22 Exercise 2, expected output: One row per employee with nullable peer average. The final columns are `employee_id`, `department_id`, `salary`, and `other_employee_average`. The final order is `e.department_id, e.employee_id`.
--    Verify: For sql-22 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `other_employee_average`, then verify output keys remain `employee_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-22 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.employee_id` before applying the row cap.
-- 3. [Query writing] Show each order's distance from its customer's average and standard deviation.
--    Hint: Compute independent partition windows and guard interpretation when variation is zero.
--    Inputs: For sql-22 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-22 Exercise 3, expected output: One row per order. The final columns are `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-22 Exercise 3, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-22 Exercise 3, check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 4. [Prediction] Sessionize events using a 30-minute gap and predict why the first event starts a session.
--    Hint: Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.
--    Inputs: For sql-22 Exercise 4, read from `events`. Build the answer toward `event_id`, `customer_id`, `event_time`, and `session_number`; keep `event_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-22 Exercise 4, expected output: One row per event with session number starting at one. The final columns are `event_id`, `customer_id`, `event_time`, and `session_number`. The final order is `customer_id, event_time, event_id`.
--    Verify: For sql-22 Exercise 4, choose one complete partition from `events`; hand-calculate its first, middle, and final window values for `event_time`, then verify output keys remain `event_id`. Use a one-row partition and a partition tied on `customer_id`; verify `event_id` and `customer_id, event_time, event_id` preserve the intended first/last row.
--    Hint ladder, rung 1: For sql-22 Exercise 4, run `sequenced`, and `flagged` one at a time. Record each CTE's row count and `event_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Find consecutive calendar-day islands in customer order dates without nesting windows.
--    Hint: Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.
--    Inputs: For sql-22 Exercise 5, read from `orders`. Build the answer toward `customer_id`, `island_start`, `island_end`, and `days_in_island`; keep `customer_id`, and `island_key` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-22 Exercise 5, expected output: One row per customer/date island. The final columns are `customer_id`, `island_start`, `island_end`, and `days_in_island`. The final order is `customer_id, island_start`.
--    Verify: For sql-22 Exercise 5, independently aggregate `orders` by `customer_id`, and `island_key`; require one output row for every distinct `customer_id`, and `island_key` tuple and compare `island_start`, `island_end`, and `days_in_island` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `days_in_island` for the existing `customer_id`, and `island_key` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-22 Exercise 5, run `order_days`, `numbered`, and `grouped` one at a time. Record each CTE's row count and `customer_id`, and `island_key` uniqueness before the next stage uses it.
-- 6. [Extension] Summarize sessions from the sessionized event stream with start, end, event count, and duration.
--    Hint: Aggregate only after session IDs exist at event grain.
--    Inputs: For sql-22 Exercise 6, read from `events`. Build the answer toward `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`; keep `customer_id`, and `session_number` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-22 Exercise 6, expected output: One row per customer session. The final columns are `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`. The final order is `customer_id, session_number`.
--    Verify: For sql-22 Exercise 6, independently aggregate `events` by `customer_id`, and `session_number`; require one output row for every distinct `customer_id`, and `session_number` tuple and compare `event_count`, and `session_duration` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `event_count`, and `session_duration` for the existing `customer_id`, and `session_number` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-22 Exercise 6, run `sequenced`, `flagged`, and `assigned` one at a time. Record each CTE's row count and `customer_id`, and `session_number` uniqueness before the next stage uses it.

ROLLBACK;
