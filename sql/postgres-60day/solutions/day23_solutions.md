# Day 23 — Solutions: Common Table Expressions

A CTE names an intermediate relation for one statement. It improves readability
here by separating “build the metric” from “filter, aggregate, or present it.”

## Exercise 1 — Monthly revenue, top three months

```sql
SET search_path TO training, public;

WITH monthly_revenue AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(
           oi.unit_price * oi.quantity * (1 - oi.discount)
         ) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY date_trunc('month', o.order_date)
)
SELECT month,
       ROUND(revenue, 2) AS revenue
FROM monthly_revenue
ORDER BY revenue DESC, month
LIMIT 3;
```

Expected shape: at most three rows, ordered from highest to lowest net
line-item revenue. The query calculates revenue from `order_items`; using
`orders.total_amount` is also valid if the exercise explicitly treats that
stored total as authoritative.

## Exercise 2 — Electronics orders aggregated by country

The CTE retains one row per Electronics order line. The outer query joins the
customer dimension and rolls those lines up by country.

```sql
SET search_path TO training, public;

WITH electronics AS (
  SELECT o.order_id,
         o.customer_id,
         o.order_date,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE p.category = 'Electronics'
)
SELECT c.country,
       ROUND(SUM(e.line_revenue), 2) AS revenue
FROM electronics e
JOIN customers c ON c.customer_id = e.customer_id
GROUP BY c.country
ORDER BY revenue DESC, c.country;
```

Expected shape: one row per country with Electronics revenue. Countries with no
Electronics orders are absent because the exercise says to filter Electronics
orders; use a dimension-first `LEFT JOIN` if zero-revenue countries must appear.

## Pitfalls

- A CTE exists only for the single statement that follows it.
- `ORDER BY` belongs in the final query unless ordering is required to implement
  `LIMIT` or a window calculation inside the CTE.
- Since PostgreSQL 12, a side-effect-free CTE may be inlined. Use
  `MATERIALIZED` only when you intentionally need an optimization fence.
