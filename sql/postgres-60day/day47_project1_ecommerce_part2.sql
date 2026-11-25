-- Day 47: Project 1 - E-commerce Analytics (Part 2)
-- BEGINNER WORKFLOW - sql-47: Project 1 Ecommerce Part 2
-- Guide: sql/postgres-60day/companion-guides/day47_project1_ecommerce_part2.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-47.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Topics: Cohort retention analysis
BEGIN;
SET search_path TO training, public;

WITH orders_m AS (
  SELECT
    o.customer_id,
    date_trunc('month', o.order_date)::date AS order_month
  FROM
    orders o
  GROUP BY
    o.customer_id,
    date_trunc('month', o.order_date)
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at)::date AS cohort_month
  FROM
    customers c
),
retention AS (
  SELECT
    co.cohort_month,
    om.order_month,
    (EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12 + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month)))::int AS month_offset,
    COUNT(DISTINCT om.customer_id) AS active_customers
  FROM
    orders_m om
    JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY
    co.cohort_month,
    om.order_month
)
SELECT
  cohort_month,
  month_offset,
  active_customers
FROM
  retention
WHERE
  month_offset BETWEEN 0 AND 12
ORDER BY
  cohort_month DESC,
  month_offset;

-- Exercises
-- 1. Convert active_customers to retention_rate by dividing by cohort size.
--    Inputs: For sql-47 Exercise 1, start from the lesson's cohort query over `customers` and `orders`: keep the `cohort_sizes` CTE (one row per signup `cohort_month`) and divide `active_customers` by `cohort_size` as `numeric` to produce `retention_rate`, rounded to 4 places.
--    Expected result/shape: For sql-47 Exercise 1, expected output: one row per `cohort_month` and `month_offset` for the latest six cohorts, with every `retention_rate` between 0 and 1. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`.
--    Verify: For sql-47 Exercise 1, for one `cohort_month`, recount its customers with `SELECT COUNT(*) FROM customers WHERE date_trunc('month', created_at)::date = <that month>` and compare the result with `cohort_size`; then confirm that `retention_rate = ROUND(active_customers::numeric / cohort_size, 4)` and `active_customers <= cohort_size` on every row.
--    Hint ladder, rung 1: For sql-47 Exercise 1, run `cohort_sizes` alone and check one row per `cohort_month` before you join it to the activity counts.
-- 2. Chart retention curves for last 6 cohorts (outside SQL).
--    Inputs: For sql-47 Exercise 2, reuse the Exercise 1 query and keep only cohorts listed in `latest_six`, the six newest `cohort_month` values from `cohort_sizes`; the charting itself happens outside SQL, with `cohort_month` as the series, `month_offset` on the x axis, and `retention_rate` on the y axis.
--    Expected result/shape: For sql-47 Exercise 2, expected output: one row per (`cohort_month`, `month_offset`) pair for the six newest cohorts, ordered by `cohort_month DESC`, then `month_offset`, with columns `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; 27 rows on our load, because each cohort has only as many offsets as months have passed (2 for the newest, 7 for the sixth).
--    Verify: For sql-47 Exercise 2, confirm 6 distinct `cohort_month` values, a unique (`cohort_month`, `month_offset`) pair on every row, one `cohort_size` per cohort, and `active_customers <= cohort_size` everywhere; then recount one point directly, such as the newest cohort at offset 1, with `COUNT(DISTINCT o.customer_id)` over orders in the next calendar month from customers created in that cohort month, and compare it with `active_customers` (8 of 9 on our load).
--    Hint ladder, rung 1: For sql-47 Exercise 2, run `cohorts`, `cohort_sizes`, `active_months`, `retained`, `curves`, and `latest_six` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 3. Prediction: decide whether signup month or first-order month is the better
--    cohort anchor for a purchase-retention question; state the metric change.
--    Inputs: For sql-47 Exercise 3, `LEFT JOIN orders` to `customers`, group by `c.customer_id` and the signup month, and report `date_trunc('month', c.created_at)` as `signup_cohort` beside `date_trunc('month', MIN(o.order_date))` as `first_order_cohort`.
--    Expected result/shape: For sql-47 Exercise 3, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `signup_cohort`, and `first_order_cohort`, ordered by `customer_id`; `first_order_cohort` is `NULL` for the 62 customers without orders.
--    Verify: For sql-47 Exercise 3, count the rows where the two anchors match (39), where the first order comes in a later month (399), and where `first_order_cohort` is `NULL` (62), and confirm they add up to 500; check customer 2, who signed up in 2026-09 but first ordered in 2026-10 on our load, and confirm the largest gap is 10 months, which is how far a curve shifts when it switches anchors.
--    Hint ladder, rung 1: For sql-47 Exercise 3, compute `MIN(o.order_date)` per customer first, then truncate both timestamps to months; keep the join `LEFT` so the 62 customers without orders stay in the result.
-- 4. Construction: build a complete cohort/month-offset spine so missing
--    activity appears as zero rather than an absent row.
--    Inputs: For sql-47 Exercise 4, `CROSS JOIN` the 48 signup cohorts in `sizes` with `generate_series(0, 12)` in `offsets`, then `LEFT JOIN` the `activity` counts (distinct ordering customers by cohort and month offset) on both `cohort_month` and `month_offset`, using `COALESCE(..., 0)` for missing activity.
--    Expected result/shape: For sql-47 Exercise 4, expected output: 624 rows, one per (`cohort_month`, `month_offset`) pair for 48 cohorts times 13 offsets, with columns `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`, ordered by `cohort_month DESC`, then `month_offset`.
--    Verify: For sql-47 Exercise 4, confirm that every cohort has exactly 13 rows with offsets 0 to 12 and that `cohort_size` summed over one offset is 500; count the zero rows (137 on our load) and compare them with the latest order month: 66 are offsets after it, which cannot be observed yet, and 71 are observed months with no orders. Then remove the `LEFT JOIN` and use an inner join, and confirm that every zero row disappears.
--    Hint ladder, rung 1: For sql-47 Exercise 4, run `cohorts`, `sizes`, `offsets`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 5. Debugging: prevent month_offset < 0 when synthetic orders precede a
--    customer's recorded signup timestamp.
--    Inputs: For sql-47 Exercise 5, join `customers` to `orders`, group by `customer_id` and `created_at`, and keep customers whose `MIN(o.order_date)` is earlier than `c.created_at`, which would produce a negative `month_offset`.
--    Expected result/shape: For sql-47 Exercise 5, expected output: one row per `customer_id` whose first order precedes signup, with columns `customer_id`, `created_at`, and `first_order_at`, ordered by `customer_id`; on the course data this returns 0 rows, which is the passing answer.
--    Verify: For sql-47 Exercise 5, confirm the empty result independently: the smallest gap between signup and first order over the 438 ordering customers is just over 2 days. Then, in a transaction, set customer 1's earliest order to `created_at - interval '1 day'`, rerun the query, confirm it returns exactly that customer with `first_order_at` one day before `created_at`, and `ROLLBACK`.
--    Hint ladder, rung 1: For sql-47 Exercise 5, compare `MIN(o.order_date)` with `c.created_at` in `HAVING`, after grouping; an empty result is correct here, so plan a rolled-back edit that makes one row appear.
-- 6. Edge case: separate not-yet-observable future offsets from observed zero
--    retention instead of displaying both as zero.
--    Inputs: For sql-47 Exercise 6, take the latest observed month as `date_trunc('month', MAX(order_date))` from `orders`, build a `sample` of (`cohort_month`, `month_offset`) pairs with `VALUES` for the current month at offsets 0 and 6, and flag each pair observable when `cohort_month + make_interval(months => month_offset)` is on or before that month.
--    Expected result/shape: For sql-47 Exercise 6, expected output: 2 rows, one per sample pair, with columns `cohort_month`, `month_offset`, and `is_observable`; offset 0 is `true` and offset 6 is `false` when the latest order month is the current month, as it is on a fresh load. A rate for an unobservable offset should then be `NULL`, never 0.
--    Verify: For sql-47 Exercise 6, confirm the latest observed month from `orders` (2026-11 on our load) and check both flags by hand; then apply the same test to the 624-row spine from Exercise 4 and confirm 66 rows are not observable, all currently shown as 0, while the 71 observed zeros stay real zeros. On an older load where `CURRENT_DATE` is past the last order month, offset 0 also becomes `false`.
--    Hint ladder, rung 1: For sql-47 Exercise 6, run `latest` alone and note the latest order month; then add months to each sample `cohort_month` and compare the result with that month.
ROLLBACK;
