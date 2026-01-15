# Day 47 — Solutions (Project 1: E‑commerce Analytics, Part 2)

Today’s goal is cohort retention. We’ll compute cohort sizes, active customers by month_offset, and retention rates, then extract the last 6 cohorts for charting.

Reference from lesson (annotated)
```sql
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
```
Explanation
- orders_m: reduce to 1 row per (customer_id, order_month). This counts activity per month without double‑counting multiple orders.
- cohorts: anchor each user to their signup month.
- retention: count distinct active customers per (cohort_month, order_month), and compute month_offset = months since cohort start.

Exercise 1 — Convert active_customers to retention_rate
Goal
- retention_rate = active_customers / cohort_size at each month_offset.

Solution
```sql
WITH orders_m AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), cohort_size AS (
  SELECT cohort_month, COUNT(*) AS customers_in_cohort
  FROM cohorts
  GROUP BY cohort_month
), retention AS (
  SELECT co.cohort_month,
         om.order_month,
         EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT r.cohort_month,
       r.month_offset,
       r.active_customers,
       cs.customers_in_cohort,
       ROUND(r.active_customers::numeric / NULLIF(cs.customers_in_cohort, 0), 4) AS retention_rate
FROM retention r
JOIN cohort_size cs USING (cohort_month)
WHERE r.month_offset BETWEEN 0 AND 12
ORDER BY r.cohort_month DESC, r.month_offset;
```
Line‑by‑line notes
- cohort_size: compute denominator once per cohort.
- retention_rate: cast numerator to numeric to avoid integer division; guard divide‑by‑zero with NULLIF.
- WHERE month_offset filter ensures lifecycle months 0..12 only.

Exercise 2 — Chart retention curves for last 6 cohorts (outside SQL)
Goal
- Produce a narrow table (cohort_month, month_offset, retention_rate) filtered to last 6 cohorts. Then export to CSV and chart in your tool of choice.

SQL to extract last 6 cohorts
```sql
WITH orders_m AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), cohort_size AS (
  SELECT cohort_month, COUNT(*) AS customers_in_cohort
  FROM cohorts
  GROUP BY cohort_month
), retention AS (
  SELECT co.cohort_month,
         om.order_month,
         EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
), last6 AS (
  SELECT DISTINCT cohort_month
  FROM cohorts
  ORDER BY cohort_month DESC
  LIMIT 6
)
SELECT r.cohort_month,
       r.month_offset,
       ROUND(r.active_customers::numeric / NULLIF(cs.customers_in_cohort, 0), 4) AS retention_rate
FROM retention r
JOIN cohort_size cs USING (cohort_month)
JOIN last6 l ON l.cohort_month = r.cohort_month
WHERE r.month_offset BETWEEN 0 AND 12
ORDER BY r.cohort_month, r.month_offset;
```
Charting instructions
- Export results to CSV.
- Plot lines: x = month_offset, y = retention_rate, color = cohort_month. Expect downward‑sloping curves; compare shapes.
