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
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Chart retention curves for last 6 cohorts (outside SQL).
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: decide whether signup month or first-order month is the better
--    cohort anchor for a purchase-retention question; state the metric change.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: build a complete cohort/month-offset spine so missing
--    activity appears as zero rather than an absent row.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: prevent month_offset < 0 when synthetic orders precede a
--    customer's recorded signup timestamp.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: separate not-yet-observable future offsets from observed zero
--    retention instead of displaying both as zero.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
