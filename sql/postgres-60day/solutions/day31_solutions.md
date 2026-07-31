# Day 31 — Solutions: `EXPLAIN` and `EXPLAIN ANALYZE`


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day31_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day31_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Plan node, Cost estimate, Loop count. Its worked-model focus is:
Run the same safe filter first with EXPLAIN and then with EXPLAIN (ANALYZE, BUFFERS). Start at the scan leaf, compare estimated rows with actual rows × loops, note rows removed by the filter, and only then read the parent LIMIT or aggregate node.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 1, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-31 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, and `total_amount`.
- **Independent verification:** For sql-31 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-31 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-31 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, and `total_amount`.
- **Alternative/trade-off:** For sql-31 Exercise 1, the chosen form is justified by this lesson-specific rationale: These three queries ask for progressively smaller portions of `orders`. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 2, run the underlying read-only query over `orders`, `customers`, and `order_items` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-31 Exercise 2, expected output: one row per `country`. The final columns are `country`, and `units`.
- **Independent verification:** For sql-31 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-31 Exercise 2, start with the first relation in `orders`, `customers`, and `order_items`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-31 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, `customers`, and `order_items`, preserve one row per `country`, and finish with `country`, and `units`.
- **Alternative/trade-off:** For sql-31 Exercise 2, the chosen form is justified by this lesson-specific rationale: `EXPLAIN` plans but does not run the `SELECT`; `EXPLAIN ANALYZE` executes it and adds actual timing, loops, and row counts. Evaluate another form against the concrete expected result (one row per `country`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- `EXPLAIN ANALYZE` really executes the statement. Use `BEGIN`/`ROLLBACK` when
  analyzing writes and never assume it is harmless in production.
- One timing run includes cache and system noise. Repeat measurements and use
  representative parameters.
- Planning cost units are not milliseconds. Actual time is shown separately.
- A sequential scan is often correct for a small table or a low-selectivity
  predicate.

## Exercise 3 — Predict broad and selective plans

The two queries differ only in threshold, so estimated/actual rows and buffers
are comparable. `> 0` should be broader than `> 900`; scan choice still depends
on table size and cost. See the fully runnable query in
[`day31_solutions.sql`](day31_solutions.sql).

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 3, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-31 Exercise 3, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-31 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-31 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-31 Exercise 3, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-31 Exercise 3, the chosen form is justified by this lesson-specific rationale: The two queries differ only in threshold, so estimated/actual rows and buffers are comparable. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 4 — Read a verbose join plan

Start at each scan, follow rows into the join, then into the aggregate and root.
`VERBOSE` identifies qualified output expressions; it does not make the query
faster.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 4, run the underlying read-only query over `customers`, and `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-31 Exercise 4, expected output: one row per `country`. The final columns are `country`, and `order_count`.
- **Independent verification:** For sql-31 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-31 Exercise 4, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
- **Clause check:** For sql-31 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `customers`, and `orders`, preserve one row per `country`, and finish with `country`, and `order_count`.
- **Alternative/trade-off:** For sql-31 Exercise 4, the chosen form is justified by this lesson-specific rationale: Start at each scan, follow rows into the join, then into the aggregate and root. Evaluate another form against the concrete expected result (one row per `country`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 5 — Analyze DML safely

`EXPLAIN ANALYZE UPDATE` performs the update. The answer uses an impossible key
and a savepoint, then rolls back to and releases that savepoint.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 5, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-31 Exercise 5, expected output: one row per `order_id`. The final columns are `update`, and `analyze`.
- **Independent verification:** For sql-31 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-31 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-31 Exercise 5, the solution actually uses `WHERE`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `update`, and `analyze`.
- **Alternative/trade-off:** For sql-31 Exercise 5, the chosen form is justified by this lesson-specific rationale: `EXPLAIN ANALYZE UPDATE` performs the update. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 6 — Interpret an empty result

The negative-total predicate returns zero because the schema forbids negative
totals. A zero actual with a small nonzero estimate can be ordinary statistical
uncertainty; it is not, alone, proof statistics are stale.

### Reasoning and verification

- **Inputs/evidence:** For sql-31 Exercise 6, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-31 Exercise 6, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-31 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-31 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-31 Exercise 6, the solution actually uses `WITH`, `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-31 Exercise 6, the chosen form is justified by this lesson-specific rationale: The negative-total predicate returns zero because the schema forbids negative totals. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
