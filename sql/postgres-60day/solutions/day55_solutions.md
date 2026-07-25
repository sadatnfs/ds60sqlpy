# Day 55 Solutions — BI Drill-down and Subtotals

The two exercises compare `ROLLUP` and `CUBE`, then add order status to a
country/category/product top-five drill-down. See
[`day55_solutions.sql`](day55_solutions.sql).

## Exercise 1 — Compare row counts

```sql
SET search_path TO training, public;

WITH line AS (
  SELECT c.country,
         p.category,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), rollup_rows AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY ROLLUP (country, category)
), cube_rows AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
)
SELECT (SELECT COUNT(*) FROM rollup_rows) AS rollup_row_count,
       (SELECT COUNT(*) FROM cube_rows) AS cube_row_count;
```

Expected shape: one comparison row. `CUBE(country, category)` adds category-only
subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count
is greater on this seed.

## Exercise 2 — Status-aware top five

```sql
SET search_path TO training, public;

WITH line AS (
  SELECT c.country,
         p.category,
         o.status,
         p.product_id,
         p.name,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), product_revenue AS (
  SELECT country,
         category,
         status,
         product_id,
         name,
         SUM(revenue) AS revenue
  FROM line
  GROUP BY country, category, status, product_id, name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country, category, status
           ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
SELECT country,
       category,
       status,
       product_id,
       name,
       ROUND(revenue, 2) AS revenue,
       product_rank
FROM ranked
WHERE product_rank <= 5
ORDER BY country, category, status, product_rank;
```

Expected grain: up to five rows per `(country, category, status)`.

## Reasoning, safety, and pitfalls

- `CUBE` grows quickly: three dimensions produce up to eight grouping sets,
  before considering the number of distinct dimension values.
- `NULL` can mean a subtotal or a real null dimension value. Include
  `GROUPING(...)` flags in user-facing subtotal reports when ambiguity exists.
- Aggregate product revenue before ranking.
- `ROW_NUMBER` plus `product_id` yields exactly five deterministic rows when at
  least five products exist; `RANK` can return more because of ties.
