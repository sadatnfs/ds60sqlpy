-- Day 26: CTEs with Window Functions
-- BEGINNER WORKFLOW — sql-26: CTEs with Windows
-- Guide: sql/postgres-60day/companion-guides/day26_ctes_with_windows.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-26/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
  SELECT o.order_id, o.customer_id, o.order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), ranked AS (
  SELECT line.*,
         RANK() OVER (
           PARTITION BY customer_id
           ORDER BY order_total DESC
         ) AS rnk
  FROM line
)
SELECT customer_id, order_id, order_date, order_total, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY customer_id, rnk, order_total DESC, order_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate monthly stored revenue and its prior-month value/change.
--    Hint: Aggregate to month in a CTE, then lag the monthly measure.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Rank product categories by net revenue within each UTC order month.
--    Hint: Aggregate month/category first, then rank the stable aggregate.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Return the top three category revenue levels per month.
--    Hint: Rank in one CTE and filter the window result outside.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Calculate each category's cumulative share of monthly revenue in descending contribution order.
--    Hint: Divide running category revenue by the full monthly total; use explicit frames.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Calculate a three-month moving average after building a dense month calendar.
--    Hint: Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Reconcile the final cumulative monthly revenue with the independent order total.
--    Hint: Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
