# Day 27 — Solutions (Pivot and Unpivot)

We show multiple ways to pivot (rows→columns) and unpivot (columns→rows) in Postgres. We prefer portable SUM(CASE WHEN ...) for simple pivots and crosstab() for wide/unknown sets. For unpivot, we use UNION ALL or a VALUES/LATERAL approach.

Setup
- Tables: orders(order_id, order_date), order_items(order_id, product_id, quantity, unit_price, discount), products(product_id, category)
- Extension: crosstab() requires tablefunc: `CREATE EXTENSION IF NOT EXISTS tablefunc;`

Exercise 1 — Pivot daily revenue by category (portable)
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         p.category,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS rev
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY 1,2
)
SELECT d,
       SUM(CASE WHEN category='electronics' THEN rev ELSE 0 END) AS electronics,
       SUM(CASE WHEN category='apparel'     THEN rev ELSE 0 END) AS apparel,
       SUM(CASE WHEN category='home'        THEN rev ELSE 0 END) AS home
FROM daily
GROUP BY d
ORDER BY d;
```
Notes
- This approach is explicit and index‑friendly. Add columns per category you care about.

Exercise 2 — Pivot with crosstab() for many categories
```sql
-- 1) source rows: rowid, category, value
WITH src AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         p.category,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS rev
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY 1,2
  ORDER BY 1,2
)
SELECT *
FROM crosstab(
    $$ SELECT d::text AS rowid, category, rev FROM src ORDER BY 1,2 $$,
    $$ SELECT DISTINCT category FROM products ORDER BY 1 $$
) AS ct(
    d text,
    "apparel" numeric,
    "electronics" numeric,
    "home" numeric
)
ORDER BY d;
```
Caveats
- Output columns must be declared up front and in the same order as the category SQL. For dynamic schemas, generate SQL.

Exercise 3 — Unpivot columns to rows
Method A: UNION ALL
```sql
SELECT order_id, 'subtotal' AS metric, subtotal AS value FROM invoices
UNION ALL
SELECT order_id, 'tax'     , tax      FROM invoices
UNION ALL
SELECT order_id, 'shipping', shipping FROM invoices;
```
Method B: VALUES/LATERAL (concise)
```sql
SELECT i.order_id, x.metric, x.value
FROM invoices i
CROSS JOIN LATERAL (
  VALUES
    ('subtotal', i.subtotal),
    ('tax',      i.tax),
    ('shipping', i.shipping)
) AS x(metric, value);
```
Why
- Unpivoting simplifies later aggregations and filters by metric. The LATERAL form is compact and typically faster than multiple UNIONs for small column sets.
