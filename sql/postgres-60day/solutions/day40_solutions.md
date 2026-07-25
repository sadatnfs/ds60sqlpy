# Day 40 — Solutions: Advanced Analytic Functions

This day combines statistical aggregates with windows and ordered-set
aggregates. The answers define the input grain before computing statistics.

## Exercise 1 — Fifteen-row rolling z-score for daily revenue

```sql
SET search_path TO training, public;

WITH daily AS (
  SELECT date_trunc('day', order_date)::date AS order_day,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('day', order_date)
), rolling AS (
  SELECT order_day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY order_day
           ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS avg15,
         STDDEV_SAMP(revenue) OVER (
           ORDER BY order_day
           ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS sd15
  FROM daily
)
SELECT order_day,
       ROUND(revenue, 2) AS revenue,
       ROUND(avg15, 2) AS avg15,
       ROUND(sd15, 2) AS sd15,
       ROUND(
         (revenue - avg15) / NULLIF(sd15, 0),
         4
       ) AS z_score
FROM rolling
ORDER BY order_day;
```

Expected shape: one row per day with orders. A positive z-score is above the
rolling mean; a negative score is below it. The first row has no sample standard
deviation, and any zero-standard-deviation frame yields `NULL`.

Assumption: “15-day” in the learner example means 15 observed daily rows. To
model 15 consecutive calendar days, first join revenue to a dense date series
and decide whether missing days mean zero or unknown.

## Exercise 2 — Category P50 and P90 of order values

An order can contain several categories. This answer defines an “order total
within a category” as the sum of that category's net lines in that order; using
the whole order total for every category would double-count mixed orders.

```sql
SET search_path TO training, public;

WITH category_order_values AS (
  SELECT p.category,
         oi.order_id,
         SUM(
           oi.unit_price * oi.quantity * (1 - oi.discount)
         ) AS category_order_value
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.order_id
)
SELECT category,
       ROUND(
         PERCENTILE_CONT(0.5) WITHIN GROUP (
           ORDER BY category_order_value
         )::numeric,
         2
       ) AS p50_order_value,
       ROUND(
         PERCENTILE_CONT(0.9) WITHIN GROUP (
           ORDER BY category_order_value
         )::numeric,
         2
       ) AS p90_order_value,
       COUNT(*) AS category_orders
FROM category_order_values
GROUP BY category
ORDER BY category;
```

Expected shape: one row per sold category. `PERCENTILE_CONT` can interpolate
between observed values, so a percentile need not equal an actual order value.

## Pitfalls

- `STDDEV_SAMP` is `NULL` for a one-row frame. `NULLIF(sd15, 0)` also protects
  constant frames from division by zero.
- A `ROWS` frame counts rows, not elapsed time.
- Ordered-set aggregates such as `PERCENTILE_CONT` use `WITHIN GROUP`; they are
  not written with `OVER` in this grouped query.
- Define the analytical grain before calculating a percentile. Line-level and
  order-level percentiles answer different questions.
