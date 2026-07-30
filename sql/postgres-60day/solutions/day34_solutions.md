# Day 34 — Solutions: Query Optimization Techniques

Optimization must preserve meaning. Compare plans only after confirming that
the original and rewritten queries return the same rows at the same grain.

## Exercise 1 — Replace a subquery with a join

The first query uses `EXISTS`; the second uses joins. `DISTINCT` is necessary in
the join form because one order can contain multiple Electronics lines.

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_id,
       o.order_date
FROM orders o
WHERE EXISTS (
  SELECT 1
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  WHERE oi.order_id = o.order_id
    AND p.category = 'Electronics'
);

EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT o.order_id,
       o.order_date
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE p.category = 'Electronics';
```

PostgreSQL may already transform `EXISTS` into a semi-join, so the explicit join
is not automatically faster. Compare final row counts as well as cost and time.

## Exercise 2 — Limit rows before enrichment

Both forms request the latest 100 orders with customer country. The second form
makes the bounded order set explicit before the dimension join.

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_id,
       o.order_date,
       c.country
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 100;

EXPLAIN (ANALYZE, BUFFERS)
WITH top_orders AS MATERIALIZED (
  SELECT order_id,
         customer_id,
         order_date
  FROM orders
  ORDER BY order_date DESC, order_id DESC
  LIMIT 100
)
SELECT t.order_id,
       t.order_date,
       c.country
FROM top_orders t
JOIN customers c ON c.customer_id = t.customer_id
ORDER BY t.order_date DESC, t.order_id DESC;
```

Expected shape for either actual query: 100 rows when at least 100 orders exist.
`MATERIALIZED` is used here to make the learning contrast visible; in ordinary
code, allow PostgreSQL to inline a CTE unless an optimization fence is needed.

## Pitfalls

- A join can multiply rows. Never remove `EXISTS` without checking the
  relationship cardinality.
- “Filter early” is not a rule to duplicate everywhere; PostgreSQL can push
  many predicates itself.
- An early `LIMIT` is valid only when it selects the same ordered set the final
  query requires.
- Faster on one tiny seeded database is not sufficient evidence for a
  production rewrite.

## Exercise 3 — Compare CTE planner boundaries

`MATERIALIZED` computes/stores the CTE as a boundary. `NOT MATERIALIZED` permits
folding into the parent query. Compare plans; neither spelling is universally
faster.

## Exercise 4 — Pre-aggregate to order grain

`item_totals` emits one row per order before customer/country joins. This
reduces fanout while preserving the unit total.

## Exercise 5 — Repair two-many-side fanout

Payments and items are independently many-to-one with orders. Each is grouped
by `order_id` before their results are joined, so amounts are never multiplied.

## Exercise 6 — Write a NULL-safe anti-join

`NOT EXISTS` asks whether a matching order exists for the current customer.
Unlike nullable `NOT IN`, one NULL produced by the inner relation cannot turn
every comparison into UNKNOWN.
