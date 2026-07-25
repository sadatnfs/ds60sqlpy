-- Day 30: Phase 2 Project - Multi-stage Analysis
BEGIN;
SET search_path TO training, public;

-- Example: Customer lifetime value with cohort analysis
WITH orders_enriched AS (
  SELECT o.order_id,
         o.customer_id,
         o.order_date::date AS order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), metrics AS (
  SELECT e.customer_id,
         c.cohort_month,
         date_trunc('month', e.order_date)::date AS order_month,
         SUM(e.order_value) AS revenue
  FROM orders_enriched e
  JOIN cohorts c ON c.customer_id = e.customer_id
  GROUP BY e.customer_id, c.cohort_month, date_trunc('month', e.order_date)
), cohort_agg AS (
  SELECT cohort_month,
         order_month,
         (
           EXTRACT(YEAR FROM age(order_month, cohort_month)) * 12
           + EXTRACT(MONTH FROM age(order_month, cohort_month))
         )::int AS month_offset,
         SUM(revenue) AS cohort_revenue,
         COUNT(DISTINCT customer_id) AS active_customers
  FROM metrics
  GROUP BY cohort_month, order_month
)
SELECT cohort_month,
       month_offset,
       ROUND(cohort_revenue,2) AS revenue,
       active_customers,
       ROUND(cohort_revenue/NULLIF(active_customers,0),2) AS rev_per_active
FROM cohort_agg
ORDER BY cohort_month DESC, month_offset
LIMIT 200;

-- Deliverable: Extend with retention rate per cohort and CLV projections using moving averages.

ROLLBACK;
