# Day 02 — Solutions (Aggregations, GROUP BY, HAVING, Grouping Sets)

Deep explanations for each exercise with reasoning, pitfalls, and Postgres tips.

Setup
- Schema: training; tables: orders, order_items, products, customers
- Reminder: WHERE filters rows before grouping; HAVING filters groups after aggregation

Exercise 1 — Revenue, orders, AOV by country and month with ROLLUP
```sql
WITH order_totals AS (
  SELECT o.order_id,
         c.country,
         CAST(date_trunc('month', o.order_date) AS date) AS month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN customers c ON c.customer_id = o.customer_id
  GROUP BY o.order_id, c.country, date_trunc('month', o.order_date)
)
SELECT 
  CASE WHEN GROUPING(country)=1 THEN 'ALL_COUNTRIES' ELSE country END AS country,
  CASE WHEN GROUPING(month)=1 THEN NULL ELSE month END AS month,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(revenue),2)    AS revenue,
  ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT order_id),0), 2) AS aov
FROM order_totals
GROUP BY ROLLUP (country, month)
ORDER BY country NULLS FIRST, month NULLS FIRST;
```
Line‑by‑line
- date_trunc('month', o.order_date): Buckets orders into calendar months. CAST to date for prettier output.
- SUM(...) AS revenue: Line‑item revenue summed per order in the CTE to prevent double counting when joining later.
- GROUP BY ROLLUP (country, month): Produces (country,month) rows, country subtotals, and a grand total.
- GROUPING(): Returns 1 when a column is aggregated away (subtotal). We use it to label subtotal rows and set NULL for month when subtotal.
- COUNT(DISTINCT order_id): Orders per bucket. AOV is revenue divided by orders; NULLIF guards division by zero.
Pitfalls
- Selecting non‑grouped, non‑aggregated columns is invalid SQL.
- Putting the date filter in HAVING when it belongs in WHERE can scan more rows than necessary.

Exercise 2 — Revenue share by category with a window total
```sql
WITH cat_rev AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT category,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (),0), 4) AS share_of_total
FROM cat_rev
ORDER BY revenue DESC;
```
Explanation
- SUM(...) OVER (): Window function computes the grand total across all rows without collapsing the result set.
- Division by the window total yields each category’s share. ROUND to 4 decimals for readability.
Tip
- For large cardinalities, ensure category is indexed if used elsewhere; here aggregation scans all rows anyway.

Exercise 3 — Refund rate by region (completed vs refunded)
```sql
SELECT c.country AS region,
       SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) AS completed_orders,
       SUM(CASE WHEN o.status = 'refunded'  THEN 1 ELSE 0 END) AS refunded_orders,
       ROUND(
         SUM(CASE WHEN o.status = 'refunded' THEN 1 ELSE 0 END)::numeric
         / NULLIF(SUM(CASE WHEN o.status IN ('completed','refunded') THEN 1 ELSE 0 END), 0)
       , 4) AS refund_rate
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY refund_rate DESC;
```
Why this way
- Conditional aggregation via CASE avoids extra joins and is portable. In Postgres, COUNT(*) FILTER (WHERE ...) is another clean option.
- NULLIF prevents division by zero when a region has no completed/refunded orders.
Common mistakes
- Filtering rows with WHERE status IN (...) would remove regions entirely; we want denominators to reflect zeroes too, so we aggregate with CASE.
