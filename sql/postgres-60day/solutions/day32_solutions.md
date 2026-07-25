# Day 32 — Solutions: Index Fundamentals

Indexes trade storage and write cost for faster access to selected rows. Both
answers run inside a transaction and roll back, so rerunning the document does
not leave demonstration indexes behind.

## Exercise 1 — Index `products(category)` and test a filter

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_solution;
CREATE INDEX idx_products_category_solution
  ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id,
       name,
       price
FROM products
WHERE category = 'Electronics';

ROLLBACK;
```

Expected plan shape is not guaranteed. The seeded `products` table has only a
few hundred rows and each category is common, so a sequential scan can be
cheaper even though the index is valid.

## Exercise 2 — Compare without, with, and after dropping the index

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_compare;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

CREATE INDEX idx_products_category_compare
  ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

DROP INDEX idx_products_category_compare;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id
FROM products
WHERE category = 'Electronics';

ROLLBACK;
```

Record node type, estimated rows, actual rows, planning time, execution time,
and buffers for each plan. On this small dataset, “no visible plan change” is a
valid observation, not a failed exercise.

## Pitfalls

- Do not use `SET enable_seqscan = off` as proof that an index is useful; it
  changes the planner's choices instead of demonstrating normal behavior.
- A B-tree handles equality and ordered range predicates, so a hash index is
  rarely needed for a basic equality lookup.
- Index names share a schema namespace, which is why the solution uses unique,
  exercise-specific names.
- Indexes created in the learner script are rolled back at the end of that
  script and are not available on later days.
