-- Day 13: Date/Time functions
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
-- 2. [Query writing] Summarize orders and stored revenue by UTC month.
--    Hint: Convert to UTC before truncating when the reporting calendar is UTC.
-- 3. [Query writing] Calculate each customer's age in whole days as of the current date.
--    Hint: Compare calendar dates after declaring the UTC reporting date.
-- 4. [Prediction] Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
--    Hint: Include the month start and exclude the next month start.
-- 5. [Debugging] Compare UTC and America/Los_Angeles display times without stripping the stored instant.
--    Hint: `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
-- 6. [Extension] Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
--    Hint: Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.

ROLLBACK;
