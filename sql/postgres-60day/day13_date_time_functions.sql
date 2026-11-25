-- Day 13: Date/Time functions
-- BEGINNER WORKFLOW - sql-13: Date Time Functions
-- Guide: sql/postgres-60day/companion-guides/day13_date_time_functions.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-13.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Treat timestamps as instants, dates as calendar values, and reporting zones/window boundaries as explicit parts of the query.
-- Assumptions: Stored event/order timestamps are `timestamptz`. Relative examples use the database clock; reports label UTC explicitly where conversion matters.
-- Pitfall: `BETWEEN` is inclusive at both ends and is often wrong for adjacent time windows; use half-open `[start, end)` predicates.
-- Predict row grain and NULL/order behavior before executing each example.
-- Age of customer in system
SELECT
  customer_id,
  full_name,
  now() - created_at AS tenure,
  date_trunc('month', created_at AT TIME ZONE 'UTC')::date AS cohort_month_utc
FROM
  customers
ORDER BY
  tenure DESC,
  customer_id
LIMIT 50;

-- Rolling seven *observed-day* revenue. ROWS counts rows, so a missing calendar
-- day is not manufactured here; a dense calendar exercise addresses that case.
WITH daily AS (
  SELECT
    (o.order_date AT TIME ZONE 'UTC')::date AS d_utc,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    d_utc
)
SELECT
  d_utc,
  revenue,
  SUM(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_7_observed_days
FROM
  daily
ORDER BY
  d_utc DESC
LIMIT 30;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List orders from the last 30 days with their UTC calendar date.
--    Hint: Filter the timestamp directly and convert for display only.
--    Inputs: For sql-13 Exercise 1, read `orders.order_date` (`timestamptz`) and keep rows on or after `CURRENT_TIMESTAMP - INTERVAL '30 days'`, adding `(o.order_date AT TIME ZONE 'UTC')::date` as `utc_order_date`.
--    Expected result/shape: For sql-13 Exercise 1, return 209 rows on a freshly loaded fixture, newest first from order 2258 (`2026-11-23` UTC when loaded on 2026-11-25) back to order 734, the oldest order still inside the window. The final columns are `order_id`, `order_date`, and `utc_order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-13 Exercise 1, confirm 209 distinct `order_id` values and 0 returned rows where `order_date < CURRENT_TIMESTAMP - INTERVAL '30 days'`. Inside a rolled-back transaction, insert one order dated `CURRENT_TIMESTAMP - INTERVAL '29 days'` and one dated 31 days back; the count must become 210, so only the first one enters the window.
--    Hint ladder, rung 1: For sql-13 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.order_date DESC, o.order_id DESC` before applying the row cap.
-- 2. [Query writing] Summarize orders and stored revenue by UTC month.
--    Hint: Convert to UTC before truncating when the reporting calendar is UTC.
--    Inputs: For sql-13 Exercise 2, bucket all 4,362 `orders` by `date_trunc('month', o.order_date AT TIME ZONE 'UTC')`, counting orders and summing `total_amount` per UTC month.
--    Expected result/shape: For sql-13 Exercise 2, return 46 month rows on a freshly loaded fixture, from `2023-02-01` (2 orders, 1203.26) to the current month, which holds 151 orders and 85364.67 when loaded on 2026-11-25. The final columns are `utc_month`, `order_count`, and `stored_revenue`. The final order is `utc_month`.
--    Verify: For sql-13 Exercise 2, confirm the 46 `order_count` values add up to 4,362 and the `stored_revenue` values add up to 2355646.89, matching `SELECT SUM(total_amount) FROM orders`. Run it again after `SET LOCAL timezone = 'America/Los_Angeles'` in a rolled-back transaction; the output must not change, because the month is computed from the UTC wall time rather than the session zone.
--    Hint ladder, rung 1: For sql-13 Exercise 2, confirm the groups are `utc_month`; then check `utc_month` before applying the row cap.
-- 3. [Query writing] Calculate each customer's age in whole days as of the current date.
--    Hint: Compare calendar dates after declaring the UTC reporting date.
--    Inputs: For sql-13 Exercise 3, subtract each customer's UTC `created_at` date from today's UTC date for all 500 `customers` rows.
--    Expected result/shape: For sql-13 Exercise 3, return 500 rows, one per customer, with `customer_age_days` between 33 (customer 86) and 1,483 (customer 429) on a freshly loaded fixture; customer 1 shows 48. The final columns are `customer_id`, `created_at`, and `customer_age_days`. The final order is `c.customer_id`.
--    Verify: For sql-13 Exercise 3, confirm 500 distinct `customer_id` values and 0 rows with a negative `customer_age_days`. Inside a rolled-back transaction, set customer 1's `created_at` to `CURRENT_TIMESTAMP`; its age must become 0, not 1, because both sides are converted to UTC dates before subtracting.
--    Hint ladder, rung 1: For sql-13 Exercise 3, check `c.customer_id` before applying the row cap.
-- 4. [Prediction] Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
--    Hint: Include the month start and exclude the next month start.
--    Inputs: For sql-13 Exercise 4, build the current UTC month's start and the next month's start in a one-row `bounds` CTE, then keep `orders` with `order_date >= month_start AT TIME ZONE 'UTC'` and `order_date < next_month_start AT TIME ZONE 'UTC'`.
--    Expected result/shape: For sql-13 Exercise 4, return one row per order placed in the current UTC month, oldest first; on a fixture loaded on 2026-11-25 that is 151 orders, from order 3106 on 2026-11-01 to order 2258 on 2026-11-23. The final columns are `order_id`, and `order_date`. The final order is `o.order_date, o.order_id`.
--    Verify: For sql-13 Exercise 4, confirm the row count equals the last `order_count` from Exercise 2 (151 on that load). Inside a rolled-back transaction, insert one order one microsecond before the month start, one exactly at the month start, and one exactly at the next month's start; the count must rise by 1 only, and the new earliest row must be the one at midnight on the first.
--    Hint ladder, rung 1: For sql-13 Exercise 4, run `bounds` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Compare UTC and America/Los_Angeles display times without stripping the stored instant.
--    Hint: `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
--    Inputs: For sql-13 Exercise 5, sort the 20,000 `events` rows by `event_time, event_id`, keep the first 20, and show each instant as `AT TIME ZONE 'UTC'` and `AT TIME ZONE 'America/Los_Angeles'` wall times.
--    Expected result/shape: For sql-13 Exercise 5, return 20 rows from event 17121 (`2022-12-09 07:14:09.605663` UTC, `2022-12-08 23:14:09.605663` in Los Angeles) to event 3362 on 2023-01-22; every winter row shows Los Angeles 8 hours behind UTC. The final columns are `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`. The final order is `e.event_time, e.event_id`.
--    Verify: For sql-13 Exercise 5, confirm 20 distinct `event_id` values and that the 21st row of the same ordering is event 17001, which the `LIMIT` cuts off. Rerun after `SET LOCAL timezone = 'America/Los_Angeles'` in a rolled-back transaction: `event_time` must display as `2022-12-08 23:14:09.605663-08` while `utc_wall_time` stays the same. Event 6402 (`2023-07-01 01:13` UTC) shows the summer gap of 7 hours.
--    Hint ladder, rung 1: For sql-13 Exercise 5, check `e.event_time, e.event_id` before applying the row cap.
-- 6. [Extension] Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
--    Hint: Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
--    Inputs: For sql-13 Exercise 6, generate the last seven UTC dates with `generate_series`, count `orders` per UTC date from the first of those days onward, and `LEFT JOIN` the counts to the calendar.
--    Expected result/shape: For sql-13 Exercise 6, return exactly 7 rows ending with today's UTC date; on a fixture loaded on 2026-11-25 the counts run 4, 4, 2, 2, 1, 0, 0 from 2026-11-19, and the two zero days come from `COALESCE` on dates with no orders. The final columns are `utc_date`, and `order_count`. The final order is `c.utc_date`.
--    Verify: For sql-13 Exercise 6, confirm 7 distinct dates and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6) AT TIME ZONE 'UTC'` (13 on that load). Inside a rolled-back transaction, insert an order at `CURRENT_TIMESTAMP`; the last row must change from 0 to 1 and the row count must stay 7.
--    Hint ladder, rung 1: For sql-13 Exercise 6, run `calendar`, and `daily_orders` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
ROLLBACK;
