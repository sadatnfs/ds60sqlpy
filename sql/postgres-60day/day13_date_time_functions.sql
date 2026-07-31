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
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: List orders from the last 30 days with their UTC calendar date” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `utc_order_date`, `o`, `utc`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Filter the timestamp directly and convert for display only.
-- 2. [Query writing] Summarize orders and stored revenue by UTC month.
--    Hint: Convert to UTC before truncating when the reporting calendar is UTC.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Summarize orders and stored revenue by UTC month” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `utc_month`, `order_count`, `stored_revenue`, `o`, `utc`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Convert to UTC before truncating when the reporting calendar is UTC.
-- 3. [Query writing] Calculate each customer's age in whole days as of the current date.
--    Hint: Compare calendar dates after declaring the UTC reporting date.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Calculate each customer's age in whole days as of the current date” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `of`, `evidence`, `customer_age_days`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Compare calendar dates after declaring the UTC reporting date.
-- 4. [Prediction] Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
--    Hint: Include the month start and exclude the next month start.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 needs the plan evidence for “Prediction: Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `month_start`, `next_month_start`, `o`, `b`, `utc`.
--    Verify: For Exercise 4, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
--    Hint ladder, rung 1: Start with the guide's first rung: Include the month start and exclude the next month start.
-- 5. [Debugging] Compare UTC and America/Los_Angeles display times without stripping the stored instant.
--    Hint: `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
--    Inputs: Use `events` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 requires a written prediction and the observed result for “Debugging: Compare UTC and America/LosAngeles display times without stripping the stored instant”. Show both compared result shapes at one row at TIME ZONE on timestamptz produces a local wall-clock display value grain, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `utc_wall_time`, `los_angeles_wall_time`, `e`, `utc`.
--    Verify: For Exercise 5, run the two forms over the identical rows in `events`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: AT TIME ZONE on timestamptz produces a local wall-clock display value.
-- 6. [Extension] Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
--    Hint: Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero” observable through the exact DDL/DML command tag plus one row per requested calendar/cohort bucket and grouping key; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `utc_date`, `order_count`, `o`, `c`, `d`, `utc`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `utc_date`, `order_count`, `o`, `c`, `d`, `utc`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Generate the date spine first, aggregate orders by the same UTC date, then COALESCE absent counts.

ROLLBACK;
