# Day 26 solutions: CTEs with Window Functions: Layered Analytics


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The six answers only read `orders`, `order_items` and `products`, inside
`BEGIN`/`ROLLBACK` with `search_path` set to `training`. Month boundaries
come from `order_date AT TIME ZONE 'UTC'`, so the session time zone does not
matter. See [Read a solution](../../STUDY-GUIDE.md#read-a-solution) for the
general approach.

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day26_solutions.sql
```

## How these answers fit together

Every answer starts with a CTE that groups by UTC month, either over
`orders.total_amount` or over the item formula split by category, and then
applies a window to the grouped rows. The exact months depend on when the
fixture was loaded (46 months when this guide was checked), but the totals
do not: stored revenue adds to 2,355,646.89 and item revenue to
2,355,647.12. The final answer checks that reconciliation directly. The
learner file is [day26_ctes_with_windows.sql](../day26_ctes_with_windows.sql).

## Reading contract

- **Focus:** Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
- **Assumptions:** Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
- **Primary pitfall:** Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Calculate monthly stored revenue and its prior-month value/change.

**Reasoning:** Aggregate to month in a CTE, then lag the monthly measure.

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    SUM(o.total_amount) AS revenue
  FROM
    orders AS o
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
compared AS (
  SELECT
    month_start,
    revenue,
    LAG(revenue) OVER (ORDER BY month_start) AS previous_revenue
  FROM
    monthly
)
SELECT
  month_start,
  ROUND(revenue, 2) AS revenue,
  ROUND(previous_revenue, 2) AS previous_revenue,
  ROUND(revenue - previous_revenue, 2) AS change
FROM
  compared
ORDER BY
  month_start;
```

**Expected shape:** One row per observed month.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 1, read from `orders`, aggregate `SUM(total_amount)` to one row per UTC month in the CTE `monthly`, then use `LAG(revenue) OVER (ORDER BY month_start)` in `compared` and return `change = revenue - previous_revenue`.
- **Expected result/shape:** For sql-26 Exercise 1, expected output: one row per UTC month with orders, 46 rows from 2023-02-01 to 2026-11-01 on a November 2026 load (seed dates move with the load date); the first row is 1203.26 with NULL `previous_revenue` and `change`, and the second is 1803.43 with a change of 600.17. The final columns are `month_start`, `revenue`, `previous_revenue`, and `change`. The final order is `month_start`.
- **Independent verification:** For sql-26 Exercise 1, confirm that `month_start` is unique and that the row count equals `SELECT COUNT(DISTINCT date_trunc('month', order_date AT TIME ZONE 'UTC')) FROM orders`; exactly one row, the earliest month, has NULL `previous_revenue` and `change`, and the `revenue` values add up to 2355646.89.
- **Intermediate relation check:** `monthly` has one row per month that has at least one order. When this guide was checked that was 46 months, and the revenues summed to 2,355,646.89.
- **Clause check:** `LAG(revenue) OVER (ORDER BY month_start)` reads the previous row of the grouped data, not the previous calendar month. The first row's `previous_revenue` and `change` are therefore `NULL`, and every later row has both filled.
- **Alternative/trade-off:** `revenue - LAG(revenue) OVER (...)` in one `SELECT` avoids the `compared` CTE. Naming `previous_revenue` as its own column makes the subtraction easy to check by eye.
- **Edge case:** If a month had no orders, `LAG` would compare across the gap. The newest month is only partly filled, so its change is usually a large negative number, such as the drop of 84,814.46 seen at checking time.

## Exercise 2: Query writing

**Prompt:** Rank product categories by net revenue within each UTC order month.

**Reasoning:** Aggregate month/category first, then rank the stable aggregate.

```sql
WITH category_month AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC'),
    p.category
)
SELECT
  month_start,
  category,
  ROUND(revenue, 2) AS revenue,
  DENSE_RANK() OVER (PARTITION BY month_start ORDER BY revenue DESC) AS revenue_rank
FROM
  category_month
ORDER BY
  month_start,
  revenue_rank,
  category;
```

**Expected shape:** One row per observed month/category.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 2, read `orders` joined to `order_items` and `products`, sum net item revenue `unit_price * quantity * (1 - discount)` per UTC month and `category` in `category_month`, then apply `DENSE_RANK()` partitioned by `month_start` and ordered by `revenue DESC`.
- **Expected result/shape:** For sql-26 Exercise 2, expected output: 6 rows per month, one per category, ranked 1 through 6 (276 rows for 46 months on this load); the first month, 2023-02-01, runs from Apparel at 407.05 down to Home at 30.20. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
- **Independent verification:** For sql-26 Exercise 2, confirm `COUNT(*)` is 6 times `COUNT(DISTINCT month_start)`, every month has ranks 1 through 6 exactly once, and the 2023-02-01 revenues add to 1203.26, the stored total for that month in Exercise 1; then rank the fixture `VALUES ('A', 10), ('B', 10), ('C', 5), ('D', 3)` and confirm `DENSE_RANK` gives 1, 1, 2, 3 where `RANK` gives 1, 1, 3, 4.
- **Intermediate relation check:** `category_month` has one row per month and category. Every month in the checked data had all six categories, so the row count was 46 times 6, or 276.
- **Clause check:** `DENSE_RANK()` is partitioned by `month_start` and ordered by `revenue DESC`, so ranks restart at 1 each month and run to 6. The outer sort by `month_start, revenue_rank, category` gives a stable order even if two categories tied.
- **Alternative/trade-off:** `RANK()` and `ROW_NUMBER()` return the same numbers here, because no two categories had equal revenue in the same month. They only differ on ties: `RANK` would skip the next number and `ROW_NUMBER` would break the tie arbitrarily.
- **Edge case:** A month in which some category sold nothing has fewer than six rows. The category simply does not appear; there is no zero row unless you build one from a calendar and the category list.

## Exercise 3: Query writing

**Prompt:** Return the top three category revenue levels per month.

**Reasoning:** Rank in one CTE and filter the window result outside.

```sql
WITH category_month AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC'),
    p.category
),
ranked AS (
  SELECT
    category_month.*,
    DENSE_RANK() OVER (PARTITION BY month_start ORDER BY revenue DESC) AS revenue_rank
  FROM
    category_month
)
SELECT
  month_start,
  category,
  ROUND(revenue, 2) AS revenue,
  revenue_rank
FROM
  ranked
WHERE
  revenue_rank <= 3
ORDER BY
  month_start,
  revenue_rank,
  category;
```

**Expected shape:** Top three revenue ranks for each observed month.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 3, read `orders`, `order_items`, and `products` into the same `category_month` CTE as Exercise 2, rank it in a second CTE `ranked`, and filter `revenue_rank <= 3` only in the outer query, after the window has run.
- **Expected result/shape:** For sql-26 Exercise 3, expected output: 3 rows per month (138 rows for 46 months on this load, because no month has a revenue tie); 2023-02-01 keeps Apparel, Books, and Electronics, and 2026-11-01 keeps Sports, Books, and Apparel. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
- **Independent verification:** For sql-26 Exercise 3, confirm `COUNT(*)` is 3 times `COUNT(DISTINCT month_start)` and each month shows ranks 1, 2, and 3 once; then apply the same rank and filter to `VALUES ('A', 10), ('B', 10), ('C', 5), ('D', 3), ('E', 1)` and confirm four rows survive (ranks 1, 1, 2, 3), showing that ties in `DENSE_RANK` can return more than three categories in a month.
- **Intermediate relation check:** `ranked` is the second answer's result before filtering, 276 rows at checking time, with `revenue_rank` from 1 to 6 within each month.
- **Clause check:** `WHERE revenue_rank <= 3` runs in the outer query, after the window has been computed. With no ties it keeps three categories per month, 138 rows in the checked data.
- **Alternative/trade-off:** `FETCH FIRST 3 ROWS WITH TIES` only works for one overall ordering, not per month. A `LATERAL` subquery per month can do it, but the rank-then-filter CTE is easier to read and check.
- **Edge case:** `DENSE_RANK` allows more than three rows per month when categories tie: two categories tied at rank 2 would give four rows with ranks 1, 2, 2 and 3. Use `ROW_NUMBER` if the report must have exactly three.

## Exercise 4: Prediction

**Prompt:** Calculate each category's cumulative share of monthly revenue in descending contribution order.

**Reasoning:** Divide running category revenue by the full monthly total; use explicit frames.

```sql
WITH category_month AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC'),
    p.category
)
SELECT
  month_start,
  category,
  ROUND(revenue, 2) AS revenue,
  ROUND(SUM(revenue) OVER (PARTITION BY month_start ORDER BY revenue DESC, category ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / NULLIF (SUM(revenue) OVER (PARTITION BY month_start), 0), 4) AS cumulative_revenue_share
FROM
  category_month
ORDER BY
  month_start,
  revenue DESC,
  category;
```

**Expected shape:** One row per month/category with final share equal to one.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 4, read `orders`, `order_items`, and `products` into `category_month`, then divide a running `SUM(revenue)` ordered by `revenue DESC, category` with a `ROWS` frame by the month total `SUM(revenue) OVER (PARTITION BY month_start)`, guarded by `NULLIF`.
- **Expected result/shape:** For sql-26 Exercise 4, expected output: 276 rows on this load, 6 per month; in 2023-02-01 the shares climb 0.3383, 0.5708, 0.7510, 0.8968, 0.9749, and 1.0000. The final columns are `month_start`, `category`, `revenue`, and `cumulative_revenue_share`. The final order is `month_start, revenue DESC, category`.
- **Independent verification:** For sql-26 Exercise 4, confirm the last row of every month is exactly 1.0000 (46 such rows, one per month, and no month whose maximum differs) and that the first 2023-02-01 share equals 407.05 / 1203.26; then run both frames over `VALUES ('A', 10.0), ('B', 10.0), ('C', 5.0)` and confirm `ROWS` gives 0.4000, 0.8000, 1.0000 while the default `RANGE` frame gives 0.8000 to both tied rows.
- **Intermediate relation check:** `category_month` gives up to six rows per month. Within a month the running sum is divided by `SUM(revenue) OVER (PARTITION BY month_start)`, the month's total, which repeats on every row.
- **Clause check:** The running window orders by `revenue DESC, category` with an explicit `ROWS` frame, so each row adds exactly one category. The share grows on every row and reaches 1.0000 on the smallest category in each month; in the checked data that was true for all 46 months.
- **Alternative/trade-off:** With only `ORDER BY revenue DESC`, the default `RANGE` frame would give the same numbers today, since no revenues tie. Spelling out the frame and the tie-breaker keeps the result correct if ties ever appear.
- **Edge case:** `NULLIF(..., 0)` turns a zero month total into `NULL` instead of a division error. That can only happen if a month's items all have a 100 percent discount, which this fixture never has.

## Exercise 5: Debugging

**Prompt:** Calculate a three-month moving average after building a dense month calendar.

**Reasoning:** Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.

```sql
WITH bounds AS (
  SELECT
    MIN(date_trunc('month', o.order_date AT TIME ZONE 'UTC'))::date AS first_month,
    MAX(date_trunc('month', o.order_date AT TIME ZONE 'UTC'))::date AS last_month
  FROM
    orders AS o
),
calendar AS (
  SELECT
    generate_series(first_month, last_month, INTERVAL '1 month')::date AS month_start
  FROM
    bounds
),
monthly AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    SUM(o.total_amount) AS revenue
  FROM
    orders AS o
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
dense AS (
  SELECT
    c.month_start,
    COALESCE(m.revenue, 0) AS revenue
  FROM
    calendar AS c
    LEFT JOIN monthly AS m USING (month_start))
SELECT
  month_start,
  ROUND(revenue, 2) AS revenue,
  ROUND(AVG(revenue) OVER (ORDER BY month_start ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_3_month_average
FROM
  dense
ORDER BY
  month_start;
```

**Expected shape:** A continuous chronological month series.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 5, read `orders` three ways: `bounds` takes the first and last UTC month, `calendar` fills every month between them with `generate_series`, and `monthly` sums `total_amount`; `dense` `LEFT JOIN`s the calendar to `monthly` and turns a missing month into 0.
- **Expected result/shape:** For sql-26 Exercise 5, expected output: one row per calendar month with no gaps, 46 rows on this load; the moving average starts 1203.26, 1503.35, 2197.18 because the first two rows average only one and two months. The final columns are `month_start`, `revenue`, and `moving_3_month_average`. The final order is `month_start`.
- **Independent verification:** For sql-26 Exercise 5, confirm the row count equals the months between `MIN` and `MAX` month inclusive and that the third row averages 1203.26, 1803.43, and 3584.85; then, inside `BEGIN ... ROLLBACK`, move every 2023-04 order back one month and confirm `monthly` drops to 45 rows while the output keeps 46, with 2023-04-01 at 0.00 and its moving average 2197.18 still covering three calendar months.
- **Intermediate relation check:** `bounds` is one row with the first and last order months, and `calendar` lists every month between them. In the checked data both `calendar` and `monthly` had 46 rows, so no month was missing.
- **Clause check:** `calendar LEFT JOIN monthly USING (month_start)` keeps every calendar month, and `COALESCE(m.revenue, 0)` fills a missing one with 0 because the report defines no orders as zero revenue. The `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` frame then averages up to three consecutive months.
- **Alternative/trade-off:** Without the calendar, a three-row frame would average across any gap and silently cover more than three months. Here the gap never happens, so the dense calendar changes nothing yet, but it guards the report as data changes.
- **Edge case:** The first row averages only itself and the second row averages two months, because the frame cannot reach before the first month. Hide or mark those rows if the report needs full three-month windows.

## Exercise 6: Extension

**Prompt:** Reconcile the final cumulative monthly revenue with the independent order total.

**Reasoning:** Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
    SUM(o.total_amount) AS revenue
  FROM
    orders AS o
  GROUP BY
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
running AS (
  SELECT
    month_start,
    SUM(revenue) OVER (ORDER BY month_start ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
  FROM
    monthly
),
final AS (
  SELECT
    cumulative_revenue
  FROM
    running
  ORDER BY
    month_start DESC
  LIMIT 1
)
SELECT
  ROUND(final.cumulative_revenue, 2) AS final_cumulative,
  ROUND(SUM(o.total_amount), 2) AS independent_total,
  ROUND(final.cumulative_revenue - SUM(o.total_amount), 2) AS difference
FROM
  final
  CROSS JOIN orders AS o
GROUP BY
  final.cumulative_revenue;
```

**Expected shape:** One row with zero difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-26 Exercise 6, read from `orders`; aggregate to UTC months in `monthly`, accumulate the monthly revenue with `SUM(revenue) OVER (ORDER BY month_start)` in `running`, keep the last month's cumulative value in `final`, and compare it with an independent `SUM(total_amount)`.
- **Expected result/shape:** For sql-26 Exercise 6, expected output: exactly one row, `final_cumulative` 2355646.89, `independent_total` 2355646.89, and `difference` 0.00. The final columns are `final_cumulative`, `independent_total`, and `difference`.
- **Independent verification:** For sql-26 Exercise 6, confirm one row where `final_cumulative` and `independent_total` are both 2355646.89 and `difference` is 0.00; the `monthly` revenues must already add up to that total before the window is applied.
- **Intermediate relation check:** `running` has one row per month with a cumulative total, and `final` keeps only the newest month's value, a single row.
- **Clause check:** `final CROSS JOIN orders` repeats that single value next to all 4,362 orders, and `GROUP BY final.cumulative_revenue` collapses them back to one row. Both columns show 2,355,646.89 and `difference` is 0.00.
- **Alternative/trade-off:** Two scalar subqueries, one for the last cumulative value and one for `SUM(total_amount)`, avoid the cross join. The cross join is cheap here because one side has a single row.
- **Edge case:** If `monthly` were built from the item formula instead, the difference would be 0.23, because item revenue totals 2,355,647.12. A nonzero difference therefore points to mixed sources, not to a window bug.

## Final self-check

- Which CTE in each answer fixes the grain, and which step adds the window?
- Why can a rank only be filtered in an outer query?
- How many months does your copy of the data have, and why might it differ
  from 46?
- What would a nonzero difference in the reconciliation tell you?
