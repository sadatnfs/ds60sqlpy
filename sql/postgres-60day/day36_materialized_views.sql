-- Day 36: Materialized Views & Caching
-- BEGINNER WORKFLOW — sql-36: Materialized Views
-- Guide: sql/postgres-60day/companion-guides/day36_materialized_views.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-36/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders, mv_category_month_revenue.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Materialized view for category revenue by month
CREATE MATERIALIZED VIEW mv_category_month_revenue AS
SELECT p.category,
       date_trunc('month', o.order_date)::date AS month,
       SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
GROUP BY p.category, date_trunc('month', o.order_date);

-- Query the MV
SELECT * FROM mv_category_month_revenue ORDER BY month DESC, revenue DESC LIMIT 50;

-- Refresh when needed (will be rolled back)
REFRESH MATERIALIZED VIEW mv_category_month_revenue;

-- Exercises
-- 1. Create a MV for weekly revenue by country.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, mv_category_month_revenue) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 2. Compare query time against base tables vs MV.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, mv_category_month_revenue) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: insert a temporary order after the materialized view is built.
--    Predict whether the view changes before REFRESH, then verify.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, mv_category_month_revenue) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: add a unique index that would make a concurrent refresh
--    structurally possible; explain why this lesson still uses ordinary refresh.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, mv_category_month_revenue) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 5. Debugging: compare SUM(orders.total_amount) with line-item revenue and
--    identify which business definition the materialized view actually stores.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, mv_category_month_revenue) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 6. Edge case: query a month/category combination with no source rows and
--    explain why a materialized aggregate has no automatic zero-valued row.
--    Inputs: Use only the declared lesson objects (order_items, products, orders, mv_category_month_revenue) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
