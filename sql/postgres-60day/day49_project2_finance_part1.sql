-- Day 49: Project 2 - Financial/Operational Analysis (Part 1)
-- Revenue forecasting with time-series patterns
BEGIN;
SET search_path TO training, public;

-- Monthly revenue
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT * FROM monthly ORDER BY month DESC LIMIT 24;

-- YoY growth per month
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT m.month,
       m.revenue,
       LAG(m.revenue, 12) OVER (ORDER BY m.month) AS prev_year,
       ROUND((m.revenue - COALESCE(LAG(m.revenue,12) OVER (ORDER BY m.month),0))
             / NULLIF(LAG(m.revenue,12) OVER (ORDER BY m.month),0), 4) AS yoy_growth
FROM monthly m
ORDER BY m.month DESC
LIMIT 36;

-- Naive seasonal forecast: use last year's month as forecast
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), future AS (
  SELECT (date_trunc('month', CURRENT_DATE) + (n || ' month')::interval)::date AS month
  FROM generate_series(1, 3) AS g(n)
)
SELECT f.month,
       m_prev.revenue AS forecast_revenue
FROM future f
LEFT JOIN monthly m_prev ON m_prev.month = (f.month - interval '12 months')::date
ORDER BY f.month;

-- MA(3) forecast: average of last 3 months revenue
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), ma AS (
  SELECT month,
         revenue,
         ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS ma3
  FROM monthly
)
SELECT * FROM ma ORDER BY month DESC LIMIT 6;

-- Exercises
-- 1) Build MA(6) and MA(12) and compare MAPEs vs seasonal naive.
-- 2) Produce a combined forecast blending 50% seasonal-naive and 50% MA(6).

ROLLBACK;
