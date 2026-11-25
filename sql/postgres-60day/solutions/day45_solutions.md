# Day 45 Solution: Performance Optimization Project


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day45_solutions.sql
```

The `.sql` file runs in one transaction and rolls back both indexes it
creates. In order, it prints the baseline plan, two `CREATE INDEX` tags, the
optimized plan, the Exercise 1 plan, a single JSON plan row for Exercise 2, an
empty Exercise 3 result, Exercise 4's lone 0 and Exercise 5's two index rows. Exercise 6 is a comment, not a query. The baseline is the slow statement,
around half a second on our run. The general routine is in
[reading a solution](../../STUDY-GUIDE.md#read-a-solution).

## Clause-by-clause reading map

Read each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
The project has two layers. The first is a before-and-after pair: a baseline
that totals `order_items.quantity` through a correlated subquery, once per
recent order, and an optimized query that filters `orders` in a
`recent_orders` CTE, totals items per recent order in `item_totals` and joins
both to `customers`. The second layer, Exercises 1 to 5, isolates one claim
each: the sargable range, structured plan output, equal results, the empty
window and the index inventory. For every plan, note the scan on `orders`,
the scan on `order_items`, the loop counts and the buffer totals before
looking at time.

The deliverable is evidence, not merely a rewritten query: capture a baseline,
add plausible indexes, use a sargable predicate and set-based aggregation, then
compare actual plans. The executable project answer is
[`day45_solutions.sql`](day45_solutions.sql).

## Baseline and optimized candidate

```sql
BEGIN;
SET search_path TO training, public;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  c.country,
  SUM((
    SELECT
      SUM(oi.quantity)
    FROM order_items oi
    WHERE
      oi.order_id = o.order_id)) AS units
FROM
  orders o
  JOIN customers c USING (customer_id)
WHERE
  o.order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY
  c.country;

CREATE INDEX idx_orders_recent_customer_solution ON orders (order_date, customer_id, order_id);

CREATE INDEX idx_order_items_order_quantity_solution ON order_items (order_id) INCLUDE (quantity);

EXPLAIN (
  ANALYZE,
  BUFFERS
) WITH recent_orders AS (
  SELECT
    order_id,
    customer_id
  FROM
    orders
  WHERE
    order_date >= CURRENT_TIMESTAMP - interval '180 days'), item_totals AS (
    SELECT
      oi.order_id,
      SUM(oi.quantity) AS units
    FROM
      order_items oi
      JOIN recent_orders ro USING (order_id)
    GROUP BY
      oi.order_id
)
  SELECT
    c.country,
    SUM(it.units) AS units
FROM
  recent_orders ro
  JOIN item_totals it USING (order_id)
  JOIN customers c USING (customer_id)
GROUP BY
  c.country
ORDER BY
  units DESC;

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

## Exercise 1: Make the timestamp predicate sargable

The direct half-open range leaves `order_date` unwrapped, making the B-tree
eligible while preserving a clear time boundary.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 1, compare the learner baseline predicate `date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')` with the half-open range `order_date >= date_trunc('day', CURRENT_TIMESTAMP) - interval '180 days' AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day'` on `orders`, reading each through `EXPLAIN (ANALYZE, BUFFERS)` after the solution indexes are built.
- **Expected result/shape:** For sql-45 Exercise 1, expected output: a text plan, not rows. With `idx_orders_recent_customer_solution` on (`order_date`, `customer_id`, `order_id`) in place, the half-open range becomes an `Index Only Scan` with an `Index Cond` on both `order_date` bounds, while the wrapped baseline stays a `Seq Scan on orders` with a `Filter`, because no index stores `date_trunc('day', order_date)`. Run without `EXPLAIN`, the range returns one row per `order_id`; its only column is `order_id`.
- **Independent verification:** For sql-45 Exercise 1, run both predicates without `EXPLAIN` and confirm that `EXCEPT` in each direction returns 0 rows, so the rewrite keeps exactly the same `order_id` set (1,539 orders on our load); then run `EXPLAIN (COSTS OFF)` on each with the solution indexes present and confirm `Index Cond` for the range and `Filter: (date_trunc('day'::text, order_date) >= ...)` for the baseline. The plans may differ by machine; the predicate form decides eligibility, not the timing.
- **Intermediate relation check:** Run the `SELECT order_id ...` without `EXPLAIN`: on a fresh load it returns 1,539 rows and 1,539 distinct `order_id` values, matching the learner's day-aligned window. The solution's other queries use `CURRENT_TIMESTAMP - interval '180 days'` without truncation and keep 1,538, so the two windows differ by one order at the edge.
- **Clause check:** The `WHERE` clause compares bare `order_date` with two constants: midnight 180 days back and the next midnight. `date_trunc` still appears, but only on the constant side, where it runs once per statement instead of once per row. The `SELECT` list needs only `order_id`, the third column of `idx_orders_recent_customer_solution`, so on our run the plan never visited the table.
- **Alternative/trade-off:** `date_trunc('day', order_date) >= ...` with a matching upper bound returns the same orders and brings back the sequential scan: 65 pages and 2,823 discarded rows on our run, against 9 pages for the range form. An expression index cannot rescue the wrapped version, since `date_trunc` on a `timestamptz` is not `IMMUTABLE` and `CREATE INDEX` refuses it.
- **Edge case:** A 7-day window keeps the `Index Only Scan` and reads 19 rows from 3 pages; a 1,000-day window is still an `Index Only Scan`, now 4,160 rows from 19 pages. A covering index can beat a sequential scan even for most of a table. `Heap Fetches: 0` relies on a current visibility map, so a table that has not been vacuumed may show heap visits instead.

## Exercise 2: Capture structured evidence

`FORMAT JSON` keeps plan nodes, estimates, actual rows, buffers, and timing
machine-readable. It still describes only this run and environment.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 2, wrap `SELECT customer_id, SUM(total_amount) AS revenue FROM orders WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days' GROUP BY customer_id` in `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`; the solution captures this rewrite, and the baseline is captured the same way for the comparison.
- **Expected result/shape:** For sql-45 Exercise 2, expected output: one row with one `QUERY PLAN` value holding a JSON array; its first element has `Plan` with `"Node Type": "Aggregate"`, `"Strategy": "Hashed"`, `Actual Rows` equal to the number of customers, and `Shared Hit Blocks`, while `Execution Time` sits beside `Plan`, not inside it. Run without `EXPLAIN`, the query returns one row per `customer_id` with columns `customer_id` and `revenue`.
- **Independent verification:** For sql-45 Exercise 2, run the query without `EXPLAIN` and confirm that its row count equals the root `Actual Rows` (410 on our load) and that `SUM(revenue)` equals `SELECT SUM(total_amount) FROM orders` under the same filter; then confirm that `Plans[0]` is a `Bitmap Heap Scan` fed by a `Bitmap Index Scan` on `idx_orders_recent_customer_solution`, and that without the solution indexes (after `ROLLBACK`) the same query plans a `Seq Scan on orders`.
- **Intermediate relation check:** Without `EXPLAIN`, the query returns 410 `customer_id` rows whose `revenue` adds up to 834,482.51 on a fresh load. That total must equal `SUM(total_amount)` over the same window with no grouping, which shows the grouping neither lost nor duplicated an order.
- **Clause check:** `FORMAT JSON` changes only the printing: one row, one column, holding an array with a single object. Its `Plan` key holds the root node, an `Aggregate` with `"Strategy": "Hashed"` and 410 actual rows on our run, and `Execution Time` is a sibling of `Plan`. `total_amount` is not in the composite index, so the scan under the aggregate has to visit the heap; on our run it was a bitmap heap scan over 34 pages.
- **Alternative/trade-off:** Text output is easier to read by eye, but comparing runs then means scraping numbers out of lines such as `Execution Time: 0.4 ms`. The JSON fields, like `Shared Hit Blocks` and `Actual Total Time`, can be saved and diffed by a script across repeated runs. Neither format turns one run into a representative one.
- **Edge case:** A 7-day window shrinks the answer to 13 customers and 11,773.31 of revenue. Compare `Plan Rows` with `Actual Rows` at the root for both windows; a large gap on the narrow window points at statistics, not at the query text.

## Exercise 3: Prove semantic equivalence

Direct and pre-aggregated country totals are compared with `EXCEPT` in both
directions. Both difference sets must be empty before performance matters.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 3, build `direct` (orders joined to customers and `order_items`, last 180 days, `SUM(quantity)` by `country`), `items` (`order_items` summed by `order_id`), and `preaggregated` (orders joined to `items` and customers with the same filter, summed by `country`), then compare `direct EXCEPT preaggregated` and `preaggregated EXCEPT direct`, labeling each side with `difference_side`.
- **Expected result/shape:** For sql-45 Exercise 3, expected output: 0 rows with columns `difference_side`, `country`, and `units`, because both CTEs return the same 7 country totals (BR has no orders); any disagreement would appear as a labeled row, one per differing country on each side.
- **Independent verification:** For sql-45 Exercise 3, run `direct` and `preaggregated` alone and confirm 7 rows each with identical (`country`, `units`) pairs, such as AU with 1947 on our load; confirm `items` returns 4,362 rows with unique `order_id` and `SUM(units)` of 39257, equal to `SELECT SUM(quantity) FROM order_items`; then change only the `preaggregated` interval to `'179 days'` and confirm rows appear in pairs, one from each `difference_side` for every country whose total moved.
- **Intermediate relation check:** `direct` joins about 4,665 recent order lines to customers and returns 7 country rows. `items` ignores the date and collapses all 13,085 lines into 4,362 per-order totals, and `preaggregated` joins those to the 1,538 recent orders, again returning 7. Each `EXCEPT` therefore compares 7 `(country, units)` pairs, and both differences come back empty.
- **Clause check:** `EXCEPT` compares whole rows and removes duplicates, which is a fair test only because each side has one row per country. `UNION ALL` stacks the two directions, and `difference_side` labels which CTE contributed an unmatched row; an empty result means every pair appears on both sides.
- **Alternative/trade-off:** `FROM direct d FULL JOIN preaggregated p USING (country) WHERE d.units IS DISTINCT FROM p.units` reports the same mismatches with both totals in one row, which is easier to read. `EXCEPT ALL` would also expose a duplicated row, which matters once a side can return more than one row per country.
- **Edge case:** Shorten only the `preaggregated` window to 179 days and the query returns 12 rows on our run, one from each side for every country whose total moved. A one-day slip in a boundary is exactly what a fast plan can hide, and this check exposes it.

## Exercise 4: Test the empty-window boundary

An impossible historical window should return no rows for every equivalent
shape. An optimization must not manufacture a zero-valued group.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 4, read from `orders` with a window that matches no rows, `order_date >= TIMESTAMPTZ '1900-01-01 00:00:00+00' AND order_date < TIMESTAMPTZ '1900-01-02 00:00:00+00'`, and count the matching orders.
- **Expected result/shape:** For sql-45 Exercise 4, expected output: one row with `impossible_window_rows` 0. The final columns are `impossible_window_rows`.
- **Independent verification:** For sql-45 Exercise 4, confirm the count is 0, then run a grouped form of the same filter, such as `SELECT c.country, COUNT(*) FROM orders o JOIN customers c USING (customer_id) WHERE <same window> GROUP BY c.country`, and confirm it returns no rows: an ungrouped aggregate always returns one row, while a grouped query over empty input returns none, so every rewrite of the report must keep the same shape.
- **Intermediate relation check:** Run the window as written and again as `SELECT c.country, COUNT(*) ... GROUP BY c.country`: the first prints one row holding 0 and the second prints no rows. Nothing in the fixture predates early 2023 on a fresh load, so 1 January 1900 is safely empty.
- **Clause check:** With no `GROUP BY`, `COUNT(*)` collapses the filtered input into exactly one row even when that input is empty. Both `timestamptz` literals carry `+00`, which pins the window to UTC midnight whatever the session's `TimeZone`.
- **Alternative/trade-off:** `SELECT EXISTS (SELECT 1 FROM orders WHERE ...)` answers the same yes-or-no question with `false` and could stop at the first match. The count is kept because it behaves like the report's own aggregate on empty input.
- **Edge case:** Over the same empty window `SUM(quantity)` and `SUM(total_amount)` return `NULL`, not 0. If one version of the report wraps them in `COALESCE(..., 0)` and another does not, the two disagree on exactly this input, so settle the empty case before optimizing.

## Exercise 5: Document index tradeoffs

The candidate serves date-bounded customer work but consumes storage and makes
writes more expensive. Production creation needs a reviewed migration.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 5, inside the lesson transaction, after `idx_orders_recent_customer_solution` on `orders (order_date, customer_id, order_id)` and `idx_order_items_order_quantity_solution` on `order_items (order_id) INCLUDE (quantity)` are built, read `pg_indexes` where `schemaname = 'training'` and `indexname LIKE '%solution'`.
- **Expected result/shape:** For sql-45 Exercise 5, expected output: 2 rows, one per `indexname`: `idx_order_items_order_quantity_solution`, then `idx_orders_recent_customer_solution`, each with its full `CREATE INDEX` text in `indexdef`. The final columns are `indexname` and `indexdef`. The final order is `indexname`.
- **Independent verification:** For sql-45 Exercise 5, confirm the 2 rows and that `training` holds 16 indexes at that moment, so the `LIKE '%solution'` filter removed 14; read `pg_size_pretty(pg_relation_size(indexname::regclass))` for each (304 kB for the `INCLUDE` index and 152 kB for the composite one on our load) as the storage cost; then, after `ROLLBACK`, rerun the query and confirm 0 rows, proving the candidates were not left behind.
- **Intermediate relation check:** Inside the transaction, after both `CREATE INDEX` statements, `pg_indexes` lists 16 indexes in `training` on our run, and `LIKE '%solution'` keeps 2. After `ROLLBACK` the same query returns none, which proves the experiment left nothing behind.
- **Clause check:** `pg_indexes` is a catalog view with one row per index, so `indexname` is already unique within a schema and needs no `DISTINCT`. `schemaname = 'training'` keeps system indexes out, and `ORDER BY indexname` puts the `order_items` index before the `orders` one.
- **Alternative/trade-off:** Adding `pg_relation_size(indexname::regclass)` shows what each candidate costs: 304 kB for the `INCLUDE` index and 152 kB for the composite one on our run, against 520 kB for `orders` itself. `pg_index` exposes flags such as `indisunique`, but `indexdef` already spells out the full definition.
- **Edge case:** `idx_solution_orders` would fail the pattern, because `'%solution'` requires the word at the end, and an index in another schema would fail the `schemaname` test. A stray `idx_old_solution` would match even if another lesson made it, so the suffix is a naming convention, not a guarantee.

## Exercise 6: Write the decision record

Report correctness, plan evidence, observed timing, operational cost, and limits
as separate claims. The compact seed cannot support a universal speed promise.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 6, write a short report with three labeled parts, semantic equivalence, planner evidence, and environment-dependent timing, and support each claim with read-only output from this lesson: the empty two-way `EXCEPT` from Exercise 3, the plan nodes and buffer counts from Exercises 1 and 2, the index sizes from Exercise 5, and several timings of each form.
- **Expected result/shape:** For sql-45 Exercise 6, expected output: a written report, not a result set, with one entry per recommendation carrying `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`; for example, keep the half-open range (evidence: the same `order_id` set and an `Index Cond` in place of a `Filter`) and keep or drop the `INCLUDE` index (evidence: 304 kB of storage against the time it saves).
- **Independent verification:** For sql-45 Exercise 6, check that each equivalence claim cites the empty `EXCEPT` result, each plan claim names a node type and buffer count you printed, and each timing claim reports several runs of each form; then test the counterexample that `idx_order_items_order_quantity_solution` alone takes the correlated baseline from hundreds of milliseconds (about 380 ms on our load) to a few milliseconds, and state which `fallback` and `rollback_limit` entries apply when the index, not the rewrite, earns most of the speedup.
- **Intermediate relation check:** Exercise 6 has no query of its own; its evidence comes from earlier output. Gather the empty Exercise 3 difference, both plans' buffer totals (about 149,000 shared hits for the correlated baseline against about 118 for the optimized query on our run), several timings of each and the index sizes behind Exercise 5.
- **Clause check:** Each report row pairs a `decision` with its `evidence`. A defensible set for this fixture: keep the rewrite (equal results, far fewer buffers), and mark `idx_order_items_order_quantity_solution` unproven, because the optimized plan still scans all 97 pages of `order_items`. Give `fallback` and `rollback_limit` real content, such as `DROP INDEX CONCURRENTLY` and the time a rebuild would take.
- **Alternative/trade-off:** A bare `improvement_pct` would be simpler and misleading. On our run the baseline-to-optimized change is above 99%, but that baseline is pathological: its correlated subquery scans `order_items` once for each of 1,538 orders. Against the learner's plain join the rewrite gained closer to 60%. Name the comparison behind every percentage.
- **Edge case:** Counterexample: create only the `INCLUDE` index and rerun the correlated baseline. On our run it fell from roughly 450 ms to about 2 ms, close to the optimized query, so the index rather than the rewrite did most of the work. The `fallback` entry must say what happens if that index is later dropped.