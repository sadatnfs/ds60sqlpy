# Day 55 — Solutions (Project 4: Complex BI, Part 1 — Drilldowns with GROUPING SETS)

We’ll compare ROLLUP vs CUBE, interpret GROUPING flags, and extend the drill‑down to include order status. Explanations are line‑by‑line for beginners.

Reference (annotated)
```sql
WITH line AS (
  SELECT c.country,
         p.category,
         pm.method AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue,
         oi.quantity AS qty
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN payments pm ON pm.order_id = o.order_id
)
SELECT country,
       category,
       payment_method,
       month,
       ROUND(SUM(revenue),2) AS revenue,
       SUM(qty) AS units,
       GROUPING(country)        AS g_country,
       GROUPING(category)       AS g_category,
       GROUPING(payment_method) AS g_method,
       GROUPING(month)          AS g_month
FROM line
GROUP BY ROLLUP (country, category, payment_method, month)
ORDER BY country NULLS FIRST, category NULLS FIRST, payment_method NULLS FIRST, month NULLS FIRST;
```
Notes
- ROLLUP builds hierarchical subtotals: (country,category,payment,month) → (country,category,payment) → (country,category) → (country) → grand total.
- GROUPING(col)=1 marks that column is aggregated (subtotal level), 0 means detail value present.

Exercise 1 — Replace ROLLUP with CUBE and compare row counts
Goal
- Show that CUBE produces all combinations of subtotals (not only hierarchical). Count resulting rows and compare to ROLLUP.

Solution
```sql
WITH line AS (
  SELECT c.country,
         p.category,
         pm.method AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN payments pm ON pm.order_id = o.order_id
), roll AS (
  SELECT COUNT(*) AS n_roll
  FROM (
    SELECT 1
    FROM line
    GROUP BY ROLLUP(country, category, payment_method, month)
  ) r
), cub AS (
  SELECT COUNT(*) AS n_cube
  FROM (
    SELECT 1
    FROM line
    GROUP BY CUBE(country, category, payment_method, month)
  ) c
)
SELECT n_roll, n_cube, (n_cube - n_roll) AS extra_rows
FROM roll CROSS JOIN cub;
```
Line‑by‑line
- roll/cub: compute the number of groups produced by each operator.
- Expect n_cube ≥ n_roll. CUBE adds cross‑dimension subtotals such as (country, month) without category/payment.

Bonus — Inspect grouping combinations with GROUPING_ID
```sql
WITH line AS (
  SELECT c.country, p.category, pm.method AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c ON c.customer_id=o.customer_id
  JOIN order_items oi ON oi.order_id=o.order_id
  JOIN products p ON p.product_id=oi.product_id
  LEFT JOIN payments pm ON pm.order_id=o.order_id
)
SELECT GROUPING_ID(country, category, payment_method, month) AS gid,
       GROUPING(country) AS g_country,
       GROUPING(category) AS g_category,
       GROUPING(payment_method) AS g_method,
       GROUPING(month) AS g_month,
       ROUND(SUM(revenue),2) AS revenue
FROM line
GROUP BY CUBE(country, category, payment_method, month)
ORDER BY gid, g_country, g_category, g_method, g_month
LIMIT 30;
```
Notes
- GROUPING_ID encodes which columns are aggregated (higher values = more aggregated).

Exercise 2 — Add order status to drill‑down top‑5
Goal
- Extend the product drill‑down (country → category → product) by adding order status.

Solution
```sql
WITH prod_rev AS (
  SELECT c.country,
         p.category,
         COALESCE(o.status,'unknown') AS status,
         p.product_id,
         p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, COALESCE(o.status,'unknown'), p.product_id, p.name
), ranked AS (
  SELECT *,
         RANK() OVER (PARTITION BY country, category, status ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT country, category, status, product_id, name, ROUND(revenue,2) AS revenue
FROM ranked
WHERE rnk <= 5
ORDER BY country, category, status, rnk;
```
Line‑by‑line
- COALESCE status in case the column is NULL in your dataset.
- RANK() PARTITION BY the three dimensions so each (country,category,status) gets its own top‑5.

Tips
- If “status” is on order_items instead, adjust the join/column accordingly.
- For dense top‑N without ties, use ROW_NUMBER().
