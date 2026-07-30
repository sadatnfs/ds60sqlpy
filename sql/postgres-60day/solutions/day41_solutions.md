# Day 41 Solutions — Complex Aggregations

The learner script introduces `FILTER`, conditional aggregation, and
`string_agg`. The two exercises turn those techniques into a category dashboard
and a country-level top-product label. The canonical runnable answer is also in
[`day41_solutions.sql`](day41_solutions.sql).

## Exercise 1 — Six category dashboard metrics

Build one row per product category containing:

1. revenue in the last 30 days;
2. revenue in the last 90 days;
3. distinct orders in the last 30 days;
4. units in the last 30 days;
5. distinct customers in the last 90 days; and
6. revenue per order in the last 30 days.

```sql
SET search_path TO training, public;

WITH lines AS (
  SELECT p.category,
         o.order_id,
         o.customer_id,
         o.order_date,
         oi.quantity,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
)
SELECT category,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ), 2) AS revenue_30d,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ), 2) AS revenue_90d,
       COUNT(DISTINCT order_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS orders_30d,
       SUM(quantity) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS units_30d,
       COUNT(DISTINCT customer_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ) AS customers_90d,
       ROUND(
         SUM(revenue) FILTER (
           WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
         )
         / NULLIF(
             COUNT(DISTINCT order_id) FILTER (
               WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
             ),
             0
           ),
         2
       ) AS revenue_per_order_30d
FROM lines
GROUP BY category
ORDER BY revenue_30d DESC NULLS LAST, category;
```

Expected shape: one row for each category in `training.products`, with six
metric columns. A category with no qualifying recent activity can have `NULL`
windowed sums. `NULLIF` makes revenue per order `NULL` instead of raising a
division-by-zero error.

## Exercise 2 — Top five product names per country

Rank at `(country, product)` grain before aggregating names. This avoids the
common mistake of applying `LIMIT 5` to the entire result instead of five
products per country.

```sql
SET search_path TO training, public;

WITH product_revenue AS (
  SELECT c.country,
         p.product_id,
         p.name,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM customers c
  JOIN orders o USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY c.country, p.product_id, p.name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
SELECT country,
       string_agg(name, ', ' ORDER BY product_rank) AS top_five_products
FROM ranked
WHERE product_rank <= 5
GROUP BY country
ORDER BY country;
```

Expected shape: one row per represented country and one comma-separated label
ordered from highest to lowest product revenue.

## Reasoning, safety, and pitfalls

- Compute line revenue from `order_items`; do not multiply `orders.total_amount`
  after joining to items because that would repeat the order total per line.
- Use `DISTINCT` inside counts when the input is at line-item grain.
- Add a deterministic tie-breaker (`product_id`) to `ROW_NUMBER`.
- Both answers are read-only and safe to run repeatedly.

## Exercise 3 — Compare grouping sets and CUBE

The `CUBE(country, category)` answer emits detail, both one-dimensional
subtotals, and the grand total. `GROUPING(country, category)` identifies each
generated level.

## Exercise 4 — State metric populations with FILTER

Each status/time population appears beside its aggregate, making several
country metrics readable without repeating the whole grouped relation.

## Exercise 5 — Distinguish stored and generated NULLs

`GROUPING(country)` is one only for the generated subtotal. A stored NULL, if
allowed by the model, keeps grouping flag zero and receives a different label.

## Exercise 6 — Return a typed empty collection

`array_agg` over no qualifying inputs is NULL. The answer uses
`COALESCE(..., '{}'::text[])`; the explicit type must match the aggregate type.
