# Day 57 Solutions — Forecast Accuracy and Anomalies


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day57_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day57_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Seasonal naive, MAD, Anomaly candidate. Its worked-model focus is:
Build a complete daily spine before LAG(revenue, 7) so the offset means seven calendar days. Calculate a trailing forecast that excludes the current actual, then score the same six-month rows. For anomaly output, retain raw revenue, center, dispersion, and both scores beside the rank.

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

The exercises compare a seven-day moving average with a weekly seasonal naive,
then rank recent positive and negative anomalies using standard-deviation and
MAD scores. See [`day57_solutions.sql`](day57_solutions.sql).

## Exercise 1 — Compare MA(7) and lag-7 MAPE

The calendar spine makes “seven days ago” mean seven calendar days, including
days with no orders as zero revenue.

```sql
SET search_path TO training, public;

WITH bounds AS (
  SELECT MIN(order_date)::date AS min_day,
         MAX(order_date)::date AS max_day
  FROM orders
), calendar AS (
  SELECT day::date
  FROM bounds
  CROSS JOIN LATERAL generate_series(min_day, max_day, interval '1 day') AS day
), daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), complete AS (
  SELECT c.day, COALESCE(d.revenue, 0) AS revenue
  FROM calendar c
  LEFT JOIN daily d USING (day)
), forecasts AS (
  SELECT day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
         ) AS ma7_forecast,
         LAG(revenue, 7) OVER (ORDER BY day) AS seasonal_naive
  FROM complete
)
SELECT 'MA(7)' AS model,
       ROUND(AVG(ABS(revenue - ma7_forecast) / NULLIF(revenue, 0)), 4) AS mape
FROM forecasts
WHERE day >= CURRENT_DATE - 180
  AND ma7_forecast IS NOT NULL
UNION ALL
SELECT 'seasonal naive (lag 7)',
       ROUND(AVG(ABS(revenue - seasonal_naive) / NULLIF(revenue, 0)), 4)
FROM forecasts
WHERE day >= CURRENT_DATE - 180
  AND seasonal_naive IS NOT NULL
ORDER BY model;
```

Expected shape: two model rows. Zero-revenue days are excluded from MAPE by
`NULLIF`; disclose that choice.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 1, read `orders` into a one-row-per-day calendar spine, calculate `ma7_forecast` and `seasonal_naive` in `forecasts`, and aggregate the final `model` and `mape`; the output grain is model, not order.
- **Expected result/shape:** For sql-57 Exercise 1, expected output: two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice. The final columns are `model`, and `mape`. The final order is `model`.
- **Independent verification:** For sql-57 Exercise 1, require exactly two rows with model values `MA(7)` and `seasonal naive (lag 7)` and require unique `model`. From the same `forecasts` rows and 180-day evaluation window, independently recompute each model's absolute percentage-error numerator and eligible denominator, compare the resulting `mape`, and disclose that zero-revenue days and NULL forecasts are excluded.
- **Intermediate relation check:** For sql-57 Exercise 1, run `bounds`, `calendar`, `daily`, `complete`, and `forecasts` one at a time. Confirm that `calendar`, `complete`, and `forecasts` have unique `day` values before the final aggregation changes the grain to model.
- **Clause check:** For sql-57 Exercise 1, the solution uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, `UNION ALL`, and `ORDER BY`. It begins at `orders`, establishes one row per `day`, and then returns one aggregate row per `model` ordered by `model`.
- **Alternative/trade-off:** For sql-57 Exercise 1, the chosen form is justified by this lesson-specific rationale: The calendar spine makes “seven days ago” mean seven calendar days, including days with no orders as zero revenue. Evaluate another form against the concrete expected result (two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice) and the verification above.
- **Edge case:** If every eligible actual is zero, MAPE is NULL because its denominator is empty after `NULLIF`; report that state rather than replacing it with zero.

## Exercise 2 — Top ten positive and negative anomalies

```sql
SET search_path TO training, public;

WITH daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '6 months'
  GROUP BY order_date::date
), moments AS (
  SELECT AVG(revenue) AS mean_revenue,
         STDDEV_SAMP(revenue) AS sd_revenue
  FROM daily
), median AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_revenue
  FROM daily
), deviations AS (
  SELECT d.*,
         m.median_revenue,
         ABS(d.revenue - m.median_revenue) AS absolute_deviation
  FROM daily d
  CROSS JOIN median m
), mad AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY absolute_deviation) AS mad
  FROM deviations
), scored AS (
  SELECT d.day,
         d.revenue,
         (d.revenue - mo.mean_revenue) / NULLIF(mo.sd_revenue, 0) AS sd_z,
         0.6745 * (d.revenue - d.median_revenue) / NULLIF(mad.mad, 0)
           AS modified_z
  FROM deviations d
  CROSS JOIN moments mo
  CROSS JOIN mad
), ranked AS (
  SELECT *,
         CASE WHEN revenue >= (SELECT mean_revenue FROM moments)
              THEN 'positive' ELSE 'negative' END AS direction,
         ROW_NUMBER() OVER (
           PARTITION BY (
             CASE WHEN revenue >= (SELECT mean_revenue FROM moments)
                  THEN 'positive' ELSE 'negative' END
           )
           ORDER BY ABS(sd_z) + ABS(modified_z) DESC, day
         ) AS anomaly_rank
  FROM scored
)
SELECT direction,
       anomaly_rank,
       day,
       ROUND(revenue, 2) AS revenue,
       ROUND(sd_z::numeric, 3) AS sd_z,
       ROUND(modified_z::numeric, 3) AS modified_z
FROM ranked
WHERE anomaly_rank <= 10
ORDER BY direction DESC, anomaly_rank;
```

Expected shape: up to ten positive and ten negative rows. The combined absolute
score is a ranking heuristic; it is not a calibrated probability.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 2, read from `orders`. Build the answer toward `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`; keep `day` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-57 Exercise 2, expected output: up to ten positive and ten negative rows. The combined absolute score is a ranking heuristic; it is not a calibrated probability. The final columns are `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`. The final order is `direction DESC, anomaly_rank`.
- **Independent verification:** For sql-57 Exercise 2, project `day` plus the raw source columns from `orders` at each join stage; record row count and distinct `day`, then assert the final `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z` values match those staged rows without unintended fanout or loss. Give two rows the same `direction DESC` value and different `anomaly_rank` values; verify `direction DESC, anomaly_rank` produces the intended rank and display order.
- **Intermediate relation check:** For sql-57 Exercise 2, run `daily`, `moments`, `median`, `deviations`, `mad`, `scored`, and `ranked` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
- **Clause check:** For sql-57 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `day`, and finish with `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z` ordered by `direction DESC, anomaly_rank`.
- **Alternative/trade-off:** For sql-57 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected shape: up to ten positive and ten negative rows. Evaluate another form against the concrete expected result (up to ten positive and ten negative rows. The combined absolute score is a ranking heuristic; it is not a calibrated probability) and the verification above.
- **Edge case:** Give two rows the same `direction DESC` value and different `anomaly_rank` values; verify `direction DESC, anomaly_rank` produces the intended rank and display order.

## Reasoning, safety, and pitfalls

- A moving average must exclude the current day to avoid leakage.
- The SD score is sensitive to extreme values; the MAD score is more robust.
- `NULLIF` handles zero dispersion. An undefined score should not be silently
  relabeled zero.
- The anomaly query groups only days with orders, unlike the forecast query's
  complete calendar. Choose and document the intended population.
- Anomaly detection flags candidates for investigation, not proven incidents.

## Annotated query anatomy

The exact runnable answers are in
[`day57_solutions.sql`](day57_solutions.sql). The notes below explain why every
stage exists, so the query can be rebuilt rather than memorized.

### Clause map for Exercise 1 — Compare two forecasts without leakage

- `bounds` finds the observed date extent; it avoids assuming that course data
  ends today.
- `calendar` generates one row per date. Without it, `LAG(..., 7)` means seven
  observed rows rather than seven calendar days.
- `daily` aggregates orders to the forecasting grain: one amount per date.
- `complete` left-joins those amounts to the calendar and makes the explicit
  policy choice that no-order days have zero revenue.
- `forecasts` calculates MA(7) over `7 PRECEDING` through `1 PRECEDING`, which
  excludes the target actual. It also calculates the weekly seasonal naive with
  `LAG(revenue, 7)`.
- The two final SELECT branches use the same window and eligibility rules.
  `NULLIF(revenue, 0)` removes undefined percentage errors; that exclusion must
  be reported.

`UNION ALL` retains one row per model. `ORDER BY model` makes the small result
stable but has no analytical effect.

### Clause map for Exercise 2 — Rank robust anomaly candidates

- `daily` establishes one observation per represented order date.
- `moments` calculates the mean and sample standard deviation used by the
  conventional z-score.
- `median` calculates the robust center.
- `deviations` retains the raw value, center, and absolute distance for audit.
- `mad` takes the median of those distances, producing median absolute
  deviation.
- `scored` computes both scores and uses `NULLIF` for zero dispersion.
- `ranked` separates positive and negative direction, then applies a
  deterministic row number. The combined absolute score is a ranking heuristic,
  not a probability.

The final filter keeps ten per direction *after* ranking. Ordering direction
then rank makes review reproducible.

## Exercise 3 — Prove what seven means

The answer calculates `observed_row_lag7` before building a spine and
`calendar_day_lag7` after it. Joining the outputs by date makes any gaps visible.
Neither population is automatically correct; the metric contract decides.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 3, read from `orders`. Build the answer toward `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`; keep `day` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-57 Exercise 3, expected output: at most 30 rows keyed by `day`. The final columns are `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`. The final order is `c.day DESC`.
- **Independent verification:** For sql-57 Exercise 3, assert no more than 30 rows, no duplicate `day`, and no adjacent pair that violates `c.day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7` came from the same source rows. Run with 30 minus one and 30 plus one eligible rows; require the output cap of 30 while retaining `c.day DESC`.
- **Intermediate relation check:** For sql-57 Exercise 3, run `bounds`, `observed_daily`, `observed_lag`, `calendar_daily`, and `calendar_lag` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
- **Clause check:** For sql-57 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `day`, and finish with `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7` ordered by `c.day DESC`.
- **Alternative/trade-off:** For sql-57 Exercise 3, the chosen form is justified by this lesson-specific rationale: The answer calculates `observed_row_lag7` before building a spine and `calendar_day_lag7` after it. Evaluate another form against the concrete expected result (at most 30 rows keyed by `day`) and the verification above.
- **Edge case:** Run with 30 minus one and 30 plus one eligible rows; require the output cap of 30 while retaining `c.day DESC`.

## Exercise 4 — Compare MAE, RMSE, and MAPE fairly

`calendar_daily` and `forecasts` repeat the leakage-free foundation.
`common_scoring_rows` uses LATERAL `VALUES` to reshape model columns into
`(model_name, forecast)` rows and requires both forecasts to exist. This gives
both models one evaluation population.

- MAE reports average absolute currency error.
- RMSE squares error before averaging, so large misses receive more weight.
- MAPE reports relative error but is undefined at zero actual.
- `scored_rows` and `zero_actual_rows` disclose denominators and exclusions.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 4, derive `common_scoring_rows` from `orders`, reshape both forecasts to `model_name` rows, and build `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`; keep `model_name` as the final grouping key.
- **Expected result/shape:** For sql-57 Exercise 4, expected output: one row per `model_name`. The final columns are `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`. The final order is `model_name`.
- **Independent verification:** For sql-57 Exercise 4, independently aggregate `common_scoring_rows` by `model_name` and require exactly two unique `model_name` rows. Require both models to have the same `scored_rows` and `zero_actual_rows` because they share one evaluation population; recompute `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` for each model and compare every value, preserving NULL `mape` when the eligible percentage-error denominator is zero.
- **Intermediate relation check:** For sql-57 Exercise 4, run `bounds`, `daily`, `calendar_daily`, `forecasts`, and `common_scoring_rows` one at a time. Record each CTE's row count and `model_name` uniqueness before the next stage uses it.
- **Clause check:** For sql-57 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `model_name`, and finish with `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` ordered by `model_name`.
- **Alternative/trade-off:** For sql-57 Exercise 4, the chosen form is justified by this lesson-specific rationale: `calendar_daily` and `forecasts` repeat the leakage-free foundation. Evaluate another form against the concrete expected result (one row per `model_name`) and the verification above.
- **Edge case:** A zero-revenue day remains in `scored_rows` and `zero_actual_rows`, contributes to MAE and RMSE, and contributes no percentage term to MAPE.

## Exercise 5 — Detect a leaky frame

The leaky window ends at `CURRENT ROW`, so the day's actual helps predict itself.
The corrected frame ends at `1 PRECEDING`. Displaying both columns is a direct
proof of the semantic difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 5, read from `orders`. Build the answer toward `day`, `revenue`, `leaky_window`, and `forecast_window`; keep `day` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-57 Exercise 5, expected output: at most 20 rows keyed by `day`. The final columns are `day`, `revenue`, `leaky_window`, and `forecast_window`. The final order is `day DESC`.
- **Independent verification:** For sql-57 Exercise 5, assert no more than 20 rows, no duplicate `day`, and no adjacent pair that violates `day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, `leaky_window`, and `forecast_window` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.
- **Intermediate relation check:** For sql-57 Exercise 5, run `daily` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
- **Clause check:** For sql-57 Exercise 5, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `day`, and finish with `day`, `revenue`, `leaky_window`, and `forecast_window` ordered by `day DESC`.
- **Alternative/trade-off:** For sql-57 Exercise 5, the chosen form is justified by this lesson-specific rationale: The leaky window ends at `CURRENT ROW`, so the day's actual helps predict itself. Evaluate another form against the concrete expected result (at most 20 rows keyed by `day`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.

## Exercise 6 — Preserve undefined zero-dispersion scores

The constant three-day fixture has standard deviation and MAD equal to zero.
Both score formulas divide by `NULLIF(dispersion, 0)`, yielding NULL. That means
“this scoring method is undefined for this population,” not “the observation is
normal.”

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 6, read from `constant`. Build the answer toward `day`, `revenue`, `sd_z`, and `modified_mad_z`; keep `day` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-57 Exercise 6, expected output: one row per `day`. The final columns are `day`, `revenue`, `sd_z`, and `modified_mad_z`. The final order is `d.day`.
- **Independent verification:** For sql-57 Exercise 6, project `day` plus the raw source columns from `constant` at each join stage; record row count and distinct `day`, then assert the final `day`, `revenue`, `sd_z`, and `modified_mad_z` values match those staged rows without unintended fanout or loss. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
- **Intermediate relation check:** For sql-57 Exercise 6, run `center`, `deviations`, and `dispersion` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
- **Clause check:** For sql-57 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `constant`, preserve one row per `day`, and finish with `day`, `revenue`, `sd_z`, and `modified_mad_z` ordered by `d.day`.
- **Alternative/trade-off:** For sql-57 Exercise 6, the chosen form is justified by this lesson-specific rationale: The constant three-day fixture has standard deviation and MAD equal to zero. Evaluate another form against the concrete expected result (one row per `day`) and the verification above.
- **Edge case:** Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
