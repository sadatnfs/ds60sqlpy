-- Day 26: CTEs with Window Functions
-- BEGINNER WORKFLOW - sql-26: CTEs with Window Functions
-- Guide: sql/postgres-60day/companion-guides/day26_ctes_with_windows.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-26.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
-- Assumptions: Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
-- Pitfall: Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
-- Predict row grain and NULL/order behavior before executing each example.
WITH line AS (
  SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    o.order_date
),
ranked AS (
  SELECT
    line.*,
    RANK() OVER (PARTITION BY customer_id ORDER BY order_total DESC) AS rnk
  FROM
    line
)
SELECT
  customer_id,
  order_id,
  order_date,
  order_total,
  rnk
FROM
  ranked
WHERE
  rnk <= 3
ORDER BY
  customer_id,
  rnk,
  order_total DESC,
  order_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate monthly stored revenue and its prior-month value/change.
--    Hint: Aggregate to month in a CTE, then lag the monthly measure.
--    Inputs: For sql-26 Exercise 1, read from `orders`, aggregate `SUM(total_amount)` to one row per UTC month in the CTE `monthly`, then use `LAG(revenue) OVER (ORDER BY month_start)` in `compared` and return `change = revenue - previous_revenue`.
--    Expected result/shape: For sql-26 Exercise 1, expected output: one row per UTC month with orders, 46 rows from 2023-02-01 to 2026-11-01 on a November 2026 load (seed dates move with the load date); the first row is 1203.26 with NULL `previous_revenue` and `change`, and the second is 1803.43 with a change of 600.17. The final columns are `month_start`, `revenue`, `previous_revenue`, and `change`. The final order is `month_start`.
--    Verify: For sql-26 Exercise 1, confirm that `month_start` is unique and that the row count equals `SELECT COUNT(DISTINCT date_trunc('month', order_date AT TIME ZONE 'UTC')) FROM orders`; exactly one row, the earliest month, has NULL `previous_revenue` and `change`, and the `revenue` values add up to 2355646.89.
--    Hint ladder, rung 1: For sql-26 Exercise 1, run `monthly` alone and confirm one row per `month_start` before `compared` applies `LAG`.
-- 2. [Query writing] Rank product categories by net revenue within each UTC order month.
--    Hint: Aggregate month/category first, then rank the stable aggregate.
--    Inputs: For sql-26 Exercise 2, read `orders` joined to `order_items` and `products`, sum net item revenue `unit_price * quantity * (1 - discount)` per UTC month and `category` in `category_month`, then apply `DENSE_RANK()` partitioned by `month_start` and ordered by `revenue DESC`.
--    Expected result/shape: For sql-26 Exercise 2, expected output: 6 rows per month, one per category, ranked 1 through 6 (276 rows for 46 months on this load); the first month, 2023-02-01, runs from Apparel at 407.05 down to Home at 30.20. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
--    Verify: For sql-26 Exercise 2, confirm `COUNT(*)` is 6 times `COUNT(DISTINCT month_start)`, every month has ranks 1 through 6 exactly once, and the 2023-02-01 revenues add to 1203.26, the stored total for that month in Exercise 1; then rank the fixture `VALUES ('A', 10), ('B', 10), ('C', 5), ('D', 3)` and confirm `DENSE_RANK` gives 1, 1, 2, 3 where `RANK` gives 1, 1, 3, 4.
--    Hint ladder, rung 1: For sql-26 Exercise 2, run `category_month` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 3. [Query writing] Return the top three category revenue levels per month.
--    Hint: Rank in one CTE and filter the window result outside.
--    Inputs: For sql-26 Exercise 3, read `orders`, `order_items`, and `products` into the same `category_month` CTE as Exercise 2, rank it in a second CTE `ranked`, and filter `revenue_rank <= 3` only in the outer query, after the window has run.
--    Expected result/shape: For sql-26 Exercise 3, expected output: 3 rows per month (138 rows for 46 months on this load, because no month has a revenue tie); 2023-02-01 keeps Apparel, Books, and Electronics, and 2026-11-01 keeps Sports, Books, and Apparel. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
--    Verify: For sql-26 Exercise 3, confirm `COUNT(*)` is 3 times `COUNT(DISTINCT month_start)` and each month shows ranks 1, 2, and 3 once; then apply the same rank and filter to `VALUES ('A', 10), ('B', 10), ('C', 5), ('D', 3), ('E', 1)` and confirm four rows survive (ranks 1, 1, 2, 3), showing that ties in `DENSE_RANK` can return more than three categories in a month.
--    Hint ladder, rung 1: For sql-26 Exercise 3, run `category_month`, and `ranked` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 4. [Prediction] Calculate each category's cumulative share of monthly revenue in descending contribution order.
--    Hint: Divide running category revenue by the full monthly total; use explicit frames.
--    Inputs: For sql-26 Exercise 4, read `orders`, `order_items`, and `products` into `category_month`, then divide a running `SUM(revenue)` ordered by `revenue DESC, category` with a `ROWS` frame by the month total `SUM(revenue) OVER (PARTITION BY month_start)`, guarded by `NULLIF`.
--    Expected result/shape: For sql-26 Exercise 4, expected output: 276 rows on this load, 6 per month; in 2023-02-01 the shares climb 0.3383, 0.5708, 0.7510, 0.8968, 0.9749, and 1.0000. The final columns are `month_start`, `category`, `revenue`, and `cumulative_revenue_share`. The final order is `month_start, revenue DESC, category`.
--    Verify: For sql-26 Exercise 4, confirm the last row of every month is exactly 1.0000 (46 such rows, one per month, and no month whose maximum differs) and that the first 2023-02-01 share equals 407.05 / 1203.26; then run both frames over `VALUES ('A', 10.0), ('B', 10.0), ('C', 5.0)` and confirm `ROWS` gives 0.4000, 0.8000, 1.0000 while the default `RANGE` frame gives 0.8000 to both tied rows.
--    Hint ladder, rung 1: For sql-26 Exercise 4, run `category_month` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 5. [Debugging] Calculate a three-month moving average after building a dense month calendar.
--    Hint: Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
--    Inputs: For sql-26 Exercise 5, read `orders` three ways: `bounds` takes the first and last UTC month, `calendar` fills every month between them with `generate_series`, and `monthly` sums `total_amount`; `dense` `LEFT JOIN`s the calendar to `monthly` and turns a missing month into 0.
--    Expected result/shape: For sql-26 Exercise 5, expected output: one row per calendar month with no gaps, 46 rows on this load; the moving average starts 1203.26, 1503.35, 2197.18 because the first two rows average only one and two months. The final columns are `month_start`, `revenue`, and `moving_3_month_average`. The final order is `month_start`.
--    Verify: For sql-26 Exercise 5, confirm the row count equals the months between `MIN` and `MAX` month inclusive and that the third row averages 1203.26, 1803.43, and 3584.85; then, inside `BEGIN ... ROLLBACK`, move every 2023-04 order back one month and confirm `monthly` drops to 45 rows while the output keeps 46, with 2023-04-01 at 0.00 and its moving average 2197.18 still covering three calendar months.
--    Hint ladder, rung 1: For sql-26 Exercise 5, run `bounds`, `calendar`, `monthly`, and `dense` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. [Extension] Reconcile the final cumulative monthly revenue with the independent order total.
--    Hint: Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
--    Inputs: For sql-26 Exercise 6, read from `orders`; aggregate to UTC months in `monthly`, accumulate the monthly revenue with `SUM(revenue) OVER (ORDER BY month_start)` in `running`, keep the last month's cumulative value in `final`, and compare it with an independent `SUM(total_amount)`.
--    Expected result/shape: For sql-26 Exercise 6, expected output: exactly one row, `final_cumulative` 2355646.89, `independent_total` 2355646.89, and `difference` 0.00. The final columns are `final_cumulative`, `independent_total`, and `difference`.
--    Verify: For sql-26 Exercise 6, confirm one row where `final_cumulative` and `independent_total` are both 2355646.89 and `difference` is 0.00; the `monthly` revenues must already add up to that total before the window is applied.
--    Hint ladder, rung 1: For sql-26 Exercise 6, check that the `monthly` revenues add up to 2355646.89 before you build `running` and `final`.
ROLLBACK;
