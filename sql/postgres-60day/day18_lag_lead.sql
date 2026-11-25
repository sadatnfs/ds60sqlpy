-- Day 18: LAG and LEAD
-- BEGINNER WORKFLOW - sql-18: LAG and LEAD
-- Guide: sql/postgres-60day/companion-guides/day18_lag_lead.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-18.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    o.customer_id,
    o.order_id,
    o.order_date,
    o.total_amount
  FROM
    orders o
)
SELECT
  customer_id,
  order_id,
  order_date,
  total_amount,
  LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS prev_order_amount,
  total_amount - LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS delta_from_prev,
  LEAD(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS next_order_amount
FROM
  cust_orders
ORDER BY
  customer_id,
  order_date,
  order_id
LIMIT 100;

-- YoY comparison by month
WITH monthly AS (
  SELECT
    date_trunc('month', order_date AT TIME ZONE 'UTC')::date AS month_utc,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    month_utc
),
compared AS (
  SELECT
    month_utc,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY month_utc) AS revenue_prev_year
  FROM
    monthly
)
SELECT
  month_utc,
  revenue,
  revenue_prev_year,
  ROUND((revenue - revenue_prev_year) / NULLIF (revenue_prev_year, 0), 4) AS yoy_growth
FROM
  compared
ORDER BY
  month_utc DESC
LIMIT 36;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show each order with the previous order timestamp for that customer.
--    Hint: Partition by customer and order by timestamp plus ID.
--    Inputs: For sql-18 Exercise 1, attach `LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id)` to each of the 4,362 `orders` rows; every buyer has at least 4 orders.
--    Expected result/shape: For sql-18 Exercise 1, return 4,362 rows, one per order, with `previous_order_date` `NULL` on exactly 438 rows, one per buyer's first order; customer 1's orders 1 to 5 show `NULL` and then the dates of orders 1, 2, 3, and 4. The final columns are `order_id`, `customer_id`, `order_date`, and `previous_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-18 Exercise 1, confirm 4,362 distinct `order_id` values, 438 `NULL` previous dates, and that every non-null `previous_order_date` is earlier than its row's `order_date`. Inside a rolled-back transaction, add one order for customer 8, who has none; that new one-row partition must show `NULL`, and customer 1's first row must stay order 1 with `NULL`.
--    Hint ladder, rung 1: For sql-18 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 2. [Query writing] Calculate days since each customer's previous order.
--    Hint: Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
--    Inputs: For sql-18 Exercise 2, compute `previous_order_date` with `LAG` in the `sequenced` CTE, then convert the gap to days with `EXTRACT(EPOCH FROM (order_date - previous_order_date)) / 86400.0`.
--    Expected result/shape: For sql-18 Exercise 2, return 4,362 rows, one per order, with 438 `NULL` gaps; customer 1's four gaps are each 7.9005282256944444 days, and the 3,924 non-null gaps run from 2.2882 to 296.6473 days and average 65.4524. The final columns are `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`. The final order is `customer_id, order_date, order_id`.
--    Verify: For sql-18 Exercise 2, confirm 3,924 non-null `days_since_previous` values and none at zero or below, since no customer has two orders at the same instant. Inside a rolled-back transaction, add an order for customer 1 with order 5's exact `order_date`; it sorts after order 5 by `order_id` and must show a gap of exactly 0.
--    Hint ladder, rung 1: For sql-18 Exercise 2, run `sequenced` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 3. [Query writing] Show each promotion with the next promotion start date for the same product.
--    Hint: Partition by product and define a stable chronological order.
--    Inputs: For sql-18 Exercise 3, attach `LEAD(pr.start_date) OVER (PARTITION BY pr.product_id ORDER BY pr.start_date, pr.promotion_id)` to each of the 200 `promotions` rows, which cover 200 different products.
--    Expected result/shape: For sql-18 Exercise 3, return 200 rows, one per promotion, and every `next_promotion_start` is `NULL`, because no product has a second promotion; the first row is promotion 7 for product 1. The final columns are `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`. The final order is `pr.product_id, pr.start_date, pr.promotion_id`.
--    Verify: For sql-18 Exercise 3, confirm that `SELECT product_id FROM promotions GROUP BY product_id HAVING COUNT(*) > 1` returns no rows, which explains the 200 `NULL` values. Inside a rolled-back transaction, copy promotion 7 for product 1 with both dates moved 30 days later; promotion 7 must then show the copy's `start_date` as its next start, while the copy shows `NULL`, leaving 201 rows with 200 `NULL` values.
--    Hint ladder, rung 1: For sql-18 Exercise 3, inspect one window partition before projecting; then check `pr.product_id, pr.start_date, pr.promotion_id` before applying the row cap.
-- 4. [Prediction] Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
--    Hint: NULL means there is no prior observation; preserve that semantic state.
--    Inputs: For sql-18 Exercise 4, attach `LAG(o.order_id)` per customer, ordered by `o.order_date, o.order_id`, in the `sequenced` CTE, then keep the rows where `previous_order_id IS NULL`.
--    Expected result/shape: For sql-18 Exercise 4, return 438 rows, one first order per buyer, with no rows for the 62 customers who never ordered; customer 1 returns order 1 and customer 500 returns order 4353. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `customer_id`.
--    Verify: For sql-18 Exercise 4, confirm 438 distinct `customer_id` values and that all 438 rows match `SELECT customer_id, MIN(order_date) FROM orders GROUP BY customer_id`; their `total_amount` values add up to 236703.47. `order_id`, `customer_id`, and `order_date` are all `NOT NULL`, so test with inserts instead: inside a rolled-back transaction, add an order for customer 1 dated one day before order 1 and an order for customer 8; the result must grow to 439 rows, and customer 1 must return the new order instead of order 1.
--    Hint ladder, rung 1: For sql-18 Exercise 4, run `sequenced` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Compute month-over-month stored-revenue change after aggregating to month grain.
--    Hint: Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
--    Inputs: For sql-18 Exercise 5, read from `orders`, aggregate `SUM(total_amount)` to one row per UTC month in the CTE `monthly`, then apply `LAG(revenue) OVER (ORDER BY month_start)` to those monthly rows and compute `revenue_change = revenue - previous_revenue`.
--    Expected result/shape: For sql-18 Exercise 5, return 46 rows, one per UTC month with orders; on a fixture loaded on 2026-11-25 the first row is `2023-02-01` with revenue 1203.26 and `NULL` comparisons, and the last is the partial month `2026-11-01` with 85364.67, a change of -84814.46 from 170179.13. The final columns are `month_start`, `revenue`, `previous_revenue`, and `revenue_change`. The final order is `month_start`.
--    Verify: For sql-18 Exercise 5, confirm that `month_start` is unique and that the row count equals `SELECT COUNT(DISTINCT date_trunc('month', order_date AT TIME ZONE 'UTC')) FROM orders`; exactly one row, the earliest month, has NULL `previous_revenue` and `revenue_change`, and the `revenue` values add up to 2355646.89, the total of `orders.total_amount`.
--    Hint ladder, rung 1: For sql-18 Exercise 5, run `monthly` alone and check that it has one row per month before `compared` applies `LAG`; applying `LAG` to raw orders would compare adjacent orders, not months.
-- 6. [Extension] Compare each product price with the next higher price in its category.
--    Hint: Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
--    Inputs: For sql-18 Exercise 6, attach `LEAD(p.price) OVER (PARTITION BY p.category ORDER BY p.price, p.product_id)` to each of the 300 `products` rows across 6 categories.
--    Expected result/shape: For sql-18 Exercise 6, return 300 rows, one per product, with `next_price` `NULL` only on the 6 most expensive products, one per category; `Apparel` starts with product 1 at 10.37 followed by 12.59, and `Sports` ends with product 299 at 120.63. The final columns are `product_id`, `category`, `price`, and `next_price`. The final order is `p.category, p.price, p.product_id`.
--    Verify: For sql-18 Exercise 6, confirm 294 non-null `next_price` values and that `next_price - price` is exactly 2.22 on all of them, because each category's prices rise in even steps. Inside a rolled-back transaction, set product 7's price to 10.37; product 1 must then show a `next_price` of 10.37 (the tie is broken by `p.product_id`) and product 7 must show 14.81.
--    Hint ladder, rung 1: For sql-18 Exercise 6, inspect one window partition before projecting; then check `p.category, p.price, p.product_id` before applying the row cap.
ROLLBACK;
