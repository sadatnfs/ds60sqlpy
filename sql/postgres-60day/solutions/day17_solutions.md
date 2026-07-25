# Day 17 solutions — ranking functions

These answers match the exercises in [Day 17](../day17_rank_functions.sql).

## Exercise 1 — Rank products by revenue within category

```sql
WITH product_revenue AS (
  SELECT
    p.category,
    p.product_id,
    p.name,
    COALESCE(
      SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
      0
    ) AS revenue
  FROM training.products AS p
  LEFT JOIN training.order_items AS oi
    ON oi.product_id = p.product_id
  GROUP BY p.category, p.product_id, p.name
)
SELECT
  category,
  product_id,
  name,
  ROUND(revenue, 2) AS revenue,
  RANK() OVER (
    PARTITION BY category
    ORDER BY revenue DESC
  ) AS revenue_rank,
  DENSE_RANK() OVER (
    PARTITION BY category
    ORDER BY revenue DESC
  ) AS dense_revenue_rank
FROM product_revenue
ORDER BY category, revenue DESC, product_id;
```

Tied products receive the same value from both functions. `RANK` then leaves a gap; `DENSE_RANK` uses the next consecutive rank. Do not add `product_id` to the window ordering if you want equal revenue to remain a tie.

## Exercise 2 — Top three customers per country

```sql
WITH customer_revenue AS (
  SELECT
    c.country,
    c.customer_id,
    c.full_name,
    COALESCE(
      SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
      0
    ) AS lifetime_revenue
  FROM training.customers AS c
  LEFT JOIN training.orders AS o
    ON o.customer_id = c.customer_id
  LEFT JOIN training.order_items AS oi
    ON oi.order_id = o.order_id
  GROUP BY c.country, c.customer_id, c.full_name
),
ranked_customers AS (
  SELECT
    cr.*,
    ROW_NUMBER() OVER (
      PARTITION BY cr.country
      ORDER BY cr.lifetime_revenue DESC, cr.customer_id
    ) AS country_position
  FROM customer_revenue AS cr
)
SELECT
  country,
  customer_id,
  full_name,
  ROUND(lifetime_revenue, 2) AS lifetime_revenue,
  country_position
FROM ranked_customers
WHERE country_position <= 3
ORDER BY country, country_position;
```

`ROW_NUMBER` guarantees at most three rows per country. If the business rule should include every customer tied at third place, use `RANK` or `DENSE_RANK` instead and accept that a country can return more than three rows.

## Check yourself

- Rank values restart for each category or country.
- The clean seed’s zero-revenue products make the tie behavior visible.
- Exercise 2 returns three rows for every country that has at least three customers.
