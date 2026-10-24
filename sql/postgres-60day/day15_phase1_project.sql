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
--    Inputs: For sql-15 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`; keep `customer_id`, `full_name`, and `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-15 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`. The final order is `stored_revenue DESC, c.customer_id`.
--    Verify: For sql-15 Exercise 1, independently aggregate `customers`, and `orders` by `customer_id`, `full_name`, and `country`; require one output row for every distinct `customer_id`, `full_name`, and `country` tuple and compare `order_count`, `stored_revenue`, and `latest_order_date` tuple by tuple. Use one key absent from `orders`; then tie two candidates on `stored_revenue DESC` and verify `c.customer_id` selects the same row on every run.
--    Hint ladder, rung 1: For sql-15 Exercise 1, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, `full_name`, and `country` so the exact fanout or loss is visible.
-- 2. [Query writing] Create a product profitability table from net order-line revenue and catalog cost.
--    Hint: Calculate line revenue and line cost at item grain, then aggregate to product.
--    Inputs: For sql-15 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`; keep `product_id`, `name`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-15 Exercise 2, expected output: One row per sold product. The final columns are `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`. The final order is `gross_profit DESC, p.product_id`.
--    Verify: For sql-15 Exercise 2, independently aggregate `products`, and `order_items` by `product_id`, `name`, and `category`; require one output row for every distinct `product_id`, `name`, and `category` tuple and compare `units_sold`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `units_sold`, and `net_revenue` for the existing `product_id`, and `name` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-15 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id`, `name`, and `category` so the exact fanout or loss is visible.
-- 3. [Query writing] Build a UTC monthly order-status report with counts and stored revenue.
--    Hint: Derive one reporting month and group by month/status.
--    Inputs: For sql-15 Exercise 3, read from `orders`. Build the answer toward `utc_month`, `status`, `order_count`, and `stored_revenue`; keep `status` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-15 Exercise 3, expected output: One row per observed month and status. The final columns are `utc_month`, `status`, `order_count`, and `stored_revenue`. The final order is `utc_month, o.status`.
--    Verify: For sql-15 Exercise 3, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `status` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-15 Exercise 3, confirm the groups are `status`; then check `utc_month, o.status` before applying the row cap.
-- 4. [Debugging] Reconcile stored order total, computed line total, and paid total without multiplying details.
--    Hint: Aggregate items and payments independently to order grain before joining.
--    Inputs: For sql-15 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-15 Exercise 4, expected output: One row per order with differences. The final columns are `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`. The final order is `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
--    Verify: For sql-15 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-15 Exercise 4, run `line_totals`, and `paid_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Prediction] Compare monthly budgets with actual expenses and preserve missing sides.
--    Hint: Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
--    Inputs: For sql-15 Exercise 5, read from `expenses`, and `budgets`. Build the answer toward `category`, `period`, `budget_amount`, `actual_amount`, and `variance`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-15 Exercise 5, expected output: One row per category/month in either source. The final columns are `category`, `period`, `budget_amount`, `actual_amount`, and `variance`. The final order is `period, category`.
--    Verify: For sql-15 Exercise 5, project `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `category`, then assert the final `category`, `period`, `budget_amount`, `actual_amount`, and `variance` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
--    Hint ladder, rung 1: For sql-15 Exercise 5, run `actual`, and `planned` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 6. [Extension] Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
--    Hint: Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
--    Inputs: For sql-15 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Build the answer toward `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-15 Exercise 6, expected output: Exactly one summary row. The final columns are `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
--    Verify: For sql-15 Exercise 6, project `customer_id` plus the raw source columns from `customers`, `orders`, `order_items`, and `payments` at each join stage; record row count and distinct `customer_id`, then assert the final `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-15 Exercise 6, run `customer_kpis`, `order_kpis`, `line_kpis`, and `payment_kpis` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.

ROLLBACK;
