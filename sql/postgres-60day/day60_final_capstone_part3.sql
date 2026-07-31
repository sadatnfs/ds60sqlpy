-- Day 60: Final Capstone - Integrated Data Challenge (Part 3)
-- BEGINNER WORKFLOW — sql-60: Final Capstone Part3
-- Guide: sql/postgres-60day/companion-guides/day60_final_capstone_part3.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-60/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, expenses, budgets.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Focus: End-to-end solution: DQ -> Transform -> Analytics -> Performance sign-off
-- Success Criteria:
--  - All critical queries complete < 10s on your dataset
--  - DQ checks pass with documented exceptions
--  - Clear documentation of choices and optimizations

BEGIN;
SET search_path TO training, public;

-- 1. DQ Summary Views (re-usable) ------------------------------------------
CREATE OR REPLACE VIEW v_dq_customers AS
SELECT COUNT(*) AS total,
       SUM(CASE WHEN email IS NULL OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$' THEN 1 ELSE 0 END) AS invalid_email,
       SUM(CASE WHEN country IS NULL OR country !~ '^[A-Z]{2}$' THEN 1 ELSE 0 END) AS invalid_country,
       SUM(CASE WHEN full_name IS NULL OR btrim(full_name) = '' THEN 1 ELSE 0 END) AS invalid_name
FROM customers;

CREATE OR REPLACE VIEW v_dq_orders AS
SELECT COUNT(*) AS total,
       SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts,
       SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer
FROM orders;

SELECT * FROM v_dq_customers;
SELECT * FROM v_dq_orders;

-- 2. Core Business Views ----------------------------------------------------
-- Lifetime value per customer.
--
-- Grain: exactly one row per customer, including customers who have not placed
-- an order. `orders.total_amount` is the authoritative revenue measure for this
-- capstone. Re-summing order lines here could silently change the definition
-- by excluding header-only orders or omitting adjustments stored on the header.
CREATE OR REPLACE VIEW v_customer_ltv AS
SELECT c.customer_id,
       c.full_name,
       c.country,
       c.segment,
       COUNT(o.order_id) AS order_count,
       COALESCE(SUM(o.total_amount), 0)::numeric(14,2) AS ltv
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.full_name, c.country, c.segment;

-- Control 1: zero-order customers must still appear in the view.
SELECT COUNT(*) AS customers_missing_from_ltv
FROM customers c
LEFT JOIN v_customer_ltv l USING (customer_id)
WHERE l.customer_id IS NULL;

-- Control 2: customer-level LTV must reconcile to the authoritative order
-- header total. Expected `difference` is 0.00 on the course seed.
SELECT ROUND(COALESCE(SUM(ltv), 0), 2) AS ltv_total,
       (SELECT ROUND(COALESCE(SUM(total_amount), 0), 2) FROM orders) AS order_total,
       ROUND(COALESCE(SUM(ltv), 0), 2)
         - (SELECT ROUND(COALESCE(SUM(total_amount), 0), 2) FROM orders) AS difference
FROM v_customer_ltv;

-- Monthly revenue and MoM growth
CREATE OR REPLACE VIEW v_monthly_revenue AS
WITH m AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT m.month,
       m.revenue,
       LAG(m.revenue) OVER (ORDER BY m.month) AS prev_month,
       ROUND((m.revenue - COALESCE(LAG(m.revenue) OVER (ORDER BY m.month),0)) / NULLIF(LAG(m.revenue) OVER (ORDER BY m.month),0), 4) AS mom_growth
FROM m;

-- 3. Stakeholder-ready Queries ---------------------------------------------
-- Finance: Budget vs Actual by month/category (YTD)
WITH exp AS (
  SELECT date_trunc('month', expense_date)::date AS month, category, SUM(amount) AS actual
  FROM expenses WHERE expense_date >= date_trunc('year', now()) GROUP BY 1,2
), bud AS (
  SELECT date_trunc('month', period)::date AS month, category, SUM(amount) AS budget
  FROM budgets WHERE period >= date_trunc('year', now()) GROUP BY 1,2
)
SELECT COALESCE(b.category, e.category) AS category,
       COALESCE(b.month, e.month) AS month,
       COALESCE(b.budget,0) AS budget,
       COALESCE(e.actual,0) AS actual,
       ROUND(COALESCE(e.actual,0) - COALESCE(b.budget,0),2) AS variance
FROM bud b FULL OUTER JOIN exp e ON e.month=b.month AND e.category=b.category
ORDER BY month DESC, category
LIMIT 120;

-- Marketing: Cohort retention for the latest 6 signup cohorts.
--
-- A cohort is the customer's signup month. An active customer has at least one
-- order in the lifecycle month being measured. `cohort_size` includes every
-- signup, including people who never order; dividing by only active customers
-- would inflate the reported retention rate.
WITH orders_m AS (
  SELECT DISTINCT
         o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), latest_six_cohorts AS (
  SELECT cohort_month
  FROM cohorts
  GROUP BY cohort_month
  ORDER BY cohort_month DESC
  LIMIT 6
), cohort_members AS (
  SELECT c.customer_id, c.cohort_month
  FROM cohorts c
  JOIN latest_six_cohorts latest USING (cohort_month)
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*)::numeric AS cohort_size
  FROM cohort_members
  GROUP BY cohort_month
), month_offsets AS (
  -- The seven requested lifecycle buckets are month 0 through month 6.
  SELECT generate_series(0, 6)::int AS month_offset
), retention AS (
  SELECT cm.cohort_month,
         offsets.month_offset,
         sizes.cohort_size,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM cohort_members cm
  JOIN cohort_sizes sizes USING (cohort_month)
  CROSS JOIN month_offsets offsets
  LEFT JOIN orders_m om
    ON om.customer_id = cm.customer_id
   AND om.order_month = (
         cm.cohort_month + make_interval(months => offsets.month_offset)
       )::date
  GROUP BY cm.cohort_month, offsets.month_offset, sizes.cohort_size
)
SELECT cohort_month,
       month_offset,
       cohort_size,
       active_customers,
       ROUND(
         active_customers::numeric / NULLIF(cohort_size, 0),
         4
       ) AS retention_rate
FROM retention
ORDER BY cohort_month DESC, month_offset;

-- Operations: Top slow queries to optimize (use EXPLAIN ANALYZE in-session)
EXPLAIN
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '180 days'
GROUP BY p.category
ORDER BY qty DESC;

-- 4. Performance Checklist ---------------------------------------------------
-- Indexes helpful for above queries (will be rolled back unless COMMIT)
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_oi_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_expenses_month ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period);

-- Validate plan improvements quickly
EXPLAIN ANALYZE SELECT * FROM v_monthly_revenue ORDER BY month DESC LIMIT 12;

-- 5. Documentation Hints ----------------------------------------------------
-- Include in your write-up:
--  - Data quality findings (from v_dq_*) and remediation steps
--  - Core model entities used and rationale (customers/orders/items/events/etc.)
--  - Queries and indexes that moved the needle, with before/after EXPLAIN metrics
--  - Any compromises (freshness vs speed, materialized views, partitioning)

-- Exercises
-- 1. Prediction: identify which views are snapshot-independent and which use
--    CURRENT_DATE/now(), then explain the reproducibility consequence.
--    Inputs: For sql-60 Exercise 1, read from the inline `VALUES` fixture. Build the answer toward `object_name`, and `clock_contract`; keep `object_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 1, expected output: one row per `object_name`. The final columns are `object_name`, and `clock_contract`.
--    Verify: For sql-60 Exercise 1, reselect the returned keys directly from the source; require unique `object_name` where the expected grain is one row per key and confirm the projected `object_name`, and `clock_contract` against the inline `VALUES` fixture. Add one source row with a new `object_name`; verify the result gains exactly one row carrying that `object_name` value.
--    Hint ladder, rung 1: For sql-60 Exercise 1, select `object_name` from the inline `VALUES` fixture before adding derived columns.
-- 2. Construction: build a single sign-off query whose rows are named checks
--    with observed_value, expected_value, pass, severity, and remediation.
--    Inputs: For sql-60 Exercise 2, read from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`. The final order is `severity, check_name`.
--    Verify: For sql-60 Exercise 2, project `order_id` plus the raw source columns from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-60 Exercise 2, run `checks` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 3. Debugging: remove repeated LAG expressions from v_monthly_revenue by using
--    a second CTE, while preserving the first month's NULL growth rate.
--    Inputs: For sql-60 Exercise 3, read from `orders`, and `v_monthly_revenue_refactored_solution`. Build the answer toward `month`, `revenue`, `previous_month`, and `month_over_month_growth`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 3, expected output: one row per `month`. The final columns are `month`, `revenue`, `previous_month`, and `month_over_month_growth`. The final order is `month`.
--    Verify: For sql-60 Exercise 3, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `revenue`, `previous_month`, and `month_over_month_growth` against `orders`, and `v_monthly_revenue_refactored_solution`. Repeat with `NULL` in `LAG` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-60 Exercise 3, run `monthly`, and `with_previous` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 4. Edge case: represent an incomplete current month separately so it is not
--    compared directly with a complete prior month.
--    Inputs: For sql-60 Exercise 4, read from `v_monthly_revenue_refactored_solution`. Build the answer toward `month`, `revenue`, and `is_incomplete_month`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 4, expected output: one row per `month`. The final columns are `month`, `revenue`, and `is_incomplete_month`. The final order is `month DESC`.
--    Verify: For sql-60 Exercise 4, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `revenue`, and `is_incomplete_month` against `v_monthly_revenue_refactored_solution`. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
--    Hint ladder, rung 1: For sql-60 Exercise 4, check `month DESC` before applying the row cap.
-- 5. Performance: capture before/after plans in JSON and document plan shape,
--    estimates, actual rows, buffers, and timing without promising universal gains.
--    Inputs: For sql-60 Exercise 5, run the underlying read-only query over `v_monthly_revenue_refactored_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-60 Exercise 5, expected output: at most 12 rows keyed by `plan_node`. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`. The final order is `month DESC`.
--    Verify: For sql-60 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-60 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows.
-- 6. Explanation: produce a release checklist covering rollback, ownership,
--    permissions, refresh cadence, monitoring, data contracts, and known limits.
--    Inputs: For sql-60 Exercise 6, read from the inline `VALUES` fixture. Build the answer toward `item`, `evidence`, and `owner`; keep `evidence` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 6, expected output: one row per `evidence`. The final columns are `item`, `evidence`, and `owner`.
--    Verify: For sql-60 Exercise 6, reselect the returned keys directly from the source; require unique `evidence` where the expected grain is one row per key and confirm the projected `item`, `evidence`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `evidence`; verify the result gains exactly one row carrying that `evidence` value.
--    Hint ladder, rung 1: For sql-60 Exercise 6, select `evidence` from the inline `VALUES` fixture before adding derived columns.
-- 7. Construction: create a lineage table that maps each published metric to
--    its source tables, transformation grain, and validation query.
--    Inputs: For sql-60 Exercise 7, read from the inline `VALUES` fixture. Build the answer toward `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`; keep `metric_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 7, expected output: one row per `metric_name`. The final columns are `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
--    Verify: For sql-60 Exercise 7, reselect the returned keys directly from the source; require unique `metric_name` where the expected grain is one row per key and confirm the projected `metric_name`, `source_tables`, `transformation_grain`, and `validation_query` against the inline `VALUES` fixture. Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.
--    Hint ladder, rung 1: For sql-60 Exercise 7, select `metric_name` from the inline `VALUES` fixture before adding derived columns.
-- 8. Debugging: prove every dashboard subtotal reconciles to a simpler control
--    query before approving any performance optimization.
--    Inputs: For sql-60 Exercise 8, read from `v_monthly_revenue_refactored_solution`, and `orders`. Compute `dashboard_total`, `source_total`, and `difference` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-60 Exercise 8, expected output: exactly one aggregate summary row. The final columns are `dashboard_total`, `source_total`, and `difference`.
--    Verify: For sql-60 Exercise 8, evaluate each of `dashboard_total`, and `source_total` in a separate control `SELECT` over `v_monthly_revenue_refactored_solution`, and `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-60 Exercise 8, select `order_id` from `v_monthly_revenue_refactored_solution`, and `orders` before adding derived columns.
-- 9. Edge case: test empty, one-row, NULL-heavy, and duplicate-key fixtures and
--    record which assumptions prevent each from reaching production.
--    Inputs: For sql-60 Exercise 9, read from `edge_fixture`. Build the answer toward `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`; keep `fixture_rows` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 9, expected output: one row per `fixture_rows`. The final columns are `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
--    Verify: For sql-60 Exercise 9, reselect the returned keys directly from the source; require unique `fixture_rows` where the expected grain is one row per key and confirm the projected `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows` against `edge_fixture`. Repeat with `NULL` in `fixture_rows`, and `null_email_rows` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-60 Exercise 9, inspect the source keys that survive `WHERE`.
-- 10. Final sign-off: return PASS/FAIL/NOT_RUN for every acceptance criterion;
--     prose alone must never turn an unexecuted check into PASS.

-- When ready to persist created views/indexes, replace ROLLBACK with COMMIT.
--    Inputs: For sql-60 Exercise 10, read from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Build the answer toward `criterion`, and `result`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-60 Exercise 10, expected output: one row per `order_id`. The final columns are `criterion`, and `result`. The final order is `criterion`.
--    Verify: For sql-60 Exercise 10, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `criterion`, and `result` against `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-60 Exercise 10, check `criterion` before applying the row cap.
ROLLBACK;
