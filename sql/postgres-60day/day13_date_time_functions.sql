-- Day 13: Date/Time functions
-- BEGINNER WORKFLOW — sql-13: Date Time Functions
-- Guide: sql/postgres-60day/companion-guides/day13_date_time_functions.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-13/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
SELECT customer_id, full_name,
       now() - created_at AS tenure,
       date_trunc('month', created_at AT TIME ZONE 'UTC')::date
         AS cohort_month_utc
FROM customers
ORDER BY tenure DESC, customer_id
LIMIT 50;

-- Rolling seven *observed-day* revenue. ROWS counts rows, so a missing calendar
-- day is not manufactured here; a dense calendar exercise addresses that case.
WITH daily AS (
  SELECT (o.order_date AT TIME ZONE 'UTC')::date AS d_utc,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY d_utc
)
SELECT d_utc,
       revenue,
       SUM(revenue) OVER (
         ORDER BY d_utc
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS revenue_7_observed_days
FROM daily
ORDER BY d_utc DESC
LIMIT 30;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List orders from the last 30 days with their UTC calendar date.
--    Hint: Filter the timestamp directly and convert for display only.
--    Inputs: For sql-13 Exercise 1, read from `orders`. Build the answer toward `order_id`, `order_date`, and `utc_order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-13 Exercise 1, expected output: Recent order rows in deterministic order. The final columns are `order_id`, `order_date`, and `utc_order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-13 Exercise 1, run an anti-check that counts rows where NOT ((o.order_date >= CURRENT_TIMESTAMP - INTERVAL '30 days')); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `order_date`, and `utc_order_date` against `orders`. Tie two rows on `o.order_date DESC` and give them different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-13 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.order_date DESC, o.order_id DESC` before applying the row cap.
-- 2. [Query writing] Summarize orders and stored revenue by UTC month.
--    Hint: Convert to UTC before truncating when the reporting calendar is UTC.
--    Inputs: For sql-13 Exercise 2, read from `orders`. Build the answer toward `utc_month`, `order_count`, and `stored_revenue`; keep `utc_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-13 Exercise 2, expected output: One row per observed UTC month. The final columns are `utc_month`, `order_count`, and `stored_revenue`. The final order is `utc_month`.
--    Verify: For sql-13 Exercise 2, independently aggregate `orders` by `utc_month`; require one output row for every distinct `utc_month` tuple and compare `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `utc_month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-13 Exercise 2, confirm the groups are `utc_month`; then check `utc_month` before applying the row cap.
-- 3. [Query writing] Calculate each customer's age in whole days as of the current date.
--    Hint: Compare calendar dates after declaring the UTC reporting date.
--    Inputs: For sql-13 Exercise 3, read from `customers`. Build the answer toward `customer_id`, `created_at`, and `customer_age_days`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-13 Exercise 3, expected output: One row per customer with nonnegative age days. The final columns are `customer_id`, `created_at`, and `customer_age_days`. The final order is `c.customer_id`.
--    Verify: For sql-13 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `created_at`, and `customer_age_days` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-13 Exercise 3, check `c.customer_id` before applying the row cap.
-- 4. [Prediction] Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
--    Hint: Include the month start and exclude the next month start.
--    Inputs: For sql-13 Exercise 4, read from `orders`. Build the answer toward `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-13 Exercise 4, expected output: Orders in exactly one UTC month. The final columns are `order_id`, and `order_date`. The final order is `o.order_date, o.order_id`.
--    Verify: For sql-13 Exercise 4, project `order_id` plus the raw source columns from `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, and `order_date` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-13 Exercise 4, run `bounds` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Compare UTC and America/Los_Angeles display times without stripping the stored instant.
--    Hint: `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
--    Inputs: For sql-13 Exercise 5, read from `events`. Build the answer toward `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`; keep `event_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-13 Exercise 5, expected output: One row per sampled event with two displays of the same instant. The final columns are `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`. The final order is `e.event_time, e.event_id`.
--    Verify: For sql-13 Exercise 5, assert no more than 20 rows, no duplicate `event_id`, and no adjacent pair that violates `e.event_time, e.event_id`. Rejoin the returned keys to `events` to confirm `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `e.event_time, e.event_id`.
--    Hint ladder, rung 1: For sql-13 Exercise 5, check `e.event_time, e.event_id` before applying the row cap.
-- 6. [Extension] Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
--    Hint: Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
--    Inputs: For sql-13 Exercise 6, read from `orders`. Build the answer toward `utc_date`, and `order_count`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-13 Exercise 6, expected output: Exactly seven chronological rows. The final columns are `utc_date`, and `order_count`. The final order is `c.utc_date`.
--    Verify: For sql-13 Exercise 6, project `order_id` plus the raw source columns from `orders` at each join stage; record row count and distinct `order_id`, then assert the final `utc_date`, and `order_count` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-13 Exercise 6, run `calendar`, and `daily_orders` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.

ROLLBACK;
