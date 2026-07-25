# Day 31 — Solutions: `EXPLAIN` and `EXPLAIN ANALYZE`

Execution plans are observations, not fixed expected text. PostgreSQL may choose
different nodes after a version change, data refresh, or statistics update.
Compare estimates, actuals, buffers, and timing rather than memorizing one plan.

## Exercise 1 — Change predicates and observe selectivity

These three queries ask for progressively smaller portions of `orders`.

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, total_amount
FROM orders;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, total_amount
FROM orders
WHERE total_amount > 500;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, total_amount
FROM orders
WHERE total_amount > 500
  AND order_date >= CURRENT_TIMESTAMP - interval '30 days';
```

Compare `rows=` on each plan node and the top-level actual row count. A more
selective predicate returns fewer rows, but it does not guarantee an index scan:
the setup table is small and PostgreSQL can reasonably prefer a sequential
scan.

## Exercise 2 — Compare estimated and actual rows

`EXPLAIN` plans but does not run the `SELECT`; `EXPLAIN ANALYZE` executes it and
adds actual timing, loops, and row counts.

```sql
SET search_path TO training, public;

EXPLAIN
SELECT c.country,
       SUM(oi.quantity) AS units
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
GROUP BY c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.country,
       SUM(oi.quantity) AS units
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
GROUP BY c.country;
```

For each node, compare estimated `rows` with `actual ... rows`. Large,
repeatable discrepancies can indicate stale statistics or correlated columns
that ordinary statistics do not model well.

## Pitfalls

- `EXPLAIN ANALYZE` really executes the statement. Use `BEGIN`/`ROLLBACK` when
  analyzing writes and never assume it is harmless in production.
- One timing run includes cache and system noise. Repeat measurements and use
  representative parameters.
- Planning cost units are not milliseconds. Actual time is shown separately.
- A sequential scan is often correct for a small table or a low-selectivity
  predicate.
