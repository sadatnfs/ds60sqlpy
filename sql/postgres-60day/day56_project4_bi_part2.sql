-- Day 56: Project 4 - Complex BI (Part 2)
-- BEGINNER WORKFLOW - sql-56: Project 4 BI Part 2
-- Guide: sql/postgres-60day/companion-guides/day56_project4_bi_part2.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-56.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    c.country,
    date_trunc('month', o.order_date)::date AS month,
    o.total_amount AS amt
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
)
SELECT
  country,
  month,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM
  orders_m
GROUP BY
  country,
  month
ORDER BY
  month DESC,
  country
LIMIT 200;

-- Top-N per dimension (category) within country using window rank
WITH prod_rev AS (
  SELECT
    c.country,
    p.category,
    p.product_id,
    p.name,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    c.country,
    p.category,
    p.product_id,
    p.name
),
ranked AS (
  SELECT
    *,
    RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk_country,
    RANK() OVER (PARTITION BY country,
      category ORDER BY revenue DESC) AS rnk_in_cat
  FROM
    prod_rev
)
SELECT
  *
FROM
  ranked
WHERE
  rnk_in_cat <= 5
ORDER BY
  country,
  category,
  rnk_in_cat;

-- CUBE for multi-dimensional subtotals across country, category
WITH line AS (
  SELECT
    c.country,
    p.category,
    (oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
)
SELECT
  country,
  category,
  ROUND(SUM(revenue), 2) AS revenue,
  GROUPING (country) AS g_country,
  GROUPING (category) AS g_cat
FROM
  line
GROUP BY
  CUBE (country,
    category)
ORDER BY
  country NULLS FIRST,
  category NULLS FIRST;

-- Exercises
-- 1. Add payment method to the CUBE and measure row count increase.
--    Inputs: For sql-56 Exercise 1, build `line` with one row per order item (13,085 rows) carrying `country`, `category`, and `payment_method`, where `payment_method` is the method with the largest paid amount for the order (ties broken by method name, `unpaid` when the order has no payment), then count the rows of `CUBE (country, category)` and of `CUBE (country, category, payment_method)`.
--    Expected result/shape: For sql-56 Exercise 1, expected output: one row with `two_dimension_rows` 56 and `three_dimension_rows` 336. The 7 ordering countries plus a subtotal times the 6 categories plus a subtotal gives 56, and the 5 payment values (`bank`, `card`, `credit`, `paypal`, `unpaid`) plus a subtotal multiply that by 6. The final columns are `two_dimension_rows` and `three_dimension_rows`.
--    Verify: For sql-56 Exercise 1, confirm that `line` has 13085 rows and 210 distinct `(country, category, payment_method)` tuples (7 x 6 x 5, so every combination occurs and the cube is complete), and that `primary_payment` has one row per paid order (3489). In a rolled-back transaction, run `UPDATE payments SET method = 'bank' WHERE method = 'card'`: `two_dimension_rows` stays 56 while `three_dimension_rows` falls to 280 (56 x 5).
--    Hint ladder, rung 1: For sql-56 Exercise 1, run `payment_by_method`, `ranked_payment`, and `primary_payment` alone and confirm `primary_payment` has 3489 rows, one per paid order, before `line` left-joins it to the 13085 order lines.
-- 2. Compute p50/p90 of order values per category-month.
--    Inputs: For sql-56 Exercise 2, sum line revenue per `(month, category, order_id)` in `category_orders`, so an order contributes one value to each category it bought from, then take `percentile_cont` at 0.50 and 0.90 of those values per `(month, category)`, rounded to 2 decimals.
--    Expected result/shape: For sql-56 Exercise 2, expected output: 276 rows, one per `(month, category)` for 46 months (2023-02 to 2026-11) and 6 categories, starting with 2026-11 Apparel at `p50_order_value` 122.86 and `p90_order_value` 361.16. The final columns are `month`, `category`, `p50_order_value`, and `p90_order_value`. The final order is `month DESC, category`.
--    Verify: For sql-56 Exercise 2, confirm 276 rows with no repeated `(month, category)` and that all six February 2023 rows show the same value for both percentiles, because each holds a single order. In a rolled-back transaction, add a January 2023 order with one 10.00 Books line: the result grows to 277 rows and the new 2023-01 Books row shows 10.00 for both percentiles.
--    Hint ladder, rung 1: For sql-56 Exercise 2, run `category_orders` alone and confirm 13085 rows, one per `(month, category, order_id)`, before you take percentiles; no order here has two lines in the same category.
-- 3. Prediction: explain why joining raw payments to raw order_items multiplies
--    revenue when an order has several rows in both tables.
--    Inputs: For sql-56 Exercise 3, join `orders` to `order_items` and to `payments` on `order_id` without pre-aggregation and count the joined rows, the distinct `order_item_id` values, and the distinct `payment_id` values.
--    Expected result/shape: For sql-56 Exercise 3, expected output: one row with `raw_join_rows` 10816, `distinct_items` 10469, and `distinct_payments` 3836; an order with two payments repeats each of its items, so the joined rows exceed the distinct items. The final columns are `raw_join_rows`, `distinct_items`, and `distinct_payments`.
--    Verify: For sql-56 Exercise 3, confirm that `raw_join_rows` equals `SELECT SUM(i.n * p.n) FROM (SELECT order_id, COUNT(*) n FROM order_items GROUP BY order_id) i JOIN (SELECT order_id, COUNT(*) n FROM payments GROUP BY order_id) p USING (order_id)` (10816); summing item revenue over this join would count every line once per payment of its order.
--    Hint ladder, rung 1: For sql-56 Exercise 3, count `order_items` and `payments` per `order_id` first; the join produces their product for each order.
-- 4. Construction: pre-aggregate payment methods at order grain before joining
--    line revenue, and reconcile the result to total line revenue.
--    Inputs: For sql-56 Exercise 4, reduce `payments` to one `reporting_method` per order with `MIN(method)`, an alphabetical rule that differs from the largest-amount rule of Exercise 1, reduce `order_items` to one revenue total per order, left-join them at order grain with `unpaid` for orders without payments, and sum revenue per reporting method.
--    Expected result/shape: For sql-56 Exercise 4, expected output: 5 rows, one per `reporting_method` (`bank`, `card`, `credit`, `paypal`, and `unpaid`), whose `revenue` values add up to `reconciled_total` (2355647.1235), the exact line revenue repeated on every row. The final columns are `reporting_method`, `revenue`, and `reconciled_total`. The final order is `reporting_method`.
--    Verify: For sql-56 Exercise 4, confirm that the five `revenue` values add up to `SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items` (2355647.1235) and that `method` has one row per paid order (3489), so no order's revenue is counted twice.
--    Hint ladder, rung 1: For sql-56 Exercise 4, run `method` and `lines` alone and confirm one row per `order_id` in each before you join them.
-- 5. Debugging: correct a percentile query that calculates percentiles over
--    line items when the metric definition says order value.
--    Inputs: For sql-56 Exercise 5, sum line revenue per `(category, order_id)` in `category_order` first, then take `percentile_cont(0.5)` of those order values per category with `COUNT(*)` as `observations`; the faulty version takes the percentile over raw `order_items` rows instead.
--    Expected result/shape: For sql-56 Exercise 5, expected output: 6 rows whose `observations` add up to 13085 (Apparel 2192, Beauty 2189, Books 2145, Electronics 2187, Home 2186, Sports 2186), with `p50` between 146.54 (Home) and 150.24 (Electronics). The final columns are `category`, `observations`, and `p50`. The final order is `category`.
--    Verify: For sql-56 Exercise 5, confirm that the line-grain query over `order_items` joined to `products` returns the same counts and medians here, because no order has two lines in one category. In a rolled-back transaction, add a second Apparel line (product 1, quantity 1, `unit_price` 10.00) to order 1: the line-grain count for Apparel rises to 2193, while `observations` stays 2192 because order 1 still contributes one Apparel value, now 166.92.
--    Hint ladder, rung 1: For sql-56 Exercise 5, run `category_order` alone and confirm 13085 rows, one per `(category, order_id)`, before you take the percentile.
-- 6. Edge case: compare percentile_cont and percentile_disc for a category-month
--    with an even number of orders and explain which output is an observed value.
--    Inputs: For sql-56 Exercise 6, reuse `category_order` (one value per category and order) and compute `percentile_cont(0.5)` and `percentile_disc(0.5)` side by side per category with `COUNT(*)` as `observations`; Apparel (2192), Home (2186), and Sports (2186) are the even-sized groups.
--    Expected result/shape: For sql-56 Exercise 6, expected output: 6 rows in which `continuous_p50` equals `discrete_p50` in every category (Apparel 149.5, Beauty 147.66, Books 149.88, Electronics 150.24, Home 146.54, Sports 148.05), because the two middle values of each even group are tied. The final columns are `category`, `observations`, `continuous_p50`, and `discrete_p50`. The final order is `category`.
--    Verify: For sql-56 Exercise 6, add `date_trunc('month', o.order_date)` to `category_order` and to the grouping, then compare the two columns: on the checked load 122 of the 133 even-sized category-months show different medians. For 2026-11 Electronics (82 orders) the two middle orders are 134.64 and 141.36, so `continuous_p50` returns their midpoint 138 while `discrete_p50` returns the observed 134.64.
--    Hint ladder, rung 1: For sql-56 Exercise 6, run `category_order` alone and count orders per category to see which groups are even (Apparel, Home, and Sports) before you compare the two percentile functions.
ROLLBACK;
