-- Day 40 solutions: advanced analytics
SET search_path TO training, public;

-- Exercise 1: trailing 15-observation z-score for daily revenue.
WITH daily AS (
  SELECT order_date::date AS day,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), stats AS (
  SELECT day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS avg15,
         STDDEV_SAMP(revenue) OVER (
           ORDER BY day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS sd15
  FROM daily
)
SELECT day,
       ROUND(revenue, 2) AS revenue,
       ROUND(avg15, 2) AS avg15,
       ROUND(sd15, 2) AS sd15,
       ROUND(((revenue - avg15) / NULLIF(sd15, 0))::numeric, 3) AS z_score
FROM stats
ORDER BY day DESC;

-- Exercise 2: category-level distribution of order value attributable to it.
WITH category_orders AS (
  SELECT p.category,
         oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS category_order_total
  FROM order_items oi
  JOIN products p USING (product_id)
  GROUP BY p.category, oi.order_id
)
SELECT category,
       ROUND(
         percentile_cont(0.50) WITHIN GROUP (ORDER BY category_order_total)::numeric,
         2
       ) AS p50_order_total,
       ROUND(
         percentile_cont(0.90) WITHIN GROUP (ORDER BY category_order_total)::numeric,
         2
       ) AS p90_order_total
FROM category_orders
GROUP BY category
ORDER BY category;

-- Exercise 3: discrete chooses an observed input; continuous interpolates.
WITH values(value) AS (VALUES (10::numeric), (20), (100), (200))
SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY value) AS discrete_median,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY value) AS continuous_median
FROM values;

-- Exercise 4: first aggregate at month/category grain; the window denominator
-- then sums only peer category rows within that month.
WITH category_month AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         p.category,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY date_trunc('month', o.order_date), p.category
)
SELECT month,
       category,
       ROUND(revenue, 2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY month), 0), 4)
         AS month_share,
       ROW_NUMBER() OVER (
         PARTITION BY month ORDER BY revenue DESC, category
       ) AS category_rank
FROM category_month
ORDER BY month DESC, category_rank;

-- Exercise 5: CURRENT ROW would leak the target actual into its forecast.
WITH daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders GROUP BY order_date::date
)
SELECT day,
       revenue,
       AVG(revenue) OVER (
         ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
       ) AS prior_seven_forecast
FROM daily
ORDER BY day DESC
LIMIT 20;

-- Exercise 6: NULLIF preserves “undefined” when all values are identical.
WITH constant(value) AS (VALUES (5::numeric), (5), (5)), moments AS (
  SELECT value, AVG(value) OVER () AS mean_value,
         STDDEV_SAMP(value) OVER () AS sd_value
  FROM constant
)
SELECT value, (value - mean_value) / NULLIF(sd_value, 0) AS z_score
FROM moments;
