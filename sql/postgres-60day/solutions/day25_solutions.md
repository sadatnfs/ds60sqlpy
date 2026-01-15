# Day 25 — Solutions (Multiple CTEs and Hierarchical Patterns)

We compose several CTEs to express complex logic clearly, including hierarchical expansions and rollups. The goal is correctness and readability first, then performance tuning.

Setup
- Tables: orders, order_items, customers, products, categories(category_id, parent_id)
- Patterns: build once (order_lines), constrain (time windows), enrich (dimensions), aggregate

Exercise 1 — Multi-CTE pipeline to compute last-quarter revenue by country and category
```sql
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
), last_q AS (
  SELECT DATE_TRUNC('quarter', CURRENT_DATE) - INTERVAL '3 months' AS start_q,
         DATE_TRUNC('quarter', CURRENT_DATE)                       AS end_q
), fact AS (
  SELECT o.order_id, o.customer_id, o.order_date, ol.order_revenue
  FROM orders o
  JOIN order_lines ol ON ol.order_id = o.order_id
  WHERE o.order_date >= (SELECT start_q FROM last_q)
    AND o.order_date <  (SELECT end_q   FROM last_q)
), sku_cat AS (
  SELECT oi.order_id,
         (ARRAY_AGG(p.category ORDER BY (oi.unit_price*oi.quantity*(1-oi.discount)) DESC))[1] AS category
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY oi.order_id
)
SELECT c.country,
       sc.category,
       ROUND(SUM(f.order_revenue),2) AS revenue
FROM fact f
JOIN customers c ON c.customer_id = f.customer_id
JOIN sku_cat   sc ON sc.order_id = f.order_id
GROUP BY c.country, sc.category
ORDER BY revenue DESC
LIMIT 200;
```
Why
- Clear staging: compute lines once; define quarter window; filter early; attribute to a dominant category per order.

Exercise 2 — Hierarchical category rollups with CTE reuse
```sql
WITH RECURSIVE up AS (
  SELECT c.category_id AS node, c.category_id AS anc
  FROM categories c
  UNION ALL
  SELECT u.node, c.parent_id AS anc
  FROM up u JOIN categories c ON c.category_id = u.anc
  WHERE c.parent_id IS NOT NULL
), leaf_sales AS (
  SELECT p.category_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category_id
)
SELECT anc AS rollup_category,
       ROUND(SUM(COALESCE(ls.revenue,0)),2) AS revenue
FROM up u
LEFT JOIN leaf_sales ls ON ls.category_id = u.node
GROUP BY anc
ORDER BY revenue DESC
LIMIT 200;
```
Notes
- up CTE is re-usable; you can join it with other per-node metrics as needed.

Exercise 3 — Debugging and validating multi-CTE plans
- Use EXPLAIN (ANALYZE, BUFFERS) to see whether CTEs are inlined; consider derived tables or TEMP tables for heavy reuse.
- Sanity checks: compare `SUM(order_revenue)` vs `SUM(total_amount)` for a given window to detect definition drift.
