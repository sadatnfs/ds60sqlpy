-- Day 18: LAG and LEAD
-- BEGINNER WORKFLOW — sql-18: Lag Lead
-- Guide: sql/postgres-60day/companion-guides/day18_lag_lead.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-18/ copy, and prints the full
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
-- Focus: Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
-- Assumptions: Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
-- Pitfall: Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
-- Predict row grain and NULL/order behavior before executing each example.

-- Period-over-period change per customer
WITH cust_orders AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount
  FROM orders o
)
SELECT customer_id,
       order_id,
       order_date,
       total_amount,
       LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS prev_order_amount,
       total_amount - LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS delta_from_prev,
       LEAD(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS next_order_amount
FROM cust_orders
ORDER BY customer_id, order_date, order_id
LIMIT 100;

-- YoY comparison by month
WITH monthly AS (
  SELECT date_trunc('month', order_date AT TIME ZONE 'UTC')::date AS month_utc,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY month_utc
), compared AS (
  SELECT month_utc,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month_utc) AS revenue_prev_year
  FROM monthly
)
SELECT month_utc,
       revenue,
       revenue_prev_year,
       ROUND(
         (revenue - revenue_prev_year)
         / NULLIF(revenue_prev_year, 0),
         4
       ) AS yoy_growth
FROM compared
ORDER BY month_utc DESC
LIMIT 36;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show each order with the previous order timestamp for that customer.
--    Hint: Partition by customer and order by timestamp plus ID.
--    Inputs: For sql-18 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `previous_order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-18 Exercise 1, expected output: One row per order; first customer order has NULL previous timestamp. The final columns are `order_id`, `customer_id`, `order_date`, and `previous_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-18 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, and `previous_order_date`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-18 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 2. [Query writing] Calculate days since each customer's previous order.
--    Hint: Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
--    Inputs: For sql-18 Exercise 2, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-18 Exercise 2, expected output: One row per order with nullable interval/days. The final columns are `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`. The final order is `customer_id, order_date, order_id`.
--    Verify: For sql-18 Exercise 2, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-18 Exercise 2, run `sequenced` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 3. [Query writing] Show each promotion with the next promotion start date for the same product.
--    Hint: Partition by product and define a stable chronological order.
--    Inputs: For sql-18 Exercise 3, read from `promotions`. Build the answer toward `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`; keep `promotion_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-18 Exercise 3, expected output: One row per promotion; last product promotion has NULL next date. The final columns are `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`. The final order is `pr.product_id, pr.start_date, pr.promotion_id`.
--    Verify: For sql-18 Exercise 3, choose one complete partition from `promotions`; hand-calculate its first, middle, and final window values for `product_id`, `start_date`, and `next_promotion_start`, then verify output keys remain `promotion_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-18 Exercise 3, inspect one window partition before projecting; then check `pr.product_id, pr.start_date, pr.promotion_id` before applying the row cap.
-- 4. [Prediction] Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
--    Hint: NULL means there is no prior observation; preserve that semantic state.
--    Inputs: For sql-18 Exercise 4, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-18 Exercise 4, expected output: One row per customer's first order. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `customer_id`.
--    Verify: For sql-18 Exercise 4, run an anti-check that counts rows where NOT ((previous_order_id IS NULL)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `order_date` against `orders`. Repeat with `NULL` in `order_id`, and `customer_id` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-18 Exercise 4, run `sequenced` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Compute month-over-month stored-revenue change after aggregating to month grain.
--    Hint: Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
--    Inputs: For sql-18 Exercise 5, read from `orders`. Build the answer toward `month_start`, `revenue`, `previous_revenue`, and `revenue_change`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-18 Exercise 5, expected output: One row per month with nullable first change. The final columns are `month_start`, `revenue`, `previous_revenue`, and `revenue_change`. The final order is `month_start`.
--    Verify: For sql-18 Exercise 5, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month_start`, `revenue`, `previous_revenue`, and `revenue_change` against `orders`. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
--    Hint ladder, rung 1: For sql-18 Exercise 5, run `monthly`, and `compared` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 6. [Extension] Compare each product price with the next higher price in its category.
--    Hint: Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
--    Inputs: For sql-18 Exercise 6, read from `products`. Build the answer toward `product_id`, `category`, `price`, and `next_price`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-18 Exercise 6, expected output: One row per product with nullable next price. The final columns are `product_id`, `category`, `price`, and `next_price`. The final order is `p.category, p.price, p.product_id`.
--    Verify: For sql-18 Exercise 6, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `category`, `price`, and `next_price`, then verify output keys remain `product_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-18 Exercise 6, inspect one window partition before projecting; then check `p.category, p.price, p.product_id` before applying the row cap.

ROLLBACK;
