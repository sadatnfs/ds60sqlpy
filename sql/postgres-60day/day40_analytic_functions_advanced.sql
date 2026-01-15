-- Day 40: Analytic Functions - Advanced (statistics and distributions)
BEGIN;
SET search_path TO training, public;

-- Statistical aggregates over windows
WITH daily AS (
  SELECT date_trunc('day', o.order_date) AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT d,
       revenue,
       ROUND(AVG(revenue)  OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS ma15,
       ROUND(STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS sd15,
       ROUND(VAR_POP(revenue)      OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS var15
FROM daily
ORDER BY d DESC
LIMIT 60;

-- Percentiles using PERCENTILE_CONT (continuous) within month
WITH monthly AS (
  SELECT date_trunc('month', o.order_date) AS m,
         o.total_amount AS amt
  FROM orders o
)
SELECT m,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM monthly
GROUP BY m
ORDER BY m DESC
LIMIT 12;

-- Ratio to total (ratio_to_report equivalent)
WITH cat AS (
  SELECT p.category, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT category,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (),0), 4) AS share_of_total
FROM cat
ORDER BY revenue DESC;

-- Exercises
-- 1) Compute z-score for daily revenue: (rev - avg15)/sd15.
-- 2) For each category, compute P50 and P90 of order totals.

ROLLBACK;
