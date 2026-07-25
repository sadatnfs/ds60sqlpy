# Day 07 solutions — Week 1 report project

These answers extend the report in [Day 07](../day07_week1_project.sql). Both queries retain the lesson’s discounted line-revenue formula.

## Exercise 1 — Add payment method

An order can have several payment rows. This solution defines its primary method as the method with the largest total paid amount for that order, with method name as a deterministic tie-breaker.

```sql
WITH payment_by_method AS (
  SELECT
    p.order_id,
    p.method,
    SUM(p.amount) AS paid_amount
  FROM training.payments AS p
  GROUP BY p.order_id, p.method
),
ranked_payment AS (
  SELECT
    pbm.*,
    ROW_NUMBER() OVER (
      PARTITION BY pbm.order_id
      ORDER BY pbm.paid_amount DESC, pbm.method
    ) AS payment_rank
  FROM payment_by_method AS pbm
),
primary_payment AS (
  SELECT order_id, method
  FROM ranked_payment
  WHERE payment_rank = 1
),
line AS (
  SELECT
    o.customer_id,
    c.country,
    p.category,
    COALESCE(pp.method, 'unpaid') AS payment_method,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM training.orders AS o
  JOIN training.customers AS c
    ON c.customer_id = o.customer_id
  JOIN training.order_items AS oi
    ON oi.order_id = o.order_id
  JOIN training.products AS p
    ON p.product_id = oi.product_id
  LEFT JOIN primary_payment AS pp
    ON pp.order_id = o.order_id
  WHERE o.order_date >= CURRENT_TIMESTAMP - INTERVAL '90 days'
)
SELECT
  country,
  category,
  payment_method,
  ROUND(SUM(line_revenue), 2) AS revenue,
  COUNT(DISTINCT customer_id) AS buyers,
  ROUND(
    SUM(line_revenue) / NULLIF(COUNT(DISTINCT customer_id), 0),
    2
  ) AS revenue_per_buyer
FROM line
GROUP BY country, category, payment_method
ORDER BY revenue DESC, country, category, payment_method;
```

Pre-aggregating and ranking payments prevents payment rows from multiplying order-item revenue. Unpaid orders remain visible under the explicit `unpaid` label.

## Exercise 2 — Add customer cohort month

```sql
WITH line AS (
  SELECT
    o.customer_id,
    DATE_TRUNC('month', c.created_at) AS cohort_month,
    c.country,
    p.category,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM training.orders AS o
  JOIN training.customers AS c
    ON c.customer_id = o.customer_id
  JOIN training.order_items AS oi
    ON oi.order_id = o.order_id
  JOIN training.products AS p
    ON p.product_id = oi.product_id
  WHERE o.order_date >= CURRENT_TIMESTAMP - INTERVAL '90 days'
)
SELECT
  cohort_month,
  country,
  category,
  ROUND(SUM(line_revenue), 2) AS revenue,
  COUNT(DISTINCT customer_id) AS buyers,
  ROUND(
    SUM(line_revenue) / NULLIF(COUNT(DISTINCT customer_id), 0),
    2
  ) AS revenue_per_buyer
FROM line
GROUP BY cohort_month, country, category
ORDER BY cohort_month DESC, revenue DESC;
```

The cohort is based on customer creation month, not order month. A customer therefore stays in the same cohort across all later purchases.

## Validation ideas

- Sum the report revenue and compare it with the same 90-day line-revenue total without extra dimensions.
- Do not join raw `payments` directly to raw `order_items`; that creates a many-to-many fanout.
- Describe an observed pattern only after running the query. Do not invent numeric insights from the SQL text alone.
