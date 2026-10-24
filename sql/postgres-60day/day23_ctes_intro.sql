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
--    Inputs: For sql-23 Exercise 1, read from `orders`, and `order_items`. Build the answer toward `customer_id`, `order_count`, and `net_revenue`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-23 Exercise 1, expected output: One row per ordering customer. The final columns are `customer_id`, `order_count`, and `net_revenue`. The final order is `net_revenue DESC, ov.customer_id`.
--    Verify: For sql-23 Exercise 1, independently aggregate `orders`, and `order_items` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `order_count`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `net_revenue` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-23 Exercise 1, run `order_values` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 2. [Query writing] Use one category-revenue CTE twice to return the highest category and total revenue.
--    Hint: A named aggregate can support multiple scalar reads without repeating the business formula.
--    Inputs: For sql-23 Exercise 2, read from `order_items`, and `products`. Compute `top_category`, and `all_revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-23 Exercise 2, expected output: One summary row. The final columns are `top_category`, and `all_revenue`.
--    Verify: For sql-23 Exercise 2, evaluate each of `all_revenue` in a separate control `SELECT` over `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
--    Hint ladder, rung 1: For sql-23 Exercise 2, run `category_revenue` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
-- 3. [Query writing] Create staged payment reconciliation CTEs at order grain.
--    Hint: Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
--    Inputs: For sql-23 Exercise 3, read from `payments`, and `orders`. Build the answer toward `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-23 Exercise 3, expected output: One row per order. The final columns are `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`. The final order is `ABS(total_amount - paid_amount) DESC, order_id`.
--    Verify: For sql-23 Exercise 3, project `order_id` plus the raw source columns from `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_total`, `paid_amount`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-23 Exercise 3, run `paid`, and `reconciled` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 4. [Prediction] Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
--    Hint: Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
--    Inputs: For sql-23 Exercise 4, read from `orders`, `materialized_orders`, and `inline_orders`. Build the answer toward `variant`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-23 Exercise 4, expected output: Two count rows with equal values. The final columns are `variant`, and `row_count`. The final order is `variant`.
--    Verify: For sql-23 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `variant`, and `row_count` against `orders`, `materialized_orders`, and `inline_orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-23 Exercise 4, inspect the source keys that survive `WHERE`; then check `variant` before applying the row cap.
-- 5. [Debugging] Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
--    Hint: Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
--    Inputs: For sql-23 Exercise 5, read from `orders`, `order_items`, and `customers`. Build the answer toward `country`, and `country_revenue`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-23 Exercise 5, expected output: One row per country. The final columns are `country`, and `country_revenue`. The final order is `country_revenue DESC, c.country`.
--    Verify: For sql-23 Exercise 5, independently aggregate `orders`, `order_items`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `country_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-23 Exercise 5, run `order_values`, and `customer_revenue` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 6. [Extension] Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
--    Hint: The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
--    Inputs: For sql-23 Exercise 6, read the target keys from `products` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-23 Exercise 6, expected output: One summary row for a bounded three-product update. The final columns are `updated_rows`, `first_updated_product`, and `last_updated_product`.
--    Verify: For sql-23 Exercise 6, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `products` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.
--    Hint ladder, rung 1: For sql-23 Exercise 6, run `candidates`, and `updated` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.

ROLLBACK;
