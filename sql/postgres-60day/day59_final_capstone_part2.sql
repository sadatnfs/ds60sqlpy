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

-- b) Ordered conversion funnel from events -> orders (last 90 days).
-- First collect the earliest page view. Each later CTE can only choose a
-- timestamp at or after the timestamp supplied by its previous stage.
WITH viewed_stage AS (
  SELECT c.customer_id,
         MIN(e.event_time) FILTER (
           WHERE e.event_type = 'page_view'
         ) AS viewed_at
  FROM customers c
  LEFT JOIN events e
    ON e.customer_id = c.customer_id
   AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY c.customer_id
), added_stage AS (
  SELECT viewed.customer_id,
         viewed.viewed_at,
         MIN(event.event_time) AS added_at
  FROM viewed_stage viewed
  LEFT JOIN events event
    ON event.customer_id = viewed.customer_id
   AND event.event_type = 'add_to_cart'
   AND event.event_time >= viewed.viewed_at
  GROUP BY viewed.customer_id, viewed.viewed_at
), checkout_stage AS (
  SELECT added.customer_id,
         added.viewed_at,
         added.added_at,
         MIN(event.event_time) AS checkout_at
  FROM added_stage added
  LEFT JOIN events event
    ON event.customer_id = added.customer_id
   AND event.event_type = 'checkout'
   AND event.event_time >= added.added_at
  GROUP BY added.customer_id, added.viewed_at, added.added_at
), purchase_stage AS (
  SELECT checkout.customer_id,
         checkout.viewed_at,
         checkout.added_at,
         checkout.checkout_at,
         MIN(customer_order.order_date) AS purchased_at
  FROM checkout_stage checkout
  LEFT JOIN orders customer_order
    ON customer_order.customer_id = checkout.customer_id
   AND customer_order.order_date >= checkout.checkout_at
   AND customer_order.order_date >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY checkout.customer_id, checkout.viewed_at,
           checkout.added_at, checkout.checkout_at
), activity AS (
  SELECT customer_id,
         viewed_at IS NOT NULL AS viewed,
         added_at IS NOT NULL AND added_at >= viewed_at AS added,
         checkout_at IS NOT NULL AND checkout_at >= added_at AS checked_out,
         purchased_at IS NOT NULL AND purchased_at >= checkout_at AS bought
  FROM purchase_stage
)
SELECT COUNT(*) FILTER (WHERE viewed) AS viewers,
       COUNT(*) FILTER (WHERE added) AS adders,
       COUNT(*) FILTER (WHERE checked_out) AS checkouts,
       COUNT(*) FILTER (WHERE bought) AS buyers
FROM activity;

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
  SELECT e.customer_id,
         e.event_time,
         e.metadata->>'campaign' AS campaign
  FROM events e
  WHERE e.event_type IN ('page_view', 'add_to_cart', 'checkout')
    AND e.metadata ? 'campaign'
    AND NULLIF(trim(e.metadata->>'campaign'), '') IS NOT NULL
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
--    Inputs: For sql-59 Exercise 2, derive `viewed_at`, `added_at`, `checkout_at`, and `purchased_at` per customer over the same trailing-90-day window.
--    Expected result/shape: For sql-59 Exercise 2, expected output: exactly one summary row with ordered stage counts, `buyers_without_view`, and three conversion rates whose denominators are the preceding ordered populations.
--    Verify: For sql-59 Exercise 2, require `added_at >= viewed_at`, `checkout_at >= added_at`, and `purchased_at >= checkout_at`. Prove `buyers <= checkouts <= adders <= viewers`; every nonzero stage rate must be between zero and one.
--    Hint ladder, rung 1: Inspect the four stage CTEs before reducing timestamps to nested boolean populations.
-- 3. Debugging: reconcile stored order totals, calculated line revenue, and
--    payments before choosing which measure each stakeholder KPI should use.
--    Inputs: For sql-59 Exercise 3, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-59 Exercise 3, expected output: at most 50 rows keyed by `order_id`. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`. The final order is `o.order_id`.
--    Verify: For sql-59 Exercise 3, assert no more than 50 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `order_items`, `payments`, and `orders` to confirm `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header` came from the same source rows. Run with 50 minus one and 50 plus one eligible rows; require the output cap of 50 while retaining `o.order_id`.
--    Hint ladder, rung 1: For sql-59 Exercise 3, run `lines`, and `paid` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 4. Edge case: assign purchases with no qualifying campaign touch to a
--    '(direct)' bucket and prove attribution counts reconcile to purchases.
--    Inputs: For sql-59 Exercise 4, start from `orders` and choose at most one event whose `event_type` is in the declared marketing-touch whitelist (`page_view`, `add_to_cart`, `checkout`), whose campaign metadata is present, and whose timestamp is in the preceding seven-day half-open window.
--    Expected result/shape: For sql-59 Exercise 4, expected output: one row per `attribution_bucket`, with `purchases`; every order contributes to exactly one campaign bucket or `(direct)`. The final order is `purchases DESC, attribution_bucket`.
--    Verify: For sql-59 Exercise 4, assert that `SUM(purchases)` equals `COUNT(*)` from `orders`. Add a tagged non-touch event and prove the attribution result is unchanged; then add two qualifying touches for one order and prove the latest timestamp, with `event_id` as tie-breaker, wins exactly once.
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
