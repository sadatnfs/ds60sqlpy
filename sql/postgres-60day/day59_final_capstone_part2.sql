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
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 2. Construction: turn the funnel counts into step-to-step and overall
--    conversion rates while preserving customers who purchased without a
--    recorded event.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Debugging: reconcile stored order totals, calculated line revenue, and
--    payments before choosing which measure each stakeholder KPI should use.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 4. Edge case: assign purchases with no qualifying campaign touch to a
--    '(direct)' bucket and prove attribution counts reconcile to purchases.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Performance: compare the customer/date index with a date/customer index
--    for the date-bounded aggregation; explain the leftmost-column tradeoff.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 6. Explanation: write a metric contract for one KPI covering name, grain,
--    numerator, denominator, time zone, NULL policy, exclusions, and owner.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 7. Construction: produce a stakeholder-safe product-pair report with support,
--    confidence, lift, minimum basket count, and deterministic ordering.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 8. Sign-off: assemble one result set that reconciles the customer, finance,
--    funnel, attribution, and market-basket outputs to named control totals.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers, events, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
