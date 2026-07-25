# Day 05 solutions — CROSS JOINs and self-joins

These answers match the exercises in [Day 05](../day05_cross_self_joins.sql).

## Exercise 1 — Cross the top five categories and countries

```sql
WITH category_revenue AS (
  SELECT
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM training.order_items AS oi
  JOIN training.products AS p
    ON p.product_id = oi.product_id
  GROUP BY p.category
  ORDER BY revenue DESC, p.category
  LIMIT 5
),
country_revenue AS (
  SELECT
    c.country,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM training.customers AS c
  JOIN training.orders AS o
    ON o.customer_id = c.customer_id
  JOIN training.order_items AS oi
    ON oi.order_id = o.order_id
  GROUP BY c.country
  ORDER BY revenue DESC, c.country
  LIMIT 5
)
SELECT
  cr.category,
  ROUND(cr.revenue, 2) AS category_revenue,
  cor.country,
  ROUND(cor.revenue, 2) AS country_revenue
FROM category_revenue AS cr
CROSS JOIN country_revenue AS cor
ORDER BY cr.revenue DESC, cor.revenue DESC;
```

Each CTE produces five rows. The `CROSS JOIN` therefore produces 25 category-country combinations; it does not claim that a combination itself earned either displayed total.

## Exercise 2 — Show a three-level employee hierarchy

```sql
SELECT
  e.employee_id,
  e.full_name AS employee,
  m.full_name AS manager,
  gm.full_name AS managers_manager
FROM training.employees AS e
LEFT JOIN training.employees AS m
  ON m.employee_id = e.manager_id
LEFT JOIN training.employees AS gm
  ON gm.employee_id = m.manager_id
ORDER BY e.employee_id;
```

The same table appears three times with three aliases. Both manager joins are optional because the hierarchy can end before all three levels are present.

## Check yourself

- Exercise 1 returns 25 rows when both top-five CTEs contain five rows.
- Exercise 2 retains top-level employees and shows `NULL` for missing hierarchy levels.
