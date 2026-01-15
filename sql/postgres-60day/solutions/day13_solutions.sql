-- Day 13 - Solutions: Date/Time Functions and Time Zones
-- Assumes: orders(order_date), customers(created_at)

/*
Exercise 1) Compute weekly cohorts and retention at 4-week horizons.
Why: Bucket customers by signup week; then count distinct active customers at week offsets.
*/
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

/*
Exercise 2) Fill a daily calendar with zeros and left join daily revenue.
Why: generate_series with date bounds; COALESCE revenue to 0 to make gaps explicit.
*/
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

-- End of Day 13 solutions
