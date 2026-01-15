-- Day 47: Project 1 - E-commerce Analytics (Part 2)
-- Topics: Cohort retention analysis
BEGIN;
SET search_path TO training, public;

WITH orders_m AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), retention AS (
  SELECT co.cohort_month,
         om.order_month,
         EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT cohort_month, month_offset, active_customers
FROM retention
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;

-- Exercises
-- 1) Convert active_customers to retention_rate by dividing by cohort size.
-- 2) Chart retention curves for last 6 cohorts (outside SQL).

ROLLBACK;
