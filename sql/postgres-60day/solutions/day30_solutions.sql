-- Day 30 solution: cohort retention and a moving-average CLV projection
SET search_path TO training, public;

WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), cohort_months AS (
  SELECT c.cohort_month,
         ov.order_month,
         (
           EXTRACT(year FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(ov.order_month, c.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT ov.customer_id) AS active_customers,
         SUM(ov.order_value) AS revenue
  FROM cohorts c
  JOIN order_values ov ON ov.customer_id = c.customer_id
  GROUP BY c.cohort_month, ov.order_month
), metrics AS (
  SELECT cm.*,
         cs.cohort_size,
         cm.active_customers::numeric / NULLIF(cs.cohort_size, 0) AS retention_rate,
         cm.revenue / NULLIF(cm.active_customers, 0) AS revenue_per_active
  FROM cohort_months cm
  JOIN cohort_sizes cs USING (cohort_month)
), projected AS (
  SELECT *,
         AVG(revenue_per_active) OVER (
           PARTITION BY cohort_month
           ORDER BY month_offset
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
         ) AS moving_avg_revenue_per_active
  FROM metrics
)
SELECT cohort_month,
       order_month,
       month_offset,
       cohort_size,
       active_customers,
       ROUND(retention_rate, 4) AS retention_rate,
       ROUND(revenue, 2) AS revenue,
       ROUND(revenue_per_active, 2) AS revenue_per_active,
       ROUND(moving_avg_revenue_per_active * 12, 2) AS projected_12m_clv
FROM projected
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
