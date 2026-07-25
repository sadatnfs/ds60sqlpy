-- Day 19 solutions: running aggregates
SET search_path TO training, public;

-- Exercise 1: an exact 30-calendar-day moving revenue sum and average.
WITH bounds AS (
  SELECT MIN(order_date)::date AS min_date,
         MAX(order_date)::date AS max_date
  FROM orders
), calendar AS (
  SELECT d::date AS day
  FROM bounds
  CROSS JOIN LATERAL generate_series(min_date, max_date, interval '1 day') AS d
), daily AS (
  SELECT order_date::date AS day,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), complete_daily AS (
  SELECT c.day, COALESCE(d.revenue, 0) AS revenue
  FROM calendar c
  LEFT JOIN daily d USING (day)
)
SELECT day,
       revenue,
       ROUND(SUM(revenue) OVER (
         ORDER BY day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
       ), 2) AS revenue_sum_30d,
       ROUND(AVG(revenue) OVER (
         ORDER BY day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
       ), 2) AS revenue_avg_30d
FROM complete_daily
ORDER BY day DESC;

-- Exercise 2: cumulative units for every product within its category.
WITH daily_product AS (
  SELECT p.category,
         p.product_id,
         o.order_date::date AS order_day,
         SUM(oi.quantity) AS units
  FROM products p
  JOIN order_items oi ON oi.product_id = p.product_id
  JOIN orders o ON o.order_id = oi.order_id
  GROUP BY p.category, p.product_id, o.order_date::date
)
SELECT category,
       product_id,
       order_day,
       units,
       SUM(units) OVER (
         PARTITION BY category, product_id
         ORDER BY order_day
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_units
FROM daily_product
ORDER BY category, product_id, order_day;
