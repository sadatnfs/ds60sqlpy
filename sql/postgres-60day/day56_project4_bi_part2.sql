-- Day 56: Project 4 - Complex BI (Part 2)
-- Ranking and percentile reporting, multi-dimensional splits
BEGIN;
SET search_path TO training, public;

-- Percentile distribution of order values per country-month
WITH orders_m AS (
  SELECT c.country,
         date_trunc('month', o.order_date)::date AS month,
         o.total_amount AS amt
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
)
SELECT country,
       month,
       PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM orders_m
GROUP BY country, month
ORDER BY month DESC, country
LIMIT 200;

-- Top-N per dimension (category) within country using window rank
WITH prod_rev AS (
  SELECT c.country,
         p.category,
         p.product_id,
         p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk_country,
            RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk_in_cat
  FROM prod_rev
)
SELECT * FROM ranked
WHERE rnk_in_cat <= 5
ORDER BY country, category, rnk_in_cat;

-- CUBE for multi-dimensional subtotals across country, category
WITH line AS (
  SELECT c.country, p.category,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category, ROUND(SUM(revenue),2) AS revenue,
       GROUPING(country) AS g_country, GROUPING(category) AS g_cat
FROM line
GROUP BY CUBE (country, category)
ORDER BY country NULLS FIRST, category NULLS FIRST;

-- Exercises
-- 1. Add payment method to the CUBE and measure row count increase.
-- 2. Compute p50/p90 of order values per category-month.
-- 3. Prediction: explain why joining raw payments to raw order_items multiplies
--    revenue when an order has several rows in both tables.
-- 4. Construction: pre-aggregate payment methods at order grain before joining
--    line revenue, and reconcile the result to total line revenue.
-- 5. Debugging: correct a percentile query that calculates percentiles over
--    line items when the metric definition says order value.
-- 6. Edge case: compare percentile_cont and percentile_disc for a category-month
--    with an even number of orders and explain which output is an observed value.

ROLLBACK;
