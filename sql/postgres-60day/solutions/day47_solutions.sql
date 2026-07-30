-- Day 47 solutions: cohort retention
SET search_path TO training, public;

-- Exercise 1: calculate active-customer rate with cohort size retained.
-- Exercise 2: restrict the final tidy output to the latest six cohorts.
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

-- Exercise 3: expose both anchors. Signup cohorts answer onboarding retention;
-- first-order cohorts answer repeat-purchase retention.
SELECT c.customer_id,
       date_trunc('month', c.created_at)::date AS signup_cohort,
       date_trunc('month', MIN(o.order_date))::date AS first_order_cohort
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id, date_trunc('month', c.created_at)
ORDER BY c.customer_id;

-- Exercise 4: CROSS JOIN builds every requested offset; the LEFT JOIN turns
-- absent activity into an explicit zero count.
WITH cohorts AS (
  SELECT customer_id, date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts GROUP BY cohort_month
), offsets AS (
  SELECT generate_series(0, 12) AS month_offset
), activity AS (
  SELECT c.cohort_month,
         (
           EXTRACT(year FROM age(date_trunc('month', o.order_date), c.cohort_month)) * 12
           + EXTRACT(month FROM age(date_trunc('month', o.order_date), c.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT o.customer_id) AS active_customers
  FROM cohorts c
  JOIN orders o USING (customer_id)
  WHERE o.order_date::date >= c.cohort_month
  GROUP BY c.cohort_month, month_offset
)
SELECT s.cohort_month, x.month_offset, s.cohort_size,
       COALESCE(a.active_customers, 0) AS active_customers
FROM sizes s
CROSS JOIN offsets x
LEFT JOIN activity a
  ON a.cohort_month = s.cohort_month AND a.month_offset = x.month_offset
ORDER BY s.cohort_month DESC, x.month_offset;

-- Exercise 5: surface bad chronology instead of letting a negative offset enter
-- the retention curve.
SELECT c.customer_id, c.created_at, MIN(o.order_date) AS first_order_at
FROM customers c
JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.created_at
HAVING MIN(o.order_date) < c.created_at
ORDER BY c.customer_id;

-- Exercise 6: the observation flag keeps future offsets NULL rather than zero.
WITH latest AS (
  SELECT date_trunc('month', MAX(order_date))::date AS latest_observed_month
  FROM orders
), sample(cohort_month, month_offset) AS (
  VALUES (date_trunc('month', CURRENT_DATE)::date, 0),
         (date_trunc('month', CURRENT_DATE)::date, 6)
)
SELECT s.*,
       (s.cohort_month + make_interval(months => s.month_offset))
         <= l.latest_observed_month AS is_observable
FROM sample s CROSS JOIN latest l;
