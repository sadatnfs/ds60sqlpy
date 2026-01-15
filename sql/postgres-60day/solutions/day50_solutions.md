# Day 50 — Solutions (Project 2: Finance/Operations, Part 2 — Expense/Budget Variance)

We compute monthly actual vs budget, rolling totals, and now tackle YoY variance and a pivoted report.

Reference join (annotated)
```sql
WITH monthly_exp AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), monthly_budget AS (
  SELECT period AS month,
         category,
         SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
)
SELECT coalesce(b.category, e.category) AS category,
       coalesce(b.month, e.month) AS month,
       COALESCE(b.budget, 0) AS budget,
       COALESCE(e.actual, 0) AS actual
FROM monthly_budget b
FULL OUTER JOIN monthly_exp e
  ON e.month = b.month AND e.category = b.category
ORDER BY month DESC, category
LIMIT 100;
```

Exercise 1 — Compute YoY variance and highlight categories with > 15% overspend
Goal
- For each category‑month, compute actual − budget and (actual − budget) / budget. Compare to prior year.

Solution
```sql
WITH exp AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT date_trunc('month', period)::date AS month,
         category,
         SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), joined AS (
  SELECT COALESCE(b.category, e.category) AS category,
         COALESCE(b.month, e.month) AS month,
         COALESCE(b.budget, 0) AS budget,
         COALESCE(e.actual, 0) AS actual
  FROM bud b
  FULL JOIN exp e ON e.month = b.month AND e.category = b.category
), with_yoy AS (
  SELECT category,
         month,
         actual,
         budget,
         ROUND(actual - budget, 2) AS variance,
         ROUND((actual - budget) / NULLIF(budget, 0), 4) AS variance_pct,
         LAG(actual, 12) OVER (PARTITION BY category ORDER BY month) AS actual_prev_year,
         LAG(budget, 12) OVER (PARTITION BY category ORDER BY month) AS budget_prev_year
  FROM joined
)
SELECT category,
       month,
       actual,
       budget,
       variance,
       variance_pct,
       CASE WHEN variance_pct IS NOT NULL AND variance_pct > 0.15 THEN 'overspend>15%' ELSE 'ok' END AS flag
FROM with_yoy
ORDER BY month DESC, category
LIMIT 120;
```
Line‑by‑line notes
- FULL JOIN ensures visibility when either actual or budget is missing.
- variance_pct uses NULLIF to avoid divide‑by‑zero when budget is 0.
- LAG(...) provides prior‑year comparators if you wish to show YoY deltas.

Exercise 2 — Pivot categories as columns and months as rows with variance
Options
- Dynamic pivot: use tablefunc.crosstab (requires CREATE EXTENSION tablefunc).
- Static pivot for a small, known set of categories using conditional aggregates.

A) Static pivot with conditional aggregates
```sql
WITH exp AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT date_trunc('month', period)::date AS month,
         category,
         SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), j AS (
  SELECT COALESCE(b.category, e.category) AS category,
         COALESCE(b.month, e.month) AS month,
         COALESCE(b.budget, 0) AS budget,
         COALESCE(e.actual, 0) AS actual
  FROM bud b FULL JOIN exp e ON e.month = b.month AND e.category = b.category
)
SELECT month,
       ROUND(SUM(CASE WHEN category='COGS'          THEN actual - budget END),2) AS var_cogs,
       ROUND(SUM(CASE WHEN category='Payroll'       THEN actual - budget END),2) AS var_payroll,
       ROUND(SUM(CASE WHEN category='Infrastructure'THEN actual - budget END),2) AS var_infra,
       ROUND(SUM(CASE WHEN category='G&A'           THEN actual - budget END),2) AS var_gna
FROM j
GROUP BY month
ORDER BY month DESC
LIMIT 24;
```
Note
- Edit the WHEN clauses to match your organization’s category names.

B) Dynamic pivot using crosstab (optional)
```sql
-- Enable once per database (requires superuser privileges in some setups)
-- CREATE EXTENSION IF NOT EXISTS tablefunc;

WITH base AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT date_trunc('month', period)::date AS month,
         category,
         SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), diff AS (
  SELECT COALESCE(b.month, e.month) AS month,
         COALESCE(b.category, e.category) AS category,
         COALESCE(e.actual,0) - COALESCE(b.budget,0) AS variance
  FROM bud b FULL JOIN base e ON e.month=b.month AND e.category=b.category
)
SELECT *
FROM crosstab(
  $$
  SELECT to_char(month, 'YYYY-MM') AS row_name,
         category AS category,
         variance AS value
  FROM diff
  ORDER BY 1,2
  $$
) AS ct(row_name text, "COGS" numeric, "Payroll" numeric, "Infrastructure" numeric, "G&A" numeric)
ORDER BY row_name DESC
LIMIT 24;
```
Notes
- You must enumerate output columns/types in AS ct(...). Add or change categories as needed.
