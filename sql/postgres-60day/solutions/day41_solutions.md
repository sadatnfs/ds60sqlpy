# Day 41 — Solutions (Complex Aggregations)

We combine advanced grouping patterns, conditional aggregates, window + group hybrids, and ratio-of-ratios safely. We also show how to format subtotal/grand-total rows and label them with GROUPING().

Setup
- Tables: orders(order_id, customer_id, order_date, total_amount), order_items(order_id, product_id, quantity, unit_price, discount), customers(country, segment), products(category)

Exercise 1 — Multi-level totals with GROUPING SETS and labels
```sql
WITH base AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         c.country,
         SUM(o.total_amount) AS revenue
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  GROUP BY 1, 2
)
SELECT 
  CASE WHEN GROUPING(month)=1   THEN NULL ELSE month   END AS month,
  CASE WHEN GROUPING(country)=1 THEN 'ALL_COUNTRIES' ELSE country END AS country,
  SUM(revenue) AS revenue
FROM base
GROUP BY GROUPING SETS ((month, country), (month), ())
ORDER BY month NULLS FIRST, country NULLS FIRST;
```
Notes
- GROUPING(month)=1 marks subtotal/grand-total rows so you can format them explicitly.

Exercise 2 — Conditional aggregation with FILTER and CASE
```sql
SELECT c.country,
       COUNT(*)                                         AS orders,
       COUNT(*) FILTER (WHERE o.total_amount >= 100)    AS big_orders,
       SUM(o.total_amount)                              AS revenue,
       SUM(CASE WHEN o.total_amount >= 100 THEN o.total_amount ELSE 0 END) AS big_revenue
FROM orders o
JOIN customers c ON c.customer_id=o.customer_id
GROUP BY c.country
ORDER BY revenue DESC;
```
Why
- FILTER is concise in Postgres; CASE is portable. Both compute segment-specific metrics without extra joins.

Exercise 3 — Product share of category with window-denominator
```sql
WITH prod_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.quantity*oi.unit_price*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.product_id
)
SELECT category,
       product_id,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY category),0), 4) AS share_in_category
FROM prod_rev
ORDER BY category, share_in_category DESC
LIMIT 300;
```
Notes
- Windowed denominator avoids self-joins and preserves each row’s context.

Exercise 4 — Ratio-of-ratios: category share within a country and global share
```sql
WITH line_rev AS (
  SELECT c.country, p.category,
         SUM(oi.quantity*oi.unit_price*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id=o.order_id
  JOIN customers c    ON c.customer_id=o.customer_id
  JOIN products p     ON p.product_id=oi.product_id
  GROUP BY c.country, p.category
)
SELECT country,
       category,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY country),0), 4) AS share_in_country,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (),0), 4)                    AS share_global
FROM line_rev
ORDER BY country, revenue DESC;
```
Cautions
- Always guard denominators with NULLIF to avoid division-by-zero.
- Distinguish between row-level windows and grouped results to avoid fanout.
