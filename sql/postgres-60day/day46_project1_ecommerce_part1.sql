-- Day 46: Project 1 - E-commerce Analytics (Part 1)
-- BEGINNER WORKFLOW - sql-46: Project 1 Ecommerce Part 1
-- Guide: sql/postgres-60day/companion-guides/day46_project1_ecommerce_part1.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-46.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    o.order_id
),
ltv AS (
  SELECT
    customer_id,
    ROUND(SUM(order_value), 2) AS ltv
  FROM
    order_values
  GROUP BY
    customer_id
)
SELECT
  c.customer_id,
  c.country,
  c.segment,
  l.ltv,
  NTILE(4) OVER (ORDER BY l.ltv DESC) AS ltv_quartile
FROM
  customers c
  JOIN ltv l ON l.customer_id = c.customer_id
ORDER BY
  l.ltv DESC
LIMIT 100;

-- Cohort setup by signup month
SELECT
  date_trunc('month', created_at)::date AS cohort_month,
  COUNT(*) AS new_customers
FROM
  customers
GROUP BY
  1
ORDER BY
  cohort_month DESC;

-- Exercises
-- 1. Create LTV segments (gold/silver/bronze) based on thresholds and analyze by country.
--    Inputs: For sql-46 Exercise 1, build `lifetime` from `customers` `LEFT JOIN orders` grouped by `customer_id` and `country` with `COALESCE(SUM(total_amount), 0)` as `ltv`, label it in `segmented` with `ltv >= 20000` as gold and `ltv >= 10000` as silver, then count customers and sum LTV by `country` and `ltv_segment`.
--    Expected result/shape: For sql-46 Exercise 1, expected output: one row per (`country`, `ltv_segment`) pair that has customers, with columns `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`, ordered by `country`, then `avg_ltv DESC`. On the course data every customer is bronze, so it returns 8 rows, one per country.
--    Verify: For sql-46 Exercise 1, confirm that `customers` sums to 500 and `total_ltv` sums to 2355646.89, equal to `SELECT SUM(total_amount) FROM orders`; confirm BR shows 62 customers at 0.00 and the highest single LTV is 9502.21 (customer 181), below the silver cutoff; then evaluate the same `CASE` on `VALUES (20000.00), (19999.99), (10000.00), (9999.99)` and confirm gold, silver, silver, bronze, so each boundary value falls into the higher band.
--    Hint ladder, rung 1: For sql-46 Exercise 1, run `lifetime`, and `segmented` one at a time. Record each CTE's row count and `country`, and `ltv_segment` uniqueness before the next stage uses it.
-- 2. Compute revenue per cohort month at month offsets 0..12.
--    Inputs: For sql-46 Exercise 2, take each customer's `cohort_month` from `date_trunc('month', created_at)`, sum `orders.total_amount` by `customer_id` and order month in `monthly_customer`, compute `month_offset` from `age()` as years times 12 plus months, and keep offsets 0 through 12.
--    Expected result/shape: For sql-46 Exercise 2, expected output: one row per (`cohort_month`, `month_offset`) pair with any revenue, with columns `cohort_month`, `month_offset`, and `revenue`, ordered by `cohort_month DESC`, then `month_offset`; 487 rows over 48 cohorts on our load, with offsets from 0 to 12.
--    Verify: For sql-46 Exercise 2, confirm that (`cohort_month`, `month_offset`) is unique and that `SUM(revenue)` equals an independent `SUM(o.total_amount)` over orders whose order month falls on or after the customer's cohort month and before that month plus `interval '13 months'` (1410578.53 on our load); then check that `age(date '2025-02-01', date '2024-01-01')` gives offset 13, not 1, so the year term is what keeps that month out of the result.
--    Hint ladder, rung 1: For sql-46 Exercise 2, run `cohorts`, `monthly_customer`, and `cohort_revenue` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 3. Prediction: compare NTILE(4) with fixed monetary thresholds. Explain why a
--    customer's label can change under NTILE when unrelated customers arrive.
--    Inputs: For sql-46 Exercise 3, from `lifetime` (one row per `customer_id` with `COALESCE(SUM(total_amount), 0)` as `ltv`), assign `NTILE(4) OVER (ORDER BY ltv DESC, customer_id)` and a fixed `CASE` that labels `ltv >= 5000` gold and `ltv >= 2000` silver.
--    Expected result/shape: For sql-46 Exercise 3, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`, ordered by `ltv DESC`, then `customer_id`; each quartile has exactly 125 customers, while the fixed labels give 246 gold, 171 silver, and 83 bronze.
--    Verify: For sql-46 Exercise 3, cross-tabulate `population_quartile` by `fixed_segment` and confirm that quartile 2 holds 121 gold and 4 silver customers and quartile 4 holds 83 bronze and 42 silver; check the boundary rows by `row_number()`: customer 203 at 6971.42 is the last row of quartile 1 and customer 139 at 6961.84 the first of quartile 2. Then, in a rolled-back transaction, insert 4 customers with orders above 9502.21 and confirm customer 203 moves to quartile 2 while its fixed label stays gold.
--    Hint ladder, rung 1: For sql-46 Exercise 3, run `lifetime` alone first and confirm 500 rows with unique `customer_id`; then add the `NTILE` column and count rows per quartile before adding the fixed labels.
-- 4. Construction: calculate customer LTV, order count, average order value, and
--    days since last order in one customer-grain result.
--    Inputs: For sql-46 Exercise 4, aggregate `orders` to one row per `customer_id` in `behavior` (`COUNT(*)`, `SUM(total_amount)`, `AVG(total_amount)`, and `MAX(order_date)`), then `LEFT JOIN` it from `customers` so customers without orders stay in the result.
--    Expected result/shape: For sql-46 Exercise 4, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`, ordered by `ltv DESC`, then `customer_id`; customer 181 leads with 16 orders and 9502.21.
--    Verify: For sql-46 Exercise 4, confirm that `order_count` sums to 4362 and `ltv` sums to 2355646.89, matching `orders`, and that exactly 62 rows have `order_count` 0, `ltv` 0, and `NULL` in both `average_order_value` and `days_since_last_order`; recompute customer 181 directly from `orders` (16 orders, average 593.89) and confirm that `days_since_last_order` equals `CURRENT_DATE - MAX(order_date)::date`, which changes with the run date.
--    Hint ladder, rung 1: For sql-46 Exercise 4, run `behavior` alone and confirm 438 rows with unique `customer_id`; the 62 missing customers come back only through the `LEFT JOIN` from `customers`.
-- 5. Debugging: repair an LTV query that joins payments and order_items at raw
--    grain and therefore multiplies revenue.
--    Inputs: For sql-46 Exercise 5, sum `quantity * unit_price * (1 - discount)` from `order_items` joined to `orders` into `order_value` at one row per `order_id`, then sum those values by `customer_id`; compare against the raw form that also joins `payments` before summing lines.
--    Expected result/shape: For sql-46 Exercise 5, expected output: 438 rows, one per `customer_id` with at least one order, with columns `customer_id` and `line_ltv`, ordered by `line_ltv DESC`, then `customer_id`; the order grain lives in the `order_value` CTE (4,362 rows), not in the final result.
--    Verify: For sql-46 Exercise 5, confirm that `line_ltv` sums to 2355647.12 and that customer 181 shows 9502.22, a cent above its 9502.21 `total_amount` sum because each order total is rounded; then run the raw form with `LEFT JOIN payments` and confirm it reads 13,432 rows instead of 13,085 line rows and reports 9682.06 for customer 181, because 347 orders have two payments. With an inner join to `payments` instead, the 873 orders without a payment also drop out.
--    Hint ladder, rung 1: For sql-46 Exercise 5, run `order_value` alone and confirm 4,362 rows with unique `order_id`; count `payments` per `order_id` to see why joining them before summing lines repeats some lines.
-- 6. Edge case: retain customers with no orders, assign zero LTV, and explain
--    where COALESCE belongs so the LEFT JOIN remains outer.
--    Inputs: For sql-46 Exercise 6, `LEFT JOIN orders` to `customers`, group by `c.customer_id`, take `COALESCE(SUM(o.total_amount), 0)` as `ltv`, and label `activity_status` from `COUNT(o.order_id)`, keeping every order condition out of `WHERE`.
--    Expected result/shape: For sql-46 Exercise 6, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `ltv`, and `activity_status`, ordered by `customer_id`; 438 rows are `has-order` and 62 are `no-order` with `ltv` 0.
--    Verify: For sql-46 Exercise 6, confirm the 438 and 62 split and that `ltv` sums to 2355646.89; then add `WHERE o.order_date >= '2020-01-01'` and confirm the result drops to 438 rows, because the filter rejects the `NULL` order rows the `LEFT JOIN` kept; finally move a recent-order condition such as `o.order_date >= CURRENT_DATE - 90` into the `ON` clause and confirm all 500 customers remain.
--    Hint ladder, rung 1: For sql-46 Exercise 6, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
ROLLBACK;
