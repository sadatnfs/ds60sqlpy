# Day 03 solutions — INNER JOINs

These answers match the exercises in [Day 03](../day03_inner_joins.sql). The join keys preserve the intended grain of each result.

## Exercise 1 — Top 20 customers by revenue

```sql
SELECT
  c.customer_id,
  c.full_name,
  ROUND(
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
    2
  ) AS total_revenue
FROM training.customers AS c
JOIN training.orders AS o
  ON o.customer_id = c.customer_id
JOIN training.order_items AS oi
  ON oi.order_id = o.order_id
GROUP BY c.customer_id, c.full_name
ORDER BY total_revenue DESC, c.customer_id
LIMIT 20;
```

The join reaches the line-item grain, so revenue uses the discounted line formula. Grouping by customer collapses those lines back to one row per customer.

## Exercise 2 — Last 100 paid orders with payment methods

This answer interprets “paid orders” as rows whose course status is exactly `paid`. A different business definition—such as any order with a payment—would require a different predicate.

```sql
WITH latest_paid_orders AS (
  SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.total_amount
  FROM training.orders AS o
  WHERE o.status = 'paid'
  ORDER BY o.order_date DESC, o.order_id DESC
  LIMIT 100
),
payment_summary AS (
  SELECT
    p.order_id,
    STRING_AGG(DISTINCT p.method, ', ' ORDER BY p.method) AS payment_methods,
    SUM(p.amount) AS amount_paid
  FROM training.payments AS p
  JOIN latest_paid_orders AS lpo
    ON lpo.order_id = p.order_id
  GROUP BY p.order_id
)
SELECT
  lpo.order_id,
  lpo.customer_id,
  lpo.order_date,
  lpo.total_amount,
  ps.payment_methods,
  ROUND(ps.amount_paid, 2) AS amount_paid
FROM latest_paid_orders AS lpo
LEFT JOIN payment_summary AS ps
  ON ps.order_id = lpo.order_id
ORDER BY lpo.order_date DESC, lpo.order_id DESC;
```

An order can have more than one payment row. Aggregating payments before the final join preserves one output row per order; joining raw payments and then applying `LIMIT 100` would limit payment rows instead.

## Exercise 3 — Employees and their managers by department

```sql
SELECT
  d.name AS department,
  e.employee_id,
  e.full_name AS employee,
  m.full_name AS manager
FROM training.departments AS d
JOIN training.employees AS e
  ON e.department_id = d.department_id
LEFT JOIN training.employees AS m
  ON m.employee_id = e.manager_id
ORDER BY d.name, e.full_name, e.employee_id;
```

The second reference to `employees` is a self-join. It is a `LEFT JOIN` because top-level employees have no manager and should remain visible with a `NULL` manager.

## Check yourself

- Exercise 1 returns no more than 20 customers.
- Exercise 2 returns no more than 100 orders, even when an order has multiple payments.
- Exercise 3 retains employees whose `manager_id` is `NULL`.
