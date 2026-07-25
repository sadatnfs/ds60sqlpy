# Day 26 — Solutions: CTEs with Window Functions

Both exercises use one CTE to establish the analytical grain and another to
apply a window. Window functions do not reduce row count, so the aggregation
must happen first.

## Exercise 1 — Monthly totals and month-over-month growth

```sql
SET search_path TO training, public;

WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), compared AS (
  SELECT month,
         revenue,
         LAG(revenue) OVER (
           ORDER BY month
         ) AS previous_month_revenue
  FROM monthly
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(previous_month_revenue, 2) AS previous_month_revenue,
       ROUND(
         (revenue - previous_month_revenue)
           / NULLIF(previous_month_revenue, 0),
         4
       ) AS month_over_month_growth
FROM compared
ORDER BY month;
```

Expected shape: one row per month that has orders. The first row has no prior
month and therefore a `NULL` growth rate. The rate is a decimal (`0.10` means
10%), not a preformatted percentage.

Assumption: missing calendar months are skipped. If a true month-over-month
comparison must show zero-revenue months, build a calendar with
`generate_series`, left join the totals, and then use `LAG`.

## Exercise 2 — Top five orders by value for each product

```sql
SET search_path TO training, public;

WITH product_orders AS (
  SELECT p.product_id,
         p.name,
         oi.order_id,
         SUM(
           oi.unit_price * oi.quantity * (1 - oi.discount)
         ) AS product_order_value
  FROM products p
  JOIN order_items oi ON oi.product_id = p.product_id
  GROUP BY p.product_id, p.name, oi.order_id
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY product_id
           ORDER BY product_order_value DESC, order_id
         ) AS product_order_rank
  FROM product_orders
)
SELECT product_id,
       name,
       order_id,
       ROUND(product_order_value, 2) AS product_order_value,
       product_order_rank
FROM ranked
WHERE product_order_rank <= 5
ORDER BY product_id, product_order_rank;
```

Expected shape: up to five rows per sold product; unsold products do not
appear. `ROW_NUMBER` enforces exactly five rows when at least five orders exist.
Use `RANK` instead if all ties at the fifth value must be retained.

## Pitfalls

- A window alias cannot be filtered in the same query level in PostgreSQL;
  calculate it in `ranked`, then filter outside.
- Cast or use numeric operands for division. `NULLIF` protects against a zero
  previous-month denominator.
- Rank the per-product contribution to an order, not the whole
  `orders.total_amount`, because an order can contain several products.
