-- Day 55: Project 4 - Complex BI (Part 1)
-- BEGINNER WORKFLOW — sql-55: Project4 BI Part1
-- Guide: sql/postgres-60day/companion-guides/day55_project4_bi_part1.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-55/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: payments, orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Multi-dimensional analysis (drill-down capability)
BEGIN;
SET search_path TO training, public;

-- Use GROUPING SETS/ROLLUP/CUBE for flexible drilldowns.
-- Dimensions: country, category, primary payment method, month.
-- An order can have split payments, so first choose one reporting label:
-- the method with the greatest paid amount (method name breaks ties).
WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS method_amount
  FROM payments
  GROUP BY order_id, method
), primary_payment_method AS (
  SELECT order_id, method
  FROM (
    SELECT order_id,
           method,
           ROW_NUMBER() OVER (
             PARTITION BY order_id
             ORDER BY method_amount DESC, method
           ) AS method_rank
    FROM payment_by_method
  ) ranked_methods
  WHERE method_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(pm.method, 'unpaid') AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue,
         oi.quantity AS qty
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN primary_payment_method pm ON pm.order_id = o.order_id
)
SELECT country,
       category,
       payment_method,
       month,
       ROUND(SUM(revenue),2) AS revenue,
       SUM(qty) AS units,
       GROUPING(country)        AS g_country,
       GROUPING(category)       AS g_category,
       GROUPING(payment_method) AS g_method,
       GROUPING(month)          AS g_month
FROM line
GROUP BY ROLLUP (country, category, payment_method, month)
ORDER BY country NULLS FIRST, category NULLS FIRST, payment_method NULLS FIRST, month NULLS FIRST;

-- Drill-down example: country -> category -> product (top-N per level)
WITH prod_rev AS (
  SELECT c.country, p.category, p.product_id, p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *,
         RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT * FROM ranked WHERE rnk <= 5
ORDER BY country, category, rnk;

-- Exercises
-- 1. Replace ROLLUP with CUBE to get all subtotal combinations and compare row counts.
--    Inputs: Use only the declared lesson objects (payments, orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 2. Add a dimension for order status and re-run the drill-down with top-5.
--    Inputs: Use only the declared lesson objects (payments, orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: list the grouping sets produced by ROLLUP(country, category,
--    month) and contrast them with CUBE before running either query.
--    Inputs: Use only the declared lesson objects (payments, orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: use PostgreSQL's GROUPING(country, category) bit mask to
--    assign stable detail/subtotal/grand-total labels without mistaking stored
--    NULLs for subtotal markers.
--    Inputs: Use only the declared lesson objects (payments, orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Debugging: replace RANK with ROW_NUMBER plus a deterministic tie-breaker
--    when the dashboard must show exactly five products per group.
--    Inputs: Use only the declared lesson objects (payments, orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: preserve a real '(unknown)' country member separately from the
--    ALL-countries subtotal in both machine-readable and display columns.
--    Inputs: Use only the declared lesson objects (payments, orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
