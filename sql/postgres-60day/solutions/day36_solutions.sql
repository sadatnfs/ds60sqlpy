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

ROLLBACK;
