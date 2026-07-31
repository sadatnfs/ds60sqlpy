-- Day 59: Final Capstone - Integrated Data Challenge (Part 2)
-- BEGINNER WORKFLOW — sql-59: Final Capstone Part2
-- Guide: sql/postgres-60day/companion-guides/day59_final_capstone_part2.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-59/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers, events, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Focus: Complex business logic, performance requirements, stakeholder queries
BEGIN;
SET search_path TO training, public;

-- 1. Business KPI Suite (multi-level calculations)
-- a) LTV by cohort and segment
WITH order_values AS (
  SELECT o.customer_id, o.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value,
         o.order_date
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id, o.order_date
), ltv AS (
  SELECT customer_id,
         date_trunc('month', MIN(order_date))::date AS first_order_month,
         SUM(order_value) AS ltv
  FROM order_values
  GROUP BY customer_id
), cohort AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month,
         COALESCE(c.segment,'standard') AS segment
  FROM customers c
)
SELECT cohort.segment,
       cohort.cohort_month,
       ROUND(AVG(ltv.ltv),2) AS avg_ltv,
       COUNT(*) AS customers
FROM ltv
JOIN cohort ON cohort.customer_id = ltv.customer_id
GROUP BY cohort.segment, cohort.cohort_month
ORDER BY cohort.cohort_month DESC, avg_ltv DESC
LIMIT 100;

-- b) Conversion funnel from events -> orders (last 90 days)
WITH ev AS (
  SELECT e.customer_id,
         MAX(CASE WHEN e.event_type='page_view'  THEN 1 ELSE 0 END) AS page_view,
         MAX(CASE WHEN e.event_type='add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
         MAX(CASE WHEN e.event_type='checkout'   THEN 1 ELSE 0 END) AS checkout
  FROM events e
  WHERE e.event_time >= now() - interval '90 days'
  GROUP BY e.customer_id
), buyers AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= now() - interval '90 days'
)
SELECT 
  SUM(page_view)    AS viewers,
  SUM(add_to_cart)  AS adders,
  SUM(checkout)     AS checkouts,
  (SELECT COUNT(*) FROM buyers) AS buyers
FROM ev;

-- c) Top product pairs by co-occurrence (market basket)
WITH items AS (
  SELECT order_id, product_id FROM order_items GROUP BY order_id, product_id
), pairs AS (
  SELECT a.product_id AS p1, b.product_id AS p2, COUNT(*) AS together
  FROM items a
  JOIN items b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p1.name AS product_a, p2.name AS product_b, together
FROM pairs
JOIN products p1 ON p1.product_id = pairs.p1
JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY together DESC
LIMIT 20;

-- 2. Performance Aids (indexes/partitioning hints) - run EXPLAIN before/after
-- Note: These DDLs are rolled back unless you COMMIT intentionally
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_date ON payments(order_id, payment_date);

EXPLAIN ANALYZE
SELECT o.customer_id, SUM(o.total_amount)
FROM orders o
WHERE o.order_date >= now() - interval '180 days'
GROUP BY o.customer_id
ORDER BY SUM(o.total_amount) DESC
LIMIT 50;

-- 3. Stakeholder Views
-- a) Finance: Budget vs Actual YTD by category
WITH ytd_exp AS (
  SELECT date_trunc('year', expense_date)::date AS yr,
         category,
         SUM(amount) AS actual
  FROM expenses
  WHERE expense_date >= date_trunc('year', now())
  GROUP BY 1,2
), ytd_bud AS (
  SELECT date_trunc('year', period)::date AS yr,
         category,
         SUM(amount) AS budget
  FROM budgets
  WHERE period >= date_trunc('year', now())
  GROUP BY 1,2
)
SELECT COALESCE(b.category, e.category) AS category,
       COALESCE(b.yr, e.yr) AS year,
       COALESCE(b.budget,0) AS budget_ytd,
       COALESCE(e.actual,0) AS actual_ytd,
       ROUND(COALESCE(e.actual,0) - COALESCE(b.budget,0),2) AS variance
FROM ytd_bud b
FULL OUTER JOIN ytd_exp e ON e.yr=b.yr AND e.category=b.category
ORDER BY category;

-- b) Marketing: Campaign-assisted purchases (within 7 days)
WITH first_purchase AS (
  SELECT o.customer_id, MIN(o.order_date) AS first_buy
  FROM orders o
  GROUP BY o.customer_id
), touch AS (
  SELECT e.customer_id, e.event_time, COALESCE(e.metadata->>'campaign','none') AS campaign
  FROM events e
)
SELECT t.campaign,
       COUNT(DISTINCT t.customer_id) AS assisted_customers
FROM touch t
JOIN first_purchase fp ON fp.customer_id = t.customer_id
WHERE t.event_time BETWEEN fp.first_buy - interval '7 days' AND fp.first_buy
GROUP BY t.campaign
ORDER BY assisted_customers DESC
LIMIT 20;

-- 4. Large-scale considerations
-- For 100M+ rows, favor partitioning by time on orders/events, and use partial indexes on recent partitions.
-- Ensure queries constrain partition key (order_date, event_time) to enable pruning.

-- Exercises
-- 1. Prediction: state the grain of every CTE in the LTV query and identify the
--    exact step where order-grain values become customer-grain values.
--    Inputs: For sql-59 Exercise 1, read from the inline `VALUES` fixture. Build the answer toward `step_name`, `row_grain`, and `key_columns`; keep `step_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 1, expected output: one row per `step_name`. The final columns are `step_name`, `row_grain`, and `key_columns`.
--    Verify: For sql-59 Exercise 1, reselect the returned keys directly from the source; require unique `step_name` where the expected grain is one row per key and confirm the projected `step_name`, `row_grain`, and `key_columns` against the inline `VALUES` fixture. Add one source row with a new `step_name`; verify the result gains exactly one row carrying that `step_name` value.
--    Hint ladder, rung 1: For sql-59 Exercise 1, select `step_name` from the inline `VALUES` fixture before adding derived columns.
-- 2. Construction: turn the funnel counts into step-to-step and overall
--    conversion rates while preserving customers who purchased without a
--    recorded event.
--    Inputs: For sql-59 Exercise 2, read from `orders`, `customers`, and `events`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
--    Verify: For sql-59 Exercise 2, project `order_id` plus the raw source columns from `orders`, `customers`, and `events` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-59 Exercise 2, run `activity`, and `counts` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 3. Debugging: reconcile stored order totals, calculated line revenue, and
--    payments before choosing which measure each stakeholder KPI should use.
--    Inputs: For sql-59 Exercise 3, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 3, expected output: at most 50 rows keyed by `order_id`. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`. The final order is `o.order_id`.
--    Verify: For sql-59 Exercise 3, assert no more than 50 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `order_items`, `payments`, and `orders` to confirm `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header` came from the same source rows. Run with 50 minus one and 50 plus one eligible rows; require the output cap of 50 while retaining `o.order_id`.
--    Hint ladder, rung 1: For sql-59 Exercise 3, run `lines`, and `paid` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 4. Edge case: assign purchases with no qualifying campaign touch to a
--    '(direct)' bucket and prove attribution counts reconcile to purchases.
--    Inputs: For sql-59 Exercise 4, read from `orders`, and `events`. Build the answer toward `attribution_bucket`, and `purchases`; keep `attribution_bucket`, and `purchases` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 4, expected output: one row per `attribution_bucket`, and `purchases`. The final columns are `attribution_bucket`, and `purchases`. The final order is `purchases DESC, attribution_bucket`.
--    Verify: For sql-59 Exercise 4, independently aggregate `orders`, and `events` by `attribution_bucket`, and `purchases`; require one output row for every distinct `attribution_bucket`, and `purchases` tuple and compare `row_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-59 Exercise 4, start with the first relation in `orders`, and `events`; after each join, record total rows and distinct `attribution_bucket`, and `purchases` so the exact fanout or loss is visible.
-- 5. Performance: compare the customer/date index with a date/customer index
--    for the date-bounded aggregation; explain the leftmost-column tradeoff.
--    Inputs: For sql-59 Exercise 5, run the underlying read-only query over `orders`, and `idx_orders_date_customer_day59_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-59 Exercise 5, expected output: one row per `customer_id`. The final columns are `customer_id`, and `revenue`.
--    Verify: For sql-59 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-59 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
-- 6. Explanation: write a metric contract for one KPI covering name, grain,
--    numerator, denominator, time zone, NULL policy, exclusions, and owner.
--    Inputs: For sql-59 Exercise 6, read from the inline `VALUES` fixture. Build the answer toward `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`; keep `metric_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 6, expected output: one row per `metric_name`. The final columns are `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
--    Verify: For sql-59 Exercise 6, reselect the returned keys directly from the source; require unique `metric_name` where the expected grain is one row per key and confirm the projected `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.
--    Hint ladder, rung 1: For sql-59 Exercise 6, select `metric_name` from the inline `VALUES` fixture before adding derived columns.
-- 7. Construction: produce a stakeholder-safe product-pair report with support,
--    confidence, lift, minimum basket count, and deterministic ordering.
--    Inputs: For sql-59 Exercise 7, read from `order_items`. Build the answer toward `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`; keep `order_item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 7, expected output: at most 20 rows keyed by `order_item_id`. The final columns are `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`. The final order is `lift DESC, together DESC, product_a, product_b`.
--    Verify: For sql-59 Exercise 7, assert no more than 20 rows, no duplicate `order_item_id`, and no adjacent pair that violates `lift DESC, together DESC, product_a, product_b`. Rejoin the returned keys to `order_items` to confirm `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, together DESC, product_a, product_b`.
--    Hint ladder, rung 1: For sql-59 Exercise 7, run `baskets`, `totals`, `product_baskets`, and `pairs` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
-- 8. Sign-off: assemble one result set that reconciles the customer, finance,
--    funnel, attribution, and market-basket outputs to named control totals.
--    Inputs: For sql-59 Exercise 8, read from `customers`, `orders`, `order_items`, and `payments`. Build the answer toward `control_name`, and `observed_value`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 8, expected output: one row per `customer_id`. The final columns are `control_name`, and `observed_value`. The final order is `control_name`.
--    Verify: For sql-59 Exercise 8, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `control_name`, and `observed_value` against `customers`, `orders`, `order_items`, and `payments`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-59 Exercise 8, check `control_name` before applying the row cap.

ROLLBACK;
