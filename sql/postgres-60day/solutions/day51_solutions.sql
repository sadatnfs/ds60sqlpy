-- Day 51 solutions: cash flow and operating margin
SET search_path TO training, public;

-- Exercise 1: operating margin by month using the categories named in prompt.
WITH cash AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY date_trunc('month', payment_date)
), operating_expense AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) FILTER (
           WHERE category IN ('COGS', 'Payroll', 'Infrastructure', 'G&A')
         ) AS operating_cost
  FROM expenses
  GROUP BY date_trunc('month', expense_date)
)
SELECT COALESCE(c.month, e.month) AS month,
       ROUND(COALESCE(c.cash_in, 0), 2) AS cash_in,
       ROUND(COALESCE(e.operating_cost, 0), 2) AS operating_cost,
       ROUND(
         (COALESCE(c.cash_in, 0) - COALESCE(e.operating_cost, 0))
           / NULLIF(c.cash_in, 0),
         4
       ) AS operating_margin
FROM cash c
FULL OUTER JOIN operating_expense e USING (month)
ORDER BY month DESC;

-- Exercise 2: seasonal average for the next three calendar months.
-- Assumption: "matching months" means the same calendar month in prior years.
WITH cash AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY date_trunc('month', payment_date)
), expense AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) AS cash_out
  FROM expenses
  GROUP BY date_trunc('month', expense_date)
), historical AS (
  SELECT COALESCE(c.month, e.month) AS month,
         COALESCE(c.cash_in, 0) - COALESCE(e.cash_out, 0) AS net_cash
  FROM cash c
  FULL OUTER JOIN expense e USING (month)
), future AS (
  SELECT (
           date_trunc('month', CURRENT_DATE)
           + n * interval '1 month'
         )::date AS forecast_month
  FROM generate_series(1, 3) AS g(n)
)
SELECT f.forecast_month,
       ROUND(AVG(h.net_cash), 2) AS projected_net_cash,
       COUNT(h.month) AS matching_historical_months
FROM future f
LEFT JOIN historical h
  ON EXTRACT(month FROM h.month) = EXTRACT(month FROM f.forecast_month)
 AND h.month < f.forecast_month
GROUP BY f.forecast_month
ORDER BY f.forecast_month;

-- Exercise 3: cash receipts and order revenue answer different timing questions.
SELECT date_trunc('month', o.order_date)::date AS month,
       SUM(o.total_amount) AS booked_order_revenue,
       COALESCE(p.cash_received, 0) AS cash_received
FROM orders o
LEFT JOIN (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_received
  FROM payments GROUP BY 1
) p ON p.month = date_trunc('month', o.order_date)::date
GROUP BY date_trunc('month', o.order_date), p.cash_received
ORDER BY month;

-- Exercise 4: monthly flows establish the grain; the running SUM turns net
-- movement into an ending balance from the declared zero opening balance.
WITH flow AS (
  SELECT month, SUM(cash_in) AS cash_in, SUM(cash_out) AS cash_out
  FROM (
    SELECT date_trunc('month', payment_date)::date AS month,
           amount AS cash_in, 0::numeric AS cash_out FROM payments
    UNION ALL
    SELECT date_trunc('month', expense_date)::date, 0::numeric, amount
    FROM expenses
  ) entries
  GROUP BY month
), balances AS (
  SELECT month, cash_in, cash_out, cash_in - cash_out AS net_cash,
         SUM(cash_in - cash_out) OVER (ORDER BY month) AS ending_cash
  FROM flow
)
SELECT month,
       LAG(ending_cash, 1, 0::numeric) OVER (ORDER BY month) AS beginning_cash,
       cash_in, cash_out, net_cash, ending_cash
FROM balances
ORDER BY month;

-- Exercise 5: the calendar spine retains months appearing on only one side.
WITH bounds AS (
  SELECT LEAST((SELECT MIN(payment_date)::date FROM payments),
               (SELECT MIN(expense_date) FROM expenses)) AS first_day,
         GREATEST((SELECT MAX(payment_date)::date FROM payments),
                  (SELECT MAX(expense_date) FROM expenses)) AS last_day
), months AS (
  SELECT generate_series(date_trunc('month', first_day),
                         date_trunc('month', last_day),
                         interval '1 month')::date AS month
  FROM bounds
), cash AS (
  SELECT date_trunc('month', payment_date)::date AS month, SUM(amount) AS cash_in
  FROM payments GROUP BY 1
), costs AS (
  SELECT date_trunc('month', expense_date)::date AS month, SUM(amount) AS cash_out
  FROM expenses GROUP BY 1
)
SELECT m.month, COALESCE(c.cash_in, 0) AS cash_in,
       COALESCE(x.cash_out, 0) AS cash_out
FROM months m
LEFT JOIN cash c USING (month)
LEFT JOIN costs x USING (month)
ORDER BY m.month;

-- Exercise 6: NULLIF preserves an undefined margin and the status explains it.
WITH toy(month, cash_in, operating_cost) AS (
  VALUES (date '2026-01-01', 0::numeric, 100::numeric),
         (date '2026-02-01', 500, 300)
)
SELECT month,
       (cash_in - operating_cost) / NULLIF(cash_in, 0) AS operating_margin,
       CASE WHEN cash_in = 0 THEN 'undefined: zero cash in'
            ELSE 'defined' END AS margin_status
FROM toy;
