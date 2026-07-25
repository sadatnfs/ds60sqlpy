# Day 56 Solutions — CUBE and Percentiles

The exercises add payment method to a multidimensional cube and calculate
category-attributable order-value percentiles by month. See
[`day56_solutions.sql`](day56_solutions.sql).

## Exercise 1 — Add payment method and measure cube growth

An order can have more than one payment. The answer defines its primary method
as the method with the greatest total paid amount, breaking ties by method name.
Reducing to one method prevents order lines from being duplicated; unpaid
orders remain visible.

```sql
SET search_path TO training, public;

WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS paid_amount
  FROM payments
  GROUP BY order_id, method
), ranked_payment AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY order_id ORDER BY paid_amount DESC, method
         ) AS payment_rank
  FROM payment_by_method
), primary_payment AS (
  SELECT order_id, method
  FROM ranked_payment
  WHERE payment_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(pp.method, 'unpaid') AS payment_method,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  LEFT JOIN primary_payment pp USING (order_id)
), cube_two AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
), cube_three AS (
  SELECT country, category, payment_method, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category, payment_method)
)
SELECT (SELECT COUNT(*) FROM cube_two) AS two_dimension_rows,
       (SELECT COUNT(*) FROM cube_three) AS three_dimension_rows;
```

Expected shape: one row; `three_dimension_rows` should be larger.

## Exercise 2 — Category-month p50 and p90

The metric is each category's contribution to an order, not the entire order
total repeated for every category.

```sql
SET search_path TO training, public;

WITH category_orders AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         p.category,
         o.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY date_trunc('month', o.order_date), p.category, o.order_id
)
SELECT month,
       category,
       ROUND(
         percentile_cont(0.50) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p50_order_value,
       ROUND(
         percentile_cont(0.90) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p90_order_value
FROM category_orders
GROUP BY month, category
ORDER BY month DESC, category;
```

Expected grain: one row per represented `(month, category)`.

## Reasoning, safety, and pitfalls

- Joining all payment rows to lines would multiply revenue for split-payment
  orders. Define a payment attribution policy before adding that dimension.
- Aggregate by `(order_id, method)` before ranking so split payments using the
  same method are compared by their total paid amount.
- The method-name tie-break makes the primary-method policy deterministic.
- `percentile_cont` interpolates and returns a floating type; cast to numeric
  before two-argument `ROUND`.
- Percentiles need enough observations. Always accompany production percentiles
  with sample counts.
