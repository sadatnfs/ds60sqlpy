# Day 54 Solutions — Warehouse Aggregates and Refresh Procedure


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day54_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day54_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Aggregate table, Idempotent refresh, Late-arriving fact. Its worked-model focus is:
For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.

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

Run [`day52_solutions.sql`](day52_solutions.sql) first in the same database.
Day 54 creates and tests aggregate objects inside a transaction, then rolls
everything back. The complete runnable answer is
[`day54_solutions.sql`](day54_solutions.sql).

## Exercise 1 — `agg_sales_product_month`

The answer uses this grain and schema:

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TABLE agg_sales_product_month (
  year int NOT NULL,
  month int NOT NULL,
  product_sk int NOT NULL REFERENCES dim_product(product_sk),
  revenue numeric(14,2) NOT NULL,
  units bigint NOT NULL,
  orders bigint NOT NULL,
  PRIMARY KEY (year, month, product_sk)
);

INSERT INTO agg_sales_product_month(
  year, month, product_sk, revenue, units, orders
)
SELECT dd.year,
       dd.month,
       fs.product_sk,
       ROUND(SUM(fs.amount), 2),
       SUM(fs.quantity),
       COUNT(DISTINCT fs.order_id)
FROM fact_sales fs
JOIN dim_date dd USING (date_key)
GROUP BY dd.year, dd.month, fs.product_sk;

WITH aggregate_total AS (
  SELECT year, month, SUM(revenue) AS revenue
  FROM agg_sales_product_month
  GROUP BY year, month
), fact_total AS (
  SELECT dd.year, dd.month, ROUND(SUM(fs.amount), 2) AS revenue
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  GROUP BY dd.year, dd.month
)
SELECT a.year,
       a.month,
       a.revenue AS aggregate_revenue,
       f.revenue AS fact_revenue,
       a.revenue - f.revenue AS difference
FROM aggregate_total a
JOIN fact_total f USING (year, month)
ORDER BY a.year, a.month;

ROLLBACK;
```

The two sides are aggregated independently before joining, preventing join
fanout. Expected `difference` is zero for every built month.

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

## Exercise 2 — Refresh all aggregates for `(year, month)`

The executable solution creates:

```text
dwh.refresh_sales_aggregates_solution(p_year int, p_month int)
```

Within one procedure call it:

1. deletes the target month from category, customer, and product aggregates;
2. inserts category revenue and units;
3. inserts customer revenue and distinct orders;
4. inserts product revenue, units, and distinct orders.

The delete-then-insert design is idempotent for a target period. The answer
discovers the latest fact month and calls the procedure for that month, then
reconciles product aggregate revenue with `fact_sales`.

To inspect the result after running the canonical file, remember that it ends
with `ROLLBACK`; the aggregate objects intentionally will not persist.

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

## Required Days 52–54 sequence

```text
psql -X -v ON_ERROR_STOP=1 -d course -f day52_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d course -f day53_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d course -f day54_solutions.sql
```

Day 52 persists course-owned warehouse state. Days 53 and 54 prove their
solutions and roll back. Day 54 does not require Day 53 changes to persist.

## Reasoning, state, and pitfalls

- State the aggregate grain in the primary key; otherwise duplicate loads can
  silently inflate reports.
- Delete and rebuild all related aggregates in one transaction so readers do
  not observe mismatched periods.
- Reconcile totals after every refresh and treat nonzero differences as a load
  failure.
- The compact seed does not justify aggregate tables for performance; this is a
  warehouse-design exercise.
- Reconcile independently aggregated sides; joining aggregates to detail rows
  before summing can fan out both measures.

## Exercise 3 — Account for late facts

The period inventory identifies every loaded month. A late fact requires
refreshing its own affected period, not merely the newest month.

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

## Exercise 4 — Refresh atomically

Delete and all aggregate inserts run in one transaction through the procedure.
Failure rolls back the whole period instead of leaving partial tables.

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

## Exercise 5 — Make reconciliation NULL-safe

FULL JOIN preserves a period missing on either side, and coalesced arithmetic
turns that absence into a visible nonzero difference.

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

## Exercise 6 — Prove idempotency

The answer snapshots category aggregates, reruns the same latest period, and
uses two-way `EXCEPT`. Both difference sets must be empty.

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
