# Day 11 solutions — CASE expressions

These answers match the exercises in [Day 11](../day11_case_expressions.sql). The prompts do not prescribe tier thresholds, hour boundaries, or a time zone, so this solution states those business rules explicitly.

## Exercise 1 — Tier customers by lifetime revenue

This example defines:

- `platinum`: at least $10,000
- `gold`: at least $5,000
- `silver`: at least $1,000
- `bronze`: some revenue below $1,000
- `no_orders`: zero lifetime revenue

```sql
WITH customer_revenue AS (
  SELECT
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
  GROUP BY c.customer_id, c.full_name
)
SELECT
  customer_id,
  full_name,
  ROUND(lifetime_revenue, 2) AS lifetime_revenue,
  CASE
    WHEN lifetime_revenue >= 10000 THEN 'platinum'
    WHEN lifetime_revenue >= 5000 THEN 'gold'
    WHEN lifetime_revenue >= 1000 THEN 'silver'
    WHEN lifetime_revenue > 0 THEN 'bronze'
    ELSE 'no_orders'
  END AS revenue_tier
FROM customer_revenue
ORDER BY lifetime_revenue DESC, customer_id;
```

`CASE` uses the first matching branch, so thresholds must be tested from highest to lowest. The outer joins and `COALESCE` preserve customers without orders.

## Exercise 2 — Bucket order hour

This example interprets timestamps in UTC and defines morning as 06:00–11:59, afternoon as 12:00–16:59, evening as 17:00–21:59, and night as all other hours.

```sql
WITH order_hours AS (
  SELECT
    o.order_id,
    o.order_date,
    EXTRACT(
      HOUR FROM o.order_date AT TIME ZONE 'UTC'
    )::integer AS order_hour_utc
  FROM training.orders AS o
)
SELECT
  order_id,
  order_date,
  order_hour_utc,
  CASE
    WHEN order_hour_utc >= 6 AND order_hour_utc < 12 THEN 'morning'
    WHEN order_hour_utc >= 12 AND order_hour_utc < 17 THEN 'afternoon'
    WHEN order_hour_utc >= 17 AND order_hour_utc < 22 THEN 'evening'
    ELSE 'night'
  END AS day_part
FROM order_hours
ORDER BY order_date, order_id;
```

Using an explicit time zone makes the result independent of the database session’s local time-zone setting.

## Check yourself

- Every customer receives exactly one tier.
- Customers with no orders are not silently lost.
- Every integer hour from 0 through 23 maps to exactly one day part.
