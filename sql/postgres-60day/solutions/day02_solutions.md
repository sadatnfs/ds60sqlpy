# Day 02 solutions — aggregates, GROUP BY, and HAVING

These answers match the exercises in [Day 02](../day02_aggregates_groupby_having.sql). Every selected non-aggregate column appears in `GROUP BY`.

## Exercise 1 — Total payments by method

```sql
SELECT
  p.method,
  ROUND(SUM(p.amount), 2) AS total_payments
FROM training.payments AS p
GROUP BY p.method
HAVING SUM(p.amount) > 1000000
ORDER BY total_payments DESC, p.method;
```

`WHERE` filters input rows before grouping. `HAVING` filters the completed groups, so it is the correct place for the `SUM(...) > 1000000` condition.

## Exercise 2 — Average customer age in the system by country

```sql
SELECT
  c.country,
  COUNT(*) AS customers,
  AVG(CURRENT_TIMESTAMP - c.created_at) AS average_time_as_customer
FROM training.customers AS c
GROUP BY c.country
ORDER BY c.country;
```

Subtracting a timestamp from `CURRENT_TIMESTAMP` produces an interval. PostgreSQL can average intervals directly, which keeps the result readable as elapsed time.

## Exercise 3 — Top five categories by gross margin

```sql
SELECT
  p.category,
  ROUND(SUM((p.price - p.cost) * oi.quantity), 2) AS gross_margin
FROM training.order_items AS oi
JOIN training.products AS p
  ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY gross_margin DESC, p.category
LIMIT 5;
```

The exercise defines gross margin as `(price - cost) * quantity`, so the solution follows that formula exactly. It does not subtract the order-item discount; that would answer a different net-margin question.

## Check yourself

- Exercise 1 has at most one row per payment method.
- Exercise 2 has one row per country.
- Exercise 3 has at most five rows and is ordered by the calculated margin.
