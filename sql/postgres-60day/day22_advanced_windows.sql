-- Day 22: Advanced Window Function Scenarios
-- BEGINNER WORKFLOW — sql-22: Advanced Windows
-- Guide: sql/postgres-60day/companion-guides/day22_advanced_windows.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-22/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
-- Assumptions: Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
-- Pitfall: Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
-- Predict row grain and NULL/order behavior before executing each example.

-- Multi-level analysis: rank within partition, then across all
WITH prod_rev AS (
  SELECT p.product_id,
         p.name,
         p.category,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.product_id, p.name, p.category
)
SELECT *,
  RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
  RANK() OVER (ORDER BY revenue DESC) AS rank_overall
FROM prod_rev
ORDER BY category, rank_in_category, revenue DESC, product_id
LIMIT 100;

-- Combine multiple windows in one query
SELECT o.customer_id,
       o.order_id,
       o.total_amount,
       AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS avg_per_customer,
       SUM(o.total_amount) OVER () AS total_revenue_all,
       RANK() OVER (PARTITION BY o.customer_id ORDER BY o.total_amount DESC) AS order_value_rank
FROM orders o
ORDER BY o.customer_id,
         order_value_rank,
         o.total_amount DESC,
         o.order_id
LIMIT 100;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Use a named window to show each order with customer count, average, first date, and last date.
--    Hint: Name a full-partition customer window once and reuse it.
--    Inputs: Use only the declared lesson objects (order_items, products, orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Compare each employee salary with the average of other employees in the department.
--    Hint: Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.
--    Inputs: Use only the declared lesson objects (order_items, products, orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 3. [Query writing] Show each order's distance from its customer's average and standard deviation.
--    Hint: Compute independent partition windows and guard interpretation when variation is zero.
--    Inputs: Use only the declared lesson objects (order_items, products, orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Sessionize events using a 30-minute gap and predict why the first event starts a session.
--    Hint: Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.
--    Inputs: Use only the declared lesson objects (order_items, products, orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Find consecutive calendar-day islands in customer order dates without nesting windows.
--    Hint: Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.
--    Inputs: Use only the declared lesson objects (order_items, products, orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Summarize sessions from the sessionized event stream with start, end, event count, and duration.
--    Hint: Aggregate only after session IDs exist at event grain.
--    Inputs: Use only the declared lesson objects (order_items, products, orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
