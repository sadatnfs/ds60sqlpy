# Day 47 Solutions — E-commerce Analytics, Part 2


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day47_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day47_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Cohort size, Active customer, Retention curve. Its worked-model focus is:
Deduplicate activity to (customerid, ordermonth), count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.

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

The deliverables are a true retention rate and a tidy six-cohort result suitable
for a line chart. See [`day47_solutions.sql`](day47_solutions.sql).

## Exercises 1 and 2 — Retention rate and chart-ready curves

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), active_months AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), retained AS (
  SELECT c.cohort_month,
         a.order_month,
         (
           EXTRACT(year FROM age(a.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(a.order_month, c.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT a.customer_id) AS active_customers
  FROM cohorts c
  JOIN active_months a USING (customer_id)
  GROUP BY c.cohort_month, a.order_month
), curves AS (
  SELECT r.cohort_month,
         r.month_offset,
         s.cohort_size,
         r.active_customers,
         r.active_customers::numeric / NULLIF(s.cohort_size, 0) AS retention_rate
  FROM retained r
  JOIN cohort_sizes s USING (cohort_month)
  WHERE r.month_offset BETWEEN 0 AND 12
), latest_six AS (
  SELECT cohort_month
  FROM cohort_sizes
  ORDER BY cohort_month DESC
  LIMIT 6
)
SELECT cohort_month,
       month_offset,
       cohort_size,
       active_customers,
       ROUND(retention_rate, 4) AS retention_rate
FROM curves
WHERE cohort_month IN (SELECT cohort_month FROM latest_six)
ORDER BY cohort_month DESC, month_offset;
```

Expected grain: one row per `(cohort_month, month_offset)` for the six newest
signup cohorts, with numerator, denominator, and rate. Chart with
`month_offset` on X, `retention_rate` on Y, and `cohort_month` as the series.
The chart itself is explicitly outside SQL; this answer produces the tidy data
to export or pass to a notebook/BI tool.

## Reasoning, safety, and pitfalls

- `active_months` deliberately deduplicates multiple orders by one customer in
  one month.
- Cohort size is all signups in the cohort, not only customers who eventually
  ordered.
- Cast before division to avoid integer truncation.
- A missing row at an offset is different from a zero-rate row. To force a
  complete retention matrix, cross join cohorts to `generate_series(0, 12)` and
  left join activity.
- The seed is synthetic, so chart shape demonstrates technique rather than a
  business retention benchmark.

## Exercise 1 — Calculate retention rates

`cohort_sizes` supplies the denominator and active distinct customers supply the
numerator. Numeric casting prevents integer truncation.

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

## Exercise 2 — Return six tidy curves

The final rows retain cohort month, offset, size, active count, and rate. “Chart
it” is downstream presentation; SQL should preserve the auditable components.

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

## Exercise 3 — Choose a cohort anchor

Signup month measures post-registration behavior; first-order month measures
repeat purchasing. The answer displays both per customer so the semantic choice
is visible.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
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

## Exercise 4 — Complete the cohort grid

Cross joining cohorts with offsets creates every expected cell. A left join
then turns missing observed activity into zero without losing cohort size.

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

## Exercise 5 — Reject negative chronology

The diagnostic returns customers whose first order precedes recorded signup.
Such rows should be corrected or explicitly excluded before retention math.

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

## Exercise 6 — Preserve future unknowns

An offset beyond the latest observed month is not a measured zero. The
`is_observable` flag keeps not-yet-available periods distinct.

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
