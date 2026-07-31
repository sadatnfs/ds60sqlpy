# Day 35 — Solutions: Avoiding Performance Pitfalls


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day35_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day35_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Sargability, Half-open range, Set-based rewrite. Its worked-model focus is:
Compare datetrunc('day', orderdate) = targetday with orderdate >= targetday AND orderdate < targetday + interval '1 day'. Test timestamps at both boundaries, reconcile row IDs, and compare plans with a matching orderdate index.

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

This learner day asks for three rewrites that keep functions off an indexed
column and one rewrite of a correlated subquery. The examples use half-open
timestamp ranges because they are precise and B-tree friendly.

## Exercise 1 — Three sargable predicate rewrites

Each “better” predicate leaves `order_date` bare, allowing an index on that
column to define a contiguous range.

```sql
SET search_path TO training, public;

-- 1. One calendar day
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE date_trunc('day', order_date) = date_trunc('day', CURRENT_TIMESTAMP);

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('day', CURRENT_TIMESTAMP)
  AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day';

-- 2. Current calendar year
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE EXTRACT(year FROM order_date) = EXTRACT(year FROM CURRENT_DATE);

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('year', CURRENT_DATE)
  AND order_date < date_trunc('year', CURRENT_DATE) + interval '1 year';

-- 3. Last seven calendar dates, including today
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date::date >= CURRENT_DATE - 6;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= (CURRENT_DATE - 6)::timestamptz
  AND order_date < (CURRENT_DATE + 1)::timestamptz;
```

Expected result sets within each pair are equivalent under the session time
zone. Plan nodes can remain sequential scans because the dataset is small or
because the demonstration index from Day 32 was rolled back.

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

## Exercise 2 — Replace a per-customer correlated aggregate

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id,
       (
         SELECT SUM(o.total_amount)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS lifetime_revenue
FROM customers c;

EXPLAIN (ANALYZE, BUFFERS)
WITH order_totals AS (
  SELECT customer_id,
         SUM(total_amount) AS lifetime_revenue
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id,
       ot.lifetime_revenue
FROM customers c
LEFT JOIN order_totals ot ON ot.customer_id = c.customer_id;
```

Expected shape: one row per customer in both forms. The `LEFT JOIN` is required
to retain customers with no orders; changing it to an inner join would alter
the answer.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** Pre-aggregation or a differently ordered join pipeline is valid only if it prevents fanout and reconciles to the same scoped control total.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Pitfalls

- Sargability does not guarantee an index scan; it merely gives the planner the
  option.
- Timestamp-to-date conversion uses the session time zone. Define business
  timezone semantics before reporting calendar periods.
- PostgreSQL can decorrelate some subqueries. Confirm the plan instead of
  assuming every correlated expression runs once per outer row.
- Do not hide fanout with `DISTINCT`; fix the join grain.

## Exercise 3 — Diagnose wildcard search

`LIKE 'A%'` has a fixed starting prefix; `LIKE '%A%'` does not. A normal B-tree
therefore has a more direct opportunity on the first pattern, subject to
collation/operator-class details.

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

## Exercise 4 — Replace OFFSET with a seek tuple

The boundary tuple comes from `(order_date DESC, order_id DESC)`. The next page
uses the matching tuple comparison and repeats that deterministic order.

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

## Exercise 5 — Fix payment/item fanout

The answer groups each many-side by `order_id` before joining. `DISTINCT` would
only conceal duplicated output, not repair multiplied sums.

### Reasoning and verification

- **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
- **Independent verification:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
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

## Exercise 6 — Define nullable counts

`COUNT(*)` measures customer rows; `COUNT(email)` measures customers with a
non-NULL email. The difference is a useful missingness count, not a discrepancy.

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
