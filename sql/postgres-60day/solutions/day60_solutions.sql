-- Day 60 solution: end-to-end sign-off
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_dq_customers_solution AS
SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (
         WHERE email IS NULL
            OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
       ) AS invalid_email,
       COUNT(*) FILTER (WHERE country !~ '^[A-Z]{2}$') AS invalid_country,
       COUNT(*) FILTER (WHERE trim(full_name) = '') AS invalid_name
FROM customers;

CREATE VIEW v_customer_ltv_solution AS
SELECT c.customer_id,
       c.country,
       COALESCE(SUM(o.total_amount), 0)::numeric(14,2) AS ltv
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.country;

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
)
SELECT month,
       revenue,
       LAG(revenue) OVER (ORDER BY month) AS previous_month,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY month))
           / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
         4
       ) AS month_over_month_growth
FROM monthly;

-- DQ sign-off and business-view reconciliation.
SELECT * FROM v_dq_customers_solution;

SELECT (SELECT ROUND(SUM(ltv), 2) FROM v_customer_ltv_solution)
         AS customer_ltv_total,
       (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS order_total,
       (SELECT ROUND(SUM(ltv), 2) FROM v_customer_ltv_solution)
         - (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS difference;

-- Candidate production indexes remain rolled back in this tutorial answer.
CREATE INDEX idx_orders_date_day60_solution ON orders(order_date);
CREATE INDEX idx_orders_customer_day60_solution ON orders(customer_id);
CREATE INDEX idx_order_items_order_day60_solution ON order_items(order_id);
CREATE INDEX idx_expenses_date_day60_solution ON expenses(expense_date);
CREATE INDEX idx_budgets_period_day60_solution ON budgets(period);

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM v_monthly_revenue_solution
ORDER BY month DESC
LIMIT 12;

-- The written capstone should record these sign-off items and measured values.
SELECT item
FROM (
  VALUES
    ('DQ exceptions and remediation'),
    ('model grain and join rationale'),
    ('before/after EXPLAIN evidence'),
    ('freshness versus performance tradeoffs'),
    ('known limitations and next steps')
) AS checklist(item);

-- Exercise 1: clock-dependent queries need an as-of value for reproducibility.
SELECT *
FROM (
  VALUES
    ('v_dq_customers_solution', 'snapshot-independent'),
    ('v_customer_ltv_solution', 'snapshot-independent'),
    ('trailing/current-period reports', 'clock-dependent: bind as_of_date')
) AS reproducibility(object_name, clock_contract);

-- Exercise 2: every sign-off row carries observed/expected values, severity, and
-- remediation. PASS is computed, never typed by hand.
WITH checks AS (
  SELECT 'invalid_customer_emails' AS check_name,
         invalid_email::numeric AS observed_value,
         0::numeric AS expected_value,
         'critical' AS severity,
         'quarantine invalid customer records' AS remediation
  FROM v_dq_customers_solution
  UNION ALL
  SELECT 'ltv_reconciles_to_orders',
         ABS(
           (SELECT SUM(ltv) FROM v_customer_ltv_solution)
           - (SELECT SUM(total_amount) FROM orders)
         ),
         0, 'critical', 'repair customer-grain join or revenue definition'
)
SELECT *, observed_value = expected_value AS pass
FROM checks
ORDER BY severity, check_name;

-- Exercise 3: compute LAG once in `with_previous`, then use that named value.
-- The first month intentionally retains NULL growth because no comparison exists.
CREATE VIEW v_monthly_revenue_refactored_solution AS
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), with_previous AS (
  SELECT month, revenue,
         LAG(revenue) OVER (ORDER BY month) AS previous_month
  FROM monthly
)
SELECT month, revenue, previous_month,
       ROUND((revenue - previous_month) / NULLIF(previous_month, 0), 4)
         AS month_over_month_growth
FROM with_previous;
SELECT * FROM v_monthly_revenue_refactored_solution ORDER BY month;

-- Exercise 4: flag the open calendar month instead of comparing it as if it
-- were complete. A production report should bind an explicit as-of date.
SELECT month, revenue,
       month = date_trunc('month', CURRENT_DATE)::date AS is_incomplete_month
FROM v_monthly_revenue_refactored_solution
ORDER BY month DESC;

-- Exercise 5: structured plan evidence records estimates, actuals, buffers, and
-- timing. Results remain specific to this server, seed, and cache state.
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM v_monthly_revenue_refactored_solution
ORDER BY month DESC
LIMIT 12;

-- Exercise 6: ownership and operations are part of release readiness.
SELECT *
FROM (
  VALUES
    ('rollback plan', 'documented', 'release owner'),
    ('object ownership/privileges', 'review required', 'database owner'),
    ('refresh cadence', 'not applicable to ordinary views', 'analytics owner'),
    ('monitoring and alerts', 'review required', 'operations'),
    ('data contracts', 'executable checks above', 'data owner'),
    ('known limits', 'synthetic seed and local plans', 'analytics owner')
) AS release_check(item, evidence, owner);

-- Exercise 7: lineage states source, transformation grain, and its validation.
SELECT *
FROM (
  VALUES
    ('customer_ltv', 'customers + orders', 'customer',
     'SUM(ltv) = SUM(orders.total_amount)'),
    ('monthly_revenue', 'orders', 'calendar month',
     'SUM(month revenue) = SUM(order totals)'),
    ('customer_dq', 'customers', 'one snapshot summary',
     'invalid counts are zero or approved exceptions')
) AS lineage(metric_name, source_tables, transformation_grain, validation_query);

-- Exercise 8: dashboard monthly revenue must equal the simpler source control.
SELECT (SELECT ROUND(SUM(revenue), 2)
        FROM v_monthly_revenue_refactored_solution) AS dashboard_total,
       (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS source_total,
       (SELECT ROUND(SUM(revenue), 2)
        FROM v_monthly_revenue_refactored_solution)
       - (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS difference;

-- Exercise 9: explicit miniature fixtures make boundary assumptions reviewable
-- without corrupting the canonical training data.
WITH edge_fixture(id, email, amount) AS (
  VALUES (1, NULL::text, NULL::numeric),
         (2, 'DUP@example.com', 10),
         (2, 'dup@example.com', 10)
)
SELECT COUNT(*) AS fixture_rows,
       COUNT(*) FILTER (WHERE email IS NULL) AS null_email_rows,
       COUNT(*) - COUNT(DISTINCT id) AS duplicate_key_rows,
       COUNT(amount) AS nonnull_amount_rows
FROM edge_fixture;

-- Exercise 10: NOT_RUN is distinct from FAIL. Only executed evidence can PASS.
SELECT criterion,
       CASE
         WHEN executed AND observed = expected THEN 'PASS'
         WHEN executed THEN 'FAIL'
         ELSE 'NOT_RUN'
       END AS result
FROM (
  VALUES
    ('customer DQ', true,
     (SELECT invalid_email::numeric FROM v_dq_customers_solution), 0::numeric),
    ('LTV reconciliation', true,
     ABS((SELECT SUM(ltv) FROM v_customer_ltv_solution)
         - (SELECT SUM(total_amount) FROM orders)), 0::numeric),
    ('Windows CI bootstrap', false, NULL::numeric, NULL::numeric)
) AS acceptance(criterion, executed, observed, expected)
ORDER BY criterion;

ROLLBACK;
