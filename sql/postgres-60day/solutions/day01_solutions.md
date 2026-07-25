# Day 01 solutions — SELECT, WHERE, ORDER BY, and LIMIT

These answers match the exercises in [Day 01](../day01_select_where_orderby.sql). Try each exercise before reading its solution. The queries are read-only and use fully qualified `training` table names.

## Exercise 1 — List the 20 newest orders

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount,
  o.order_date
FROM training.orders AS o
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 20;
```

`ORDER BY` happens before `LIMIT`, so PostgreSQL sorts the complete result before keeping 20 rows. The `order_id` tie-breaker makes the result deterministic when two timestamps match.

## Exercise 2 — Find the 10 most expensive recently created products

```sql
SELECT
  p.product_id,
  p.name,
  p.category,
  p.price,
  p.created_at
FROM training.products AS p
WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
ORDER BY p.price DESC, p.product_id
LIMIT 10;
```

The date predicate keeps only the last 90 days. The price sort then finds the most expensive products inside that filtered set.

## Exercise 3 — Find recent GB or DE customers

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  c.created_at
FROM training.customers AS c
WHERE c.country IN ('GB', 'DE')
  AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'
ORDER BY c.created_at DESC, c.customer_id;
```

`IN` is a concise form of `country = 'GB' OR country = 'DE'`. Keep the date condition joined with `AND`; otherwise older rows from one country can slip into the result.

## Check yourself

- Exercise 1 returns at most 20 rows in newest-first order.
- Exercise 2 never returns a product older than 90 days.
- Exercise 3 contains only `GB` and `DE`.
