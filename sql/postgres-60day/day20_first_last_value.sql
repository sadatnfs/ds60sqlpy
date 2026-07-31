-- Day 20: FIRST_VALUE and LAST_VALUE
-- BEGINNER WORKFLOW — sql-20: First Last Value
-- Guide: sql/postgres-60day/companion-guides/day20_first_last_value.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-20/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
-- Assumptions: First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
-- Pitfall: The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
-- Predict row grain and NULL/order behavior before executing each example.

-- First and last order amount per customer
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       FIRST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS first_order_amount,
       LAST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS last_order_amount
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 100;

-- Compare current to first/last
WITH per_cust AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount,
         FIRST_VALUE(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         ) AS first_amt
  FROM orders o
)
SELECT *, ROUND(total_amount - first_amt, 2) AS delta_from_first
FROM per_cust
ORDER BY customer_id, order_date, order_id
LIMIT 100;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show every order with the customer's first and last order timestamps.
--    Hint: Use one full-partition frame from unbounded preceding through unbounded following.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Show each product with the cheapest and most expensive price in its category.
--    Hint: Order by price and use a full frame; values tie without needing row identity.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Compare every payment with the first and last payment amount for its order.
--    Hint: Partition by order, order by timestamp/payment ID, and keep the full frame.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 4. [Prediction] Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
--    Hint: The default ends at the current row; explicit following reaches the true last row.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Return one first and one last order per customer without using window output as an accidental duplicate report.
--    Hint: Compute first/last IDs with full-frame windows, then select distinct customer-level output.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
--    Hint: `DISTINCT ON` keeps the first row under its mandatory leading order keys.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.

ROLLBACK;
