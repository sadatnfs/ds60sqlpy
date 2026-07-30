-- Day 36 solutions: materialized views
BEGIN;
SET search_path TO training, public;

-- Exercise 1: weekly revenue by country.
CREATE MATERIALIZED VIEW mv_weekly_country_revenue_solution AS
SELECT date_trunc('week', o.order_date)::date AS week,
       c.country,
       SUM(o.total_amount) AS revenue,
       COUNT(*) AS orders
FROM orders o
JOIN customers c USING (customer_id)
GROUP BY date_trunc('week', o.order_date), c.country;

CREATE UNIQUE INDEX idx_mv_weekly_country_solution
  ON mv_weekly_country_revenue_solution(week, country);

-- Exercise 2: compare equivalent base-table and materialized-view plans.
EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('week', o.order_date)::date AS week,
       c.country,
       SUM(o.total_amount) AS revenue,
       COUNT(*) AS orders
FROM orders o
JOIN customers c USING (customer_id)
GROUP BY date_trunc('week', o.order_date), c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT week, country, revenue, orders
FROM mv_weekly_country_revenue_solution;

-- Exercise 3: change one disposable base row after materialization. The first
-- comparison exposes staleness; REFRESH then makes the view current.
UPDATE orders
SET total_amount = total_amount + 1
WHERE order_id = (SELECT MIN(order_id) FROM orders);

SELECT (SELECT SUM(total_amount) FROM orders) AS live_total,
       (SELECT SUM(revenue) FROM mv_weekly_country_revenue_solution) AS stale_mv_total;
REFRESH MATERIALIZED VIEW mv_weekly_country_revenue_solution;
SELECT (SELECT SUM(total_amount) FROM orders) AS live_total,
       (SELECT SUM(revenue) FROM mv_weekly_country_revenue_solution) AS refreshed_mv_total;

-- Exercise 4: the unique (week,country) index above is the structural
-- prerequisite for REFRESH ... CONCURRENTLY after initial population. Ordinary
-- REFRESH remains appropriate inside this single-session rollback lab.
SELECT indexdef
FROM pg_indexes
WHERE schemaname = 'training'
  AND tablename = 'mv_weekly_country_revenue_solution';

-- Exercise 5: this view stores order-header totals. Name that definition and
-- show the line-item alternative rather than assuming they are interchangeable.
SELECT (SELECT SUM(total_amount) FROM orders) AS header_revenue,
       (SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items)
         AS line_revenue;

-- Exercise 6: a spine supplies requested combinations; the outer join turns
-- missing aggregate rows into an explicit display zero by policy.
WITH months AS (
  SELECT DISTINCT date_trunc('week', order_date)::date AS week FROM orders
), countries AS (
  SELECT DISTINCT country FROM customers
)
SELECT m.week, c.country, COALESCE(v.revenue, 0) AS revenue
FROM months m
CROSS JOIN countries c
LEFT JOIN mv_weekly_country_revenue_solution v
  ON v.week = m.week AND v.country = c.country
ORDER BY m.week DESC, c.country
LIMIT 20;

ROLLBACK;
