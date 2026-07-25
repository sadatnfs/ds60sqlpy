# Day 51 Solutions — Cash Flow and Operating Margin

The project finishes with monthly operating margin and a three-month seasonal
cash projection. See [`day51_solutions.sql`](day51_solutions.sql).

## Exercise 1 — Monthly operating margin

The prompt defines operating cost as `COGS + Payroll + Infrastructure + G&A`;
Marketing is deliberately excluded.

```sql
SET search_path TO training, public;

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
```

Expected grain: one row per month appearing in either payments or operating
expenses. Margin is `NULL` when there is no cash-in denominator.

## Exercise 2 — Next three months by matching calendar month

The phrase “matching months” is interpreted as the same calendar month in
earlier years.

```sql
SET search_path TO training, public;

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
```

Expected shape: exactly three future month rows. The count column shows how much
history supports each estimate; a `NULL` projection means there was none.

## Reasoning, safety, and pitfalls

- Cash flow uses payments, not booked order revenue.
- The operating-margin definition is course policy; real financial statements
  may classify categories differently.
- A seasonal average needs multiple years to be convincing. Treat a one-point
  average as a naive forecast and disclose the sample count.
- Both answers are read-only.
