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

- **Expected result/shape:** Exercise 1 requires a written prediction and the observed result for “Compare MA(7) with calendar-week seasonal naive using MAPE”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `day`, `revenue`, `ma7_forecast`, `seasonal_naive`, `model`, `mape`, `ma`.
- **Independent verification:** For Exercise 1, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 1: compare prior-seven-day average with seven-day seasonal naive.
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

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Rank positive/negative anomalies with SD and MAD scores” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `absolute_deviation`, `mad`, `sd_z`, `modified_z`, `direction`, `anomaly_rank`, `sd`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: rank positive and negative anomalies using both standard and median-absolute-deviation scores.
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

- **Expected result/shape:** Exercise 3 requires a written prediction and the observed result for “Predict how removing the date spine changes LAG(..., 7)”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `max_day`, `day`, `revenue`, `observed_row_lag7`, `calendar`, `calendar_day_lag7`, `lag`.
- **Independent verification:** For Exercise 3, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 3: show exactly why the calendar spine matters. observeddaily has one row only when orders exist, so LAG(..., 7) means “seven prior observations.” calendardaily has one row per calendar date, so the same offset means “seven calendar days.”
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

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Compare MAE, RMSE, MAPE, and scored-row counts on one window”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `error`, `model`, `scored_rows`, `mae`, `rmse`, `mape`, `zero_actual_rows`.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: score both forecast models on one identical evaluation set. 1. calendardaily establishes one row per date and a documented zero policy. 2. forecasts uses only prior rows: MA(7) ends at 1 PRECEDING, while the seasonal model reads exactly seven calendar rows back. 3. LATERAL VALUES reshapes the two model columns to a common tidy model grain. 4. The WHERE clause requires both forecasts, so model comparisons use the same dates. MAPE additionally excludes zero actuals through NULLIF.
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

## Exercise 5 — Detect a leaky frame

The leaky window ends at `CURRENT ROW`, so the day's actual helps predict itself.
The corrected frame ends at `1 PRECEDING`. Displaying both columns is a direct
proof of the semantic difference.

### Reasoning and verification

- **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Detect and remove current-row forecast leakage” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `day`, `revenue`, `leaky_window`, `forecast_window`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 5, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 5: place the leaky and honest frames side by side. The leaky result includes the current actual, so it is not a forecast of that day. The honest frame ends at 1 PRECEDING and can be computed before the target is known.
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

## Exercise 6 — Preserve undefined zero-dispersion scores

The constant three-day fixture has standard deviation and MAD equal to zero.
Both score formulas divide by `NULLIF(dispersion, 0)`, yielding NULL. That means
“this scoring method is undefined for this population,” not “the observation is
normal.”

### Reasoning and verification

- **Expected result/shape:** Exercise 6 requires a written prediction and the observed result for “Preserve undefined scores for a constant series. Compare absent no-order days with explicit zero-revenue days”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `median_revenue`, `mean_revenue`, `sd_revenue`, `absolute_deviation`, `mad`, `sd_z`, `modified_mad_z`.
- **Independent verification:** For Exercise 6, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 6: constant data has zero SD and zero MAD. Both denominators use NULLIF, preserving an undefined score as NULL instead of declaring the points “normal” with a fabricated zero score.
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
