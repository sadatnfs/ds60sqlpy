# Day 35 — Solutions: Avoiding Performance Pitfalls

This learner day asks for three rewrites that keep functions off an indexed
column and one rewrite of a correlated subquery. The examples use half-open
timestamp ranges because they are precise and B-tree friendly.

## Exercise 1 — Three sargable predicate rewrites

Each “better” predicate leaves `order_date` bare, allowing an index on that
column to define a contiguous range.

```sql
SET search_path TO training, public;

-- 1. One calendar day
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE date_trunc('day', order_date) = date_trunc('day', CURRENT_TIMESTAMP);

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('day', CURRENT_TIMESTAMP)
  AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day';

-- 2. Current calendar year
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE EXTRACT(year FROM order_date) = EXTRACT(year FROM CURRENT_DATE);

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('year', CURRENT_DATE)
  AND order_date < date_trunc('year', CURRENT_DATE) + interval '1 year';

-- 3. Last seven calendar dates, including today
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date::date >= CURRENT_DATE - 6;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= (CURRENT_DATE - 6)::timestamptz
  AND order_date < (CURRENT_DATE + 1)::timestamptz;
```

Expected result sets within each pair are equivalent under the session time
zone. Plan nodes can remain sequential scans because the dataset is small or
because the demonstration index from Day 32 was rolled back.

## Exercise 2 — Replace a per-customer correlated aggregate

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id,
       (
         SELECT SUM(o.total_amount)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS lifetime_revenue
FROM customers c;

EXPLAIN (ANALYZE, BUFFERS)
WITH order_totals AS (
  SELECT customer_id,
         SUM(total_amount) AS lifetime_revenue
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id,
       ot.lifetime_revenue
FROM customers c
LEFT JOIN order_totals ot ON ot.customer_id = c.customer_id;
```

Expected shape: one row per customer in both forms. The `LEFT JOIN` is required
to retain customers with no orders; changing it to an inner join would alter
the answer.

## Pitfalls

- Sargability does not guarantee an index scan; it merely gives the planner the
  option.
- Timestamp-to-date conversion uses the session time zone. Define business
  timezone semantics before reporting calendar periods.
- PostgreSQL can decorrelate some subqueries. Confirm the plan instead of
  assuming every correlated expression runs once per outer row.
- Do not hide fanout with `DISTINCT`; fix the join grain.

## Exercise 3 — Diagnose wildcard search

`LIKE 'A%'` has a fixed starting prefix; `LIKE '%A%'` does not. A normal B-tree
therefore has a more direct opportunity on the first pattern, subject to
collation/operator-class details.

## Exercise 4 — Replace OFFSET with a seek tuple

The boundary tuple comes from `(order_date DESC, order_id DESC)`. The next page
uses the matching tuple comparison and repeats that deterministic order.

## Exercise 5 — Fix payment/item fanout

The answer groups each many-side by `order_id` before joining. `DISTINCT` would
only conceal duplicated output, not repair multiplied sums.

## Exercise 6 — Define nullable counts

`COUNT(*)` measures customer rows; `COUNT(email)` measures customers with a
non-NULL email. The difference is a useful missingness count, not a discrepancy.
