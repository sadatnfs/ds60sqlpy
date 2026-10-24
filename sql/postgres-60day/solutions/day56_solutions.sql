-- Day 56 solutions: CUBE, payment method, and percentiles
-- SOLUTION READING MAP — sql-56: Project4 BI Part2
-- Explanation: sql/postgres-60day/solutions/day56_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day56_solutions.sql
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

WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS paid_amount
  FROM payments
  GROUP BY order_id, method
), ranked_payment AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY order_id ORDER BY paid_amount DESC, method
         ) AS payment_rank
  FROM payment_by_method
), primary_payment AS (
  SELECT order_id, method
  FROM ranked_payment
  WHERE payment_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(fp.method, 'unpaid') AS payment_method,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  LEFT JOIN primary_payment fp USING (order_id)
), cube_two AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
), cube_three AS (
  SELECT country, category, payment_method, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category, payment_method)
)
-- Exercise 1: quantify the row-count increase.
SELECT (SELECT COUNT(*) FROM cube_two) AS two_dimension_rows,
       (SELECT COUNT(*) FROM cube_three) AS three_dimension_rows;

-- Exercise 2: p50 and p90 category-attributable order values per month.
WITH category_orders AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         p.category,
         o.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY date_trunc('month', o.order_date), p.category, o.order_id
)
SELECT month,
       category,
       ROUND(
         percentile_cont(0.50) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p50_order_value,
       ROUND(
         percentile_cont(0.90) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p90_order_value
FROM category_orders
GROUP BY month, category
ORDER BY month DESC, category;

-- Exercise 3: compare raw join rows with source rows. Multi-payment and
-- multi-item orders make the raw cross product larger than either source.
SELECT COUNT(*) AS raw_join_rows,
       COUNT(DISTINCT oi.order_item_id) AS distinct_items,
       COUNT(DISTINCT p.payment_id) AS distinct_payments
FROM orders o
JOIN order_items oi USING (order_id)
JOIN payments p USING (order_id);

-- Exercise 4: choose one payment-method policy at order grain, then join line
-- revenue. The reconciliation proves the dimension did not multiply revenue.
WITH method AS (
  SELECT order_id, MIN(method) AS reporting_method
  FROM payments GROUP BY order_id
), lines AS (
  SELECT oi.order_id,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
  FROM order_items oi GROUP BY oi.order_id
), attributed AS (
  SELECT COALESCE(m.reporting_method, 'unpaid') AS reporting_method,
         SUM(l.revenue) AS revenue
  FROM lines l LEFT JOIN method m USING (order_id)
  GROUP BY COALESCE(m.reporting_method, 'unpaid')
)
SELECT reporting_method, revenue,
       SUM(revenue) OVER () AS reconciled_total
FROM attributed
ORDER BY reporting_method;

-- Exercise 5: the CTE deliberately emits one row per category/order before the
-- percentile, matching the declared order-value population.
WITH category_order AS (
  SELECT p.category, o.order_id,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY p.category, o.order_id
)
SELECT category, COUNT(*) AS observations,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY order_value) AS p50
FROM category_order
GROUP BY category
ORDER BY category;

-- Exercise 6: continuous may interpolate; discrete always returns one observed
-- order value. Retain observation count to interpret even populations.
WITH category_order AS (
  SELECT p.category, o.order_id,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS order_value
  FROM orders o JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY p.category, o.order_id
)
SELECT category, COUNT(*) AS observations,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY order_value) AS continuous_p50,
       percentile_disc(0.5) WITHIN GROUP (ORDER BY order_value) AS discrete_p50
FROM category_order
GROUP BY category
ORDER BY category;
