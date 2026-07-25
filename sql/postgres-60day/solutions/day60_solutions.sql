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

ROLLBACK;
