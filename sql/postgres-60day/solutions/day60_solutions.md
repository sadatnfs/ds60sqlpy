# Day 60 — Solutions (Final Capstone, Part 3 — E2E Docs, Views, Performance Sign‑off)

Today ties everything together: we build DQ and business views, run stakeholder queries, and check performance. Below are detailed, line‑by‑line explanations and practical tips to flip ROLLBACK→COMMIT when you’re satisfied.

Section 1 — Data Quality (DQ) Summary Views
```sql
CREATE OR REPLACE VIEW v_dq_customers AS
SELECT COUNT(*) AS total,
       SUM(CASE WHEN email IS NULL OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$' THEN 1 ELSE 0 END) AS invalid_email,
       SUM(CASE WHEN country IS NULL OR country !~ '^[A-Z]{2}$' THEN 1 ELSE 0 END) AS invalid_country,
       SUM(CASE WHEN full_name IS NULL OR btrim(full_name) = '' THEN 1 ELSE 0 END) AS invalid_name
FROM customers;
```
Line‑by‑line
- total: total customer rows.
- invalid_email: email missing or regex‑failing (case‑insensitive !~* matches invalids).
- invalid_country: country missing or not 2 letters (you can harden using a reference map).
- invalid_name: blank after trimming.

```sql
CREATE OR REPLACE VIEW v_dq_orders AS
SELECT COUNT(*) AS total,
       SUM(CASE WHEN total_amount < 0 THEN 1 ELSE 0 END) AS negative_amounts,
       SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer
FROM orders;
```
Notes
- negative_amounts: catches data errors or refund rows; decide policy.
- missing_customer: should be zero under enforced FKs.

Quick check
```sql
SELECT * FROM v_dq_customers;
SELECT * FROM v_dq_orders;
```

Section 2 — Business Views (reusable)
A) Customer Lifetime Value (LTV)
```sql
CREATE OR REPLACE VIEW v_customer_ltv AS
WITH line AS (
  SELECT o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
)
SELECT customer_id, ROUND(SUM(order_value),2) AS ltv
FROM line
GROUP BY customer_id;
```
Line‑by‑line
- line: reduce each order to a single value (sum of items net of discount) so orders don’t double‑count.
- Final: sum orders per customer; round for currency presentation.

B) Monthly Revenue with MoM Growth
```sql
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
```
Line‑by‑line
- m: monthly rollup.
- prev_month: window LAG by month.
- mom_growth: safe divide; when prev is 0 or NULL, result is NULL to avoid divide‑by‑zero.

Section 3 — Stakeholder‑ready Queries
A) Finance — YTD Budget vs Actual by month/category
```sql
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
```
Line‑by‑line
- Restricts to current year.
- FULL OUTER JOIN shows categories present in only one side.
- variance = actual − budget per month.

B) Marketing — Cohort retention (last 6 cohorts)
```sql
WITH orders_m AS (
  SELECT o.customer_id, date_trunc('month', o.order_date)::date AS order_month FROM orders o GROUP BY 1,2
), cohorts AS (
  SELECT c.customer_id, date_trunc('month', c.created_at)::date AS cohort_month FROM customers c
), retention AS (
  SELECT co.cohort_month, om.order_month,
         EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
), last6 AS (
  SELECT DISTINCT cohort_month FROM cohorts ORDER BY cohort_month DESC LIMIT 6
)
SELECT * FROM retention WHERE month_offset BETWEEN 0 AND 6 AND cohort_month IN (SELECT cohort_month FROM last6)
ORDER BY cohort_month DESC, month_offset;
```
Notes
- month_offset: lifecycle months since cohort signup.
- Filter to a small preview window (0..6) for quick charts.

C) Operations — Identify a heavy query and inspect its plan
```sql
EXPLAIN
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '180 days'
GROUP BY p.category
ORDER BY qty DESC;
```
Tips
- Replace EXPLAIN with EXPLAIN ANALYZE to execute and measure.
- Ensure an index on orders(order_date) to prune time range efficiently.

Section 4 — Performance Checklist (DDL staged under transaction)
```sql
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_oi_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_expenses_month ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period);

EXPLAIN ANALYZE SELECT * FROM v_monthly_revenue ORDER BY month DESC LIMIT 12;
```
Line‑by‑line
- CREATE INDEX IF NOT EXISTS: safe to run repeatedly; no effect if present.
- Final EXPLAIN ANALYZE: validate plans/timings after indexes.

Persisting vs testing safely
- Lesson script ends with ROLLBACK; switch to COMMIT only once you’re happy with the views and indexes.
- In production, create change scripts (DDL) separate from ad‑hoc EXPLAINs and keep before/after plan snapshots.

Troubleshooting patterns
- If EXPLAIN shows sequential scans on large tables: verify predicate sargability (no functions on columns), stats up‑to‑date (ANALYZE), and relevant indexes exist.
- If sorts spill to disk: raise work_mem for the session temporarily or add appropriate indexes to avoid large sorts.

What to hand off
- DQ snapshots from v_dq_* with remediation notes.
- A short readme listing the views created and the indexes added.
- Before/after EXPLAIN ANALYZE for two or three critical queries with timings.
