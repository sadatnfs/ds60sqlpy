-- Day 56: Project 4 - Complex BI (Part 2)
-- BEGINNER WORKFLOW — sql-56: Project4 BI Part2
-- Guide: sql/postgres-60day/companion-guides/day56_project4_bi_part2.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-56/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Ranking and percentile reporting, multi-dimensional splits
BEGIN;
SET search_path TO training, public;

-- Percentile distribution of order values per country-month
WITH orders_m AS (
  SELECT c.country,
         date_trunc('month', o.order_date)::date AS month,
         o.total_amount AS amt
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
)
SELECT country,
       month,
       PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM orders_m
GROUP BY country, month
ORDER BY month DESC, country
LIMIT 200;

-- Top-N per dimension (category) within country using window rank
WITH prod_rev AS (
  SELECT c.country,
         p.category,
         p.product_id,
         p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk_country,
            RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk_in_cat
  FROM prod_rev
)
SELECT * FROM ranked
WHERE rnk_in_cat <= 5
ORDER BY country, category, rnk_in_cat;

-- CUBE for multi-dimensional subtotals across country, category
WITH line AS (
  SELECT c.country, p.category,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category, ROUND(SUM(revenue),2) AS revenue,
       GROUPING(country) AS g_country, GROUPING(category) AS g_cat
FROM line
GROUP BY CUBE (country, category)
ORDER BY country NULLS FIRST, category NULLS FIRST;

-- Exercises
-- 1. Add payment method to the CUBE and measure row count increase.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Compute p50/p90 of order values per category-month.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: explain why joining raw payments to raw order_items multiplies
--    revenue when an order has several rows in both tables.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 4. Construction: pre-aggregate payment methods at order grain before joining
--    line revenue, and reconcile the result to total line revenue.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: correct a percentile query that calculates percentiles over
--    line items when the metric definition says order value.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: compare percentile_cont and percentile_disc for a category-month
--    with an even number of orders and explain which output is an observed value.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
