# Day 30 — Solutions (Phase 2 Project: Performance & Robustness)

We produce a set of production‑ready queries (and patterns) for a Phase‑2 analytical project: parameterized date windows, KPI dashboards, SLAs, and built‑in validation. We also show how to reason about performance (indexes, EXPLAIN) and correctness (reconciliation checks).

Setup
- Facts: orders(order_id, customer_id, order_date, total_amount), order_items(order_id, product_id, quantity, unit_price, discount)
- Dimensions: customers(customer_id, country, segment), products(product_id, category), dates (optional)
- Parameters: use a params CTE for time windows so the same code works for different ranges

Exercise 1 — KPI dashboard (orders, revenue, AOV) by day with YOY comparison
```sql
WITH params AS (
  SELECT DATE_TRUNC('day', CURRENT_DATE) - INTERVAL '30 days' AS start_d,
         DATE_TRUNC('day', CURRENT_DATE)                     AS end_d
), daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         COUNT(DISTINCT o.order_id) AS orders,
         SUM(o.total_amount)        AS revenue
  FROM orders o
  WHERE o.order_date >= (SELECT start_d FROM params)
    AND o.order_date <  (SELECT end_d   FROM params)
  GROUP BY 1
), daily_yoy AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         COUNT(DISTINCT o.order_id) AS orders_yoy,
         SUM(o.total_amount)        AS revenue_yoy
  FROM orders o
  WHERE o.order_date >= (SELECT start_d FROM params) - INTERVAL '1 year'
    AND o.order_date <  (SELECT end_d   FROM params) - INTERVAL '1 year'
  GROUP BY 1
)
SELECT d.d,
       d.orders,
       d.revenue,
       ROUND(d.revenue / NULLIF(d.orders,0), 2) AS aov,
       dy.orders_yoy,
       dy.revenue_yoy,
       ROUND((d.revenue - dy.revenue_yoy) / NULLIF(dy.revenue_yoy,0), 4) AS yoy_revenue_growth
FROM daily d
LEFT JOIN daily_yoy dy ON dy.d = d.d - INTERVAL '1 year'
ORDER BY d.d;
```
Line‑by‑line
- params: isolates the 30‑day window; change once to shift the whole report
- daily and daily_yoy: identical structure with a 1‑year offset for the comparison
- Final SELECT: AOV and YoY revenue growth derived with safe NULLIF guards

Exercise 2 — SLA: fulfillment‑time distribution and percentiles
```sql
-- Assume shipments(order_id, shipped_at) exists; SLA measured as shipped_at - order_date
WITH params AS (
  SELECT CURRENT_DATE - INTERVAL '90 days' AS start_d,
         CURRENT_DATE                     AS end_d
), spans AS (
  SELECT o.order_id,
         EXTRACT(EPOCH FROM (s.shipped_at - o.order_date)) / 3600.0 AS hours_to_ship
  FROM orders o
  JOIN shipments s ON s.order_id = o.order_id
  WHERE o.order_date >= (SELECT start_d FROM params)
    AND o.order_date <  (SELECT end_d   FROM params)
)
SELECT ROUND(AVG(hours_to_ship), 2) AS avg_hours,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY hours_to_ship) AS p50_hours,
       percentile_cont(0.90) WITHIN GROUP (ORDER BY hours_to_ship) AS p90_hours,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY hours_to_ship) AS p95_hours,
       COUNT(*) AS shipments
FROM spans;
```
Explanation
- spans CTE computes numeric hours; final SELECT uses ordered‑set aggregates for percentiles
- These metrics feed SLAs; pick thresholds from p90/p95 as operational targets

Exercise 3 — Segment revenue by country and category with fanout‑safe aggregation
```sql
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
), fact AS (
  SELECT o.order_id, o.customer_id, o.order_date, ol.order_revenue
  FROM orders o JOIN order_lines ol ON ol.order_id = o.order_id
), sku_cat AS (
  SELECT oi.order_id,
         (ARRAY_AGG(p.category ORDER BY (oi.unit_price*oi.quantity*(1-oi.discount)) DESC))[1] AS category
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY oi.order_id
)
SELECT DATE_TRUNC('month', f.order_date)::date AS month,
       c.country,
       COALESCE(c.segment,'standard') AS segment,
       sc.category,
       ROUND(SUM(f.order_revenue),2) AS revenue,
       COUNT(*) AS orders
FROM fact f
JOIN customers c ON c.customer_id = f.customer_id
JOIN sku_cat   sc ON sc.order_id = f.order_id
GROUP BY 1,2,3,4
ORDER BY month DESC, revenue DESC
LIMIT 500;
```
Notes
- Pre‑aggregate order_lines to avoid double counting when re‑joining order_items later
- If multi‑category attribution is required, replace dominant category with proportional splits

Exercise 4 — Built‑in validation (reconciliation)
```sql
WITH params AS (
  SELECT CURRENT_DATE - INTERVAL '30 days' AS start_d,
         CURRENT_DATE                     AS end_d
), by_lines AS (
  SELECT SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS rev
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_date >= (SELECT start_d FROM params)
    AND o.order_date <  (SELECT end_d   FROM params)
), by_orders AS (
  SELECT SUM(o.total_amount) AS rev
  FROM orders o
  WHERE o.order_date >= (SELECT start_d FROM params)
    AND o.order_date <  (SELECT end_d   FROM params)
)
SELECT ROUND((SELECT rev FROM by_lines),2)  AS rev_by_lines,
       ROUND((SELECT rev FROM by_orders),2) AS rev_by_orders,
       ROUND((SELECT rev FROM by_lines) - (SELECT rev FROM by_orders), 2) AS diff;
```
Guidance
- Expect small differences (tax, shipping, rounding) depending on your business definition; large diffs need investigation

Performance checklist
- Indexes to consider:
  - orders(order_date) for time slicing
  - order_items(order_id) for line aggregation
  - shipments(order_id) for SLA joins
  - customers(country, segment) if frequently grouped/filtered
- Use partial indexes for hot ranges (e.g., orders where order_date >= current_date - interval '180 days')
- `EXPLAIN (ANALYZE, BUFFERS)`:
  - Verify index scans on time filters; avoid seq scans on large tables during routine reporting
  - Ensure CTEs don’t force materialization unnecessarily (PG12+ inlines by default)

Robustness tips
- Always parameterize time windows via a params CTE or function arguments
- Use NULLIF guards in ratios; COALESCE to label unknown segments; explicit ORDER BY for reproducibility
- Prefer windows for attaching global/partition metrics over joins where possible
