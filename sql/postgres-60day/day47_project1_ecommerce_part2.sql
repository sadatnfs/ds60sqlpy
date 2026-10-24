-- Day 47: Project 1 - E-commerce Analytics (Part 2)
-- BEGINNER WORKFLOW — sql-47: Project1 Ecommerce Part2
-- Guide: sql/postgres-60day/companion-guides/day47_project1_ecommerce_part2.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-47/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), retention AS (
  SELECT co.cohort_month,
         om.order_month,
         (
           EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT cohort_month, month_offset, active_customers
FROM retention
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;

-- Exercises
-- 1. Convert active_customers to retention_rate by dividing by cohort size.
--    Inputs: For sql-47 Exercise 1, read from `orders`, `customers`, and `age`. Build the answer toward `cohort_sizes`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-47 Exercise 1, expected output: one row per `order_id`. The final columns are `cohort_sizes`.
--    Verify: For sql-47 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `cohort_sizes` against `orders`, `customers`, and `age`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-47 Exercise 1, select `order_id` from `orders`, `customers`, and `age` before adding derived columns.
-- 2. Chart retention curves for last 6 cohorts (outside SQL).
--    Inputs: For sql-47 Exercise 2, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-47 Exercise 2, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `cohort_month DESC, month_offset`.
--    Verify: For sql-47 Exercise 2, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` values match those staged rows without unintended fanout or loss. Tie two rows on `cohort_month DESC` and give them different `month_offset` values; verify `cohort_month DESC, month_offset` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-47 Exercise 2, run `cohorts`, `cohort_sizes`, `active_months`, `retained`, `curves`, and `latest_six` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 3. Prediction: decide whether signup month or first-order month is the better
--    cohort anchor for a purchase-retention question; state the metric change.
--    Inputs: For sql-47 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `signup_cohort`, and `first_order_cohort`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-47 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `signup_cohort`, and `first_order_cohort`. The final order is `c.customer_id`.
--    Verify: For sql-47 Exercise 3, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `first_order_cohort` tuple by tuple. Use one key absent from `orders`; then tie two candidates on `c.customer_id` and verify `c.customer_id` selects the same row on every run.
--    Hint ladder, rung 1: For sql-47 Exercise 3, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
-- 4. Construction: build a complete cohort/month-offset spine so missing
--    activity appears as zero rather than an absent row.
--    Inputs: For sql-47 Exercise 4, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-47 Exercise 4, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month DESC, x.month_offset`.
--    Verify: For sql-47 Exercise 4, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
--    Hint ladder, rung 1: For sql-47 Exercise 4, run `cohorts`, `sizes`, `offsets`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 5. Debugging: prevent month_offset < 0 when synthetic orders precede a
--    customer's recorded signup timestamp.
--    Inputs: For sql-47 Exercise 5, read from `customers`, and `orders`. Build the answer toward `customer_id`, `created_at`, and `first_order_at`; keep `customer_id`, and `created_at` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-47 Exercise 5, expected output: one row per `customer_id`, and `created_at`. The final columns are `customer_id`, `created_at`, and `first_order_at`. The final order is `c.customer_id`.
--    Verify: For sql-47 Exercise 5, independently aggregate `customers`, and `orders` by `customer_id`, and `created_at`; require one output row for every distinct `customer_id`, and `created_at` tuple and compare `first_order_at` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `first_order_at` for the existing `customer_id`, and `created_at` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-47 Exercise 5, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `created_at` so the exact fanout or loss is visible.
-- 6. Edge case: separate not-yet-observable future offsets from observed zero
--    retention instead of displaying both as zero.
--    Inputs: For sql-47 Exercise 6, read from `orders`, and `sample`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-47 Exercise 6, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
--    Verify: For sql-47 Exercise 6, project `order_id` plus the raw source columns from `orders`, and `sample` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-47 Exercise 6, run `latest` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.

ROLLBACK;
