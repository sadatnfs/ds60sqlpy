# Day 15 solution — Phase 1 report project

This answer completes the deliverable in [Day 15](../day15_phase1_project.sql) by adding product category and a primary payment method to the existing month, segment, and country dimensions.

## Business rule for payment method

An order can have multiple payment rows and methods. To keep one payment dimension per order, this solution defines the primary method as the method with the largest total payment amount for that order. Ties use the method name for deterministic selection. Orders with no payment are labeled `unpaid`.

## Extended report

```sql
WITH order_dimensions AS (
  SELECT
    o.order_id,
    o.customer_id,
    DATE_TRUNC('month', o.order_date) AS order_month,
    COALESCE(
      (
        SELECT p.method
        FROM training.payments AS p
        WHERE p.order_id = o.order_id
        GROUP BY p.method
        ORDER BY SUM(p.amount) DESC, p.method
        LIMIT 1
      ),
      'unpaid'
    ) AS primary_payment_method
  FROM training.orders AS o
),
report_rows AS (
  SELECT
    od.order_id,
    od.customer_id,
    od.order_month,
    COALESCE(c.segment, 'standard') AS segment,
    c.country,
    p.category,
    od.primary_payment_method,
    oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM order_dimensions AS od
  JOIN training.customers AS c
    ON c.customer_id = od.customer_id
  JOIN training.order_items AS oi
    ON oi.order_id = od.order_id
  JOIN training.products AS p
    ON p.product_id = oi.product_id
)
SELECT
  order_month,
  segment,
  country,
  category,
  primary_payment_method,
  ROUND(SUM(line_revenue), 2) AS revenue,
  COUNT(DISTINCT order_id) AS orders,
  COUNT(DISTINCT customer_id) AS active_customers,
  ROUND(
    SUM(line_revenue) / NULLIF(COUNT(DISTINCT customer_id), 0),
    2
  ) AS revenue_per_active_customer
FROM report_rows
GROUP BY
  order_month,
  segment,
  country,
  category,
  primary_payment_method
ORDER BY order_month DESC, revenue DESC;
```

The correlated payment subquery returns at most one method per order before the query joins order items. This prevents a multi-payment order from multiplying its line revenue.

## Validate before interpreting

The report’s total revenue should reconcile to the discounted line total:

```sql
SELECT ROUND(
  SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
  2
) AS expected_total_revenue
FROM training.order_items AS oi;
```

After running the report, document evidence rather than guessing. Useful observations include:

- which category leads within a specific month and segment;
- whether `unpaid` revenue is concentrated in a country or category;
- whether revenue and active-customer count tell different stories.

If report revenue does not reconcile, check for fanout before drawing any business conclusion.
