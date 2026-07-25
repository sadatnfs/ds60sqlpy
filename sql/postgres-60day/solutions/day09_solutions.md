# Day 09 solutions — correlated subqueries and EXISTS

These answers match the exercises in [Day 09](../day09_correlated_subqueries.sql).

## Exercise 1 — Customers with an order over $1,000

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.country
FROM training.customers AS c
WHERE EXISTS (
  SELECT 1
  FROM training.orders AS o
  WHERE o.customer_id = c.customer_id
    AND o.total_amount > 1000
)
ORDER BY c.customer_id;
```

`EXISTS` asks whether at least one matching row exists. PostgreSQL does not need the inner query to return an order’s columns, so `SELECT 1` states the intent clearly.

## Exercise 2 — Products never purchased

```sql
SELECT
  p.product_id,
  p.name,
  p.category
FROM training.products AS p
WHERE NOT EXISTS (
  SELECT 1
  FROM training.order_items AS oi
  WHERE oi.product_id = p.product_id
)
ORDER BY p.product_id;
```

`NOT EXISTS` is null-safe because it checks row existence rather than comparing a value with a list. The clean seed deliberately leaves products 276–300 unpurchased.

## Check yourself

- Exercise 1 returns each qualifying customer once even if they have several large orders.
- Exercise 2 returns the same product IDs as the Day 04 outer-join solution.
- Do not replace `NOT EXISTS` with `NOT IN` unless you have proved the subquery cannot return `NULL`.
