-- Day 46 solutions: e-commerce analytics, Part 1
-- SOLUTION READING MAP — sql-46: Project1 Ecommerce Part1
-- Explanation: sql/postgres-60day/solutions/day46_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day46_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
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

-- Exercise 3: NTILE is population-relative; fixed thresholds encode a stable
-- policy. Show both so consumers can choose rather than conflate them.
WITH lifetime AS (
  SELECT c.customer_id, COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id
)
SELECT customer_id,
       ROUND(ltv, 2) AS ltv,
       NTILE(4) OVER (ORDER BY ltv DESC, customer_id) AS population_quartile,
       CASE WHEN ltv >= 5000 THEN 'gold'
            WHEN ltv >= 2000 THEN 'silver'
            ELSE 'bronze' END AS fixed_segment
FROM lifetime
ORDER BY ltv DESC, customer_id;

-- Exercise 4: orders aggregate to one customer row before joining customers.
-- This preserves the requested customer grain and all no-order customers.
WITH behavior AS (
  SELECT customer_id,
         COUNT(*) AS order_count,
         SUM(total_amount) AS ltv,
         AVG(total_amount) AS average_order_value,
         MAX(order_date) AS last_order_at
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id,
       COALESCE(b.order_count, 0) AS order_count,
       COALESCE(b.ltv, 0) AS ltv,
       b.average_order_value,
       CURRENT_DATE - b.last_order_at::date AS days_since_last_order
FROM customers c
LEFT JOIN behavior b USING (customer_id)
ORDER BY ltv DESC, c.customer_id;

-- Exercise 5: line revenue is first reduced to order grain. Joining raw
-- payments too would multiply line rows, so payment behavior belongs in a
-- separate order-grain CTE if the metric needs it.
WITH order_value AS (
  SELECT o.order_id, o.customer_id,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS value
  FROM orders o JOIN order_items oi USING (order_id)
  GROUP BY o.order_id, o.customer_id
)
SELECT customer_id, ROUND(SUM(value), 2) AS line_ltv
FROM order_value
GROUP BY customer_id
ORDER BY line_ltv DESC, customer_id;

-- Exercise 6: COALESCE is applied after the LEFT JOIN. Applying an order filter
-- in WHERE would discard no-order customers and accidentally make it inner.
SELECT c.customer_id,
       COALESCE(SUM(o.total_amount), 0) AS ltv,
       CASE WHEN COUNT(o.order_id) = 0 THEN 'no-order'
            ELSE 'has-order' END AS activity_status
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id
ORDER BY c.customer_id;
