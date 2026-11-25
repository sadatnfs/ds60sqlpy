-- Day 60: Final Capstone - Integrated Data Challenge (Part 3)
-- BEGINNER WORKFLOW - sql-60: Final Capstone Part 3
-- Guide: sql/postgres-60day/companion-guides/day60_final_capstone_part3.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-60.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  COUNT(*) AS total,
  SUM(
    CASE WHEN email IS NULL
      OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$' THEN
      1
    ELSE
      0
    END) AS invalid_email,
  SUM(
    CASE WHEN country IS NULL
      OR country !~ '^[A-Z]{2}$' THEN
      1
    ELSE
      0
    END) AS invalid_country,
  SUM(
    CASE WHEN full_name IS NULL
      OR btrim(full_name) = '' THEN
      1
    ELSE
      0
    END) AS invalid_name
FROM
  customers;

CREATE OR REPLACE VIEW v_dq_orders AS
SELECT
  COUNT(*) AS total,
  SUM(
    CASE WHEN total_amount < 0 THEN
      1
    ELSE
      0
    END) AS negative_amounts,
  SUM(
    CASE WHEN customer_id IS NULL THEN
      1
    ELSE
      0
    END) AS missing_customer
FROM
  orders;

SELECT
  *
FROM
  v_dq_customers;

SELECT
  *
FROM
  v_dq_orders;

-- 2. Core Business Views ----------------------------------------------------
-- Lifetime value per customer.
--
-- Grain: exactly one row per customer, including customers who have not placed
-- an order. `orders.total_amount` is the authoritative revenue measure for this
-- capstone. Re-summing order lines here could silently change the definition
-- by excluding header-only orders or omitting adjustments stored on the header.
CREATE OR REPLACE VIEW v_customer_ltv AS
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  c.segment,
  COUNT(o.order_id) AS order_count,
  COALESCE(SUM(o.total_amount), 0)::numeric(14, 2) AS ltv
FROM
  customers c
  LEFT JOIN orders o USING (customer_id)
GROUP BY
  c.customer_id,
  c.full_name,
  c.country,
  c.segment;

-- Control 1: zero-order customers must still appear in the view.
SELECT
  COUNT(*) AS customers_missing_from_ltv
FROM
  customers c
  LEFT JOIN v_customer_ltv l USING (customer_id)
WHERE
  l.customer_id IS NULL;

-- Control 2: customer-level LTV must reconcile to the authoritative order
-- header total. Expected `difference` is 0.00 on the course seed.
SELECT
  ROUND(COALESCE(SUM(ltv), 0), 2) AS ltv_total,
  (
    SELECT
      ROUND(COALESCE(SUM(total_amount), 0), 2)
    FROM
      orders) AS order_total,
  ROUND(COALESCE(SUM(ltv), 0), 2) - (
    SELECT
      ROUND(COALESCE(SUM(total_amount), 0), 2)
    FROM
      orders) AS difference
FROM
  v_customer_ltv;

-- Monthly revenue and MoM growth
CREATE OR REPLACE VIEW v_monthly_revenue AS
WITH m AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  m.month,
  m.revenue,
  LAG(m.revenue) OVER (ORDER BY m.month) AS prev_month,
  ROUND((m.revenue - COALESCE(LAG(m.revenue) OVER (ORDER BY m.month), 0)) / NULLIF (LAG(m.revenue) OVER (ORDER BY m.month), 0), 4) AS mom_growth
FROM
  m;

-- 3. Stakeholder-ready Queries ---------------------------------------------
-- Finance: Budget vs Actual by month/category (YTD)
WITH exp AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  WHERE
    expense_date >= date_trunc('year', now())
  GROUP BY
    1,
    2
),
bud AS (
  SELECT
    date_trunc('month', period)::date AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  WHERE
    period >= date_trunc('year', now())
  GROUP BY
    1,
    2
)
SELECT
  COALESCE(b.category, e.category) AS category,
  COALESCE(b.month, e.month) AS month,
  COALESCE(b.budget, 0) AS budget,
  COALESCE(e.actual, 0) AS actual,
  ROUND(COALESCE(e.actual, 0) - COALESCE(b.budget, 0), 2) AS variance
FROM
  bud b
  FULL OUTER JOIN exp e ON e.month = b.month
  AND e.category = b.category
ORDER BY
  month DESC,
  category
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
  FROM
    orders o
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at)::date AS cohort_month
  FROM
    customers c
),
latest_six_cohorts AS (
  SELECT
    cohort_month
  FROM
    cohorts
  GROUP BY
    cohort_month
  ORDER BY
    cohort_month DESC
  LIMIT 6
),
cohort_members AS (
  SELECT
    c.customer_id,
    c.cohort_month
  FROM
    cohorts c
    JOIN latest_six_cohorts latest USING (cohort_month)
),
cohort_sizes AS (
  SELECT
    cohort_month,
    COUNT(*)::numeric AS cohort_size
  FROM
    cohort_members
  GROUP BY
    cohort_month
),
month_offsets AS (
  -- The seven requested lifecycle buckets are month 0 through month 6.
  SELECT
    generate_series(0, 6)::int AS month_offset
),
retention AS (
  SELECT
    cm.cohort_month,
    offsets.month_offset,
    sizes.cohort_size,
    COUNT(DISTINCT om.customer_id) AS active_customers
  FROM
    cohort_members cm
    JOIN cohort_sizes sizes USING (cohort_month)
    CROSS JOIN month_offsets offsets
    LEFT JOIN orders_m om ON om.customer_id = cm.customer_id
      AND om.order_month = (cm.cohort_month + make_interval(months => offsets.month_offset))::date
  GROUP BY
    cm.cohort_month, offsets.month_offset, sizes.cohort_size
)
SELECT
  cohort_month,
  month_offset,
  cohort_size,
  active_customers,
  ROUND(active_customers::numeric / NULLIF (cohort_size, 0), 4) AS retention_rate
FROM
  retention
ORDER BY
  cohort_month DESC,
  month_offset;

-- Operations: Top slow queries to optimize (use EXPLAIN ANALYZE in-session)
EXPLAIN
SELECT
  p.category,
  SUM(oi.quantity) AS qty
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
WHERE
  o.order_date >= now() - interval '180 days'
GROUP BY
  p.category
ORDER BY
  qty DESC;

-- 4. Performance Checklist ---------------------------------------------------
-- Indexes helpful for above queries (will be rolled back unless COMMIT)
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders (order_date);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);

CREATE INDEX IF NOT EXISTS idx_oi_order ON order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);

CREATE INDEX IF NOT EXISTS idx_expenses_month ON expenses (expense_date);

CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets (period);

-- Validate plan improvements quickly
EXPLAIN ANALYZE
SELECT
  *
FROM
  v_monthly_revenue
ORDER BY
  month DESC
LIMIT 12;

-- 5. Documentation Hints ----------------------------------------------------
-- Include in your write-up:
--  - Data quality findings (from v_dq_*) and remediation steps
--  - Core model entities used and rationale (customers/orders/items/events/etc.)
--  - Queries and indexes that moved the needle, with before/after EXPLAIN metrics
--  - Any compromises (freshness vs speed, materialized views, partitioning)
-- Exercises
-- 1. Prediction: identify which views are snapshot-independent and which use
--    CURRENT_DATE/now(), then explain the reproducibility consequence.
--    Inputs: For sql-60 Exercise 1, read the definitions of `v_dq_customers_solution` and `v_customer_ltv_solution` and of the trailing or current-period queries (the learner Finance CTEs and Operations filter call `now()`, and Exercise 4 calls `CURRENT_DATE`), then record each object's clock dependence in an inline `VALUES` fixture with `object_name` and `clock_contract`.
--    Expected result/shape: For sql-60 Exercise 1, expected output: 3 rows: `v_dq_customers_solution` and `v_customer_ltv_solution` marked `snapshot-independent`, and `trailing/current-period reports` marked `clock-dependent: bind as_of_date`. The final columns are `object_name` and `clock_contract`.
--    Verify: For sql-60 Exercise 1, inside the solution transaction run `SELECT viewname FROM pg_views WHERE schemaname = 'training' AND definition ~* '(now\(\)|current_date|current_timestamp)'`: it returns 0 rows, which backs both `snapshot-independent` labels. Then create a rolled-back probe view `v_clock_probe AS SELECT CURRENT_DATE AS as_of` and rerun the search: it returns exactly `v_clock_probe`, so the search does detect a clock call.
--    Hint ladder, rung 1: For sql-60 Exercise 1, list the views the capstone creates and search each `pg_views.definition` for `now()` and `CURRENT_DATE` before you type a `clock_contract` for it.
-- 2. Construction: build a single sign-off query whose rows are named checks
--    with observed_value, expected_value, pass, severity, and remediation.
--    Inputs: For sql-60 Exercise 2, read `invalid_email` from the one-row `v_dq_customers_solution` and compare `SUM(ltv)` from `v_customer_ltv_solution` with `SUM(total_amount)` from `orders`; write each check as one `UNION ALL` branch of `checks` with `check_name`, `observed_value`, `expected_value`, `severity`, and `remediation`, then compute `pass` as `observed_value = expected_value`.
--    Expected result/shape: For sql-60 Exercise 2, expected output: 2 rows, one per `check_name`: `invalid_customer_emails` (observed 0) and `ltv_reconciles_to_orders` (observed 0.00, the absolute gap between LTV and order totals), both `critical` with `expected_value` 0 and `pass` true. The final columns are `check_name`, `observed_value`, `expected_value`, `severity`, `remediation`, and `pass`. The final order is `severity, check_name`.
--    Verify: For sql-60 Exercise 2, confirm that `SELECT invalid_email FROM v_dq_customers_solution` returns 0 and that `SUM(ltv)` and `SUM(total_amount)` both return 2,355,646.89, matching the two observed values. In a rolled-back transaction set customer 1's email to `'not-an-email'` (or to NULL): `invalid_customer_emails` then reports observed 1 and `pass` false, so the gate fails on a real defect.
--    Hint ladder, rung 1: For sql-60 Exercise 2, run each `UNION ALL` branch of `checks` alone; each returns one row, so `checks` holds 2 rows before `pass` is computed.
-- 3. Debugging: remove repeated LAG expressions from v_monthly_revenue by using
--    a second CTE, while preserving the first month's NULL growth rate.
--    Inputs: For sql-60 Exercise 3, read `orders` through two CTEs: `monthly` sums `total_amount` by `date_trunc('month', order_date)::date`, and `with_previous` adds `LAG(revenue) OVER (ORDER BY month)` once as `previous_month`; the outer `SELECT` of `v_monthly_revenue_refactored_solution` derives `month_over_month_growth` from that column.
--    Expected result/shape: For sql-60 Exercise 3, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, with `previous_month` and `month_over_month_growth` NULL only on the first row and 13 negative growth values. The final columns are `month`, `revenue`, `previous_month`, and `month_over_month_growth`. The final order is `month`.
--    Verify: For sql-60 Exercise 3, compare the refactored view with `v_monthly_revenue_solution` and with the learner `v_monthly_revenue` using `EXCEPT` in both directions: 0 rows each way, and `SUM(revenue)` is 2,355,646.89. In a rolled-back transaction set every February 2023 order's `total_amount` to 0: 2023-02-01 shows `revenue` 0.00, and 2023-03-01 shows `previous_month` 0.00 with NULL growth from `NULLIF` instead of a division error. Deleting the 37 May 2024 orders instead leaves 45 rows and gives 2024-06-01 April's 20,055.03 as `previous_month`, because `LAG` reads the previous row, not the previous calendar month.
--    Hint ladder, rung 1: For sql-60 Exercise 3, run `monthly` alone (46 rows, one per month, summing to 2,355,646.89), then `with_previous`, and check that `previous_month` is NULL only on 2023-02-01.
-- 4. Edge case: represent an incomplete current month separately so it is not
--    compared directly with a complete prior month.
--    Inputs: For sql-60 Exercise 4, read the 46 rows of `v_monthly_revenue_refactored_solution` and add `is_incomplete_month` as `month = date_trunc('month', CURRENT_DATE)::date`.
--    Expected result/shape: For sql-60 Exercise 4, expected output: 46 rows, one per `month`, newest first, with `is_incomplete_month` true only on the current calendar month (2026-11-01 at 85,364.67 when `CURRENT_DATE` was 2026-11-25) and false on the 45 complete months. The final columns are `month`, `revenue`, and `is_incomplete_month`. The final order is `month DESC`.
--    Verify: For sql-60 Exercise 4, confirm that `COUNT(*) FILTER (WHERE is_incomplete_month)` is 1 of 46 rows and that the flagged month holds `MAX(order_date)`: on the checked load November 2026 had 151 orders over 23 order days against October's 313 over 31. Replace `CURRENT_DATE` with `DATE '2026-10-15'` and the flag moves to 2026-10-01 (170,179.13), which shows the result depends on the clock and needs a bound as-of date.
--    Hint ladder, rung 1: For sql-60 Exercise 4, select `month`, `revenue`, and `month = date_trunc('month', CURRENT_DATE)::date` for the newest two months first; only 2026-11-01 was true on the checked load.
-- 5. Performance: capture before/after plans in JSON and document plan shape,
--    estimates, actual rows, buffers, and timing without promising universal gains.
--    Inputs: For sql-60 Exercise 5, run `SELECT * FROM v_monthly_revenue_refactored_solution ORDER BY month DESC LIMIT 12` alone first (12 rows, 2026-11-01 back to 2025-12-01), then wrap the same statement in `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` with seed rows, settings, and statistics unchanged.
--    Expected result/shape: For sql-60 Exercise 5, expected output: one row in a single `QUERY PLAN` column holding a JSON array with one plan of 8 nodes: `Limit` (12 actual rows), `Sort` (top-N heapsort), `Subquery Scan` on `with_previous`, `WindowAgg`, `Sort`, `Subquery Scan` on `monthly`, a hashed `Aggregate`, and a `Seq Scan` on `orders` (4,362 rows). The final column is `QUERY PLAN`.
--    Verify: For sql-60 Exercise 5, read each node's `Plan Rows` beside `Actual Rows` times `Actual Loops`: the hashed `Aggregate` plans 4,362 groups and returns 46, and the `Seq Scan` touches all 65 pages of `orders` (`Shared Hit Blocks` plus `Shared Read Blocks`). In a rolled-back transaction run `CREATE STATISTICS orders_month_stats ON (date_trunc('month', order_date)) FROM orders` and `ANALYZE orders`, then explain again: the same 8 nodes return the same 12 rows, but the `Aggregate` estimate drops to 46.
--    Hint ladder, rung 1: For sql-60 Exercise 5, run the `SELECT ... ORDER BY month DESC LIMIT 12` without `EXPLAIN` first, then read the JSON one node at a time from the `Seq Scan` upward.
-- 6. Explanation: produce a release checklist covering rollback, ownership,
--    permissions, refresh cadence, monitoring, data contracts, and known limits.
--    Inputs: For sql-60 Exercise 6, list the release checklist as an inline `VALUES` relation with one row per `item`, its current `evidence`, and its `owner`.
--    Expected result/shape: For sql-60 Exercise 6, expected output: 6 rows, one per checklist `item`: rollback plan, object ownership/privileges, refresh cadence, monitoring and alerts, data contracts, and known limits. The final columns are `item`, `evidence`, and `owner`.
--    Verify: For sql-60 Exercise 6, confirm 6 rows with no NULL `evidence` or `owner` and no repeated `item`; every row whose `evidence` reads `review required` still needs a named reviewer before release.
--    Hint ladder, rung 1: For sql-60 Exercise 6, write the `VALUES` list with column aliases first and check that each `item` appears once.
-- 7. Construction: create a lineage table that maps each published metric to
--    its source tables, transformation grain, and validation query.
--    Inputs: For sql-60 Exercise 7, write an inline `VALUES` lineage fixture with one row per published metric (`customer_ltv`, `monthly_revenue`, and `customer_dq`) giving its `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
--    Expected result/shape: For sql-60 Exercise 7, expected output: 3 rows: `customer_ltv` from customers + orders at customer grain, `monthly_revenue` from orders at calendar-month grain, and `customer_dq` from customers as one snapshot summary. The final columns are `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
--    Verify: For sql-60 Exercise 7, turn each `validation_query` into a runnable check: `SUM(ltv)` over the 500 rows of `v_customer_ltv_solution`, `SUM(revenue)` over the 46 rows of the refactored monthly view, and `SUM(total_amount)` over `orders` all return 2,355,646.89, and `v_dq_customers_solution` reports 0 invalid emails, countries, and names over 500 customers. A row whose text cannot be rewritten as a `SELECT` with a pass condition is not yet lineage evidence.
--    Hint ladder, rung 1: For sql-60 Exercise 7, write the three `VALUES` rows with column aliases first, then rewrite each `validation_query` text as a scratch `SELECT` to prove it can be executed.
-- 8. Debugging: prove every dashboard subtotal reconciles to a simpler control
--    query before approving any performance optimization.
--    Inputs: For sql-60 Exercise 8, sum `revenue` over the 46 rows of `v_monthly_revenue_refactored_solution` as `dashboard_total` and `total_amount` over the 4,362 `orders` as `source_total`, each rounded to 2 places in its own scalar subquery, and subtract them as `difference`.
--    Expected result/shape: For sql-60 Exercise 8, expected output: one row with `dashboard_total` 2,355,646.89, `source_total` 2,355,646.89, and `difference` 0.00 on the checked load. The final columns are `dashboard_total`, `source_total`, and `difference`.
--    Verify: For sql-60 Exercise 8, run the two scalar subqueries alone: both return 2,355,646.89. In a rolled-back transaction insert a 100.00 order for customer 1 dated `now()`: both totals become 2,355,746.89 and `difference` stays 0.00, so this control checks the view logic rather than the load. Make the dashboard side skip the open month with `FILTER (WHERE month < date_trunc('month', CURRENT_DATE)::date)` instead, and `difference` becomes -85,364.67, the November revenue that version would hide.
--    Hint ladder, rung 1: For sql-60 Exercise 8, run `SELECT ROUND(SUM(revenue), 2) FROM v_monthly_revenue_refactored_solution` and `SELECT ROUND(SUM(total_amount), 2) FROM orders` separately before combining them; both print 2,355,646.89 on the checked load.
-- 9. Edge case: test empty, one-row, NULL-heavy, and duplicate-key fixtures and
--    record which assumptions prevent each from reaching production.
--    Inputs: For sql-60 Exercise 9, build a three-row `VALUES` fixture `edge_fixture(id, email, amount)` with one row whose email and amount are NULL and two rows that share `id` 2 with emails that differ only in case, then count rows, NULL emails, duplicate keys, and non-null amounts.
--    Expected result/shape: For sql-60 Exercise 9, expected output: one row with `fixture_rows` 3, `null_email_rows` 1, `duplicate_key_rows` 1, and `nonnull_amount_rows` 2. The final columns are `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
--    Verify: For sql-60 Exercise 9, confirm that `duplicate_key_rows` equals `COUNT(*) - COUNT(DISTINCT id)` (3 - 2 = 1) and `nonnull_amount_rows` equals `COUNT(amount)` (2); `COUNT(DISTINCT lower(email))` is 1, so the two `id` 2 rows also collide after email normalization.
--    Hint ladder, rung 1: For sql-60 Exercise 9, count each property in its own `SELECT` over the fixture first; `COUNT(column)` skips NULL, while `COUNT(*)` does not.
-- 10. Final sign-off: return PASS/FAIL/NOT_RUN for every acceptance criterion;
--     prose alone must never turn an unexecuted check into PASS.
-- When ready to persist created views/indexes, replace ROLLBACK with COMMIT.
--    Inputs: For sql-60 Exercise 10, list the acceptance criteria as a `VALUES` relation with `criterion`, an `executed` flag, the `observed` value from the solution views, and the `expected` value, then label each criterion `PASS`, `FAIL`, or `NOT_RUN`.
--    Expected result/shape: For sql-60 Exercise 10, expected output: 3 rows ordered by `criterion`: `customer DQ` PASS, `LTV reconciliation` PASS, and `Windows CI bootstrap` NOT_RUN. The final columns are `criterion` and `result`. The final order is `criterion`.
--    Verify: For sql-60 Exercise 10, confirm that each PASS row's observed value matches its expected value when queried directly (`SELECT invalid_email FROM v_dq_customers_solution` returns 0) and that the unexecuted criterion reports `NOT_RUN`, never `PASS`.
--    Hint ladder, rung 1: For sql-60 Exercise 10, write the `CASE` so that `executed` is tested before the comparison; an unexecuted check must never fall through to `PASS`.
ROLLBACK;
