# Day 08 solutions — scalar and inline subqueries

These answers match the exercises in [Day 08](../day08_scalar_inline_subqueries.sql).

## Exercise 1 — Largest single order amount by country

```sql
SELECT
  countries.country,
  (
    SELECT MAX(o.total_amount)
    FROM training.orders AS o
    JOIN training.customers AS c
      ON c.customer_id = o.customer_id
    WHERE c.country = countries.country
  ) AS largest_order_amount
FROM (
  SELECT DISTINCT country
  FROM training.customers
) AS countries
ORDER BY countries.country;
```

The inner query is scalar: it returns one aggregate value for the current outer country. A country with no orders remains in the result with `NULL` as its largest order.

## Exercise 2 — First order date for every customer

```sql
SELECT
  c.customer_id,
  c.full_name,
  (
    SELECT MIN(o.order_date)
    FROM training.orders AS o
    WHERE o.customer_id = c.customer_id
  ) AS first_order_date
FROM training.customers AS c
ORDER BY c.customer_id;
```

The correlated subquery uses the outer row’s `customer_id`. `MIN` guarantees at most one scalar value, and customers without orders receive `NULL`.

## Check yourself

- Exercise 1 returns one row for every distinct customer country.
- Exercise 2 returns one row for every customer, including the intentionally order-free customers.
- Removing the correlation predicate from either query would calculate one global value and repeat it incorrectly.
