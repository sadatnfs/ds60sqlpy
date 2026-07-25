-- Day 60: Final Capstone - Integrated Data Challenge (Part 3)
-- Focus: End-to-end solution: DQ -> Transform -> Analytics -> Performance sign-off
-- Success Criteria:
--  - All critical queries complete < 10s on your dataset
--  - DQ checks pass with documented exceptions
--  - Clear documentation of choices and optimizations

BEGIN;
SET search_path TO training, public;

-- 1) DQ Summary Views (re-usable) ------------------------------------------
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

-- 2) Core Business Views ----------------------------------------------------
-- Lifetime value per customer
CREATE OR REPLACE VIEW v_customer_ltv AS
WITH line AS (
  SELECT o.customer_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
)
SELECT customer_id, ROUND(SUM(order_value),2) AS ltv
FROM line
GROUP BY customer_id;

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

-- 3) Stakeholder-ready Queries ---------------------------------------------
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

-- Marketing: Cohort retention for last 6 cohorts
WITH orders_m AS (
  SELECT o.customer_id, date_trunc('month', o.order_date)::date AS order_month FROM orders o GROUP BY 1,2
), cohorts AS (
  SELECT c.customer_id, date_trunc('month', c.created_at)::date AS cohort_month FROM customers c
), retention AS (
  SELECT co.cohort_month, om.order_month,
         (
           EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT * FROM retention WHERE month_offset BETWEEN 0 AND 6 ORDER BY cohort_month DESC, month_offset;

-- Operations: Top slow queries to optimize (use EXPLAIN ANALYZE in-session)
EXPLAIN
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '180 days'
GROUP BY p.category
ORDER BY qty DESC;

-- 4) Performance Checklist ---------------------------------------------------
-- Indexes helpful for above queries (will be rolled back unless COMMIT)
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_oi_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_expenses_month ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period);

-- Validate plan improvements quickly
EXPLAIN ANALYZE SELECT * FROM v_monthly_revenue ORDER BY month DESC LIMIT 12;

-- 5) Documentation Hints ----------------------------------------------------
-- Include in your write-up:
--  - Data quality findings (from v_dq_*) and remediation steps
--  - Core model entities used and rationale (customers/orders/items/events/etc.)
--  - Queries and indexes that moved the needle, with before/after EXPLAIN metrics
--  - Any compromises (freshness vs speed, materialized views, partitioning)

-- When ready to persist created views/indexes, replace ROLLBACK with COMMIT.
ROLLBACK;
