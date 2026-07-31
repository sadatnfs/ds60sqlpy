-- Day 15: Phase 1 Project - Complex Report
-- BEGINNER WORKFLOW — sql-15: Phase1 Project
-- Guide: sql/postgres-60day/companion-guides/day15_phase1_project.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-15/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
-- Assumptions: All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
-- Pitfall: Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
-- Predict row grain and NULL/order behavior before executing each example.

-- Customer purchase analysis with segmentation and temporal patterns
WITH line AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
segment AS (
  SELECT c.customer_id, COALESCE(c.segment,'standard') AS segment, c.country
  FROM customers c
)
SELECT s.segment, s.country, l.month_utc,
       ROUND(SUM(l.revenue),2) AS revenue,
       COUNT(DISTINCT l.customer_id) AS actives,
       ROUND(SUM(l.revenue)/NULLIF(COUNT(DISTINCT l.customer_id),0),2) AS rev_per_active
FROM line l
JOIN segment s ON s.customer_id = l.customer_id
GROUP BY s.segment, s.country, l.month_utc
ORDER BY l.month_utc DESC, revenue DESC, s.segment, s.country
LIMIT 200;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.
--    Hint: Left join from customers and aggregate at customer grain.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 2. [Query writing] Create a product profitability table from net order-line revenue and catalog cost.
--    Hint: Calculate line revenue and line cost at item grain, then aggregate to product.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 3. [Query writing] Build a UTC monthly order-status report with counts and stored revenue.
--    Hint: Derive one reporting month and group by month/status.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 4. [Debugging] Reconcile stored order total, computed line total, and paid total without multiplying details.
--    Hint: Aggregate items and payments independently to order grain before joining.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 5. [Prediction] Compare monthly budgets with actual expenses and preserve missing sides.
--    Hint: Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 6. [Extension] Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
--    Hint: Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
