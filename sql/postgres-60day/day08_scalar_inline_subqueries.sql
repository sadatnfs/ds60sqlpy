-- Day 8: Scalar & Inline Subqueries
-- BEGINNER WORKFLOW — sql-08: Scalar Inline Subqueries
-- Guide: sql/postgres-60day/companion-guides/day08_scalar_inline_subqueries.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-08/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
-- Assumptions: A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
-- Pitfall: Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
-- Predict row grain and NULL/order behavior before executing each example.

-- Scalar subquery in SELECT: customer lifetime revenue
SELECT c.customer_id, c.full_name,
  (
    SELECT ROUND(COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),0),2)
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id = c.customer_id
  ) AS lifetime_revenue
FROM customers c
ORDER BY lifetime_revenue DESC, c.customer_id
LIMIT 20;

-- Inline subquery in FROM
SELECT x.category, ROUND(AVG(x.order_total),2) AS avg_order_total
FROM (
  SELECT p.category, o.order_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, o.order_id
) x
GROUP BY x.category
ORDER BY avg_order_total DESC, x.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return orders whose total exceeds the overall average order total.
--    Hint: The aggregate subquery is guaranteed to return exactly one value.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Return orders whose total exceeds the overall average order total” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `o`, `all_orders`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: The aggregate subquery is guaranteed to return exactly one value.
-- 2. [Query writing] Add the total customer count as a scalar column beside each country-level customer count.
--    Hint: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Add the total customer count as a scalar column beside each country-level customer count” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `country_customers`, `all_customers`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
-- 3. [Query writing] Show each customer with their latest order timestamp using a scalar correlated subquery.
--    Hint: Use `MAX` to guarantee one result and let customers without orders receive NULL.
--    Inputs: Use `orders`, `customers` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Show each customer with their latest order timestamp using a scalar correlated subquery” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `latest_order_date`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Use MAX to guarantee one result and let customers without orders receive NULL.
-- 4. [Prediction] Demonstrate that a scalar subquery with no matching rows returns NULL.
--    Hint: Use a deliberately impossible product key and test the scalar result with `IS NULL`.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Demonstrate that a scalar subquery with no matching rows returns NULL”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `p`, `no_row_becomes_null`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Use a deliberately impossible product key and test the scalar result with IS NULL.
-- 5. [Debugging] Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
--    Hint: Choose the business reduction explicitly; this answer uses maximum price.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Repair a scalar subquery that returns many product prices by aggregating to the intended single value” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `category_max_price`, `all_products`, `global_max_price`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Choose the business reduction explicitly; this answer uses maximum price.
-- 6. [Extension] Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
--    Hint: Compute the global total once, then cross join the guaranteed one-row relation.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `customer_count`, `country_customers`, `customer_share`, `c`, `cte`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `customer_count`, `country_customers`, `customer_share`, `c`, `cte`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Compute the global total once, then cross join the guaranteed one-row relation.

ROLLBACK;
