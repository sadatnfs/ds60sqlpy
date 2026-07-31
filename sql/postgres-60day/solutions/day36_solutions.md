# Day 36 — Solutions: Materialized Views


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day36_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day36_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Materialized view, Freshness, Concurrent refresh. Its worked-model focus is:
Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.

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

A materialized view stores query results. Reads can become cheaper, but the
result is a snapshot and must be refreshed when source data changes.

## Exercise 1 — Weekly revenue by country

This demonstration is transactional and leaves no materialized view behind.

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP MATERIALIZED VIEW IF EXISTS mv_weekly_country_revenue_solution;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_solution AS
SELECT date_trunc('week', o.order_date)::date AS week_start,
       c.country,
       SUM(
         oi.unit_price * oi.quantity * (1 - oi.discount)
       ) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY date_trunc('week', o.order_date), c.country;

SELECT week_start,
       country,
       ROUND(revenue, 2) AS revenue
FROM mv_weekly_country_revenue_solution
ORDER BY week_start DESC, revenue DESC;

ROLLBACK;
```

Expected shape: one row per observed week-country pair. PostgreSQL weeks begin
on Monday under `date_trunc('week', ...)`.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
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

## Exercise 2 — Compare base-table and snapshot plans

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP MATERIALIZED VIEW IF EXISTS mv_weekly_country_revenue_compare;

CREATE MATERIALIZED VIEW mv_weekly_country_revenue_compare AS
SELECT date_trunc('week', o.order_date)::date AS week_start,
       c.country,
       SUM(
         oi.unit_price * oi.quantity * (1 - oi.discount)
       ) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY date_trunc('week', o.order_date), c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('week', o.order_date)::date AS week_start,
       c.country,
       SUM(
         oi.unit_price * oi.quantity * (1 - oi.discount)
       ) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY date_trunc('week', o.order_date), c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT week_start,
       country,
       revenue
FROM mv_weekly_country_revenue_compare;

ROLLBACK;
```

The materialized-view plan should avoid source joins and aggregation. On this
small dataset, wall-clock differences can be noisy; compare plan work and
buffers as well as execution time.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
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

## Pitfalls

- A normal `REFRESH MATERIALIZED VIEW` blocks concurrent reads of that view.
  `REFRESH ... CONCURRENTLY` requires a qualifying unique index and cannot run
  inside an explicit transaction block.
- Refresh is not automatic. Define freshness ownership and monitoring before
  using a materialized view for reporting.
- Materialized views duplicate data and add refresh cost; they are not a default
  replacement for indexing or query repair.

## Exercise 3 — Observe stale then refreshed data

The transaction changes one disposable source row after materialization.
Source and view totals diverge until `REFRESH`, making the freshness contract
visible instead of merely described.

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

## Exercise 4 — Explain concurrent-refresh eligibility

The unique `(week, country)` index supplies a stable row identity required by
concurrent refresh. Initial population and this rollback lab still use ordinary
refresh; concurrent refresh also has transaction restrictions.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
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

## Exercise 5 — Name the revenue definition

The view stores order-header totals. The control query prints header and
line-item revenue side by side so a consumer must choose a business definition.

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

## Exercise 6 — Materialize missing combinations explicitly

A cross-joined week/country spine defines requested combinations. The left join
and `COALESCE` then implement a deliberate zero-display policy.

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
