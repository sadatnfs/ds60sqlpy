# Day 19 solutions — running aggregates

These answers match the exercises in [Day 19](../day19_running_aggregates.sql). Both solutions aggregate to the intended grain before applying a window.

## Exercise 1 — 30-day moving revenue sum and average

The dense calendar gives every calendar day one row, including zero-revenue days. A `ROWS` frame of the current row plus 29 predecessors therefore represents 30 calendar days.

```sql
WITH daily_revenue AS (
  SELECT
    (o.order_date AT TIME ZONE 'UTC')::date AS order_day,
    SUM(o.total_amount) AS revenue
  FROM training.orders AS o
  GROUP BY (o.order_date AT TIME ZONE 'UTC')::date
),
day_bounds AS (
  SELECT
    MIN(order_day) AS first_day,
    MAX(order_day) AS last_day
  FROM daily_revenue
),
calendar AS (
  SELECT generated_day::date AS order_day
  FROM day_bounds AS db
  CROSS JOIN LATERAL GENERATE_SERIES(
    db.first_day,
    db.last_day,
    INTERVAL '1 day'
  ) AS g(generated_day)
),
dense_daily_revenue AS (
  SELECT
    c.order_day,
    COALESCE(dr.revenue, 0) AS revenue
  FROM calendar AS c
  LEFT JOIN daily_revenue AS dr
    ON dr.order_day = c.order_day
)
SELECT
  order_day,
  ROUND(revenue, 2) AS daily_revenue,
  ROUND(
    SUM(revenue) OVER (
      ORDER BY order_day
      ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ),
    2
  ) AS moving_30_day_sum,
  ROUND(
    AVG(revenue) OVER (
      ORDER BY order_day
      ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ),
    2
  ) AS moving_30_day_average
FROM dense_daily_revenue
ORDER BY order_day;
```

The first 29 rows use a shorter partial window because fewer than 30 historical days exist in the result.

## Exercise 2 — Cumulative product quantity within category

```sql
WITH product_daily_quantity AS (
  SELECT
    p.category,
    p.product_id,
    p.name,
    (o.order_date AT TIME ZONE 'UTC')::date AS order_day,
    SUM(oi.quantity) AS daily_quantity
  FROM training.order_items AS oi
  JOIN training.orders AS o
    ON o.order_id = oi.order_id
  JOIN training.products AS p
    ON p.product_id = oi.product_id
  GROUP BY
    p.category,
    p.product_id,
    p.name,
    (o.order_date AT TIME ZONE 'UTC')::date
)
SELECT
  category,
  product_id,
  name,
  order_day,
  daily_quantity,
  SUM(daily_quantity) OVER (
    PARTITION BY category, product_id
    ORDER BY order_day
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_quantity
FROM product_daily_quantity
ORDER BY category, product_id, order_day;
```

The partition includes both category and product, so each product’s cumulative total restarts independently inside its category. Daily pre-aggregation prevents multiple same-day order items from creating ambiguous peer rows.

## Check yourself

- The 30-day moving sum is never less than the current day’s nonnegative revenue.
- Cumulative quantity never decreases.
- Each product’s first cumulative value equals its first daily quantity.
