# Day 30 — Solution: Cohort Retention and CLV Projection

The current Day 30 deliverable extends the starter cohort query with:

1. cohort size;
2. active customers and retention by cohort age;
3. revenue per active customer; and
4. an illustrative projection based on a moving average.

The answer below is also the maintained executable solution.

```sql
SET search_path TO training, public;

WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month,
         SUM(
           oi.unit_price * oi.quantity * (1 - oi.discount)
         ) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id,
           o.customer_id,
           date_trunc('month', o.order_date)
), cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), cohort_sizes AS (
  SELECT cohort_month,
         COUNT(*) AS cohort_size
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
         cm.active_customers::numeric
           / NULLIF(cs.cohort_size, 0) AS retention_rate,
         cm.revenue
           / NULLIF(cm.active_customers, 0) AS revenue_per_active
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
       ROUND(
         moving_avg_revenue_per_active * 12,
         2
       ) AS projected_12m_clv
FROM projected
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
```

## Expected shape and interpretation

There is one row per observed cohort month and order month, limited to cohort
ages 0–12. `retention_rate` is active customers divided by the original cohort
size. `projected_12m_clv` annualizes the trailing three observed
revenue-per-active values.

## Explicit assumptions and limitations

- Cohort membership is based on `customers.created_at`, not first order date.
  Customers who never order remain in the cohort-size denominator.
- An “active” customer has at least one order in that order month.
- The query reports only observed activity months. It does not create zero rows
  for missing cohort ages, so the three-row moving frame may span gaps.
- The projection is a teaching heuristic, not a production CLV model. It does
  not model churn, margin, discount rate, future acquisition, or uncertainty.
- The year-plus-month `age` calculation is deliberate. Extracting only the
  month component would wrap after 12 months and mislabel older cohorts.

## Reconciliation checks

For a trustworthy extension, verify that `active_customers <= cohort_size`,
retention lies between 0 and 1, and summed `order_values` equals net line-item
revenue for the same scope. Do not sum revenue across overlapping cohort report
windows and call it a separate total.
