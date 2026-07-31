-- Day 11: CASE expressions and conditional logic
-- BEGINNER WORKFLOW — sql-11: Case Expressions
-- Guide: sql/postgres-60day/companion-guides/day11_case_expressions.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-11/ copy, and prints the full
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
-- Focus: Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
-- Assumptions: Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
-- Pitfall: Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
-- Predict row grain and NULL/order behavior before executing each example.

-- Label orders by size
SELECT o.order_id, o.total_amount,
  CASE
    WHEN o.total_amount >= 1000 THEN 'XL'
    WHEN o.total_amount >= 300 THEN 'L'
    WHEN o.total_amount >= 100 THEN 'M'
    ELSE 'S'
  END AS order_size
FROM orders o
ORDER BY o.total_amount DESC, o.order_id
LIMIT 50;

-- Conditional aggregation with CASE
SELECT p.category,
  SUM(CASE WHEN o.order_date >= now() - interval '30 days' THEN oi.quantity ELSE 0 END) AS qty_30d,
  SUM(CASE WHEN o.order_date >= now() - interval '90 days' THEN oi.quantity ELSE 0 END) AS qty_90d
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY qty_30d DESC, p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Classify orders as small, medium, or large by total amount.
--    Hint: Validate boundaries and place the highest threshold first.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Classify orders as small, medium, or large by total amount” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `small`, `evidence`, `order_size`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Validate boundaries and place the highest threshold first.
-- 2. [Query writing] Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
--    Hint: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `evidence`, `paid_like`, `open_orders`, `returned_orders`, `all_orders`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Each COUNT() FILTER or SUM(CASE...) should state its denominator.
-- 3. [Query writing] Label missing customer segments separately from known segment values.
--    Hint: Test `IS NULL` before comparing text values.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Label missing customer segments separately from known segment values” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `segment_group`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Test IS NULL before comparing text values.
-- 4. [Prediction] Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
--    Hint: First-match wins, so specific/high thresholds must precede broader/lower ones.
--    Inputs: Use `orders`, `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the label for 500 when >= 100 appears before >= 500, then repair the branch order”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `corrected_label`, `sample`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `orders`, `order_items`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: First-match wins, so specific/high thresholds must precede broader/lower ones.
-- 5. [Debugging] Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
--    Hint: All result branches must resolve to a compatible PostgreSQL type.
--    Inputs: Use `orders`, `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Replace a CASE expression that returns mixed numeric and text types with one consistent output type” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `value_state`, `sample`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: All result branches must resolve to a compatible PostgreSQL type.
-- 6. [Extension] Create payment-method display labels and preserve unknown future methods with an explicit fallback.
--    Hint: A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
--    Inputs: Use `payments` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Create payment-method display labels and preserve unknown future methods with an explicit fallback” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `method_label`, `payment_count`, `p`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `method_label`, `payment_count`, `p`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: A simple CASE fits equality mapping; ELSE prevents silent NULL labels.

ROLLBACK;
