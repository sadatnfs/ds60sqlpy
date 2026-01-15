# Day 36 — Solutions (Materialized Views)

We use materialized views (MVs) to cache expensive query results, add indexes on top of them, and refresh safely (including concurrently). We also discuss when to prefer MVs vs. table snapshots.

Setup
- MV basics: `CREATE MATERIALIZED VIEW ... AS SELECT ...;`
- Refresh: `REFRESH MATERIALIZED VIEW [CONCURRENTLY] ...;`
- Requirements: CONCURRENTLY needs a UNIQUE index that covers all rows (typically on a deterministic key set)

Exercise 1 — Create a materialized view for monthly revenue by country
```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_country_revenue AS
SELECT date_trunc('month', o.order_date)::date AS month,
       c.country,
       SUM(o.total_amount) AS revenue,
       COUNT(*) AS orders
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY 1,2;
```
Index the MV for common access paths
```sql
CREATE INDEX IF NOT EXISTS idx_mv_mcr_month_country
  ON mv_monthly_country_revenue(month, country);
```
Why
- The heavy GROUP BY is computed once and reused; downstream queries filter/aggregate on a much smaller MV.

Exercise 2 — CONCURRENT refresh for read availability
```sql
-- Add a unique index required for CONCURRENTLY refresh
-- Choose a key that uniquely identifies MV rows (month,country) here
CREATE UNIQUE INDEX IF NOT EXISTS uid_mv_mcr ON mv_monthly_country_revenue (month, country);

-- Now refresh without blocking readers
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_country_revenue;
```
Notes
- CONCURRENTLY builds a new MV snapshot and swaps it in, allowing reads during refresh. It’s slower than non‑concurrent but avoids downtime.

Exercise 3 — Parameterized MVs vs. table snapshots
- If your aggregation needs parameters (e.g., last N days), consider creating a date‑partitioned snapshot table and rolling window ETL instead of a single MV.
- For near‑real‑time dashboards, schedule frequent refreshes or maintain an incremental table via triggers/CDC.

Exercise 4 — Combine MVs
```sql
-- Another MV for monthly product category revenue
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_cat_revenue AS
SELECT date_trunc('month', o.order_date)::date AS month,
       p.category,
       SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id=o.order_id
JOIN products p ON p.product_id=oi.product_id
GROUP BY 1,2;

CREATE UNIQUE INDEX IF NOT EXISTS uid_mv_mcr2 ON mv_monthly_cat_revenue (month, category);
```
Consumers
```sql
SELECT * FROM mv_monthly_country_revenue WHERE month >= date_trunc('month', current_date) - interval '12 months';
```
Best practices
- Refresh cadence matches data freshness needs; consider cron or managed schedulers
- Add indexes that match query shapes on the MV
- Avoid parameter‑dependent logic inside the MV definition; precompute stable aggregates
