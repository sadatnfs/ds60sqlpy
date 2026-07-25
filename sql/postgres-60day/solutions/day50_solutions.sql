-- Day 50 solutions: expense and budget variance
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
-- Exercise 1: year-over-year change plus the requested >15% budget flag.
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

-- Exercise 2: pivot monthly actual-minus-budget variance by category.
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
