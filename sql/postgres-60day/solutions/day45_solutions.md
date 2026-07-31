# Day 45 Solution — Performance Optimization Project


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day45_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day45_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Experimental control, Buffer evidence, Regression check. Its worked-model focus is:
Capture the function-wrapped date baseline, rewrite it as a raw half-open range, and add one candidate index inside the rollback transaction. Run both forms several times, reconcile country/unit results, and calculate percentage change from comparable observations without promising 70%.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 1, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-45 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-45 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-45 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-45 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-45 Exercise 1, the chosen form is justified by this lesson-specific rationale: The direct half-open range leaves `order_date` unwrapped, making the B-tree eligible while preserving a clear time boundary. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 2 — Capture structured evidence

`FORMAT JSON` keeps plan nodes, estimates, actual rows, buffers, and timing
machine-readable. It still describes only this run and environment.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 2, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-45 Exercise 2, expected output: one row per `customer_id`. The final columns are `customer_id`, and `revenue`.
- **Independent verification:** For sql-45 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-45 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
- **Clause check:** For sql-45 Exercise 2, the solution actually uses `FROM`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `customer_id`, and finish with `customer_id`, and `revenue`.
- **Alternative/trade-off:** For sql-45 Exercise 2, the chosen form is justified by this lesson-specific rationale: `FORMAT JSON` keeps plan nodes, estimates, actual rows, buffers, and timing machine-readable. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 3 — Prove semantic equivalence

Direct and pre-aggregated country totals are compared with `EXCEPT` in both
directions. Both difference sets must be empty before performance matters.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 3, read from `orders`, `customers`, and `order_items`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-45 Exercise 3, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
- **Independent verification:** For sql-45 Exercise 3, project `order_id` plus the raw source columns from `orders`, `customers`, and `order_items` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-45 Exercise 3, run `direct`, `items`, and `preaggregated` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-45 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, `customers`, and `order_items`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
- **Alternative/trade-off:** For sql-45 Exercise 3, the chosen form is justified by this lesson-specific rationale: Direct and pre-aggregated country totals are compared with `EXCEPT` in both directions. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 4 — Test the empty-window boundary

An impossible historical window should return no rows for every equivalent
shape. An optimization must not manufacture a zero-valued group.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 4, read from `orders`. Build the answer toward `impossible_window_rows`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-45 Exercise 4, expected output: one row per `order_id`. The final columns are `impossible_window_rows`.
- **Independent verification:** For sql-45 Exercise 4, run an anti-check that counts rows where NOT ((order_date >= timestamptz '1900-01-01 00:00:00+00' AND order_date < timestamptz '1900-01-02 00:00:00+00')); require unique `order_id` where the expected grain is one row per key and confirm the projected `impossible_window_rows` against `orders`. Insert rows immediately before, exactly at, and immediately after `order_date >= timestamptz '1900-01-01 00:00:00+00'`, and `order_date < timestamptz '1900-01-02 00:00:00+00'`; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-45 Exercise 4, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-45 Exercise 4, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `impossible_window_rows`.
- **Alternative/trade-off:** For sql-45 Exercise 4, the chosen form is justified by this lesson-specific rationale: An impossible historical window should return no rows for every equivalent shape. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after `order_date >= timestamptz '1900-01-01 00:00:00+00'`, and `order_date < timestamptz '1900-01-02 00:00:00+00'`; identify which rows pass each inclusive or exclusive comparison.

## Exercise 5 — Document index tradeoffs

The candidate serves date-bounded customer work but consumes storage and makes
writes more expensive. Production creation needs a reviewed migration.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 5, read from `pg_indexes`. Build the answer toward `indexname`, and `indexdef`; keep `indexname` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-45 Exercise 5, expected output: one row per `indexname`. The final columns are `indexname`, and `indexdef`. The final order is `indexname`.
- **Independent verification:** For sql-45 Exercise 5, run an anti-check that counts rows where NOT ((schemaname = 'training' AND indexname LIKE '%solution')); require unique `indexname` where the expected grain is one row per key and confirm the projected `indexname`, and `indexdef` against `pg_indexes`. Add one row for which `(schemaname = 'training' AND indexname LIKE '%solution')` is true and one for which it is false; verify only the matching `indexname` value is returned.
- **Intermediate relation check:** For sql-45 Exercise 5, inspect the source keys that survive `WHERE`; then check `indexname` before applying the row cap.
- **Clause check:** For sql-45 Exercise 5, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_indexes`, preserve one row per `indexname`, and finish with `indexname`, and `indexdef` ordered by `indexname`.
- **Alternative/trade-off:** For sql-45 Exercise 5, the chosen form is justified by this lesson-specific rationale: The candidate serves date-bounded customer work but consumes storage and makes writes more expensive. Evaluate another form against the concrete expected result (one row per `indexname`) and the verification above.
- **Edge case:** Add one row for which `(schemaname = 'training' AND indexname LIKE '%solution')` is true and one for which it is false; verify only the matching `indexname` value is returned.

## Exercise 6 — Write the decision record

Report correctness, plan evidence, observed timing, operational cost, and limits
as separate claims. The compact seed cannot support a universal speed promise.

### Reasoning and verification

- **Inputs/evidence:** For sql-45 Exercise 6, complete the write an optimization report separating semantics plans and  written analysis and support its claims with read-only evidence from `customers`, `orders`, and `order_items`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-45 Exercise 6, expected output: a completed the write an optimization report separating semantics plans and  written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-45 Exercise 6, check the write an optimization report separating semantics plans and  written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-45 Exercise 6, check the write an optimization report separating semantics plans and  written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-45 Exercise 6, the solution actually uses `WITH`, and `FROM`. Read only those operations: begin at `customers`, `orders`, and `order_items`, preserve one row per `customer_id`, and finish with `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Alternative/trade-off:** For sql-45 Exercise 6, the chosen form is justified by this lesson-specific rationale: Report correctness, plan evidence, observed timing, operational cost, and limits as separate claims. Evaluate another form against the concrete expected result (a completed the write an optimization report separating semantics plans and  written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
