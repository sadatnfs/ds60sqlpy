# Day 51 — Solutions (Project 2: Finance/Operations, Part 3 — Cash Flow & Rolling Budgets)

We compute monthly net cash flow and rolling comparisons, then implement the practice exercises with detailed, line‑by‑line solutions.

Reference (annotated)
```sql
-- Net cash per month = payments (cash_in) - expenses (cash_out)
WITH pay_m AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY 1
), exp_m AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) AS cash_out
  FROM expenses
  GROUP BY 1
), joined AS (
  -- Full outer semantics via COALESCE across months appearing in either side
  SELECT COALESCE(p.month, e.month) AS month,
         COALESCE(p.cash_in, 0)     AS cash_in,
         COALESCE(e.cash_out, 0)    AS cash_out
  FROM pay_m p FULL OUTER JOIN exp_m e ON e.month = p.month
)
SELECT month,
       ROUND(cash_in - cash_out, 2) AS net_cash_flow,
       SUM(ROUND(cash_in - cash_out, 2)) OVER (ORDER BY month) AS cumulative_cash
FROM joined
ORDER BY month DESC
LIMIT 36;
```
Notes
- pay_m, exp_m: roll up to month grain. date_trunc('month') standardizes timestamps.
- joined: FULL JOIN allows for months with only payments or only expenses.
- cumulative_cash uses a running window ordered by month.

Exercise 1 — Operating margin
Prompt
- (cash_in − COGS − Payroll − Infrastructure − G&A) / cash_in per month.
- Treat missing categories as zero; guard divide‑by‑zero.

Solution
```sql
WITH cash_in AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY 1
), exp_cat AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS amount
  FROM expenses
  GROUP BY 1,2
), pivot AS (
  -- Pivot core categories with conditional sums; extend WHENs to match your taxonomy
  SELECT month,
         SUM(CASE WHEN category='COGS'           THEN amount ELSE 0 END) AS cogs,
         SUM(CASE WHEN category='Payroll'        THEN amount ELSE 0 END) AS payroll,
         SUM(CASE WHEN category='Infrastructure' THEN amount ELSE 0 END) AS infra,
         SUM(CASE WHEN category='G&A'            THEN amount ELSE 0 END) AS gna
  FROM exp_cat
  GROUP BY month
), joined AS (
  SELECT COALESCE(ci.month, p.month) AS month,
         COALESCE(ci.cash_in, 0)     AS cash_in,
         COALESCE(p.cogs, 0)         AS cogs,
         COALESCE(p.payroll, 0)      AS payroll,
         COALESCE(p.infra, 0)        AS infra,
         COALESCE(p.gna, 0)          AS gna
  FROM cash_in ci FULL OUTER JOIN pivot p ON p.month = ci.month
)
SELECT month,
       cash_in,
       cogs, payroll, infra, gna,
       ROUND((cash_in - cogs - payroll - infra - gna)::numeric, 2) AS operating_income,
       CASE WHEN cash_in IS NULL OR cash_in = 0 THEN NULL
            ELSE ROUND(((cash_in - cogs - payroll - infra - gna) / cash_in)::numeric, 4)
       END AS operating_margin
FROM joined
ORDER BY month DESC
LIMIT 24;
```
Line‑by‑line notes
- exp_cat: retains all categories; pivot step pinpoints those used in formula.
- FULL OUTER JOIN: ensures months present in either cash_in or expenses appear.
- operating_margin: numeric cast for precise division; guard against zero cash_in.

Exercise 2 — Project next 3 months net cash using seasonal naive
Prompt
- Forecast month t as average of the same month last year ± some smoothing. The prompt says “average of last 12 matching months (seasonal naive)”; a plain seasonal naive picks revenue from t−12. Here we average the last 12 historical months for robustness, but constrained to the same month number across years (i.e., t−12, t−24 ... if present). Given typical data horizons, use t−12 when deeper history isn’t available.

Implementation (uses t−12 only, and also shows simple trailing‑12 average as variant)
```sql
-- Step 1: Build historical monthly net cash
WITH pay_m AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY 1
), exp_m AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) AS cash_out
  FROM expenses
  GROUP BY 1
), hist AS (
  SELECT COALESCE(p.month, e.month) AS month,
         COALESCE(p.cash_in,0) - COALESCE(e.cash_out,0) AS net_cash
  FROM pay_m p FULL JOIN exp_m e ON e.month = p.month
), future AS (
  -- Next 3 calendar months after the latest historical month
  SELECT (MAX(month) + (n || ' month')::interval)::date AS month
  FROM hist, generate_series(1,3) AS g(n)
  GROUP BY n
), seasonal_naive AS (
  -- Forecast = value from 12 months ago
  SELECT f.month,
         h.net_cash AS fc_seasonal
  FROM future f
  LEFT JOIN hist h ON h.month = (f.month - interval '12 months')::date
), trailing12 AS (
  -- Variant: average of last 12 months overall (not same month-of-year)
  SELECT f.month,
         (
           SELECT AVG(h2.net_cash)::numeric
           FROM (
             SELECT net_cash
             FROM hist h2
             WHERE h2.month < f.month
             ORDER BY h2.month DESC
             LIMIT 12
           ) s
         ) AS fc_ma12
  FROM future f
)
SELECT f.month,
       ROUND(s.fc_seasonal,2) AS forecast_seasonal,
       ROUND(t.fc_ma12,2)     AS forecast_ma12
FROM future f
LEFT JOIN seasonal_naive s USING (month)
LEFT JOIN trailing12 t USING (month)
ORDER BY f.month;
```
Line‑by‑line notes
- hist: consolidate net cash per month for reuse.
- future: compute the next 3 month anchors.
- seasonal_naive: exact‑month lag of 12 months.
- trailing12: optional smoother that uses the last 12 historical months regardless of seasonality.

Tips
- Evaluate forecast error once actuals arrive using MAPE or MAE.
- If you have >24 months, consider combining seasonal_naive and MA(12) 50/50 for stability.
