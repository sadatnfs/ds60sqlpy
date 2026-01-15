# Day 23 — Solutions (CTEs Intro: Naming Subqueries, Readability, Reuse)

We refactor subqueries into named common table expressions (CTEs) to improve readability and enable reuse. We also show how to chain CTEs and why CTEs can be materialization boundaries (planner‑dependent).

Setup
- Tables: orders, order_items, customers, products
- Syntax: WITH name AS ( ... ) SELECT ... FROM name ...

Exercise 1 — Refactor a nested subquery into a named CTE
```sql
-- Before (nested subquery)
SELECT c.country,
       SUM(line_rev) AS revenue
FROM customers c
JOIN (
  SELECT oi.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS line_rev
  FROM order_items oi
  GROUP BY oi.order_id
) ol ON ol.order_id = c.customer_id -- (bug!)
GROUP BY c.country;
```
Fix and refactor
```sql
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
)
SELECT c.country,
       ROUND(SUM(ol.order_revenue),2) AS revenue
FROM orders o
JOIN order_lines ol ON ol.order_id = o.order_id
JOIN customers c    ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY revenue DESC;
```
Line‑by‑line
- order_lines encapsulates the line‑item aggregation to one row per order.
- The main SELECT joins customers via orders (correct key), then groups by country.
- This structure is easier to debug and extend (e.g., add filters in order_lines).

Exercise 2 — Chain multiple CTEs
```sql
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
), last_90d AS (
  SELECT o.order_id, o.customer_id, o.order_date, ol.order_revenue
  FROM orders o JOIN order_lines ol ON ol.order_id = o.order_id
  WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days'
), by_country AS (
  SELECT c.country,
         SUM(l.order_revenue) AS revenue
  FROM last_90d l JOIN customers c ON c.customer_id = l.customer_id
  GROUP BY c.country
)
SELECT country, ROUND(revenue,2) AS revenue
FROM by_country
ORDER BY revenue DESC;
```
Notes
- Build the result stepwise: aggregate lines → filter time → group by dimension.
- Consider adding comments in each CTE for future maintainers.

Exercise 3 — CTE vs derived table and materialization
- In Postgres 12+, CTEs are inlined by default; earlier versions materialize CTEs (which can degrade or improve performance depending on reuse and size).
- Guidance: Prefer CTEs for readability; if performance suffers, test with derived tables or explicit TEMP TABLEs for heavy reuse.
