-- Day 18: LAG and LEAD
-- BEGINNER WORKFLOW — sql-18: Lag Lead
-- Guide: sql/postgres-60day/companion-guides/day18_lag_lead.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-18/ copy, and prints the full
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
-- Focus: Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
-- Assumptions: Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
-- Pitfall: Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
-- Predict row grain and NULL/order behavior before executing each example.

-- Period-over-period change per customer
WITH cust_orders AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount
  FROM orders o
)
SELECT customer_id,
       order_id,
       order_date,
       total_amount,
       LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS prev_order_amount,
       total_amount - LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS delta_from_prev,
       LEAD(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS next_order_amount
FROM cust_orders
ORDER BY customer_id, order_date, order_id
LIMIT 100;

-- YoY comparison by month
WITH monthly AS (
  SELECT date_trunc('month', order_date AT TIME ZONE 'UTC')::date AS month_utc,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY month_utc
), compared AS (
  SELECT month_utc,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month_utc) AS revenue_prev_year
  FROM monthly
)
SELECT month_utc,
       revenue,
       revenue_prev_year,
       ROUND(
         (revenue - revenue_prev_year)
         / NULLIF(revenue_prev_year, 0),
         4
       ) AS yoy_growth
FROM compared
ORDER BY month_utc DESC
LIMIT 36;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show each order with the previous order timestamp for that customer.
--    Hint: Partition by customer and order by timestamp plus ID.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Calculate days since each customer's previous order.
--    Hint: Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Show each promotion with the next promotion start date for the same product.
--    Hint: Partition by product and define a stable chronological order.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
--    Hint: NULL means there is no prior observation; preserve that semantic state.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Compute month-over-month stored-revenue change after aggregating to month grain.
--    Hint: Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Compare each product price with the next higher price in its category.
--    Hint: Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.

ROLLBACK;
