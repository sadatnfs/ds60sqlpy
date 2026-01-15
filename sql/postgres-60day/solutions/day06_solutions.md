# Day 06 — Solutions (Set Operations: UNION/UNION ALL, INTERSECT, EXCEPT)

We derive overlaps and exclusives between cohorts, stitch monthly top‑k across partitions, and compare catalog vs facts. Each solution includes the reasoning, line‑by‑line notes, and pitfalls.

Setup
- Schema: training; tables: customers, products, orders, order_items
- Quick refresher: UNION removes duplicates; UNION ALL preserves duplicates. INTERSECT keeps rows present in both sets. EXCEPT keeps rows in A not in B.

Exercise 1 — Q1 vs Q2 cohorts: intersection and exclusives
```sql
WITH q1 AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= DATE_TRUNC('year', CURRENT_DATE)
    AND o.order_date <  DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '3 months'
), q2 AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '3 months'
    AND o.order_date <  DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '6 months'
)
-- Intersection (both Q1 and Q2)
SELECT 'intersection' AS set_type, customer_id FROM (
  SELECT customer_id FROM q1
  INTERSECT
  SELECT customer_id FROM q2
) i
UNION ALL
-- Exclusive Q1 only
SELECT 'q1_only' AS set_type, customer_id FROM (
  SELECT customer_id FROM q1
  EXCEPT
  SELECT customer_id FROM q2
) q1_only
UNION ALL
-- Exclusive Q2 only
SELECT 'q2_only' AS set_type, customer_id FROM (
  SELECT customer_id FROM q2
  EXCEPT
  SELECT customer_id FROM q1
) q2_only
ORDER BY set_type, customer_id
LIMIT 500;
```
Line‑by‑line
- DISTINCT in q1/q2: ensure each set is a set of unique customer_ids; avoids duplicate semantics confusion.
- INTERSECT: returns only IDs present in both sets.
- EXCEPT: asymmetric difference; (A EXCEPT B) ≠ (B EXCEPT A).
- UNION ALL: concatenate labeled results without dedup so counts stay additive.
Pitfalls
- Using UNION (dedup) where UNION ALL is intended; can change counts and add sorting overhead.

Exercise 2 — Monthly top‑k sellers by category across a two‑month window
```sql
WITH month_cat AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         p.category,
         oi.product_id,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
    AND o.order_date <  DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
  GROUP BY DATE_TRUNC('month', o.order_date), p.category, oi.product_id
), ranked AS (
  SELECT month,
         category,
         product_id,
         revenue,
         DENSE_RANK() OVER (PARTITION BY month, category ORDER BY revenue DESC) AS rnk
  FROM month_cat
)
SELECT month, category, product_id, revenue
FROM ranked
WHERE rnk <= 3
ORDER BY month, category, revenue DESC;
```
Explanation
- Window partition (month, category) produces separate rankings per month and category.
- DENSE_RANK keeps ties; if ties matter, consider ROW_NUMBER (breaks ties deterministically) or RANK (skips ranks on ties).
Pitfalls
- Grouping by date_trunc but selecting raw order_date will fail; always select grouped expressions or aggregates.

Exercise 3 — Catalog products never ordered
```sql
SELECT p.product_id
FROM products p
EXCEPT
SELECT DISTINCT oi.product_id
FROM order_items oi
ORDER BY product_id
LIMIT 200;
```
Why this way
- EXCEPT reads “in catalog but not in order_items.” A LEFT JOIN … WHERE oi.product_id IS NULL is equivalent; EXCEPT makes the intent crisp.
- DISTINCT on order_items avoids duplicate rows in the right set; EXCEPT applies set semantics regardless, but DISTINCT can reduce work.
