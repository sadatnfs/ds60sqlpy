# Day 49 Solutions: Revenue Forecast Backtesting


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day49_solutions.sql
```

Six read-only queries: four over `orders` grouped into 46 months and two over
small `VALUES` lists. The `.sql` file prints 4, 3, 46, 46, 1 and 1 rows; its Exercise 2 differs from the one printed below, and the Exercise 2 notes cover
both versions. Each query finishes in milliseconds. The general routine is in
[reading a solution](../../STUDY-GUIDE.md#read-a-solution).

## Clause-by-clause reading map

Read each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Two questions apply to every forecast here: which months could the model see
when it was made, and which months is it graded on? The frame answers the
first (`... AND 1 PRECEDING`), and a shared filter on history counts answers
the second. The monthly CTE always comes first, so confirm it returns 46 rows
with no repeated month before reading further.

The exercises compare moving-average and seasonal-naive forecasts, then inspect
a 50/50 blend. These are historical backtests, not a production forecasting
model. See [`day49_solutions.sql`](day49_solutions.sql).

## Exercise 1: MA(6), MA(12), seasonal naive, and MAPE

```sql
SET search_path TO training, public;

WITH monthly_observed AS (
  SELECT
    date_trunc('month', order_date)::date AS month,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    date_trunc('month', order_date)
),
bounds AS (
  SELECT
    MIN(month) AS first_month,
    MAX(month) AS last_month
  FROM
    monthly_observed
),
month_spine AS (
  SELECT
    generate_series(first_month, last_month, interval '1 month')::date AS month
  FROM
    bounds
),
monthly_complete AS (
  SELECT
    spine.month,
    COALESCE(observed.revenue, 0::numeric) AS revenue,
    observed.month IS NOT NULL AS had_source_rows
  FROM
    month_spine spine
    LEFT JOIN monthly_observed observed USING (month)
),
forecast_rows AS (
  SELECT
    month,
    revenue,
    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS ma6_forecast,
    COUNT(revenue) OVER (ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS ma6_history_rows,
    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING) AS ma12_forecast,
    COUNT(revenue) OVER (ORDER BY month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING) AS ma12_history_rows,
    LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive
  FROM
    monthly_complete
),
common_scoring_rows AS (
  SELECT
    month,
    revenue,
    ma6_forecast,
    ma12_forecast,
    seasonal_naive,
    0.5 * seasonal_naive + 0.5 * ma6_forecast AS blended_forecast
  FROM
    forecast_rows
  WHERE
    ma6_history_rows = 6
    AND ma12_history_rows = 12
    AND seasonal_naive IS NOT NULL
),
model_scores AS (
  SELECT
    rows.month,
    rows.revenue,
    model.model,
    model.forecast
  FROM
    common_scoring_rows rows
    CROSS JOIN LATERAL (
      VALUES ('MA(6)'::text, rows.ma6_forecast),
        ('MA(12)', rows.ma12_forecast),
        ('seasonal naive', rows.seasonal_naive),
        ('50% seasonal + 50% MA(6)', rows.blended_forecast)) AS model (model, forecast))
SELECT
  model,
  COUNT(*) FILTER (WHERE revenue <> 0) AS scored_rows,
  COUNT(*) FILTER (WHERE revenue = 0) AS zero_actual_rows,
  ROUND(AVG(ABS(revenue - forecast) / NULLIF (revenue, 0)), 4) AS mape
FROM
  model_scores
GROUP BY
  model
ORDER BY
  model;
```

Expected shape: four model rows scored on the identical complete-history month
set. `scored_rows` and `zero_actual_rows` make the MAPE denominator explicit.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 1, aggregate `orders` by observed month, left-join to `month_spine`, compute full-window history counts, and reshape four forecasts over `common_scoring_rows`.
- **Expected result/shape:** For sql-49 Exercise 1, expected output: exactly four rows keyed by `model`, with `scored_rows`, `zero_actual_rows`, and `mape`, ordered by `model`.
- **Independent verification:** For sql-49 Exercise 1, require `ma6_history_rows = 6`, `ma12_history_rows = 12`, and a non-NULL twelve-month seasonal value before any model is scored. All four models must have identical eligible months and equal `scored_rows`; independently recompute each MAPE.
- **Intermediate relation check:** `monthly_observed` has 46 rows and `bounds` one (2023-02-01 to 2026-11-01). `month_spine` and `monthly_complete` also have 46, all with `had_source_rows` true. `forecast_rows` keeps 46, `common_scoring_rows` keeps 34 (2024-02 onward), and the `LATERAL` list turns those into 136 rows, four per month. `GROUP BY model` returns 4.
- **Clause check:** Each `AVG ... ROWS BETWEEN n PRECEDING AND 1 PRECEDING` sits beside a `COUNT` over the same frame. Early frames are short, so `ma6_history_rows` and `ma12_history_rows` say whether an average used a full window, and the `WHERE` in `common_scoring_rows` demands 6 and 12. `NULLIF(revenue, 0)` and the two `FILTER` counts keep a zero month out of MAPE but visible in the output.
- **Alternative/trade-off:** On this dense spine the `ma12_history_rows = 12` test is redundant: a non-NULL `LAG(revenue, 12)` already needs 12 earlier rows, and removing the test leaves all four results unchanged. It still earns its place by stating the rule outright. Grading each model on its own available months instead gives MA(6) 40 months and 0.2519, a number that cannot be compared with the others.
- **Edge case:** Filter June 2025 out of `monthly_observed` and the spine brings it back with revenue 0. Each model then reports 33 `scored_rows` and 1 `zero_actual_rows`, and every MAPE rises (MA(6) to 0.2533) because the zero sits inside later averaging windows. The partial final month matters too: without it MA(6) scores 0.2151.

## Exercise 2: Month-by-month blended forecast

```sql
SET search_path TO training, public;

WITH monthly AS (
  SELECT
    date_trunc('month', order_date)::date AS month,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    date_trunc('month', order_date)
),
forecasted AS (
  SELECT
    month,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive,
    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) AS ma6_forecast
  FROM
    monthly
)
SELECT
  month,
  ROUND(revenue, 2) AS actual,
  ROUND(seasonal_naive, 2) AS seasonal_naive,
  ROUND(ma6_forecast, 2) AS ma6_forecast,
  ROUND(0.5 * seasonal_naive + 0.5 * ma6_forecast, 2) AS blended_forecast
FROM
  forecasted
WHERE
  seasonal_naive IS NOT NULL
ORDER BY
  month DESC;
```

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 2, aggregate `orders` into 46 calendar months in `monthly`, then in `forecasted` add `LAG(revenue, 12)` as `seasonal_naive` and `AVG(revenue)` over `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING` as `ma6_forecast`, and blend them 50/50 for every month that has a value a year earlier.
- **Expected result/shape:** For sql-49 Exercise 2, expected output: 34 rows, one per `month` from 2024-02-01 to 2026-11-01, with columns `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`, ordered by `month DESC`, so the partial current month comes first.
- **Independent verification:** For sql-49 Exercise 2, confirm 34 distinct months and that `forecasted` holds exactly 12 rows with a `NULL` `seasonal_naive` (2023-02 to 2024-01), which the `WHERE` removes. Recompute the oldest row by hand: 2024-02 has `actual` 14,823.22, `seasonal_naive` 1,203.26 from 2023-02, `ma6_forecast` 11,859.69 (the mean of 2023-08 to 2024-01), and `blended_forecast` 6,531.47, their average. Then, in a transaction, delete the 91 orders from 2025-03, rerun, and confirm 33 rows and that 2026-03 now takes 33,302.51 from 2025-02 as its "seasonal" value, a 13-month lag; `ROLLBACK`.
- **Intermediate relation check:** `monthly` has 46 rows and `forecasted` keeps all 46, adding `seasonal_naive` (`NULL` for the first 12) and `ma6_forecast` (`NULL` only for February 2023, then averaging whatever earlier months exist, up to six). The `WHERE` keeps 34 rows.
- **Clause check:** `WHERE seasonal_naive IS NOT NULL` is the only filter. Seasonal naive needs 12 earlier months, so every surviving row also has a full six-month MA window and no separate count check is needed. `ROUND(..., 2)` is applied only in the final `SELECT`, after the blend is computed from unrounded inputs, and `ORDER BY month DESC` puts the partial month first.
- **Alternative/trade-off:** A forward version would forecast the next three calendar months after `CURRENT_DATE`, holding the latest six-month average flat and blending it with each month a year earlier. That answers a planning question, but it cannot be scored yet, its numbers move with the run date, and the flat average includes the partial current month. The month-by-month backtest used here and in the `.sql` file shows the blend's past errors, which is what the comparison needs.
- **Edge case:** The blend inherits both models' lag. In October 2026 it forecast about 97,200 for an actual of 170,179.13; on the partial November row it overshoots instead (about 111,500 against 85,364.67). A month with no orders would vanish from `monthly` entirely, and every 12-row lag after it would then reach back 13 months; Exercise 4's spine prevents that.

## Reasoning, safety, and pitfalls

- Every window ends at `1 PRECEDING`; including the current month's actual would
  leak the answer into its forecast.
- `LAG(..., 12)` assumes one row per calendar month. If a month can be absent,
  join to a complete month calendar first.
- MAPE excludes zero actuals via `NULLIF`; disclose how many periods were
  excluded and compare MAE when zeros are common.
- Different models have different warm-up periods, so a rigorous comparison
  should score all models over the same common months.

## Exercise 3: Expose forecast leakage

The leaky frame includes `CURRENT ROW`; the honest MA(6) frame uses six preceding
rows and stops at `1 PRECEDING`. Side-by-side output makes the bias visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 3, aggregate `orders` into 46 calendar months in `monthly` and compute two six-month averages over the same `ORDER BY month` window: `leaky_ma6` with `ROWS BETWEEN 5 PRECEDING AND CURRENT ROW`, and `honest_ma6` with `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING`.
- **Expected result/shape:** For sql-49 Exercise 3, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, with columns `month`, `revenue`, `leaky_ma6`, and `honest_ma6`, ordered by `month`; only the first row has a `NULL` `honest_ma6`.
- **Independent verification:** For sql-49 Exercise 3, recompute the first three months by hand: 2023-02 has `leaky_ma6` 1,203.26 (its own revenue) and `honest_ma6` `NULL`; 2023-03 has 1,503.345 and 1,203.26; 2023-04 has 2,197.18 and 1,503.345. Then confirm with `LAG(leaky_ma6) OVER (ORDER BY month)` that every row's `honest_ma6` equals the previous row's `leaky_ma6` (0 mismatches over 46 rows), which shows the leaky forecast for a month is the honest one shifted to include the month being forecast. There is no `PARTITION BY`, so there is no partition reset to test; the frame first holds six rows at 2023-07 (leaky) and 2023-08 (honest).
- **Intermediate relation check:** `monthly` has 46 rows, and the final query returns all of them in month order. Nothing is filtered, so the warm-up rows stay visible, including the first, where the honest forecast does not exist yet.
- **Clause check:** `5 PRECEDING AND CURRENT ROW` and `6 PRECEDING AND 1 PRECEDING` both span six rows, but only the second stops before the month being forecast. In the first row the honest frame is empty, so `AVG` returns `NULL`, while the leaky frame averages the month with itself.
- **Alternative/trade-off:** `LAG(leaky_ma6) OVER (ORDER BY month)` reproduces `honest_ma6` on every row, since one month's leaky window is the next month's honest one. The learner file's trailing three-month average is the leaky kind too (it includes the current month): fine as a smoothed line on a chart, wrong as a forecast.
- **Edge case:** In the last row the leaky value (137,336.56) sits below the honest one (141,322.32), because it includes the partial November. Over the 34 common months the leaky frame's MAPE is 0.1696 against 0.2281 for the honest frame; all of that improvement comes from seeing the answer.

## Exercise 4: Build a monthly spine

`generate_series` establishes one row per calendar month before the 12-row lag.
The separate source-present flag distinguishes no row from a chosen zero policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 4, take the first and last order months from `orders` in `bounds`, build every calendar month between them with `generate_series` in `spine`, `LEFT JOIN` the monthly revenue in `actual` to it in `complete`, and apply `LAG(revenue, 12)` to the spine rather than to the observed months.
- **Expected result/shape:** For sql-49 Exercise 4, expected output: 46 rows, one per calendar `month` from 2023-02-01 to 2026-11-01, with columns `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`, ordered by `month`; `seasonal_forecast` is `NULL` for the first 12 months.
- **Independent verification:** For sql-49 Exercise 4, confirm `had_source_rows` is true on all 46 rows today and that 2024-02 takes 1,203.26 from 2023-02. Then, in a transaction, delete the 91 orders from 2025-03 and rerun: the spine still has 46 rows, 2025-03 shows `revenue` `NULL` and `had_source_rows` false, 2026-03 gets a `NULL` `seasonal_forecast` instead of February's 33,302.51, and `ROLLBACK`. Repeat with `UPDATE ... SET total_amount = 0` for those orders instead: 2025-03 shows `revenue` 0.00 with `had_source_rows` true, and 2026-03 gets 0.00.
- **Intermediate relation check:** `bounds` is one row, `spine` 46 months, `actual` 46 grouped rows and `complete` 46 after the `LEFT JOIN`. No month is missing in this fixture, so `had_source_rows` is true throughout and the lag matches one taken over observed months.
- **Clause check:** `generate_series(first_month, last_month, interval '1 month')` returns timestamps, cast back to `date` so `USING (month)` matches `actual.month`. `a.month IS NOT NULL` is evaluated after the outer join, which makes it a reliable "had orders" flag. `revenue` is not wrapped in `COALESCE`, so a missing month stays `NULL`.
- **Alternative/trade-off:** Exercise 1 makes the opposite choice: `COALESCE(observed.revenue, 0)` treats a missing month as zero sales so it can be graded. Which is right depends on whether no orders means no revenue or no data; the flag column lets a reader tell the two apart either way.
- **Edge case:** Filter June 2025 out of `actual`: the spine still prints it, with `NULL` revenue and `had_source_rows` false, and June 2026's `seasonal_forecast` becomes `NULL`. Without the spine, each month from July 2025 to June 2026 would borrow the value from 13 months back, so June 2026 would receive May 2025's 52,788.19.

## Exercise 5: Report the MAPE denominator

`NULLIF(actual, 0)` excludes undefined percentage errors, and FILTER counts
both scored and excluded observations. Never publish MAPE without that context.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 5, use the `toy` `VALUES` fixture `(100, 90), (0, 10), (50, 60)` of `actual` and `forecast` and compute MAPE as `AVG(ABS(actual - forecast) / NULLIF(actual, 0))`, counting scored rows and excluded zero actuals.
- **Expected result/shape:** For sql-49 Exercise 5, expected output: one row with `mape` 0.1500, `scored_rows` 2, and `excluded_zero_actuals` 1. The final columns are `mape`, `scored_rows`, and `excluded_zero_actuals`.
- **Independent verification:** For sql-49 Exercise 5, confirm by hand that the two scored errors are 10/100 = 0.10 and 10/50 = 0.20, whose mean is 0.15, and that the zero-actual row adds nothing because `NULLIF(actual, 0)` makes its ratio NULL, which `AVG` skips.
- **Intermediate relation check:** `toy` holds three rows. Before averaging, list `ABS(actual - forecast) / NULLIF(actual, 0)` per row: 0.10, `NULL` and 0.20. `AVG` skips the `NULL`, so it divides 0.30 by 2, not by 3.
- **Clause check:** The two `FILTER` counts split the same three rows by `actual <> 0` and `actual = 0`, so together they equal the input size. A `NULL` actual would fall into neither count, which is worth a third counter on real data.
- **Alternative/trade-off:** `WHERE actual <> 0` gives the same 0.1500 but drops the zero row before counting, so `excluded_zero_actuals` could no longer come from the same query. Weighted MAPE, `SUM(ABS(actual - forecast)) / SUM(actual)`, avoids per-row division: here 30 / 150 = 0.2000, and the zero month's miss of 10 counts instead of vanishing.
- **Edge case:** Without `NULLIF`, PostgreSQL stops with `ERROR: division by zero`, and under `ON_ERROR_STOP` the rest of the file never runs. With it the zero month drops out silently. No month of order data has zero revenue, so Exercise 1 reports `zero_actual_rows` 0 for all four models.

## Exercise 6: Compare MAE and MAPE

The deterministic fixture shows that MAE reflects currency-scale error while
MAPE can be dominated by a modest miss on a very small actual.

### Reasoning and verification

- **Inputs/evidence:** For sql-49 Exercise 6, use the `toy` fixture `(1000, 900), (10, 20)` and compute MAE, `AVG(ABS(actual - forecast))`, and MAPE, `AVG(ABS(actual - forecast) / NULLIF(actual, 0))`.
- **Expected result/shape:** For sql-49 Exercise 6, expected output: one row with `mae` 55 and `mape` 0.55. The final columns are `mae` and `mape`.
- **Independent verification:** For sql-49 Exercise 6, confirm by hand that the absolute errors are 100 and 10 (mean 55) and the percentage errors are 0.10 and 1.00 (mean 0.55); the output shows that the small month's modest miss dominates MAPE, while the large month dominates MAE.
- **Intermediate relation check:** `toy` has two rows. Listing them first shows absolute errors of 100 and 10 and percentage errors of 0.10 and 1.00; the single output row averages each pair.
- **Clause check:** `AVG(ABS(actual - forecast))` keeps the currency unit, so 55 means 55 revenue units. Dividing by `NULLIF(actual, 0)` before averaging turns each row into a ratio and gives every row equal weight, whatever its size. Nothing is rounded, so `psql` prints 55.0000000000000000 and 0.55000000000000000000.
- **Alternative/trade-off:** Weighted MAPE, `SUM(ABS(actual - forecast)) / SUM(actual)`, sits between the two: 110 / 1,010 = 0.1089, dominated by the large month as MAE is but still free of units. Report it, or MAE, beside plain MAPE when month sizes differ.
- **Edge case:** Monthly revenue in the fixture runs from 1,203.26 to 170,179.13, so the same effect shapes Exercise 1. In February 2024 MA(6) missed by 2,963.53, which is 0.1999 of that month's revenue; the same miss in October 2026 would be 0.0174.