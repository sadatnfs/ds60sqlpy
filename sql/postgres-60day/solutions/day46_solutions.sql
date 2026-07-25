-- Day 46 solutions: e-commerce analytics, Part 1
SET search_path TO training, public;

-- Exercise 1: threshold-based LTV segments analyzed by country.
-- Thresholds are policy choices; this answer makes them explicit.
WITH lifetime AS (
  SELECT c.customer_id,
         c.country,
         COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id, c.country
), segmented AS (
  SELECT *,
         CASE
           WHEN ltv >= 20000 THEN 'gold'
           WHEN ltv >= 10000 THEN 'silver'
           ELSE 'bronze'
         END AS ltv_segment
  FROM lifetime
)
SELECT country,
       ltv_segment,
       COUNT(*) AS customers,
       ROUND(AVG(ltv), 2) AS avg_ltv,
       ROUND(SUM(ltv), 2) AS total_ltv
FROM segmented
GROUP BY country, ltv_segment
ORDER BY country, avg_ltv DESC;

-- Exercise 2: cohort revenue for month offsets 0 through 12.
WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), monthly_customer AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), cohort_revenue AS (
  SELECT c.cohort_month,
         mc.order_month,
         (
           EXTRACT(year FROM age(mc.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(mc.order_month, c.cohort_month))
         )::int AS month_offset,
         SUM(mc.revenue) AS revenue
  FROM cohorts c
  JOIN monthly_customer mc USING (customer_id)
  GROUP BY c.cohort_month, mc.order_month
)
SELECT cohort_month,
       month_offset,
       ROUND(revenue, 2) AS revenue
FROM cohort_revenue
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
