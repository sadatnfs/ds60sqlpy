# Day 04 solutions — OUTER JOINs and unmatched rows

These answers match the exercises in [Day 04](../day04_outer_joins.sql). The course seed intentionally includes unpaid orders and unsold products so the unmatched cases are visible.

## Exercise 1 — Reconcile orders and payments

```sql
SELECT
  COALESCE(o.order_id, p.order_id) AS order_id,
  o.total_amount,
  p.payment_id,
  p.amount AS payment_amount,
  CASE
    WHEN o.order_id IS NULL THEN 'payment_without_order'
    WHEN p.order_id IS NULL THEN 'order_without_payment'
  END AS mismatch
FROM training.orders AS o
FULL OUTER JOIN training.payments AS p
  ON p.order_id = o.order_id
WHERE o.order_id IS NULL
   OR p.order_id IS NULL
ORDER BY order_id, p.payment_id;
```

`FULL OUTER JOIN` preserves unmatched rows from both sides. In the current schema, `payments.order_id` is a required foreign key, so a payment without an order should not exist. Orders without payments are valid and should appear.

## Exercise 2 — Find products never purchased

```sql
SELECT
  p.product_id,
  p.name,
  p.category
FROM training.products AS p
LEFT JOIN training.order_items AS oi
  ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL
ORDER BY p.product_id;
```

Test a non-nullable column from the optional side of the join. The seed deliberately leaves products 276–300 unsold, so this query has a visible result.

## Exercise 3 — Customers with no orders in the last 90 days

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.country
FROM training.customers AS c
LEFT JOIN training.orders AS o
  ON o.customer_id = c.customer_id
 AND o.order_date >= CURRENT_TIMESTAMP - INTERVAL '90 days'
WHERE o.order_id IS NULL
ORDER BY c.country, c.customer_id;
```

The date predicate belongs in `ON`. Putting it in `WHERE` would discard the null-extended rows and accidentally turn the outer join into an inner join. This result includes customers who never ordered and customers whose orders are all older than 90 days.

## Check yourself

- Exercise 1 should have no `payment_without_order` rows unless referential integrity was bypassed.
- Exercise 2 includes the intentionally unsold tail of the product catalog.
- Exercise 3 still includes unmatched customers.
