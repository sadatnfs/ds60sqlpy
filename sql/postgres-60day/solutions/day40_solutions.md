# Day 40: Solutions: Advanced Analytic Functions


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day40_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Ordered-set aggregate, Z-score, Interpolation. Its worked-model focus is:
Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive `(revenue - avg15) / NULLIF(sd15, 0)`. Keep the observation count beside the score so early, undersized windows are visible.

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
- **Expected result/shape:** For sql-40 Exercise 1, expected output: one row per day with orders. A positive z-score is above the rolling mean; a negative score is below it. The final columns are `order_day`, `revenue`, `avg15`, `sd15`, and `z_score`. The final order is `order_day`.
- **Independent verification:** For sql-40 Exercise 1, confirm one row per `order_day`, so the row count equals `SELECT COUNT(DISTINCT date_trunc('day', order_date)) FROM orders`; the first row has NULL `sd15` and `z_score` because a one-row sample has no standard deviation, and for one later day recompute `avg15` as the mean of that day's and the 14 previous days' `revenue` in `daily`.
- **Intermediate relation check:** For sql-40 Exercise 1, run `daily` alone and check one row per `order_day` before `rolling` adds the window statistics.
- **Clause check:** For sql-40 Exercise 1, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_day`, and finish with `order_day`, `revenue`, `avg15`, `sd15`, and `z_score` ordered by `order_day`.
- **Alternative/trade-off:** For sql-40 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected shape: one row per day with orders. Evaluate another form against the concrete expected result (one row per day with orders. A positive z-score is above the rolling mean; a negative score is below it) and the verification above.
- **Edge case:** The frame counts 15 observed days, not 15 calendar days; a day without orders is skipped, so a calendar-based window needs a dense date series first.

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
- **Expected result/shape:** For sql-40 Exercise 2, expected output: one row per sold category. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value. The final columns are `category`, `p50_order_value`, `p90_order_value`, and `category_orders`. The final order is `category`.
- **Independent verification:** For sql-40 Exercise 2, confirm 6 rows, one per category, and that `category_orders` equals `SELECT COUNT(DISTINCT oi.order_id) FROM order_items oi JOIN products p USING (product_id) WHERE p.category = <that category>` (for example 2192 for `Apparel`); `p90_order_value` must be at least `p50_order_value` in every row.
- **Intermediate relation check:** For sql-40 Exercise 2, run `category_order_values` alone and check that (`category`, `order_id`) is unique before you compute percentiles.
- **Clause check:** For sql-40 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `order_items`, and `products`, preserve one row per `category`, and finish with `category`, `p50_order_value`, `p90_order_value`, and `category_orders` ordered by `category`.
- **Alternative/trade-off:** For sql-40 Exercise 2, the chosen form is justified by this lesson-specific rationale: An order can contain several categories. Evaluate another form against the concrete expected result (one row per sold category. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value) and the verification above.
- **Edge case:** An order with lines in several categories contributes one value to each of those categories; using the whole order total instead would count a mixed order at full value in every category.

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
- **Intermediate relation check:** For sql-40 Exercise 3, list the sorted values with their positions first; with an even count, the two medians differ unless the two middle values are equal.
- **Clause check:** For sql-40 Exercise 3, the solution names the four values in a `WITH values (value)` CTE and computes both ordered-set aggregates, `percentile_disc(0.5) WITHIN GROUP (ORDER BY value)` and `percentile_cont(0.5) WITHIN GROUP (ORDER BY value)`, in one `SELECT` without `GROUP BY`.
- **Alternative/trade-off:** For sql-40 Exercise 3, the chosen form is justified by this lesson-specific rationale: For four values, the discrete median chooses an observed central value while the continuous median interpolates. Evaluate another form against the concrete expected result (one row per `discrete_median`) and the verification above.
- **Edge case:** `percentile_disc` always returns an observed value, which suits prices or labels that must exist; `percentile_cont` can return a value that no row contains.

## Exercise 4: Share and rank within month

Revenue is first aggregated to month/category grain. The denominator window
partitions by month, and `ROW_NUMBER` adds category as a deterministic tie-break.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 4, read from `orders`, `order_items`, and `products`. Build the answer toward `month`, `category`, `revenue`, `month_share`, and `category_rank`; keep `month`, and `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-40 Exercise 4, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `revenue`, `month_share`, and `category_rank`. The final order is `month DESC, category_rank`.
- **Independent verification:** For sql-40 Exercise 4, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, `month_share`, and `category_rank`, then verify output keys remain `month`, and `category`. Give two rows the same `month DESC` value and different `category_rank` values; verify `month DESC, category_rank` produces the intended rank and display order.
- **Intermediate relation check:** For sql-40 Exercise 4, run `category_month` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-40 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, `order_items`, and `products`, preserve one row per `month`, and `category`, and finish with `month`, `category`, `revenue`, `month_share`, and `category_rank` ordered by `month DESC, category_rank`.
- **Alternative/trade-off:** For sql-40 Exercise 4, the chosen form is justified by this lesson-specific rationale: Revenue is first aggregated to month/category grain. Evaluate another form against the concrete expected result (one row per `month`, and `category`) and the verification above.
- **Edge case:** Give two rows the same `month DESC` value and different `category_rank` values; verify `month DESC, category_rank` produces the intended rank and display order.

## Exercise 5: Remove forecast leakage

The corrected frame is `7 PRECEDING` through `1 PRECEDING`. Ending at the current
row would let the target actual influence its own forecast.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 5, read from `orders`. Build the answer toward `day`, `revenue`, and `prior_seven_forecast`; keep `day` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-40 Exercise 5, expected output: at most 20 rows keyed by `day`. The final columns are `day`, `revenue`, and `prior_seven_forecast`. The final order is `day DESC`.
- **Independent verification:** For sql-40 Exercise 5, assert no more than 20 rows, no duplicate `day`, and no adjacent pair that violates `day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, and `prior_seven_forecast` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.
- **Intermediate relation check:** For sql-40 Exercise 5, run `daily` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
- **Clause check:** For sql-40 Exercise 5, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `day`, and finish with `day`, `revenue`, and `prior_seven_forecast` ordered by `day DESC`.
- **Alternative/trade-off:** For sql-40 Exercise 5, the chosen form is justified by this lesson-specific rationale: The corrected frame is `7 PRECEDING` through `1 PRECEDING`. Evaluate another form against the concrete expected result (at most 20 rows keyed by `day`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.

## Exercise 6: Preserve undefined dispersion

The constant fixture has standard deviation zero. `NULLIF(sd, 0)` returns NULL
for every z-score, accurately distinguishing undefined from normal.

### Reasoning and verification

- **Inputs/evidence:** For sql-40 Exercise 6, read from `constant`. Build the answer toward `value`, and `z_score`; keep `value` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-40 Exercise 6, expected output: one row per `value`. The final columns are `value`, and `z_score`.
- **Independent verification:** For sql-40 Exercise 6, reselect the returned keys directly from the source; require unique `value` where the expected grain is one row per key and confirm the projected `value`, and `z_score` against `constant`. Repeat with `NULL` in `value`, and `z_score` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-40 Exercise 6, run `moments` one at a time. Record each CTE's row count and `value` uniqueness before the next stage uses it.
- **Clause check:** For sql-40 Exercise 6, the solution actually uses `WITH`, `FROM`, window `OVER`, and `SELECT`. Read only those operations: begin at `constant`, preserve one row per `value`, and finish with `value`, and `z_score`.
- **Alternative/trade-off:** For sql-40 Exercise 6, the chosen form is justified by this lesson-specific rationale: The constant fixture has standard deviation zero. Evaluate another form against the concrete expected result (one row per `value`) and the verification above.
- **Edge case:** Repeat with `NULL` in `value`, and `z_score` and state whether the row is kept, rejected, or classified.
