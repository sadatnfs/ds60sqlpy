# Day 36 — Solutions: Materialized Views

A materialized view stores query results. Reads can become cheaper, but the
result is a snapshot and must be refreshed when source data changes.

## Exercise 1 — Weekly revenue by country

This demonstration is transactional and leaves no materialized view behind.

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP MATERIALIZED VIEW IF EXISTS mv_weekly_country_revenue_solution;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_solution AS
SELECT date_trunc('week', o.order_date)::date AS week_start,
       c.country,
       SUM(
         oi.unit_price * oi.quantity * (1 - oi.discount)
       ) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY date_trunc('week', o.order_date), c.country;

SELECT week_start,
       country,
       ROUND(revenue, 2) AS revenue
FROM mv_weekly_country_revenue_solution
ORDER BY week_start DESC, revenue DESC;

ROLLBACK;
```

Expected shape: one row per observed week-country pair. PostgreSQL weeks begin
on Monday under `date_trunc('week', ...)`.

## Exercise 2 — Compare base-table and snapshot plans

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP MATERIALIZED VIEW IF EXISTS mv_weekly_country_revenue_compare;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_compare AS
SELECT date_trunc('week', o.order_date)::date AS week_start,
       c.country,
       SUM(
         oi.unit_price * oi.quantity * (1 - oi.discount)
       ) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY date_trunc('week', o.order_date), c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('week', o.order_date)::date AS week_start,
       c.country,
       SUM(
         oi.unit_price * oi.quantity * (1 - oi.discount)
       ) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY date_trunc('week', o.order_date), c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT week_start,
       country,
       revenue
FROM mv_weekly_country_revenue_compare;

ROLLBACK;
```

The materialized-view plan should avoid source joins and aggregation. On this
small dataset, wall-clock differences can be noisy; compare plan work and
buffers as well as execution time.

## Pitfalls

- A normal `REFRESH MATERIALIZED VIEW` blocks concurrent reads of that view.
  `REFRESH ... CONCURRENTLY` requires a qualifying unique index and cannot run
  inside an explicit transaction block.
- Refresh is not automatic. Define freshness ownership and monitoring before
  using a materialized view for reporting.
- Materialized views duplicate data and add refresh cost; they are not a default
  replacement for indexing or query repair.
