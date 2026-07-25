-- Day 47 solutions: cohort retention
SET search_path TO training, public;

WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), active_months AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), retained AS (
  SELECT c.cohort_month,
         a.order_month,
         (
           EXTRACT(year FROM age(a.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(a.order_month, c.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT a.customer_id) AS active_customers
  FROM cohorts c
  JOIN active_months a USING (customer_id)
  GROUP BY c.cohort_month, a.order_month
), curves AS (
  SELECT r.cohort_month,
         r.month_offset,
         s.cohort_size,
         r.active_customers,
         r.active_customers::numeric / NULLIF(s.cohort_size, 0) AS retention_rate
  FROM retained r
  JOIN cohort_sizes s USING (cohort_month)
  WHERE r.month_offset BETWEEN 0 AND 12
), latest_six AS (
  SELECT cohort_month
  FROM cohort_sizes
  ORDER BY cohort_month DESC
  LIMIT 6
)
-- Exercises 1 and 2: this tidy result is ready to chart with cohort_month as
-- series, month_offset on X, and retention_rate on Y.
SELECT cohort_month,
       month_offset,
       cohort_size,
       active_customers,
       ROUND(retention_rate, 4) AS retention_rate
FROM curves
WHERE cohort_month IN (SELECT cohort_month FROM latest_six)
ORDER BY cohort_month DESC, month_offset;
