# Day 40: Solutions: Advanced Analytic Functions


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Try all six prompts in the learner file before reading on, and keep your
transcript so the numbers can be compared. Then run the executable answer
([reading solutions](../../STUDY-GUIDE.md#read-a-solution)):

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day40_solutions.sql
```

Every statement is a read, so the file needs no `BEGIN` or `ROLLBACK`. It
prints six result sets: 1,081 daily z-score rows on a late-2026 load, 6
category percentile rows, the single median pair 20 and 60, 276
month-and-category share rows, the 20 newest forecasts and three constant
rows whose `z_score` is empty.

## How these answers fit together

The [learner script](../day40_analytic_functions_advanced.sql) computed
rolling statistics, monthly percentiles and lifetime category shares, each
at a different grain. These answers keep that discipline. The rolling
z-score and the forecast work on one row per order day, the percentiles on
one row per category and order, and the shares on one row per month and
category. The median comparison and the constant series use inline
fixtures, where the right answer can be worked out by hand before trusting
the database.

Two cautions run through all six. A `ROWS` frame counts order days, not
calendar days, so a sparse stretch of the series quietly widens the window.
And a statistic over a tiny or constant sample can be undefined, which SQL
should show as NULL rather than as a convenient zero.

## Exercise 1: Fifteen-row rolling z-score for daily revenue

```sql
SET search_path TO training, public;

WITH daily AS (
  SELECT
    date_trunc('day', order_date)::date AS order_day,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    date_trunc('day', order_date)
),
rolling AS (
  SELECT
    order_day,
    revenue,
    AVG(revenue) OVER (ORDER BY order_day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) AS avg15,
    STDDEV_SAMP(revenue) OVER (ORDER BY order_day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) AS sd15
  FROM
    daily
)
SELECT
  order_day,
  ROUND(revenue, 2) AS revenue,
  ROUND(avg15, 2) AS avg15,
  ROUND(sd15, 2) AS sd15,
  ROUND((revenue - avg15) / NULLIF (sd15, 0), 4) AS z_score
FROM
  rolling
ORDER BY
  order_day;
```

Expected shape: one row per day with orders. A positive z-score is above the
rolling mean; a negative score is below it. The first row has no sample standard
deviation, and any zero-standard-deviation frame yields `NULL`.

Assumption: “15-day” in the learner example means 15 observed daily rows. To
model 15 consecutive calendar days, first join revenue to a dense date series
and decide whether missing days mean zero or unknown.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 1, read from `orders`, sum `total_amount` per UTC day in the CTE `daily`, then compute a trailing 15-row mean and sample standard deviation (`ROWS BETWEEN 14 PRECEDING AND CURRENT ROW`) in `rolling` and the z-score `(revenue - avg15) / NULLIF(sd15, 0)`.
- **Expected result/shape:** For sql-40 Exercise 1, expected output: 1,080 rows on this load, one per UTC day with orders from 2023-02-13 to 2026-11-23; the second row, 2023-03-07, has `revenue` 1,034.00 against `avg15` 1,118.63 and `z_score` -0.7071. A positive z-score is above the rolling mean; a negative score is below it. The final columns are `order_day`, `revenue`, `avg15`, `sd15`, and `z_score`. The final order is `order_day`.
- **Independent verification:** For sql-40 Exercise 1, confirm one row per `order_day`, so the row count equals `SELECT COUNT(DISTINCT date_trunc('day', order_date)) FROM orders`; the first row has NULL `sd15` and `z_score` because a one-row sample has no standard deviation, and for one later day recompute `avg15` as the mean of that day's and the 14 previous days' `revenue` in `daily`.

- **Intermediate relation check:** `daily` alone returns one row per order day, 1,081 on a late-2026 load, starting at 2023-02-13 with 1,203.26. Its `order_day` values are unique because the CTE groups by the `date_trunc` expression it then casts to `date`, and under the course's UTC `TimeZone` each day bucket maps to one date.
- **Clause check:** Both window calls repeat the frame `ORDER BY order_day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW`, so mean and deviation cover the same rows. Rounding happens only in the last `SELECT`, after the score is built from unrounded `avg15` and `sd15`. On that load the newest row's `avg15` of 3,245.49 matches a hand average of the last 15 daily revenues.
- **Alternative/trade-off:** Adding `COUNT(*)` over the same frame exposes the 14 short frames at the start of the series, which the worked walkthrough asks you to keep visible. A `CASE` could then blank scores whose count is under 15; this answer keeps every row and leaves that judgment to the reader.
- **Edge case:** The second row scores -0.7071 or 0.7071 whatever the two revenues are, because two values always sit 0.7071 sample deviations (one over the square root of two) from their mean. Early scores therefore say little. On that load the extremes are 2.9949 and -2.3790, and 34 days fall beyond 2 in either direction.

## Exercise 2: Category P50 and P90 of order values

An order can contain several categories. This answer defines an “order total
within a category” as the sum of that category's net lines in that order; using
the whole order total for every category would double-count mixed orders.

```sql
SET search_path TO training, public;

WITH category_order_values AS (
  SELECT
    p.category,
    oi.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS category_order_value
  FROM
    order_items oi
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category,
    oi.order_id
)
SELECT
  category,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY category_order_value)::numeric, 2) AS p50_order_value,
  ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY category_order_value)::numeric, 2) AS p90_order_value,
  COUNT(*) AS category_orders
FROM
  category_order_values
GROUP BY
  category
ORDER BY
  category;
```

Expected shape: one row per sold category. `PERCENTILE_CONT` can interpolate
between observed values, so a percentile need not equal an actual order value.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 2, read from `order_items` joined to `products`, sum each order's net lines per category in `category_order_values`, then compute `PERCENTILE_CONT(0.5)` and `PERCENTILE_CONT(0.9)` of those per-order category values and count them per category.
- **Expected result/shape:** For sql-40 Exercise 2, expected output: 6 rows, one per category, whose `category_orders` run from 2,145 for Books to 2,192 for Apparel and sum to 13,085, more than the 4,362 orders because an order with lines in several categories counts once in each; `p50_order_value` runs from 146.54 for Home to 150.24 for Electronics on this load. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value. The final columns are `category`, `p50_order_value`, `p90_order_value`, and `category_orders`. The final order is `category`.
- **Independent verification:** For sql-40 Exercise 2, confirm 6 rows, one per category, and that `category_orders` equals `SELECT COUNT(DISTINCT oi.order_id) FROM order_items oi JOIN products p USING (product_id) WHERE p.category = <that category>` (for example 2192 for `Apparel`); `p90_order_value` must be at least `p50_order_value` in every row.

- **Intermediate relation check:** `category_order_values` holds 13,085 rows, one per `(category, order_id)`. That equals the number of `order_items` lines, because no order in this seed repeats a category: orders carry one to five lines, each from a different category, and 3,490 of the 4,362 orders span two or more categories.
- **Clause check:** The per-category values are small, with medians from 146.54 (Home) to 150.24 (Electronics) and P90s from 373.01 (Sports) to 386.32 (Books), while the median whole order is 561.21. That gap is the point: each value counts only one category's part of an order. `category_orders` runs from 2,145 for Books to 2,192 for Apparel and sums to 13,085.
- **Alternative/trade-off:** `PERCENTILE_DISC` would return an observed category order value instead of an interpolated one. For Apparel both functions give 149.50, which shows that its two middle values, positions 1,096 and 1,097 of 2,192, are equal; in general the two can differ.
- **Edge case:** An order with lines in several categories contributes one value to each of those categories; using the whole order total instead would count each of the 3,490 mixed orders at full value in every category it touches.

## Pitfalls

- `STDDEV_SAMP` is `NULL` for a one-row frame. `NULLIF(sd15, 0)` also protects
  constant frames from division by zero.
- A `ROWS` frame counts rows, not elapsed time.
- Ordered-set aggregates such as `PERCENTILE_CONT` use `WITHIN GROUP`; they are
  not written with `OVER` in this grouped query.
- Define the analytical grain before calculating a percentile. Line-level and
  order-level percentiles answer different questions.

## Exercise 3: Compare discrete and continuous medians

For four values, the discrete median chooses an observed central value while the
continuous median interpolates. The runnable `VALUES` fixture makes the
difference deterministic.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 3, use the inline `VALUES` fixture 10, 20, 100, 200 and compute `percentile_disc(0.5)` and `percentile_cont(0.5)` over it.
- **Expected result/shape:** For sql-40 Exercise 3, expected output: one row with `discrete_median` 20 and `continuous_median` 60. The final columns are `discrete_median` and `continuous_median`.
- **Independent verification:** For sql-40 Exercise 3, confirm by hand that `percentile_disc(0.5)` returns the first value whose cumulative share reaches 0.5, the second of four values (20), while `percentile_cont(0.5)` interpolates halfway between 20 and 100 (60); add the value 300 and expect both medians to become 100.

- **Intermediate relation check:** Sorted, the fixture is 10, 20, 100, 200, so positions 2 and 3 hold the middle pair. The cumulative shares are 0.25, 0.50, 0.75 and 1.00, and 20 is the first value to reach 0.50.
- **Clause check:** Both aggregates sit in one `SELECT` with no `GROUP BY`, so the whole fixture is a single group and the result is one row. The literal `10::numeric` types the column; `percentile_disc` returns that type (20), while `percentile_cont` returns `double precision` (60).
- **Alternative/trade-off:** The gap of 40 between the two medians comes from the sparse fixture, not from the functions. Over the 2,192 Apparel values in the previous prompt, the same pair agrees at 149.50.
- **Edge case:** Adding 300 makes the count odd, and a test run returns 100 from both functions. `percentile_disc` always returns a value present in the input, which matters for prices or sizes that must be real.

## Exercise 4: Share and rank within month

Revenue is first aggregated to month/category grain. The denominator window
partitions by month, and `ROW_NUMBER` adds category as a deterministic tie-break.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 4, read `orders` for the month, `order_items` for net line revenue `quantity * unit_price * (1 - discount)`, and `products` for `category`; the CTE `category_month` sums revenue per month and category, `SUM(revenue) OVER (PARTITION BY month)` supplies the share denominator, and `ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC, category)` supplies the rank.
- **Expected result/shape:** For sql-40 Exercise 4, expected output: 276 rows on this load, 46 months from 2023-02-01 to 2026-11-01 times all 6 categories, with `category_rank` 1 to 6 in every month; the newest month starts with Sports at 16,427.31 and a `month_share` of 0.1924 and ends with Home at rank 6. The final columns are `month`, `category`, `revenue`, `month_share`, and `category_rank`. The final order is `month DESC, category_rank`.
- **Independent verification:** For sql-40 Exercise 4, confirm 276 distinct `(month, category)` pairs, that the unrounded shares sum to exactly 1 in each of the 46 months while the rounded `month_share` values sum to between 0.9998 and 1.0002, and that `SUM(revenue)` over all rows is 2,355,647.1235, the `order_items` line total; this load has no revenue ties, so `RANK()` matches `ROW_NUMBER()` in every row, but on `VALUES ('Books', 100.00), ('Apparel', 100.00), ('Home', 90.00)` the `category` tiebreaker ranks Apparel 1 and Books 2 where `RANK()` gives both 1.

- **Intermediate relation check:** `category_month` returns 276 rows on a late-2026 load: 46 months times all 6 categories. Even February 2023, whose two orders total 1,203.26, touches every category, so no month is missing a row.
- **Clause check:** `SUM(revenue) OVER (PARTITION BY month)` is the denominator, so each month's six shares sum to 1 before rounding; after `ROUND(..., 4)` a month's six shares drift from 1 by at most 0.0002. The newest month, November 2026, starts with Sports at 16,427.31 and a share of 0.1924.
- **Alternative/trade-off:** `RANK()` would give tied categories the same rank and skip the next number, which reads more honestly on a leaderboard. No two categories tie at cent precision in any month here, so the choice changes nothing visible, but the `category` tie-break keeps `ROW_NUMBER` repeatable if a tie ever appears.
- **Edge case:** Shares in thin early months swing widely: on that load, February 2023 runs from Apparel at 0.3383 down to Home at 0.0251, while the lifetime shares in the learner script all sit between 0.1639 and 0.1687. A share is only as stable as the revenue in its month.

## Exercise 5: Remove forecast leakage

The corrected frame is `7 PRECEDING` through `1 PRECEDING`. Ending at the current
row would let the target actual influence its own forecast.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 5, read `orders`, sum `total_amount` per `order_date::date` in the CTE `daily`, then average the seven previous order days with `AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING)`, so a day's own revenue never feeds its forecast.
- **Expected result/shape:** For sql-40 Exercise 5, expected output: exactly 20 rows on this load, the consecutive days from 2026-11-23 back to 2026-11-04, each with a non-NULL forecast; the top row is 2026-11-23 with `revenue` 742.14 and `prior_seven_forecast` 2,300.43. The final columns are `day`, `revenue`, and `prior_seven_forecast`. The final order is `day DESC`.
- **Independent verification:** For sql-40 Exercise 5, confirm 2,300.43 by averaging the seven `daily` rows before 2026-11-23 (`ORDER BY day DESC LIMIT 7`), and that the leaky frame `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` reports 2,079.31 for that day; then, inside `BEGIN ... ROLLBACK`, insert a 500.00 order on 2026-11-24 and confirm it becomes the top row with forecast 2,079.31, the leaky value shifted one day, while the 20-row window now starts at 2026-11-05.

- **Intermediate relation check:** `daily` groups by `order_date::date`, which matches `date_trunc('day', ...)` under the course's UTC `TimeZone`, so it returns the same 1,081 days as the first prompt. On a late-2026 load the 20 printed days run from 2026-11-23 back to 2026-11-04.
- **Clause check:** `ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING` averages the seven previous order days and stops before the current one. For 2026-11-23 on that load, the forecast is 2,300.43 against an actual 742.14; a seven-row frame ending at `CURRENT ROW` reports 2,079.31, pulled toward the very value it claims to predict.
- **Alternative/trade-off:** Leakage flatters the error. Over every day with a forecast, the mean absolute error on that load is 883.13 for the honest frame and 771.31 for the leaky one, so the broken model looks about 13% better. If the forecast should mean calendar days, `RANGE BETWEEN INTERVAL '7 days' PRECEDING AND INTERVAL '1 day' PRECEDING` works on a `date` key and gives the same 2,300.43 for the newest day, where no day is missing.
- **Edge case:** The oldest day has no prior row, so its forecast is NULL, and the next six days average fewer than seven values. `LIMIT 20` hides both, since only the newest rows print.

## Exercise 6: Preserve undefined dispersion

The constant fixture has standard deviation zero. `NULLIF(sd, 0)` returns NULL
for every z-score, accurately distinguishing undefined from normal.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 6, use the inline `VALUES` fixture `constant`, three rows of 5; `moments` adds `AVG(value) OVER ()` and `STDDEV_SAMP(value) OVER ()` to every row, and the outer query divides `value - mean_value` by `NULLIF(sd_value, 0)`.
- **Expected result/shape:** For sql-40 Exercise 6, expected output: three rows, each with `value` 5 and a NULL `z_score`, because the sample standard deviation is 0 and `NULLIF` turns that 0 into NULL. The final columns are `value`, and `z_score`.
- **Independent verification:** For sql-40 Exercise 6, confirm that dividing by `sd_value` without `NULLIF` fails with `division by zero`, that the fixture 5, 5, 6 gives `z_score` values -0.5774, -0.5774, and 1.1547, and that adding a `NULL` row returns four rows with every `z_score` NULL: `STDDEV_SAMP` skips the NULL, so the 5s still have zero spread, and the NULL row's own difference is NULL.

- **Intermediate relation check:** `moments` keeps all three fixture rows and adds `mean_value` 5 and `sd_value` 0 to each, because `OVER ()` makes the whole fixture one window.
- **Clause check:** The result is three rows, each `value` 5 with an empty `z_score`. That is one row per fixture row, not per distinct `value`: all three keys repeat, so the verification's request for unique `value` cannot hold on this fixture. Without `NULLIF(sd_value, 0)` the same query stops with `ERROR: division by zero`.
- **Alternative/trade-off:** `COALESCE(z_score, 0)` would print a tidy zero, but zero means "exactly at the mean", a claim a series with no spread cannot support. If a report needs a label, add a separate column such as "no variation" and keep `z_score` NULL.
- **Edge case:** Adding a NULL row leaves the mean at 5 and the deviation at 0, since both aggregates skip NULL inputs, so all four scores come out NULL for two different reasons. Change one 5 to 6 and the scores become -0.5774, -0.5774 and 1.1547.
