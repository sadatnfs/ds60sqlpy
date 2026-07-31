# Day 40 — Solutions: Advanced Analytic Functions


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day40_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day40_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Ordered-set aggregate, Z-score, Interpolation. Its worked-model focus is:
Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive (revenue - avg15) / NULLIF(sd15, 0). Keep the observation count beside the score so early, undersized windows are visible.

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

This day combines statistical aggregates with windows and ordered-set
aggregates. The answers define the input grain before computing statistics.

## Exercise 1 — Fifteen-row rolling z-score for daily revenue

```sql
SET search_path TO training, public;

WITH daily AS (
  SELECT date_trunc('day', order_date)::date AS order_day,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('day', order_date)
), rolling AS (
  SELECT order_day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY order_day
           ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS avg15,
         STDDEV_SAMP(revenue) OVER (
           ORDER BY order_day
           ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS sd15
  FROM daily
)
SELECT order_day,
       ROUND(revenue, 2) AS revenue,
       ROUND(avg15, 2) AS avg15,
       ROUND(sd15, 2) AS sd15,
       ROUND(
         (revenue - avg15) / NULLIF(sd15, 0),
         4
       ) AS z_score
FROM rolling
ORDER BY order_day;
```

Expected shape: one row per day with orders. A positive z-score is above the
rolling mean; a negative score is below it. The first row has no sample standard
deviation, and any zero-standard-deviation frame yields `NULL`.

Assumption: “15-day” in the learner example means 15 observed daily rows. To
model 15 consecutive calendar days, first join revenue to a dense date series
and decide whether missing days mean zero or unknown.

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

## Exercise 2 — Category P50 and P90 of order values

An order can contain several categories. This answer defines an “order total
within a category” as the sum of that category's net lines in that order; using
the whole order total for every category would double-count mixed orders.

```sql
SET search_path TO training, public;

WITH category_order_values AS (
  SELECT p.category,
         oi.order_id,
         SUM(
           oi.unit_price * oi.quantity * (1 - oi.discount)
         ) AS category_order_value
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.order_id
)
SELECT category,
       ROUND(
         PERCENTILE_CONT(0.5) WITHIN GROUP (
           ORDER BY category_order_value
         )::numeric,
         2
       ) AS p50_order_value,
       ROUND(
         PERCENTILE_CONT(0.9) WITHIN GROUP (
           ORDER BY category_order_value
         )::numeric,
         2
       ) AS p90_order_value,
       COUNT(*) AS category_orders
FROM category_order_values
GROUP BY category
ORDER BY category;
```

Expected shape: one row per sold category. `PERCENTILE_CONT` can interpolate
between observed values, so a percentile need not equal an actual order value.

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

## Pitfalls

- `STDDEV_SAMP` is `NULL` for a one-row frame. `NULLIF(sd15, 0)` also protects
  constant frames from division by zero.
- A `ROWS` frame counts rows, not elapsed time.
- Ordered-set aggregates such as `PERCENTILE_CONT` use `WITHIN GROUP`; they are
  not written with `OVER` in this grouped query.
- Define the analytical grain before calculating a percentile. Line-level and
  order-level percentiles answer different questions.

## Exercise 3 — Compare discrete and continuous medians

For four values, the discrete median chooses an observed central value while the
continuous median interpolates. The runnable `VALUES` fixture makes the
difference deterministic.

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

## Exercise 4 — Share and rank within month

Revenue is first aggregated to month/category grain. The denominator window
partitions by month, and `ROW_NUMBER` adds category as a deterministic tie-break.

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

## Exercise 5 — Remove forecast leakage

The corrected frame is `7 PRECEDING` through `1 PRECEDING`. Ending at the current
row would let the target actual influence its own forecast.

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

## Exercise 6 — Preserve undefined dispersion

The constant fixture has standard deviation zero. `NULLIF(sd, 0)` returns NULL
for every z-score, accurately distinguishing undefined from normal.

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
