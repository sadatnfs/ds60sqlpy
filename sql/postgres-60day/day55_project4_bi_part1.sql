-- Day 55: Project 4 - Complex BI (Part 1)
-- Multi-dimensional analysis (drill-down capability)
BEGIN;
SET search_path TO training, public;

-- Use GROUPING SETS/ROLLUP/CUBE for flexible drilldowns.
-- Dimensions: country, category, primary payment method, month.
-- An order can have split payments, so first choose one reporting label:
-- the method with the greatest paid amount (method name breaks ties).
WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS method_amount
  FROM payments
  GROUP BY order_id, method
), primary_payment_method AS (
  SELECT order_id, method
  FROM (
    SELECT order_id,
           method,
           ROW_NUMBER() OVER (
             PARTITION BY order_id
             ORDER BY method_amount DESC, method
           ) AS method_rank
    FROM payment_by_method
  ) ranked_methods
  WHERE method_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(pm.method, 'unpaid') AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue,
         oi.quantity AS qty
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN primary_payment_method pm ON pm.order_id = o.order_id
)
SELECT country,
       category,
       payment_method,
       month,
       ROUND(SUM(revenue),2) AS revenue,
       SUM(qty) AS units,
       GROUPING(country)        AS g_country,
       GROUPING(category)       AS g_category,
       GROUPING(payment_method) AS g_method,
       GROUPING(month)          AS g_month
FROM line
GROUP BY ROLLUP (country, category, payment_method, month)
ORDER BY country NULLS FIRST, category NULLS FIRST, payment_method NULLS FIRST, month NULLS FIRST;

-- Drill-down example: country -> category -> product (top-N per level)
WITH prod_rev AS (
  SELECT c.country, p.category, p.product_id, p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *,
         RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT * FROM ranked WHERE rnk <= 5
ORDER BY country, category, rnk;

-- Exercises
-- 1. Replace ROLLUP with CUBE to get all subtotal combinations and compare row counts.
-- 2. Add a dimension for order status and re-run the drill-down with top-5.
-- 3. Prediction: list the grouping sets produced by ROLLUP(country, category,
--    month) and contrast them with CUBE before running either query.
-- 4. Construction: use PostgreSQL's GROUPING(country, category) bit mask to
--    assign stable detail/subtotal/grand-total labels without mistaking stored
--    NULLs for subtotal markers.
-- 5. Debugging: replace RANK with ROW_NUMBER plus a deterministic tie-breaker
--    when the dashboard must show exactly five products per group.
-- 6. Edge case: preserve a real '(unknown)' country member separately from the
--    ALL-countries subtotal in both machine-readable and display columns.

ROLLBACK;
