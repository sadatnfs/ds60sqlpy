-- Day 23: CTEs Introduction
-- BEGINNER WORKFLOW — sql-23: CTEs Intro
-- Guide: sql/postgres-60day/companion-guides/day23_ctes_intro.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-23/ copy, and prints the full
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
-- Focus: Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.
-- Assumptions: Each CTE declares its output grain. PostgreSQL 16 may inline a side-effect-free single-use CTE unless `MATERIALIZED` is requested.
-- Pitfall: A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
-- Predict row grain and NULL/order behavior before executing each example.

-- Rewrite subqueries as CTEs
WITH order_lines AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), top_customers AS (
  SELECT customer_id,
         SUM(order_total) AS lifetime_revenue
  FROM order_lines
  GROUP BY customer_id
)
SELECT tc.customer_id, tc.lifetime_revenue
FROM top_customers tc
ORDER BY lifetime_revenue DESC, tc.customer_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build order-level net value in one CTE and summarize it by customer in the outer query.
--    Hint: Name the one-row-per-order grain before changing to customer grain.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 2. [Query writing] Use one category-revenue CTE twice to return the highest category and total revenue.
--    Hint: A named aggregate can support multiple scalar reads without repeating the business formula.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Create staged payment reconciliation CTEs at order grain.
--    Hint: Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 4. [Prediction] Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
--    Hint: Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
--    Hint: Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
--    Hint: The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
