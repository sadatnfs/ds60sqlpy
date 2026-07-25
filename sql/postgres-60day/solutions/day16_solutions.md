# Day 16 solutions — window-function fundamentals

These answers match the exercises in [Day 16](../day16_window_functions_fundamentals.sql). Window functions add group-level context without collapsing the detail rows.

## Exercise 1 — Order total beside customer lifetime total

```sql
SELECT
  o.customer_id,
  o.order_id,
  o.order_date,
  o.total_amount AS order_total,
  ROUND(
    SUM(o.total_amount) OVER (
      PARTITION BY o.customer_id
    ),
    2
  ) AS customer_lifetime_total,
  ROUND(
    o.total_amount
      / NULLIF(
          SUM(o.total_amount) OVER (
            PARTITION BY o.customer_id
          ),
          0
        ),
    4
  ) AS order_share_of_lifetime
FROM training.orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;
```

`PARTITION BY customer_id` restarts the sum for each customer. Because the window has no window-level `ORDER BY`, every row in the customer partition sees the full lifetime total.

## Exercise 2 — Product share of category revenue

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
  ROUND(revenue, 2) AS product_revenue,
  ROUND(
    SUM(revenue) OVER (PARTITION BY category),
    2
  ) AS category_revenue,
  ROUND(
    revenue
      / NULLIF(SUM(revenue) OVER (PARTITION BY category), 0),
    4
  ) AS category_revenue_share
FROM product_revenue
ORDER BY category, product_revenue DESC, product_id;
```

The CTE first establishes one row per product. The window denominator can then sum those product totals safely. The outer join preserves the 25 intentionally unsold products with zero revenue.

## Check yourself

- Exercise 1 keeps one row per order.
- Customer lifetime totals repeat only within the matching customer.
- Product shares within a category sum to approximately 1, allowing for displayed rounding.
