# Day 06 solutions — set operations

These answers match the exercises in [Day 06](../day06_set_operations.sql). Each side of a set operation returns the same number of columns with compatible types.

## Exercise 1 — Products in both orders and promotions

```sql
WITH matching_product_ids AS (
  SELECT oi.product_id
  FROM training.order_items AS oi
  INTERSECT
  SELECT pr.product_id
  FROM training.promotions AS pr
)
SELECT
  p.product_id,
  p.name,
  p.category
FROM matching_product_ids AS m
JOIN training.products AS p
  ON p.product_id = m.product_id
ORDER BY p.product_id;
```

`INTERSECT` removes duplicates and retains only product IDs present in both inputs.

## Exercise 2 — Countries with customers but no orders

```sql
WITH countries_without_orders AS (
  SELECT c.country
  FROM training.customers AS c
  EXCEPT
  SELECT c.country
  FROM training.customers AS c
  JOIN training.orders AS o
    ON o.customer_id = c.customer_id
)
SELECT country
FROM countries_without_orders
ORDER BY country;
```

The first set is every customer country. The second set is countries represented by an order. `EXCEPT` subtracts the second from the first; the current seed intentionally makes `BR` an event-only market.

## Exercise 3 — Compare UNION with UNION ALL

The learner prompt permits any two filtered order sets. This example uses recent orders and high-value orders so some orders can appear in both.

```sql
WITH recent_orders AS (
  SELECT o.order_id
  FROM training.orders AS o
  WHERE o.order_date >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
high_value_orders AS (
  SELECT o.order_id
  FROM training.orders AS o
  WHERE o.total_amount >= 500
),
union_rows AS (
  SELECT order_id FROM recent_orders
  UNION
  SELECT order_id FROM high_value_orders
),
union_all_rows AS (
  SELECT order_id FROM recent_orders
  UNION ALL
  SELECT order_id FROM high_value_orders
)
SELECT 'UNION' AS operation, COUNT(*) AS rows_returned
FROM union_rows
UNION ALL
SELECT 'UNION ALL', COUNT(*)
FROM union_all_rows
ORDER BY operation;
```

`UNION` deduplicates the overlap. `UNION ALL` keeps both copies and is normally faster because it does not perform that deduplication.

## Check yourself

- Exercise 1 contains no product that is missing from either source.
- Exercise 2 returns the intentionally order-free country from a clean seed.
- The `UNION ALL` count is greater than or equal to the `UNION` count.
