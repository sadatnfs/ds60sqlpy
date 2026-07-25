# Day 33 — Solutions: Composite and Partial Indexes

Composite indexes are most useful when their leading columns match common
filter or ordering patterns. Partial indexes contain only rows satisfying an
immutable predicate.

## Exercise 1 — Composite index on `(category, created_at)`

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_created_solution;
CREATE INDEX idx_products_category_created_solution
  ON products(category, created_at);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id,
       name,
       created_at
FROM products
WHERE category = 'Electronics'
  AND created_at >= CURRENT_TIMESTAMP - interval '6 years'
ORDER BY created_at DESC;

ROLLBACK;
```

The equality condition on the leading `category` column lets the B-tree narrow
the search before applying the `created_at` range and can also support the
requested order. A predicate on `created_at` alone cannot use the leftmost
`category` key as efficiently.

## Exercise 2 — Partial index for high-value orders

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_orders_high_value_solution;
CREATE INDEX idx_orders_high_value_solution
  ON orders(total_amount, order_date)
  WHERE total_amount > 1000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id,
       total_amount,
       order_date
FROM orders
WHERE total_amount > 1000
  AND order_date >= CURRENT_TIMESTAMP - interval '365 days'
ORDER BY total_amount DESC;

ROLLBACK;
```

The query repeats the partial predicate in a form the planner can prove implies
the index condition. The index excludes lower-value orders, reducing its size.

## Pitfalls

- Partial-index predicates cannot contain volatile or merely stable expressions
  such as `CURRENT_TIMESTAMP - interval '90 days'`. A fixed business condition
  such as `total_amount > 1000` is valid.
- A logically similar parameterized predicate may not be provably compatible
  with a partial index at planning time.
- Column order matters in a composite B-tree. Design it for real query shapes,
  not simply for every column mentioned by a query.
- Small course tables may still receive sequential scans. Judge the design and
  inspect the plan; do not force a node type.
