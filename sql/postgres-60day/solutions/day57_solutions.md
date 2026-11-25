# Day 57 Solutions: Forecast Accuracy and Anomalies


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day57_solutions.sql
```

Six read-only queries run against `orders`, plus one in-line `VALUES` set for Exercise 6; the spine queries build 1,380 dates and still finish in well under
a second. Results to expect: 2, 20, 30, 2, 20 and 3 rows. Two of them depend
on today's date, as the notes below explain. For the general routine, see
[reading a solution](../../STUDY-GUIDE.md#read-a-solution).

## Clause-by-clause reading map

Walk each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Two choices recur. The first is the population: observed order days, or a
calendar spine where missing days count as zero. The second is time: whether
a calculation may see the day it describes. Exercises 1, 3 and 4 use the
spine; Exercises 2 and 5 do not.

The exercises compare a seven-day moving average with a weekly seasonal naive,
then rank recent positive and negative anomalies using standard-deviation and
MAD scores. See [`day57_solutions.sql`](day57_solutions.sql).

## Exercise 1: Compare MA(7) and lag-7 MAPE

The calendar spine makes “seven days ago” mean seven calendar days, including
days with no orders as zero revenue.

```sql
SET search_path TO training, public;

WITH bounds AS (
  SELECT
    MIN(order_date)::date AS min_day,
    MAX(order_date)::date AS max_day
  FROM
    orders
),
calendar AS (
  SELECT
    day::date
  FROM
    bounds
    CROSS JOIN LATERAL generate_series(min_day, max_day, interval '1 day') AS day
),
daily AS (
  SELECT
    order_date::date AS day,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    order_date::date
),
complete AS (
  SELECT
    c.day,
    COALESCE(d.revenue, 0) AS revenue
  FROM
    calendar c
    LEFT JOIN daily d USING (day)
),
forecasts AS (
  SELECT
    day,
    revenue,
    AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS ma7_forecast,
    LAG(revenue, 7) OVER (ORDER BY day) AS seasonal_naive
  FROM
    complete
)
SELECT
  'MA(7)' AS model,
  ROUND(AVG(ABS(revenue - ma7_forecast) / NULLIF (revenue, 0)), 4) AS mape
FROM
  forecasts
WHERE
  day >= CURRENT_DATE -180
  AND ma7_forecast IS NOT NULL
UNION ALL
SELECT
  'seasonal naive (lag 7)',
  ROUND(AVG(ABS(revenue - seasonal_naive) / NULLIF (revenue, 0)), 4)
FROM
  forecasts
WHERE
  day >= CURRENT_DATE -180
  AND seasonal_naive IS NOT NULL
ORDER BY
  model;
```

Expected shape: two model rows. Zero-revenue days are excluded from MAPE by
`NULLIF`; disclose that choice.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 1, read `orders` into a one-row-per-day calendar spine, calculate `ma7_forecast` and `seasonal_naive` in `forecasts`, and aggregate the final `model` and `mape`; the output grain is model, not order.
- **Expected result/shape:** For sql-57 Exercise 1, expected output: two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice. The final columns are `model` and `mape`. The final order is `model`.
- **Independent verification:** For sql-57 Exercise 1, require exactly two rows with model values `MA(7)` and `seasonal naive (lag 7)` and require unique `model`. Count the `forecasts` rows with `day >= CURRENT_DATE - 180` and a non-NULL forecast for each model (the same 179 days from 2026-05-29 on a run dated 2026-11-25, none with revenue 0) and recompute each `mape` as the average of `ABS(revenue - forecast) / revenue` over them (0.4289 and 0.5329 on the checked load). Then replace `CURRENT_DATE` with `date '2027-06-01'`: no day qualifies, and both model rows still print with `mape` NULL.
- **Intermediate relation check:** `bounds` is one row (2023-02-13 to 2026-11-23 on the load checked on 2026-11-25), `calendar` expands it to 1,380 dates, `daily` has 1,081 order days and `complete` joins them back to 1,380 rows, 299 of them with revenue 0. `forecasts` keeps those 1,380 rows; the first seven have no `seasonal_naive`, and the first has no `ma7_forecast` either.
- **Clause check:** `ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING` averages up to seven earlier spine rows, so a day's forecast never includes that day. `LAG(revenue, 7)` reads the same weekday last week. Each `UNION ALL` branch filters its own forecast for `IS NOT NULL` and applies `day >= CURRENT_DATE -180`, which is date minus an integer number of days.
- **Alternative/trade-off:** Exercise 4's `LATERAL (VALUES ...)` reshaping scores both models from one filtered set of rows. Here the two branches filter separately, which is shorter but could let the models score different days. On this data both branches score the same 179 days, so the comparison is still fair.
- **Edge case:** The window start follows today's date while the data stops at the last order date. Run the file a month after loading and fewer days qualify; run it more than 180 days later and no row qualifies, so `AVG` over nothing returns `NULL` `mape` for both models while both rows still print.

## Exercise 2: Top ten positive and negative anomalies

```sql
SET search_path TO training, public;

WITH daily AS (
  SELECT
    order_date::date AS day,
    SUM(total_amount) AS revenue
  FROM
    orders
  WHERE
    order_date >= CURRENT_TIMESTAMP - interval '6 months'
  GROUP BY
    order_date::date
),
moments AS (
  SELECT
    AVG(revenue) AS mean_revenue,
    STDDEV_SAMP(revenue) AS sd_revenue
  FROM
    daily
),
median AS (
  SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_revenue
  FROM
    daily
),
deviations AS (
  SELECT
    d.*,
    m.median_revenue,
    ABS(d.revenue - m.median_revenue) AS absolute_deviation
  FROM
    daily d
    CROSS JOIN median m
),
mad AS (
  SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY absolute_deviation) AS mad
  FROM
    deviations
),
scored AS (
  SELECT
    d.day,
    d.revenue,
    (d.revenue - mo.mean_revenue) / NULLIF (mo.sd_revenue, 0) AS sd_z,
    0.6745 * (d.revenue - d.median_revenue) / NULLIF (mad.mad, 0) AS modified_z
  FROM
    deviations d
    CROSS JOIN moments mo
    CROSS JOIN mad
),
ranked AS (
  SELECT
    *,
    CASE WHEN revenue >= (
      SELECT
        mean_revenue
      FROM
        moments) THEN
      'positive'
    ELSE
      'negative'
    END AS direction,
    ROW_NUMBER() OVER (PARTITION BY ( CASE WHEN revenue >= (
      SELECT
        mean_revenue
      FROM moments) THEN
        'positive'
      ELSE
        'negative'
      END) ORDER BY ABS(sd_z) + ABS(modified_z) DESC,
    day) AS anomaly_rank
FROM
  scored
)
SELECT
  direction,
  anomaly_rank,
  day,
  ROUND(revenue, 2) AS revenue,
  ROUND(sd_z::numeric, 3) AS sd_z,
  ROUND(modified_z::numeric, 3) AS modified_z
FROM
  ranked
WHERE
  anomaly_rank <= 10
ORDER BY
  direction DESC,
  anomaly_rank;
```

Expected shape: up to ten positive and ten negative rows. The combined absolute
score is a ranking heuristic; it is not a calibrated probability.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 2, read the `orders` placed since `CURRENT_TIMESTAMP - interval '6 months'`, sum `total_amount` per order day in `daily`, take one mean, sample SD, median and MAD over those days, and score each day with `sd_z` and `modified_z`; `direction` records the day's side of the mean and `anomaly_rank` numbers the days within it.
- **Expected result/shape:** For sql-57 Exercise 2, expected output: 20 rows, ten `positive` and ten `negative`, each side ranked 1 to 10 (a side with fewer than ten days would return fewer). The combined absolute score is a ranking heuristic; it is not a calibrated probability. The final columns are `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`. The final order is `direction DESC, anomaly_rank`.
- **Independent verification:** For sql-57 Exercise 2, confirm 20 rows and that `daily` holds 183 days (89 at or above the mean of 4,640.09 and 94 below on the checked load). Both scores are straight-line functions of revenue, so the `positive` list must equal the ten highest-revenue days and the `negative` list the ten lowest; check both with `ORDER BY revenue`. Then move the cutoff to `date_trunc('day', CURRENT_TIMESTAMP) - interval '6 months'`: the partial oldest day 2026-05-25 gets its full 3,758.33 instead of 1,446.62 and leaves the negative list.
- **Intermediate relation check:** `daily` has 183 rows, one per order day since the six-month cutoff. `moments`, `median` and `mad` are single rows: mean 4,640.09, standard deviation 1,750.21, median 4,587.55 and MAD 1,178.73 on the checked load. `deviations`, `scored` and `ranked` keep 183 rows, of which 89 are `positive` and 94 `negative`.
- **Clause check:** `percentile_cont(0.5) WITHIN GROUP (ORDER BY ...)` runs twice: once on revenue for the median and once on `absolute_deviation` for the MAD. `ROW_NUMBER` partitions by the same `CASE` that sets `direction` and orders by `ABS(sd_z) + ABS(modified_z) DESC, day`; `direction DESC` then lists `positive` before `negative`.
- **Alternative/trade-off:** With one global center and spread, both scores are straight-line functions of revenue, so the two top-ten lists are exactly the ten highest and ten lowest revenue days. Sorting by revenue alone (descending for `positive`, ascending for `negative`) would rank them identically. Summing the scores changes the order only when each day has its own baseline, as with the rolling window of Example 1.
- **Edge case:** `CURRENT_TIMESTAMP - interval '6 months'` cuts at a time of day, so the oldest day is partial. On a run at 09:40 UTC on 2026-11-25, 2026-05-25 kept only its orders after 09:40 and scored 1,446.62 against a full-day 3,758.33, landing at negative rank 6. The three sparse final days fill ranks 3 to 5, so neither group is a business incident.

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

### Clause map for Exercise 1: Compare two forecasts without leakage

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

### Clause map for Exercise 2: Rank robust anomaly candidates

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

## Exercise 3: Prove what seven means

The answer calculates `observed_row_lag7` before building a spine and
`calendar_day_lag7` after it. Joining the outputs by date makes any gaps visible.
Neither population is automatically correct; the metric contract decides.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 3, read `orders` twice: `observed_daily` sums revenue only for days that have orders, and `calendar_daily` left-joins those sums onto a `generate_series` spine from `bounds`, with 0 for empty days; apply `LAG(revenue, 7)` to each and join the two by `day`.
- **Expected result/shape:** For sql-57 Exercise 3, expected output: 30 rows, one per calendar `day`, newest first. The final columns are `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`. The final order is `c.day DESC`.
- **Independent verification:** For sql-57 Exercise 3, confirm 30 rows from the last order day back (2026-11-23 to 2026-10-25 on the checked load) with `observed_row_lag7` equal to `calendar_day_lag7` on every row, because no recent day is empty. Remove `LIMIT 30` and count the rows where the lags are `IS DISTINCT FROM` each other: on the checked load 728 of the 1,380 dates, the last on 2025-12-13, made of 435 observed days whose seventh earlier row is not seven days back and 293 empty spine days whose `observed_row_lag7` is NULL.
- **Intermediate relation check:** `observed_daily` and `observed_lag` hold 1,081 rows; `calendar_daily` and `calendar_lag` hold 1,380, including 299 zero days. The final query starts from `calendar_lag` and left-joins `observed_lag`, so all 1,380 dates survive until `LIMIT 30` keeps the newest.
- **Clause check:** `generate_series(bounds.min_day, bounds.max_day, interval '1 day')` returns timestamps, hence `calendar.day::date` in both the projection and the join. `LEFT JOIN observed_lag o USING (day)` leaves `observed_row_lag7` `NULL` on the 299 spine days that have no observed row, which itself shows where the gaps are.
- **Alternative/trade-off:** A self-join `daily d7 ON d7.day = d.day - 7` gets the calendar lag without a spine. It returns `NULL` rather than 0 when the earlier day had no orders, however, so the zero policy has to be stated separately. The spine makes it explicit in one `COALESCE`.
- **Edge case:** The 30 newest rows cannot show the difference, because every day since 2025-12-07 has orders. Replace `LIMIT 30` with a filter on dates up to 2025-12-13, the last day whose two lags disagree, to see the 435 mismatched observed days (on the checked load).

## Exercise 4: Compare MAE, RMSE, and MAPE fairly

`calendar_daily` and `forecasts` repeat the leakage-free foundation.
`common_scoring_rows` uses LATERAL `VALUES` to reshape model columns into
`(model_name, forecast)` rows and requires both forecasts to exist. This gives
both models one evaluation population.

- MAE reports average absolute currency error.
- RMSE squares error before averaging, so large misses receive more weight.
- MAPE reports relative error but is undefined at zero actual.
- `scored_rows` and `zero_actual_rows` disclose denominators and exclusions.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 4, derive `calendar_daily` (one row per date, 0 for days without orders) and `forecasts` from `orders`, keep the last 181 days on which both `ma7` and `seasonal_naive` exist, reshape the two forecasts with `LATERAL VALUES` into `common_scoring_rows` keyed by `day` and `model_name`, and build `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` for each model.
- **Expected result/shape:** For sql-57 Exercise 4, expected output: one row per `model_name`. That gives 2 rows, `MA(7)` and `seasonal naive`, each with 181 `scored_rows` and 0 `zero_actual_rows`; on the checked load MA(7) has MAE 1,340.94, RMSE 1,695.59, and MAPE 0.4284 against 1,715.92, 2,157.43, and 0.5349 for seasonal naive. The final columns are `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`. The final order is `model_name`.
- **Independent verification:** For sql-57 Exercise 4, group `common_scoring_rows` by `model_name` yourself: it holds 362 rows, 181 per model over the same dates, so `scored_rows` and `zero_actual_rows` must match between the models; recompute `mae` as `ROUND(AVG(ABS(error)), 2)`, `rmse` as `ROUND(SQRT(AVG(POWER(error, 2))), 2)`, and `mape` with `NULLIF(actual, 0)`, and compare every value. In a rolled-back transaction delete the orders of the day 30 days before the last order day (15 orders on 2026-10-24 on the checked load): both models keep 181 `scored_rows`, `zero_actual_rows` becomes 1, and `mape` now averages only the 180 nonzero days (0.4268 and 0.5400).
- **Intermediate relation check:** `calendar_daily` and `forecasts` have 1,380 rows. `common_scoring_rows` keeps the 181 days from 2026-05-27 onward, where both forecasts exist, and the `LATERAL VALUES` list doubles them to 362 rows, one per day and model. The final `GROUP BY model_name` returns 2 rows.
- **Clause check:** `CROSS JOIN LATERAL (VALUES ('MA(7)', f.ma7), ('seasonal naive', f.seasonal_naive))` turns two forecast columns into rows. `SQRT(AVG(POWER(error, 2)))` is RMSE, `AVG(ABS(error) / NULLIF(actual, 0))` is MAPE and `COUNT(*) FILTER (WHERE actual = 0)` reports what MAPE skipped.
- **Alternative/trade-off:** One wide row with `mae_ma7`, `mae_naive` and so on avoids the reshape, but every new model then adds three columns instead of one row. The tidy form also makes the equal `scored_rows` values a visible check that both models met the same days.
- **Edge case:** RMSE is about 26% above MAE for both models (1,695.59 against 1,340.94, and 2,157.43 against 1,715.92 on the checked load), so no handful of huge misses drives either error. A zero-revenue day would count in MAE and RMSE but not in MAPE; none falls in this window, hence `zero_actual_rows` 0.

## Exercise 5: Detect a leaky frame

The leaky window ends at `CURRENT ROW`, so the day's actual helps predict itself.
The corrected frame ends at `1 PRECEDING`. Displaying both columns is a direct
proof of the semantic difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 5, read `orders`, sum `total_amount` per observed order day in `daily` (no calendar spine), and compute two seven-row averages over `ORDER BY day`: `leaky_window` ends at `CURRENT ROW` and `forecast_window` ends at `1 PRECEDING`.
- **Expected result/shape:** For sql-57 Exercise 5, expected output: 20 rows, one per observed order `day`, newest first. The final columns are `day`, `revenue`, `leaky_window`, and `forecast_window`. The final order is `day DESC`.
- **Independent verification:** For sql-57 Exercise 5, confirm 20 rows ending at the last order day (2026-11-23 back to 2026-11-04 on the checked load) and that every `leaky_window` equals the `forecast_window` printed one row above it; recompute the newest `forecast_window` as the plain average of the seven previous days' revenue (2,300.43 on the checked load). Then, in a rolled-back transaction, add 700 to the `total_amount` of the newest day's only order: its `leaky_window` rises by exactly 100, from 2,079.31 to 2,179.31, while its `forecast_window` stays 2,300.43.
- **Intermediate relation check:** `daily` has 1,081 rows, one per observed order day, with no spine. The final query keeps them all for both window columns and returns the 20 newest. The last 20 calendar days all have orders, so observed rows and calendar days coincide here.
- **Clause check:** Both frames are seven rows wide. `6 PRECEDING AND CURRENT ROW` includes the day being predicted; `7 PRECEDING AND 1 PRECEDING` stops the day before. The leaky frame is the honest forecast for the following day, shifted by one row.
- **Alternative/trade-off:** `LAG(leaky_window) OVER (ORDER BY day)` reproduces `forecast_window` exactly. That makes it a useful test: if a supposed forecast column equals the lagged version of itself shifted forward, the frame contains the target.
- **Edge case:** Over the same 181 days as Exercise 4, the leaky frame scores MAE 1,176.69 and MAPE 0.3696 against the honest 1,340.94 and 0.4284. The smaller numbers are not a better model, just a model that sees the answer. On the first observed day `forecast_window` is `NULL`, while the leaky frame averages one value.

## Exercise 6: Preserve undefined zero-dispersion scores

The constant three-day fixture has standard deviation and MAD equal to zero.
Both score formulas divide by `NULLIF(dispersion, 0)`, yielding NULL. That means
“this scoring method is undefined for this population,” not “the observation is
normal.”

### Reasoning and verification

- **Inputs/evidence:** For sql-57 Exercise 6, read only the three-row `VALUES` fixture `constant` (revenue 100 on 2026-01-01, 2026-01-02 and 2026-01-03); `center` takes its median, mean and sample SD, `deviations` measures each day's distance from the median, and `dispersion` takes the MAD.
- **Expected result/shape:** For sql-57 Exercise 6, expected output: three rows, one per fixture `day`, each with revenue 100 and both scores NULL. The final columns are `day`, `revenue`, `sd_z`, and `modified_mad_z`. The final order is `d.day`.
- **Independent verification:** For sql-57 Exercise 6, confirm 3 rows with NULL `sd_z` and `modified_mad_z`, `center` showing SD 0 and `dispersion` showing MAD 0. Append `(date '2026-01-04', 101)`: `sd_z` becomes -0.5 for the three old days and 1.5 for the new one, while `modified_mad_z` stays NULL because three of the four deviations are 0. Make the values 100, 100, 101 and 101 and both scores are defined: `sd_z` is -0.8660 or 0.8660 and `modified_mad_z` -0.6745 or 0.6745.
- **Intermediate relation check:** `constant` holds 3 rows, `center` 1 row (median 100, mean 100, standard deviation 0), `deviations` 3 rows with `absolute_deviation` 0 and `dispersion` 1 row with MAD 0. The final query returns the 3 days.
- **Clause check:** `NULLIF(d.sd_revenue, 0)` and `NULLIF(p.mad, 0)` turn a zero spread into `NULL`, and any division by `NULL` is `NULL`. Without them PostgreSQL stops with `ERROR: division by zero`, which in a long file aborts the rest of the run.
- **Alternative/trade-off:** A `CASE` that returns 0, as the learner examples do, keeps the file running but labels every day normal. Adding a text column such as `'undefined'` keeps the `NULL` score and states the reason, which reads better in a report.
- **Edge case:** Add a fourth value of 101: the standard deviation becomes 0.5, giving `sd_z` of -0.5 and 1.5, but the deviations 0, 0, 0 and 1 still have median 0. The MAD score stays undefined until roughly half the values differ from the median.