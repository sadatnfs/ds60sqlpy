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

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 2 — Capture structured evidence

`FORMAT JSON` keeps plan nodes, estimates, actual rows, buffers, and timing
machine-readable. It still describes only this run and environment.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 3 — Prove semantic equivalence

Direct and pre-aggregated country totals are compared with `EXCEPT` in both
directions. Both difference sets must be empty before performance matters.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 4 — Test the empty-window boundary

An impossible historical window should return no rows for every equivalent
shape. An optimization must not manufacture a zero-valued group.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A different window or subquery shape is valid only with the same partition, peer, frame, tie, and output-order semantics.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Document index tradeoffs

The candidate serves date-bounded customer work but consumes storage and makes
writes more expensive. Production creation needs a reviewed migration.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Write the decision record

Report correctness, plan evidence, observed timing, operational cost, and limits
as separate claims. The compact seed cannot support a universal speed promise.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.
