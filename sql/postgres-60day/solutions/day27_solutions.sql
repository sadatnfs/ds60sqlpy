-- Day 27 solutions: pivot and unpivot
SET search_path TO training, public;

-- Exercise 1: payment revenue by method across the latest four quarters.
WITH quarter_totals AS (
  SELECT date_trunc('quarter', payment_date)::date AS quarter,
         method,
         SUM(amount) AS revenue
  FROM payments
  WHERE payment_date >= date_trunc('quarter', CURRENT_DATE) - interval '9 months'
  GROUP BY date_trunc('quarter', payment_date), method
)
SELECT quarter,
       ROUND(SUM(revenue) FILTER (WHERE method = 'card'), 2) AS card,
       ROUND(SUM(revenue) FILTER (WHERE method = 'paypal'), 2) AS paypal,
       ROUND(SUM(revenue) FILTER (WHERE method = 'bank'), 2) AS bank,
       ROUND(SUM(revenue) FILTER (WHERE method = 'credit'), 2) AS credit
FROM quarter_totals
GROUP BY quarter
ORDER BY quarter;

-- Exercise 2: budgets are already stored in long form. To demonstrate
-- unpivoting, first create a wide monthly projection, then normalize it again.
WITH wide_budgets AS (
  SELECT period,
         SUM(amount) FILTER (WHERE category = 'COGS') AS cogs,
         SUM(amount) FILTER (WHERE category = 'Marketing') AS marketing,
         SUM(amount) FILTER (WHERE category = 'Payroll') AS payroll,
         SUM(amount) FILTER (WHERE category = 'Infrastructure') AS infrastructure,
         SUM(amount) FILTER (WHERE category = 'G&A') AS general_admin
  FROM budgets
  GROUP BY period
)
SELECT w.period, u.category, u.amount
FROM wide_budgets w
CROSS JOIN LATERAL (
  VALUES
    ('COGS', w.cogs),
    ('Marketing', w.marketing),
    ('Payroll', w.payroll),
    ('Infrastructure', w.infrastructure),
    ('G&A', w.general_admin)
) AS u(category, amount)
ORDER BY w.period, u.category;
