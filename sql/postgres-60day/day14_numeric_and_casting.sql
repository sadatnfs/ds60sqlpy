-- Day 14: Numeric functions & casting
-- BEGINNER WORKFLOW — sql-14: Numeric and Casting
-- Guide: sql/postgres-60day/companion-guides/day14_numeric_and_casting.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-14/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
-- Assumptions: Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
-- Pitfall: Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
-- Predict row grain and NULL/order behavior before executing each example.

-- Rounding and casting
SELECT order_id,
       total_amount,
       round(total_amount, 0) AS rounded,
       cast(total_amount AS int) AS as_int
FROM orders
ORDER BY total_amount DESC, order_id
LIMIT 50;

-- Safe division and null handling
SELECT p.category,
       SUM(oi.quantity) AS qty,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)) / NULLIF(SUM(oi.quantity),0), 2) AS avg_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY avg_price DESC, p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
--    Hint: Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Calculate product gross margin amount and percentage, returning NULL percentage for zero price” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `margin_amount`, `margin_rate`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Keep exact numeric arithmetic and guard the denominator with NULLIF.
-- 2. [Query writing] Safely cast a set of text values to numeric only when they match a numeric grammar.
--    Hint: Validate with a regex before casting; otherwise return NULL.
--    Inputs: Use `orders`, `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Safely cast a set of text values to numeric only when they match a numeric grammar” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `parsed_numeric`, `sample`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Validate with a regex before casting; otherwise return NULL.
-- 3. [Query writing] Show order-item net revenue rounded only after summing.
--    Hint: Aggregate exact line expressions first; round the final display value.
--    Inputs: Use `order_items` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Show order-item net revenue rounded only after summing” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `evidence`, `net_order_revenue`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate exact line expressions first; round the final display value.
-- 4. [Prediction] Compare integer division with numeric division for 1 divided by 4.
--    Hint: At least one operand must be numeric to preserve the fraction.
--    Inputs: Use `orders`, `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Compare integer division with numeric division for 1 divided by 4”. Show both compared result shapes at one row at least one operand must be numeric to preserve the fraction grain, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `integer_division`, `numeric_division`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `orders`, `order_items`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: At least one operand must be numeric to preserve the fraction.
-- 5. [Debugging] Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
--    Hint: Aggregate payment amount and count distinct order IDs at one common scope.
--    Inputs: Use `payments` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders” at one row at one common scope grain. Named evidence columns/objects: `orders`, `evidence`, `average_paid_amount_per_order`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row at one common scope grain; reconcile the result's row count and any count/sum/amount with a simpler control over `payments`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Aggregate payment amount and count distinct order IDs at one common scope.
-- 6. [Extension] Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
--    Hint: This diagnostic makes the consequence of early rounding visible.
--    Inputs: Use `order_items` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference” observable through the exact DDL/DML command tag plus one summary row per grouping key explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `sum_of_rounded_lines`, `rounded_exact_total`, `rounding_difference`, `oi`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `sum_of_rounded_lines`, `rounded_exact_total`, `rounding_difference`, `oi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: This diagnostic makes the consequence of early rounding visible.

ROLLBACK;
