-- Day 2: Aggregates, GROUP BY, HAVING
-- BEGINNER WORKFLOW — sql-02: Aggregates Groupby Having
-- Guide: sql/postgres-60day/companion-guides/day02_aggregates_groupby_having.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-02/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, order_items, products, orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
-- Assumptions: Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
-- Pitfall: Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
-- Predict row grain and NULL/order behavior before executing each example.

-- Example 1: Orders per country
SELECT c.country, COUNT(*) AS customers
FROM customers c
GROUP BY c.country
ORDER BY customers DESC, c.country;

-- Example 2: Revenue by category with HAVING
SELECT p.category, ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
HAVING SUM(oi.unit_price * oi.quantity) > 10000
ORDER BY revenue DESC, p.category;

-- Example 3: Monthly orders and average order total
SELECT date_trunc('month', o.order_date) AS month,
       COUNT(*) AS orders,
       ROUND(AVG(o.total_amount),2) AS avg_order
FROM orders o
GROUP BY month
ORDER BY month DESC;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Count customers by country and order countries by count then country.
--    Hint: The output grain is one row per country; include a deterministic secondary sort.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Count customers by country and order countries by count then country” at one row per country. Named evidence columns/objects: `evidence`, `customer_count`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per country; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: The output grain is one row per country; include a deterministic secondary sort.
-- 2. [Query writing] Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
--    Hint: Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
--    Inputs: Use `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue” at one row at line grain. Named evidence columns/objects: `evidence`, `net_revenue`, `average_unit_price`, `oi`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row at line grain; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Join at line grain, aggregate once per category, and place the aggregate predicate in HAVING.
-- 3. [Query writing] Summarize order count and average total by status, retaining statuses with at least 100 orders.
--    Hint: Filter groups after aggregation with `HAVING COUNT(*)`.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Summarize order count and average total by status, retaining statuses with at least 100 orders” at one row at least 100 orders grain. Named evidence columns/objects: `evidence`, `order_count`, `average_order_total`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row at least 100 orders grain; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Filter groups after aggregation with HAVING COUNT().
-- 4. [Prediction] Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
--    Hint: `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Show COUNT(), COUNT(email), and missing-email count together; predict their relationship”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `all_rows`, `nonnull_email_rows`, `missing_email_rows`, `c`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `customers`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: COUNT(email) ignores NULL, while a filtered count makes missingness explicit.
-- 5. [Debugging] Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
--    Hint: `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
--    Inputs: Use `expenses` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Repair a query that tries to filter SUM(amount) in WHERE by moving the aggregate condition to the correct clause” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `evidence`, `total_expense`, `e`, `sum`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `expenses`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: WHERE filters expense rows before grouping; HAVING filters category groups afterward.
-- 6. [Extension] Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
--    Hint: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months” observable through the exact DDL/DML command tag plus one row per requested calendar/cohort bucket and grouping key; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_month`, `order_count`, `order_revenue`, `returned_orders`, `o`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_month`, `order_count`, `order_revenue`, `returned_orders`, `o`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.

ROLLBACK;
