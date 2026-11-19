-- Day 16: Window Functions Fundamentals
-- BEGINNER WORKFLOW - sql-16: Window Functions Fundamentals
-- Guide: sql/postgres-60day/companion-guides/day16_window_functions_fundamentals.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-16.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
-- OVER(), PARTITION BY, ORDER BY, frames
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
-- Assumptions: Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
-- Pitfall: Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
-- Predict row grain and NULL/order behavior before executing each example.
-- Aggregate once, then use a window over the grouped result to calculate
-- the grand total without a second query.
WITH category_totals AS (
  SELECT
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    order_items oi
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category
)
SELECT
  category,
  ROUND(revenue, 2) AS category_revenue,
  ROUND(SUM(revenue) OVER (), 2) AS total_revenue,
  ROUND(revenue / NULLIF (SUM(revenue) OVER (), 0), 4) AS category_share
FROM
  category_totals
ORDER BY
  category_revenue DESC,
  category;

-- Row-wise metrics without collapsing rows
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  o.total_amount,
  ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2) AS avg_customer_order,
  COUNT(*) OVER (PARTITION BY o.customer_id) AS orders_per_customer
FROM
  orders o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id
LIMIT 100;

-- Frame example. ROWS counts observed rows, not necessarily seven consecutive
-- calendar days; a dense date spine is required when empty dates matter.
WITH daily AS (
  SELECT
    (o.order_date AT TIME ZONE 'UTC')::date AS d_utc,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    d_utc
)
SELECT
  d_utc,
  revenue,
  SUM(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7_observed_days
FROM
  daily
ORDER BY
  d_utc DESC
LIMIT 30;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show each order with the customer's average order total.
--    Hint: Partition by customer ID and keep one output row per order.
--    Inputs: For sql-16 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_average`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-16 Exercise 1, expected output: One row per order. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-16 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `total_amount`, and `customer_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-16 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 2. [Query writing] Show each employee salary with department average, minimum, and maximum.
--    Hint: Partition all three window aggregates by department.
--    Inputs: For sql-16 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-16 Exercise 2, expected output: One row per employee. The final columns are `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`. The final order is `e.department_id, e.employee_id`.
--    Verify: For sql-16 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `department_average`, then verify output keys remain `employee_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-16 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.employee_id` before applying the row cap.
-- 3. [Query writing] Calculate every order's share of its customer's stored revenue.
--    Hint: Use a partition total denominator and guard it with `NULLIF`.
--    Inputs: For sql-16 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-16 Exercise 3, expected output: One row per order with shares summing near one per customer. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-16 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `total_amount`, and `customer_revenue_share`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-16 Exercise 3, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 4. [Prediction] Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.
--    Hint: Grouping collapses to one row per customer; a window preserves every order row.
--    Inputs: For sql-16 Exercise 4, compare a `grouped` CTE (`AVG(o.total_amount) ... GROUP BY o.customer_id`) with a `windowed` CTE (`AVG(o.total_amount) OVER (PARTITION BY o.customer_id)`) over `orders`, then count the rows of each.
--    Expected result/shape: For sql-16 Exercise 4, expected output: two rows ordered by `method`, with columns `method` and `row_count`: `('grouped', 438)` and `('windowed', 4362)` on the course seed.
--    Verify: For sql-16 Exercise 4, confirm that the `grouped` count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` and the `windowed` count equals `SELECT COUNT(*) FROM orders`; grouping keeps one row per ordering customer, while the window keeps every order row.
--    Hint ladder, rung 1: For sql-16 Exercise 4, predict both counts before running: one comes from `orders`' distinct customers, the other from its rows.
-- 5. [Debugging] Return orders above their customer average without placing a window function in `WHERE`.
--    Hint: Compute the window value in a CTE, then filter the named column outside.
--    Inputs: For sql-16 Exercise 5, compute `AVG(o.total_amount) OVER (PARTITION BY o.customer_id)` as `customer_average` in a `scored` CTE over `orders`, then filter `total_amount > customer_average` in the outer query.
--    Expected result/shape: For sql-16 Exercise 5, expected output: one row per `order_id` whose `total_amount` is strictly above its customer's mean (2,249 rows on the course seed), with columns `order_id`, `customer_id`, `total_amount`, and `customer_average` (rounded to 2 places), ordered by `customer_id, total_amount DESC, order_id`.
--    Verify: For sql-16 Exercise 5, compare the row count with `SELECT COUNT(*) FROM orders o WHERE o.total_amount > (SELECT AVG(i.total_amount) FROM orders i WHERE i.customer_id = o.customer_id)` (2,249), require unique `order_id`, and confirm that moving the window expression into `WHERE` fails with `window functions are not allowed in WHERE`.
--    Hint ladder, rung 1: For sql-16 Exercise 5, a window value exists only after `WHERE` has run, so name it in a CTE and filter it one query level out.
-- 6. [Extension] Show order count and revenue context at both customer and country levels in the same row.
--    Hint: Use different partitions for independent analytical contexts.
--    Inputs: For sql-16 Exercise 6, read from `orders`, and `customers`. Build the answer toward `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-16 Exercise 6, expected output: One row per order with customer and country totals. The final columns are `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`. The final order is `c.country, o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-16 Exercise 6, choose one complete partition from `orders`, and `customers`; hand-calculate its first, middle, and final window values for `customer_order_count`, `customer_revenue`, and `country_revenue`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-16 Exercise 6, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
ROLLBACK;
