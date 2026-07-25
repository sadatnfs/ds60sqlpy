# Day 50 Solutions — Expense and Budget Variance

This day adds year-over-year context, a greater-than-15% overspend flag, and a
static monthly pivot using the categories present in the course seed. See
[`day50_solutions.sql`](day50_solutions.sql).

## Exercise 1 — YoY and budget variance

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY date_trunc('month', expense_date), category
), budget AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY period, category
), joined AS (
  SELECT COALESCE(a.month, b.month) AS month,
         COALESCE(a.category, b.category) AS category,
         COALESCE(a.actual, 0) AS actual,
         COALESCE(b.budget, 0) AS budget
  FROM actual a
  FULL OUTER JOIN budget b USING (month, category)
), compared AS (
  SELECT *,
         LAG(actual, 12) OVER (
           PARTITION BY category ORDER BY month
         ) AS prior_year_actual
  FROM joined
)
SELECT month,
       category,
       ROUND(actual, 2) AS actual,
       ROUND(prior_year_actual, 2) AS prior_year_actual,
       ROUND((actual - prior_year_actual) / NULLIF(prior_year_actual, 0), 4)
         AS year_over_year_variance_pct,
       ROUND((actual - budget) / NULLIF(budget, 0), 4) AS budget_variance_pct,
       actual > budget * 1.15 AS overspent_by_more_than_15_pct
FROM compared
ORDER BY month DESC, category;
```

Expected grain: one row per month and category, including periods found on only
one side of the actual/budget comparison.

## Exercise 2 — Monthly variance pivot

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY date_trunc('month', expense_date), category
), variance AS (
  SELECT b.period AS month,
         b.category,
         COALESCE(a.actual, 0) - b.amount AS variance
  FROM budgets b
  LEFT JOIN actual a
    ON a.month = b.period
   AND a.category = b.category
)
SELECT month,
       ROUND(SUM(variance) FILTER (WHERE category = 'COGS'), 2) AS cogs,
       ROUND(SUM(variance) FILTER (WHERE category = 'Marketing'), 2) AS marketing,
       ROUND(SUM(variance) FILTER (WHERE category = 'Payroll'), 2) AS payroll,
       ROUND(SUM(variance) FILTER (WHERE category = 'Infrastructure'), 2)
         AS infrastructure,
       ROUND(SUM(variance) FILTER (WHERE category = 'G&A'), 2) AS general_admin
FROM variance
GROUP BY month
ORDER BY month DESC;
```

Expected shape: one row per budget month and one variance column per known
category.

## Reasoning, safety, and pitfalls

- Positive variance means actual spending exceeded budget because the formula
  is `actual - budget`.
- `LAG(..., 12)` assumes every category has one row for every month. Build a
  category/month spine when periods can be missing.
- The pivot is intentionally static. New categories require a new column or a
  long-form BI result.
- Treat zero or absent budgets explicitly; `NULL` percentage is safer than a
  fabricated infinite or zero rate.
