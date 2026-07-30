-- Day 50: Project 2 - Financial/Operational Analysis (Part 2)
-- Expense categorization, variance analysis vs budget
BEGIN;
SET search_path TO training, public;

-- Monthly actual expenses by category
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
       COALESCE(e.actual, 0) AS actual,
       ROUND(COALESCE(e.actual,0) - COALESCE(b.budget,0), 2) AS variance,
       ROUND((COALESCE(e.actual,0) - COALESCE(b.budget,0)) / NULLIF(b.budget,0), 4) AS variance_pct
FROM monthly_budget b
FULL OUTER JOIN monthly_exp e
  ON e.month = b.month AND e.category = b.category
ORDER BY month DESC, category
LIMIT 100;

-- Rolling 3-month actuals and budget
WITH monthly AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), joined AS (
  SELECT coalesce(b.category, m.category) AS category,
         coalesce(b.month, m.month) AS month,
         COALESCE(b.budget, 0) AS budget,
         COALESCE(m.actual, 0) AS actual
  FROM bud b FULL JOIN monthly m ON m.month = b.month AND m.category = b.category
)
SELECT category,
       month,
       SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
       SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
FROM joined
ORDER BY month DESC, category
LIMIT 100;

-- Exercises
-- 1. Compute YoY variance and highlight categories with >15% overspend.
-- 2. Build a report pivoting categories as columns and months as rows with variance.
-- 3. Prediction: decide whether an absent budget row means zero budget or
--    unknown budget, and show how that policy changes COALESCE and variance.
-- 4. Construction: add YTD actual, budget, absolute variance, and variance
--    percentage per category using window frames.
-- 5. Debugging: repair a FULL JOIN whose month/category keys are coalesced only
--    in SELECT but not consistently reused in later windows.
-- 6. Edge case: label new categories with actual spend but no budget separately
--    from overspend so stakeholders do not confuse missing plans with zero plans.

ROLLBACK;
