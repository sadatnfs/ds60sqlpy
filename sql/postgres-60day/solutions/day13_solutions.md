# Day 13 — Solutions (Date/Time Functions, Cohorts, Calendars)

We build weekly signup cohorts with retention, then create a complete daily calendar joined to daily revenue. Step‑by‑step notes explain the time arithmetic and windowing.

Setup
- Schema: training; tables: customers(created_at), orders(order_date)
- Time math: DATE_TRUNC for bucketing; generate_series for dense calendars

Exercise 1 — Weekly cohorts with 0–4 week retention
```sql
WITH cohorts AS (
  SELECT c.customer_id,
         DATE_TRUNC('week', c.created_at)::date AS cohort_week
  FROM customers c
), order_weeks AS (
  SELECT o.customer_id,
         DATE_TRUNC('week', o.order_date)::date AS order_week
  FROM orders o
), offsets AS (
  SELECT co.cohort_week,
         ow.customer_id,
         (EXTRACT(EPOCH FROM (ow.order_week - co.cohort_week)) / 604800)::int AS week_offset
  FROM cohorts co
  JOIN order_weeks ow ON ow.customer_id = co.customer_id
  WHERE ow.order_week >= co.cohort_week
), coh_sizes AS (
  SELECT cohort_week, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_week
)
SELECT o.cohort_week,
       o.week_offset,
       COUNT(DISTINCT o.customer_id) AS active_customers,
       ROUND(COUNT(DISTINCT o.customer_id)::numeric / NULLIF(cs.cohort_size,0), 4) AS retention_rate
FROM offsets o
JOIN coh_sizes cs USING (cohort_week)
WHERE o.week_offset IN (0,1,2,3,4)
GROUP BY o.cohort_week, o.week_offset, cs.cohort_size
ORDER BY o.cohort_week, o.week_offset;
```
Line‑by‑line
- DATE_TRUNC('week', ts)::date: buckets to Monday‑based weeks (default in Postgres) and casts to date for readability.
- week_offset: Difference in weeks between an order week and the cohort week. We convert the interval to seconds via EXTRACT(EPOCH ...) and divide by 604800.
- coh_sizes: cohort denominators used for retention rate.
- Final SELECT: Distinct active users per (cohort, offset) divided by cohort size yields retention; limited to weeks 0–4.
Pitfalls
- If created_at is timezone‑aware and order_date is not, normalize first (AT TIME ZONE) to avoid off‑by‑one week in edge cases.

Exercise 2 — Dense daily calendar with left‑joined revenue
```sql
WITH bounds AS (
  SELECT MIN(order_date)::date AS start_d, MAX(order_date)::date AS end_d FROM orders
), cal AS (
  SELECT gs::date AS d
  FROM bounds b
  CROSS JOIN generate_series(b.start_d, b.end_d, interval '1 day') gs
), daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT c.d,
       COALESCE(d.revenue, 0) AS revenue
FROM cal c
LEFT JOIN daily d ON d.d = c.d
ORDER BY c.d
LIMIT 500;
```
Explanation
- bounds: Captures the inclusive min/max day so generate_series produces a correct range.
- cal: One row per day. Casting gs to date trims time components.
- daily: Aggregate order totals per day.
- LEFT JOIN: Ensures days with zero revenue are present with 0 after COALESCE.
Tips
- For weekly/monthly calendars, change the generate_series step to interval '1 week' / use DATE_TRUNC('month', ...), etc.
