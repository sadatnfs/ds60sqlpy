-- Day 41: Complex Aggregations (FILTER, conditional metrics, string aggregation)
-- BEGINNER WORKFLOW — sql-41: Complex Aggregations
-- Guide: sql/postgres-60day/companion-guides/day41_complex_aggregations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-41/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Multiple metrics with FILTER
SELECT p.category,
       SUM(oi.quantity)                                                   AS total_qty,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2)           AS revenue,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount))
             FILTER (WHERE o.order_date >= now() - interval '30 days'),2) AS revenue_30d
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Conditional aggregation using CASE for multi-metric report
SELECT c.country,
       SUM(CASE WHEN o.status IN ('paid','shipped','delivered') THEN 1 ELSE 0 END) AS successful_orders,
       SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END)                      AS returned_orders,
       ROUND(SUM(CASE WHEN o.status <> 'returned' THEN o.total_amount ELSE 0 END),2) AS net_revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY net_revenue DESC;

-- String aggregation for labels
SELECT p.category,
       string_agg(DISTINCT p.name, ', ' ORDER BY p.name) AS sample_products
FROM products p
GROUP BY p.category
ORDER BY p.category
LIMIT 10;

-- Exercises
-- 1. Build a 6-metric dashboard by category using FILTER for various time windows.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Create a per-country string_agg of top 5 product names by revenue.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: compare GROUPING SETS ((country), (category), ()) with CUBE
--    (country, category). Predict which country/category detail level is absent.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: report order count, paid revenue, returned revenue, and
--    distinct customers per country using FILTER.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: distinguish a real NULL country from a subtotal NULL by adding
--    GROUPING(country) and a safe display label.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: return an empty array rather than NULL when an aggregate input
--    set is empty, and explain the COALESCE type cast.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
