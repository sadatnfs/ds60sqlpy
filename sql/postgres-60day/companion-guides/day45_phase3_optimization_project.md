# Day 45: Phase 3 Optimization Project

## How to run this lesson

Open **sql-45** in `./classroom`, choose PostgreSQL and run it as a
**Whole SQL lesson (psql)**. Your editable copy is
`.learning/sql/sql-45/lesson/workspace/sql/postgres-60day/day45_phase3_optimization_project.sql`.
The script opens a transaction in `advanced_sql_training`, builds
`idx_orders_order_date_only` and finishes with `ROLLBACK`, so the index never
outlives the run. `psql` prints three `EXPLAIN ANALYZE` plans rather than
business rows: the wrapped-date baseline, the raw-range rewrite and the
pre-aggregated variant. Because `now()` is frozen when `BEGIN` runs, all three
filter against the same 180-day boundary. Launcher steps are in the
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom), and the
notebook alternative sits in its
[contributor notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 44; monitoring and diagnostics](day44_monitoring_diagnostics.md) Day 44's plan-reading habits carry this whole project. Today two plans sit side by side, and you must explain the gap between them with node names, `Rows Removed by Filter` and buffer counts, not with a sense that one felt faster.
  and the complete performance sequence from Days 31-44
- **Artifacts:** [learner SQL](../day45_phase3_optimization_project.sql) ·
  [solution reasoning](../solutions/day45_solutions.md) ·
  [executable solution](../solutions/day45_solutions.sql)

## A beginner's mental model for this lesson

The project query answers one business question: how many units did
customers in each country buy in the last 180 days? On a fresh load that
window holds 1,539 of the 4,362 orders, placed by 410 customers, and the
answer has 7 rows. CA leads with 2,152 units and AU trails with 1,947; the 62
Brazilian customers have no orders, so BR never appears. Every faster version
must keep printing exactly those 7 rows.

**Experimental control** means changing one thing at a time while the data,
the window and the session stay fixed. The transaction helps: `now()` returns
the moment `BEGIN` ran, so every statement before `ROLLBACK` sees the same
boundary. **Buffer evidence** is the `Buffers: shared hit=... read=...` line
that `EXPLAIN (ANALYZE, BUFFERS)` adds; it counts 8 kB pages touched, which is
steadier than milliseconds on a table of only 65 pages. A **regression check**
proves the faster query still returns the same rows; here that is a two-way
`EXCEPT` between the old and new country totals.

The core idea is sargability. `date_trunc('day', o.order_date) >= ...` hides
the column inside a function, so a plain index on `order_date` cannot serve
it. `o.order_date >= date_trunc('day', now()) - interval '180 days'` moves the
arithmetic to the constant side and still selects the same 1,539 orders,
because the boundary is a midnight. Read each plan with the
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
in mind: the planner may swap scans and joins, but it never changes which rows
qualify.

## Two worked SQL examples

Both excerpts come from the top of `day45_phase3_optimization_project.sql`:
the first is the deliberately slow baseline, and the second is the one-line
index that the rewrite depends on. Neither prints business rows.

### Example 1

```sql
EXPLAIN ANALYZE
SELECT
  c.country,
  SUM(oi.quantity)
FROM
  customers c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
WHERE
  date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')
GROUP BY
  c.country
ORDER BY
  2 DESC;
```

**How to read it:** `EXPLAIN ANALYZE` really executes the join of `customers`, `orders` and
`order_items`, then prints the plan in place of the 7 country rows. The
`WHERE` clause wraps `o.order_date` in `date_trunc('day', ...)`, so PostgreSQL
must compute that function for every order before it can compare.
`ORDER BY 2 DESC` sorts by the second, unnamed column, which `psql` heads
`sum`.

**Expected result/shape:** A plan tree, not a table. On our run the `orders` node was a `Seq Scan`
whose `Filter` line repeats the `date_trunc` call and whose
`Rows Removed by Filter` was 2,823, leaving 1,539 orders; the scan read all 65
pages of `orders`, and the whole plan took about 5 ms. Your timing will
differ. Drop `EXPLAIN ANALYZE` to see the 7 rows, CA with 2,152 first and AU
with 1,947 last.

### Example 2

```sql
CREATE INDEX IF NOT EXISTS idx_orders_order_date_only ON orders (order_date);
```

**How to read it:** The statement builds a B-tree over the raw `order_date` values. That helps
only predicates that compare `order_date` itself, which is why the script
rewrites the filter right after it. `IF NOT EXISTS` turns a second build into
a notice instead of an error, and the closing `ROLLBACK` removes the index
along with everything else.

**Expected result/shape:** `psql` prints `CREATE INDEX`. Before the rollback,
`SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_orders_order_date_only'`
shows `... USING btree (order_date)`; after the script ends, the same query
finds nothing. The rewrite uses it on our run: a `Bitmap Index Scan` on
`idx_orders_order_date_only` feeds a heap scan of 34 of the 65 pages, and the
plan took about 2 ms. An expression index on
`date_trunc('day', order_date)` is no shortcut: `CREATE INDEX` rejects it,
because `date_trunc` on a `timestamptz` depends on the time zone and is not
`IMMUTABLE`.

## Learning objectives

- Run a controlled optimization experiment with comparable plans and outputs.
- Report measured improvement honestly, including a result below the target.

## Vocabulary and concepts

- **Experimental control:** fixed query semantics, data, parameters, and
  environment for a comparison.
- **Buffer evidence:** shared/local block hits, reads, dirties, and writes
  reported by `BUFFERS`.
- **Regression check:** proof that a rewrite preserves the defined output.

## Worked example / walkthrough

Capture the function-wrapped date baseline, rewrite it as a raw half-open range,
and add one candidate index inside the rollback transaction. Run both forms
several times, reconcile country/unit results, and calculate percentage change
from comparable observations without promising 70%.

## Exercises

Complete these in the
[learner SQL](../day45_phase3_optimization_project.sql):

1. Predict the effect of replacing the non-sargable timestamp expression.
   **Inputs/evidence:** For sql-45 Exercise 1, compare the learner baseline predicate `date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')` with the half-open range `order_date >= date_trunc('day', CURRENT_TIMESTAMP) - interval '180 days' AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day'` on `orders`, reading each through `EXPLAIN (ANALYZE, BUFFERS)` after the solution indexes are built.
   **Expected result/shape:** For sql-45 Exercise 1, expected output: a text plan, not rows. With `idx_orders_recent_customer_solution` on (`order_date`, `customer_id`, `order_id`) in place, the half-open range becomes an `Index Only Scan` with an `Index Cond` on both `order_date` bounds, while the wrapped baseline stays a `Seq Scan on orders` with a `Filter`, because no index stores `date_trunc('day', order_date)`. Run without `EXPLAIN`, the range returns one row per `order_id`; its only column is `order_id`.
   **Verify:** For sql-45 Exercise 1, run both predicates without `EXPLAIN` and confirm that `EXCEPT` in each direction returns 0 rows, so the rewrite keeps exactly the same `order_id` set (1,539 orders on our load); then run `EXPLAIN (COSTS OFF)` on each with the solution indexes present and confirm `Index Cond` for the range and `Filter: (date_trunc('day'::text, order_date) >= ...)` for the baseline. The plans may differ by machine; the predicate form decides eligibility, not the timing.
   **Data check:** Without `EXPLAIN`, the half-open range returns 1,539 distinct `order_id` values on a fresh load, the same set as the wrapped baseline. With only `idx_orders_order_date_only` in place, a 7-day window (19 orders) becomes a bitmap scan that touches 8 pages on our run, while the wrapped version of the same 7 days still reads all 65 pages and discards 4,343 rows.
2. Capture/compare JSON plans for baseline and rewrite.
   **Inputs/evidence:** For sql-45 Exercise 2, wrap `SELECT customer_id, SUM(total_amount) AS revenue FROM orders WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days' GROUP BY customer_id` in `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`; the solution captures this rewrite, and the baseline is captured the same way for the comparison.
   **Expected result/shape:** For sql-45 Exercise 2, expected output: one row with one `QUERY PLAN` value holding a JSON array; its first element has `Plan` with `"Node Type": "Aggregate"`, `"Strategy": "Hashed"`, `Actual Rows` equal to the number of customers, and `Shared Hit Blocks`, while `Execution Time` sits beside `Plan`, not inside it. Run without `EXPLAIN`, the query returns one row per `customer_id` with columns `customer_id` and `revenue`.
   **Verify:** For sql-45 Exercise 2, run the query without `EXPLAIN` and confirm that its row count equals the root `Actual Rows` (410 on our load) and that `SUM(revenue)` equals `SELECT SUM(total_amount) FROM orders` under the same filter; then confirm that `Plans[0]` is a `Bitmap Heap Scan` fed by a `Bitmap Index Scan` on `idx_orders_recent_customer_solution`, and that without the solution indexes (after `ROLLBACK`) the same query plans a `Seq Scan on orders`.
   **Data check:** The underlying query returns 410 `customer_id` rows whose `revenue` adds up to 834,482.51 on a fresh load. In the JSON, the root object's `Plan` holds `"Node Type": "Aggregate"` with `"Strategy": "Hashed"` and `"Actual Rows": 410`, while `Execution Time` sits beside `Plan` rather than inside it. A 7-day window gives 13 customers and 11,773.31.
3. Prove direct and pre-aggregated results equivalent with two-way `EXCEPT`.
   **Inputs/evidence:** For sql-45 Exercise 3, build `direct` (orders joined to customers and `order_items`, last 180 days, `SUM(quantity)` by `country`), `items` (`order_items` summed by `order_id`), and `preaggregated` (orders joined to `items` and customers with the same filter, summed by `country`), then compare `direct EXCEPT preaggregated` and `preaggregated EXCEPT direct`, labeling each side with `difference_side`.
   **Expected result/shape:** For sql-45 Exercise 3, expected output: 0 rows with columns `difference_side`, `country`, and `units`, because both CTEs return the same 7 country totals (BR has no orders); any disagreement would appear as a labeled row, one per differing country on each side.
   **Verify:** For sql-45 Exercise 3, run `direct` and `preaggregated` alone and confirm 7 rows each with identical (`country`, `units`) pairs, such as AU with 1947 on our load; confirm `items` returns 4,362 rows with unique `order_id` and `SUM(units)` of 39257, equal to `SELECT SUM(quantity) FROM order_items`; then change only the `preaggregated` interval to `'179 days'` and confirm rows appear in pairs, one from each `difference_side` for every country whose total moved.
   **Data check:** `direct` and `preaggregated` each return 7 country rows, `items` returns 4,362 (one per order, built from all 13,085 lines), and both `EXCEPT` directions are empty, so the query prints 0 rows. To watch the check work, shorten only the `preaggregated` window to 179 days: on our run it then returns 12 rows, one from each side for every country whose total moved.
4. Test an empty-window boundary.
   **Inputs/evidence:** For sql-45 Exercise 4, read from `orders` with a window that matches no rows, `order_date >= TIMESTAMPTZ '1900-01-01 00:00:00+00' AND order_date < TIMESTAMPTZ '1900-01-02 00:00:00+00'`, and count the matching orders.
   **Expected result/shape:** For sql-45 Exercise 4, expected output: one row with `impossible_window_rows` 0. The final columns are `impossible_window_rows`.
   **Verify:** For sql-45 Exercise 4, confirm the count is 0, then run a grouped form of the same filter, such as `SELECT c.country, COUNT(*) FROM orders o JOIN customers c USING (customer_id) WHERE <same window> GROUP BY c.country`, and confirm it returns no rows: an ungrouped aggregate always returns one row, while a grouped query over empty input returns none, so every rewrite of the report must keep the same shape.
   **Data check:** `impossible_window_rows` is 0, because the oldest order on a fresh load is from early 2023. Grouped by country, the same filter prints no rows at all, and `SUM(quantity)` over that empty window is `NULL`, not 0.
5. Design and justify one workload-specific index.
   **Inputs/evidence:** For sql-45 Exercise 5, inside the lesson transaction, after `idx_orders_recent_customer_solution` on `orders (order_date, customer_id, order_id)` and `idx_order_items_order_quantity_solution` on `order_items (order_id) INCLUDE (quantity)` are built, read `pg_indexes` where `schemaname = 'training'` and `indexname LIKE '%solution'`.
   **Expected result/shape:** For sql-45 Exercise 5, expected output: 2 rows, one per `indexname`: `idx_order_items_order_quantity_solution`, then `idx_orders_recent_customer_solution`, each with its full `CREATE INDEX` text in `indexdef`. The final columns are `indexname` and `indexdef`. The final order is `indexname`.
   **Verify:** For sql-45 Exercise 5, confirm the 2 rows and that `training` holds 16 indexes at that moment, so the `LIKE '%solution'` filter removed 14; read `pg_size_pretty(pg_relation_size(indexname::regclass))` for each (304 kB for the `INCLUDE` index and 152 kB for the composite one on our load) as the storage cost; then, after `ROLLBACK`, rerun the query and confirm 0 rows, proving the candidates were not left behind.
   **Data check:** With both solution indexes built, the query returns 2 rows: `idx_order_items_order_quantity_solution`, then `idx_orders_recent_customer_solution`. On our run `training` held 14 other indexes at that moment, and none ends in `solution`. After `ROLLBACK` the query returns nothing.
6. Write an optimization report separating semantics, plans, and timing.
   **Inputs/evidence:** For sql-45 Exercise 6, write a short report with three labeled parts, semantic equivalence, planner evidence, and environment-dependent timing, and support each claim with read-only output from this lesson: the empty two-way `EXCEPT` from Exercise 3, the plan nodes and buffer counts from Exercises 1 and 2, the index sizes from Exercise 5, and several timings of each form.
   **Expected result/shape:** For sql-45 Exercise 6, expected output: a written report, not a result set, with one entry per recommendation carrying `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`; for example, keep the half-open range (evidence: the same `order_id` set and an `Index Cond` in place of a `Filter`) and keep or drop the `INCLUDE` index (evidence: 304 kB of storage against the time it saves).
   **Verify:** For sql-45 Exercise 6, check that each equivalence claim cites the empty `EXCEPT` result, each plan claim names a node type and buffer count you printed, and each timing claim reports several runs of each form; then test the counterexample that `idx_order_items_order_quantity_solution` alone takes the correlated baseline from hundreds of milliseconds (about 380 ms on our load) to a few milliseconds, and state which `fallback` and `rollback_limit` entries apply when the index, not the rewrite, earns most of the speedup.
   **Data check:** Cite numbers you printed: the 7 matching country rows, each plan's buffer totals, several timings of each form and the index sizes from `pg_relation_size` (304 kB for the `INCLUDE` index and 152 kB for the composite one on our run). A ready counterexample: the `INCLUDE` index alone takes the correlated baseline from roughly 450 ms to about 2 ms, so the rewrite is not what earns most of the speedup.

Produce a decision record covering plan, buffers, correctness, index cost, and
whether the candidate should proceed.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Capture the function-wrapped date baseline, rewrite it as a raw half-open range, and add one candidate index inside the rollback transaction. Run both forms several times, reconcile country/unit results, and calculate percentage change from comparable observations without promising 70%.
- **Trusting one timing:** a 5 ms query on 65 pages moves by a millisecond
  between runs. Take the median of several runs and lean on buffer counts,
  which barely change.
- **Pre-aggregating too early:** the learner's `items` CTE sums all 13,085
  lines into 4,362 groups before the date filter applies, so on our run it was
  a little slower (about 5.7 ms) than the plain rewrite (about 2 ms).
  Aggregating first pays off when it shrinks rows that survive the filter.
- **Comparing different windows:** the learner script starts at midnight 180
  days ago, while the solution uses `CURRENT_TIMESTAMP - interval '180 days'`.
  On our run that is 1,539 versus 1,538 orders, and IN moves from 1,979 to
  1,977 units. Only compare plans whose windows match.
- **Assuming an index is used because it exists:** the optimized solution
  query still scans all 97 pages of `order_items` on our run;
  `idx_order_items_order_quantity_solution` appears nowhere in that plan.
  Find each index in the plan it was built for.
- Generic diagnosis steps live in the study guide's
  [recovery section](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Are result keys and totals identical before performance is discussed?
- Does the recommendation distinguish the compact seed from representative
  production-scale evidence?

## Next step

Continue to [Day 46; e-commerce LTV and cohorts](day46_project1_ecommerce_part1.md).

## Deep dive and reference

## Project goal

Measure a recent country-units query, make its predicate and aggregation more
efficient, and attempt to reduce runtime by more than 70% without changing the
result.

## What the learner script compares

1. A baseline whose date filter wraps `orders.order_date` in `date_trunc`.
2. A sargable raw-column date range after adding an `orders(order_date)` index.
3. A rewrite that pre-aggregates `order_items.quantity` by `order_id` before the
   country rollup.

All DDL and plans are inside a transaction and roll back.

## Evidence to collect

- exact SQL and seed/setup version;
- row counts and country-to-units totals for correctness;
- `EXPLAIN (ANALYZE, BUFFERS)` before and after;
- execution time, shared buffer hits/reads, rows, loops, and scan/join types;
- candidate index size and expected write cost; and
- percentage improvement calculated from comparable timings.

## Optimization reasoning

- A raw `order_date >= boundary` predicate can use a normal B-tree range.
- Set-based pre-aggregation avoids repeated line-level work.
- A covering order-item index may help but remains a measured candidate.
- Small tables can legitimately use sequential scans.

## The 70% target is not guaranteed

The target is an experiment goal, not a promised result on the compact
deterministic seed. Planning overhead, cache state, and small table size can
dominate. Report the observed percentage honestly, reconcile outputs, and use a
representative-scale dataset before recommending production changes.

Production index creation requires a separate reviewed migration and may need
`CREATE INDEX CONCURRENTLY`; the tutorial transaction intentionally persists
nothing.

## Expanded practice lab

The six explicit prompts make this a measured project instead of a single
rewrite. Begin with a prediction, capture JSON plans, and prove equivalence with
two-way `EXCEPT` before comparing performance. JSON makes the root execution
time and buffer fields machine-readable, but repeated trials and environment
notes are still required.

Test the empty-window boundary and document any proposed index as a workload
tradeoff, not free speed. The final report must keep three claims separate:
same result semantics, observed planner evidence, and timing that may change on
different hardware, cache state, cardinality, or PostgreSQL versions.

## Ask an AI tutor about this lesson

A tutor is most useful here as a skeptical reviewer of your report. Give it
your plans and timings, and ask it to point out where you changed more than
one variable or where a claim rests on a single run. Keep every number from
your own `psql` session; the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
list what to paste. The prompt below frames that review:

```text
Tutor me through sql-45: Phase 3 Project: Query Optimization.

I have completed the direct catalog prerequisite: `sql-44`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day45_phase3_optimization_project.md
- Answer-free learner SQL: sql/postgres-60day/day45_phase3_optimization_project.sql

Key terms to teach in context: Experimental control, Buffer evidence, Regression check. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture the function-wrapped date baseline, rewrite it as a raw half-open range, and add one candidate index inside the rollback transaction. Run both forms several times, reconcile country/unit results, and calculate percentage change from comparable observations without promising 70%.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-45/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
