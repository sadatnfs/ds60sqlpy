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

WITH monthly_observed AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), bounds AS (
  SELECT MIN(month) AS first_month, MAX(month) AS last_month
  FROM monthly_observed
), month_spine AS (
  SELECT generate_series(
           first_month, last_month, interval '1 month'
         )::date AS month
  FROM bounds
), monthly_complete AS (
  SELECT spine.month,
         COALESCE(observed.revenue, 0::numeric) AS revenue,
         observed.month IS NOT NULL AS had_source_rows
  FROM month_spine spine
  LEFT JOIN monthly_observed observed USING (month)
), forecast_rows AS (
  SELECT month,
         revenue,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
         ) AS ma6_forecast,
         COUNT(revenue) OVER (
           ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
         ) AS ma6_history_rows,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
         ) AS ma12_forecast,
         COUNT(revenue) OVER (
           ORDER BY month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
         ) AS ma12_history_rows,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive
  FROM monthly_complete
), common_scoring_rows AS (
  SELECT month,
         revenue,
         ma6_forecast,
         ma12_forecast,
         seasonal_naive,
         0.5 * seasonal_naive + 0.5 * ma6_forecast AS blended_forecast
  FROM forecast_rows
  WHERE ma6_history_rows = 6
    AND ma12_history_rows = 12
    AND seasonal_naive IS NOT NULL
), model_scores AS (
  SELECT rows.month,
         rows.revenue,
         model.model,
         model.forecast
  FROM common_scoring_rows rows
  CROSS JOIN LATERAL (
    VALUES
      ('MA(6)'::text, rows.ma6_forecast),
      ('MA(12)', rows.ma12_forecast),
      ('seasonal naive', rows.seasonal_naive),
      ('50% seasonal + 50% MA(6)', rows.blended_forecast)
  ) AS model(model, forecast)
)
SELECT model,
       COUNT(*) FILTER (WHERE revenue <> 0) AS scored_rows,
       COUNT(*) FILTER (WHERE revenue = 0) AS zero_actual_rows,
       ROUND(AVG(ABS(revenue - forecast) / NULLIF(revenue, 0)), 4) AS mape
FROM model_scores
GROUP BY model
ORDER BY model;
```

Expected shape: four model rows scored on the identical complete-history month
set. `scored_rows` and `zero_actual_rows` make the MAPE denominator explicit.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 1, aggregate `orders` by observed month, left-join to `month_spine`, compute full-window history counts, and reshape four forecasts over `common_scoring_rows`.
- **Expected result/shape:** For sql-49 Exercise 1, expected output: exactly four rows keyed by `model`, with `scored_rows`, `zero_actual_rows`, and `mape`, ordered by `model`.
- **Independent verification:** For sql-49 Exercise 1, require `ma6_history_rows = 6`, `ma12_history_rows = 12`, and a non-NULL twelve-month seasonal value before any model is scored. All four models must have identical eligible months and equal `scored_rows`; independently recompute each MAPE.
- **Intermediate relation check:** For sql-49 Exercise 1, inspect `month_spine`, `monthly_complete`, `forecast_rows`, and `common_scoring_rows`; prove no calendar month is missing and warm-up rows are excluded.
- **Clause check:** For sql-49 Exercise 1, full `ROWS` frames provide prior observations, the counts reject partial warm-up frames, `LAG(..., 12)` now means twelve calendar months because the spine is dense, and the lateral `VALUES` block establishes model grain.
- **Alternative/trade-off:** For sql-49 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected shape: four model rows. Evaluate another form against the concrete expected result (four model rows. Lower MAPE is better on the months each model can score) and the verification above.
- **Edge case:** Remove an observed month; `monthly_complete` must retain it as zero revenue, and all four models must still use the same complete-history scoring months.

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

- **Inputs/evidence:** For sql-49 Exercise 2, read from `orders`. Build the answer toward `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-49 Exercise 2, expected output: one row per `month`. The final columns are `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`. The final order is `month DESC`.
- **Independent verification:** For sql-49 Exercise 2, run an anti-check that counts rows where NOT ((seasonal_naive IS NOT NULL)); require unique `month` where the expected grain is one row per key and confirm the projected `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast` against `orders`. Add one row for which `(seasonal_naive IS NOT NULL)` is true and one for which it is false; verify only the matching `month` value is returned.
- **Intermediate relation check:** For sql-49 Exercise 2, run `monthly`, and `forecasted` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-49 Exercise 2, the solution actually uses `WITH`, `FROM`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `month`, and finish with `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast` ordered by `month DESC`.
- **Alternative/trade-off:** For sql-49 Exercise 2, the chosen form is justified by this lesson-specific rationale: Produce a 50/50 seasonal/MA(6) forecast.. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Add one row for which `(seasonal_naive IS NOT NULL)` is true and one for which it is false; verify only the matching `month` value is returned.

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

- **Inputs/evidence:** For sql-49 Exercise 3, read from `orders`. Build the answer toward `month`, `revenue`, `leaky_ma6`, and `honest_ma6`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-49 Exercise 3, expected output: one row per `month`. The final columns are `month`, `revenue`, `leaky_ma6`, and `honest_ma6`. The final order is `month`.
- **Independent verification:** For sql-49 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, `leaky_ma6`, and `honest_ma6`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-49 Exercise 3, run `monthly` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-49 Exercise 3, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `month`, and finish with `month`, `revenue`, `leaky_ma6`, and `honest_ma6` ordered by `month`.
- **Alternative/trade-off:** For sql-49 Exercise 3, the chosen form is justified by this lesson-specific rationale: The leaky frame includes `CURRENT ROW`; the honest MA(6) frame uses six preceding rows and stops at `1 PRECEDING`. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 4 — Build a monthly spine

`generate_series` establishes one row per calendar month before the 12-row lag.
The separate source-present flag distinguishes no row from a chosen zero policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 4, read from `orders`. Build the answer toward `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-49 Exercise 4, expected output: one row per calendar month before the 12-row lag. The final columns are `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`. The final order is `month`.
- **Independent verification:** For sql-49 Exercise 4, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, and `had_source_rows`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
- **Intermediate relation check:** For sql-49 Exercise 4, run `bounds`, `spine`, `actual`, and `complete` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-49 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `month`, and finish with `month`, `revenue`, `had_source_rows`, and `seasonal_forecast` ordered by `month`.
- **Alternative/trade-off:** For sql-49 Exercise 4, the chosen form is justified by this lesson-specific rationale: `generate_series` establishes one row per calendar month before the 12-row lag. Evaluate another form against the concrete expected result (one row per calendar month before the 12-row lag) and the verification above.
- **Edge case:** Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Exercise 5 — Report the MAPE denominator

`NULLIF(actual, 0)` excludes undefined percentage errors, and FILTER counts
both scored and excluded observations. Never publish MAPE without that context.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 5, read from `toy`. Build the answer toward `mape`, `scored_rows`, and `excluded_zero_actuals`; keep `mape` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-49 Exercise 5, expected output: one row per `mape`. The final columns are `mape`, `scored_rows`, and `excluded_zero_actuals`.
- **Independent verification:** For sql-49 Exercise 5, reselect the returned keys directly from the source; require unique `mape` where the expected grain is one row per key and confirm the projected `mape`, `scored_rows`, and `excluded_zero_actuals` against `toy`. Add one source row with a new `mape`; verify the result gains exactly one row carrying that `mape` value.
- **Intermediate relation check:** For sql-49 Exercise 5, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-49 Exercise 5, the solution actually uses `WITH`, `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `toy`, preserve one row per `mape`, and finish with `mape`, `scored_rows`, and `excluded_zero_actuals`.
- **Alternative/trade-off:** For sql-49 Exercise 5, the chosen form is justified by this lesson-specific rationale: `NULLIF(actual, 0)` excludes undefined percentage errors, and FILTER counts both scored and excluded observations. Evaluate another form against the concrete expected result (one row per `mape`) and the verification above.
- **Edge case:** Add one source row with a new `mape`; verify the result gains exactly one row carrying that `mape` value.

## Exercise 6 — Compare MAE and MAPE

The deterministic fixture shows that MAE reflects currency-scale error while
MAPE can be dominated by a modest miss on a very small actual.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 6, read from `toy`. Build the answer toward `mae`, and `mape`; keep `mae` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-49 Exercise 6, expected output: one row per `mae`. The final columns are `mae`, and `mape`.
- **Independent verification:** For sql-49 Exercise 6, reselect the returned keys directly from the source; require unique `mae` where the expected grain is one row per key and confirm the projected `mae`, and `mape` against `toy`. Add one source row with a new `mae`; verify the result gains exactly one row carrying that `mae` value.
- **Intermediate relation check:** For sql-49 Exercise 6, select `mae` from `toy` before adding derived columns.
- **Clause check:** For sql-49 Exercise 6, the solution actually uses `WITH`, `FROM`, and `SELECT`. Read only those operations: begin at `toy`, preserve one row per `mae`, and finish with `mae`, and `mape`.
- **Alternative/trade-off:** For sql-49 Exercise 6, the chosen form is justified by this lesson-specific rationale: The deterministic fixture shows that MAE reflects currency-scale error while MAPE can be dominated by a modest miss on a very small actual. Evaluate another form against the concrete expected result (one row per `mae`) and the verification above.
- **Edge case:** Add one source row with a new `mae`; verify the result gains exactly one row carrying that `mae` value.
