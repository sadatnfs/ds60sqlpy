# Day 49 Solutions — Revenue Forecast Backtesting


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day49_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day49_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Backtest, Target leakage, MAPE. Its worked-model focus is:
At complete monthly grain, compute MA(6) with a frame ending at 1 PRECEDING, place it beside actual revenue, and score only months with a forecast and nonzero actual. Compare seasonal naive on that same scoring set and retain the number of evaluated months.

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

The exercises compare moving-average and seasonal-naive forecasts, then inspect
a 50/50 blend. These are historical backtests, not a production forecasting
model. See [`day49_solutions.sql`](day49_solutions.sql).

## Exercise 1 — MA(6), MA(12), seasonal naive, and MAPE

```sql
SET search_path TO training, public;

WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), forecasts AS (
  SELECT month,
         revenue,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
         ) AS ma6_forecast,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
         ) AS ma12_forecast,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive
  FROM monthly
), scored AS (
  SELECT *,
         ABS(revenue - ma6_forecast) / NULLIF(revenue, 0) AS ape_ma6,
         ABS(revenue - ma12_forecast) / NULLIF(revenue, 0) AS ape_ma12,
         ABS(revenue - seasonal_naive) / NULLIF(revenue, 0) AS ape_seasonal,
         0.5 * seasonal_naive + 0.5 * ma6_forecast AS blended_forecast
  FROM forecasts
)
SELECT 'MA(6)' AS model, ROUND(AVG(ape_ma6), 4) AS mape
FROM scored
WHERE ma6_forecast IS NOT NULL
UNION ALL
SELECT 'MA(12)', ROUND(AVG(ape_ma12), 4)
FROM scored
WHERE ma12_forecast IS NOT NULL
UNION ALL
SELECT 'seasonal naive', ROUND(AVG(ape_seasonal), 4)
FROM scored
WHERE seasonal_naive IS NOT NULL
UNION ALL
SELECT '50% seasonal + 50% MA(6)',
       ROUND(AVG(ABS(revenue - blended_forecast) / NULLIF(revenue, 0)), 4)
FROM scored
WHERE blended_forecast IS NOT NULL
ORDER BY model;
```

Expected shape: four model rows. Lower MAPE is better on the months each model
can score.

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

## Exercise 2 — Month-by-month blended forecast

```sql
SET search_path TO training, public;

WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), forecasted AS (
  SELECT month,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
         ) AS ma6_forecast
  FROM monthly
)
SELECT month,
       ROUND(revenue, 2) AS actual,
       ROUND(seasonal_naive, 2) AS seasonal_naive,
       ROUND(ma6_forecast, 2) AS ma6_forecast,
       ROUND(0.5 * seasonal_naive + 0.5 * ma6_forecast, 2) AS blended_forecast
FROM forecasted
WHERE seasonal_naive IS NOT NULL
ORDER BY month DESC;
```

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

## Reasoning, safety, and pitfalls

- Every window ends at `1 PRECEDING`; including the current month's actual would
  leak the answer into its forecast.
- `LAG(..., 12)` assumes one row per calendar month. If a month can be absent,
  join to a complete month calendar first.
- MAPE excludes zero actuals via `NULLIF`; disclose how many periods were
  excluded and compare MAE when zeros are common.
- Different models have different warm-up periods, so a rigorous comparison
  should score all models over the same common months.

## Exercise 3 — Expose forecast leakage

The leaky frame includes `CURRENT ROW`; the honest MA(6) frame uses six preceding
rows and stops at `1 PRECEDING`. Side-by-side output makes the bias visible.

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

## Exercise 4 — Build a monthly spine

`generate_series` establishes one row per calendar month before the 12-row lag.
The separate source-present flag distinguishes no row from a chosen zero policy.

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

## Exercise 5 — Report the MAPE denominator

`NULLIF(actual, 0)` excludes undefined percentage errors, and FILTER counts
both scored and excluded observations. Never publish MAPE without that context.

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

## Exercise 6 — Compare MAE and MAPE

The deterministic fixture shows that MAE reflects currency-scale error while
MAPE can be dominated by a modest miss on a very small actual.

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
