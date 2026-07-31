-- Day 50 solutions: expense and budget variance
-- SOLUTION READING MAP — sql-50: Project2 Finance Part2
-- Explanation: sql/postgres-60day/solutions/day50_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day50_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
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

-- Exercise 3: preserve missingness before display. A NULL budget is unknown,
-- not automatically a policy-approved zero.
WITH actual AS (
  SELECT date_trunc('month', expense_date)::date AS month, category,
         SUM(amount) AS actual
  FROM expenses GROUP BY 1, 2
), budget AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets GROUP BY 1, 2
)
SELECT COALESCE(a.month, b.month) AS month,
       COALESCE(a.category, b.category) AS category,
       a.actual, b.budget,
       CASE WHEN b.category IS NULL THEN 'missing budget'
            WHEN a.category IS NULL THEN 'no actual'
            ELSE 'comparable' END AS comparison_status
FROM actual a
FULL JOIN budget b USING (month, category)
ORDER BY month DESC, category;

-- Exercise 4: first normalize joined keys/values, then apply YTD windows to the
-- single canonical month/category columns.
WITH monthly AS (
  SELECT COALESCE(a.month, b.month) AS month,
         COALESCE(a.category, b.category) AS category,
         a.actual, b.budget
  FROM (
    SELECT date_trunc('month', expense_date)::date AS month, category,
           SUM(amount) AS actual
    FROM expenses GROUP BY 1, 2
  ) a
  FULL JOIN (
    SELECT period AS month, category, SUM(amount) AS budget
    FROM budgets GROUP BY 1, 2
  ) b USING (month, category)
)
SELECT month, category,
       SUM(actual) OVER (PARTITION BY category, EXTRACT(year FROM month)
                         ORDER BY month) AS actual_ytd,
       SUM(budget) OVER (PARTITION BY category, EXTRACT(year FROM month)
                         ORDER BY month) AS budget_ytd,
       SUM(actual - budget) OVER (
         PARTITION BY category, EXTRACT(year FROM month) ORDER BY month
       ) AS variance_ytd
FROM monthly
ORDER BY month DESC, category;

-- Exercise 5 is embodied by the canonical `monthly` CTE above: every later
-- window references its coalesced keys, never one nullable join side.

-- Exercise 6: classify missing plans before applying an overspend threshold.
WITH totals AS (
  SELECT e.category, SUM(e.amount) AS actual, SUM(b.amount) AS budget
  FROM expenses e
  FULL JOIN budgets b
    ON b.category = e.category
   AND b.period = date_trunc('month', e.expense_date)::date
  GROUP BY e.category
)
SELECT category, actual, budget,
       CASE WHEN budget IS NULL THEN 'unbudgeted spend'
            WHEN budget = 0 THEN 'zero budget'
            WHEN actual > budget THEN 'overspend'
            ELSE 'within budget' END AS status
FROM totals
ORDER BY category;
