# Day 04 — Solutions (OUTER JOINs: Preserving Unmatched Rows)

We show proper placement of predicates (ON vs WHERE), counting NULL-extended rows, and FULL JOIN reconciliation.

Exercise 1 — Categories with no orders last month
```sql
WITH last_month AS (
  SELECT DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' AS start_m,
         DATE_TRUNC('month', CURRENT_DATE) AS end_m
)
SELECT p.category
FROM products p
LEFT JOIN order_items oi
  ON oi.product_id = p.product_id
LEFT JOIN orders o
  ON o.order_id = oi.order_id
  AND o.order_date >= (SELECT start_m FROM last_month)
  AND o.order_date <  (SELECT end_m FROM last_month)
GROUP BY p.category
HAVING SUM(CASE WHEN o.order_id IS NOT NULL THEN 1 ELSE 0 END) = 0
ORDER BY p.category;
```
Explanation
- Date window computed once in last_month CTE for readability and to avoid recomputing expressions.
- Predicates on the right table (orders) go in the ON clause to preserve the LEFT join; putting them in WHERE would turn it into an INNER JOIN.
- HAVING with SUM(CASE...) = 0 identifies categories with zero matched orders.

Exercise 2 — Customers without orders, by country
```sql
SELECT c.country,
       SUM(CASE WHEN o.order_id IS NULL THEN 1 ELSE 0 END) AS customers_without_orders
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY customers_without_orders DESC;
```
Explanation
- After a LEFT JOIN, unmatched right‑side columns are NULL. Counting those finds non‑buyers.
- COUNT(o.order_id) would skip NULLs silently; the CASE approach makes the intent explicit.

Exercise 3 — Reconcile keys with FULL OUTER JOIN
```sql
WITH a AS ( SELECT order_id FROM orders ),
     b AS ( SELECT DISTINCT order_id FROM payments )
SELECT COALESCE(a.order_id, b.order_id) AS order_id,
       CASE
         WHEN a.order_id IS NOT NULL AND b.order_id IS NOT NULL THEN 'both'
         WHEN a.order_id IS NOT NULL AND b.order_id IS NULL THEN 'orders_only'
         WHEN a.order_id IS NULL AND b.order_id IS NOT NULL THEN 'payments_only'
         ELSE 'unknown'
       END AS presence
FROM a
FULL JOIN b ON b.order_id = a.order_id
ORDER BY order_id
LIMIT 200;
```
Notes
- FULL JOIN keeps unmatched rows from both sides; COALESCE picks the non‑NULL key.
- presence flags help triage missing data issues quickly.
