# Day 13 solutions — date and time functions

These answers match the exercises in [Day 13](../day13_date_time_functions.sql).

## Exercise 1 — Compute the quarter for each order

The prompt says “fiscal quarter” but does not define when the fiscal year starts. This answer assumes the fiscal year follows the calendar year and evaluates the timestamp in UTC.

```sql
WITH order_calendar AS (
  SELECT
    o.order_id,
    o.order_date,
    o.order_date AT TIME ZONE 'UTC' AS order_time_utc
  FROM training.orders AS o
)
SELECT
  order_id,
  order_date,
  EXTRACT(YEAR FROM order_time_utc)::integer AS fiscal_year,
  EXTRACT(QUARTER FROM order_time_utc)::integer AS fiscal_quarter
FROM order_calendar
ORDER BY order_date, order_id;
```

For a fiscal year starting in another month, define that start month before writing the query; shifting dates without a stated rule can label both the quarter and fiscal year incorrectly.

## Exercise 2 — Days since each customer’s last order

```sql
SELECT
  c.customer_id,
  c.full_name,
  MAX(o.order_date) AS last_order_at,
  CURRENT_DATE
    - MAX((o.order_date AT TIME ZONE 'UTC')::date) AS days_since_last_order
FROM training.customers AS c
LEFT JOIN training.orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY days_since_last_order DESC NULLS LAST, c.customer_id;
```

`MAX` finds each customer’s most recent order. Customers without orders remain present; both last-order columns are `NULL` because “days since” is undefined for them.

## Check yourself

- Calendar months 1–3 map to quarter 1, 4–6 to quarter 2, and so on.
- Exercise 2 returns one row per customer.
- Do not replace a missing last order with zero days; that would falsely mean the customer ordered today.
