# Day 45 Solution — Performance Optimization Project

The deliverable is evidence, not merely a rewritten query: capture a baseline,
add plausible indexes, use a sargable predicate and set-based aggregation, then
compare actual plans. The executable project answer is
[`day45_solutions.sql`](day45_solutions.sql).

## Baseline and optimized candidate

```sql
BEGIN;
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.country,
       SUM((
         SELECT SUM(oi.quantity)
         FROM order_items oi
         WHERE oi.order_id = o.order_id
       )) AS units
FROM orders o
JOIN customers c USING (customer_id)
WHERE o.order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY c.country;

CREATE INDEX idx_orders_recent_customer_solution
  ON orders(order_date, customer_id, order_id);
CREATE INDEX idx_order_items_order_quantity_solution
  ON order_items(order_id) INCLUDE (quantity);

EXPLAIN (ANALYZE, BUFFERS)
WITH recent_orders AS (
  SELECT order_id, customer_id
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
), item_totals AS (
  SELECT oi.order_id, SUM(oi.quantity) AS units
  FROM order_items oi
  JOIN recent_orders ro USING (order_id)
  GROUP BY oi.order_id
)
SELECT c.country, SUM(it.units) AS units
FROM recent_orders ro
JOIN item_totals it USING (order_id)
JOIN customers c USING (customer_id)
GROUP BY c.country
ORDER BY units DESC;

ROLLBACK;
```

Both statements should return the same country-to-units result. Compare:

- `Execution Time`;
- shared buffer hits and reads;
- row estimates versus actual rows;
- correlated-subquery loops in the baseline; and
- scan and join choices after the indexes are present.

## The 70% target

The learner file sets a goal of reducing runtime by more than 70%. That is a
measurement target, not a guaranteed outcome on the compact seed. Small tables
often favor sequential scans, and planning overhead can dominate. Record both
plans and calculate:

```text
improvement_pct = 100 * (baseline_ms - optimized_ms) / baseline_ms
```

If the target is not met, report the observed result honestly and test at a
representative scale before changing production design.

## Reasoning, safety, and pitfalls

- The date predicate compares the raw indexed column to a boundary, so it is
  sargable.
- Pre-aggregation reduces line items to one row per recent order before the
  country rollup.
- `INCLUDE (quantity)` can enable an index-only access path, but only when the
  planner considers it cheaper and visibility-map state permits it.
- The transaction rolls back course-owned indexes. Production index creation
  requires separate change planning and may need `CREATE INDEX CONCURRENTLY`.
- Always reconcile the result values before accepting a faster plan.

## Exercise 1 — Make the timestamp predicate sargable

The direct half-open range leaves `order_date` unwrapped, making the B-tree
eligible while preserving a clear time boundary.

## Exercise 2 — Capture structured evidence

`FORMAT JSON` keeps plan nodes, estimates, actual rows, buffers, and timing
machine-readable. It still describes only this run and environment.

## Exercise 3 — Prove semantic equivalence

Direct and pre-aggregated country totals are compared with `EXCEPT` in both
directions. Both difference sets must be empty before performance matters.

## Exercise 4 — Test the empty-window boundary

An impossible historical window should return no rows for every equivalent
shape. An optimization must not manufacture a zero-valued group.

## Exercise 5 — Document index tradeoffs

The candidate serves date-bounded customer work but consumes storage and makes
writes more expensive. Production creation needs a reviewed migration.

## Exercise 6 — Write the decision record

Report correctness, plan evidence, observed timing, operational cost, and limits
as separate claims. The compact seed cannot support a universal speed promise.
