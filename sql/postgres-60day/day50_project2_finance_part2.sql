-- Day 50: Project 2 - Financial/Operational Analysis (Part 2)
-- BEGINNER WORKFLOW — sql-50: Project2 Finance Part2
-- Guide: sql/postgres-60day/companion-guides/day50_project2_finance_part2.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-50/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: expenses, budgets.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-50 Exercise 1, read from `expenses`, and `budgets`. Build the answer toward `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-50 Exercise 1, expected output: one row per month and category, including periods found on only one side of the actual/budget comparison. The final columns are `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`. The final order is `month DESC, category`.
--    Verify: For sql-50 Exercise 1, project `month` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `month`, then assert the final `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
--    Hint ladder, rung 1: For sql-50 Exercise 1, run `actual`, `budget`, `joined`, and `compared` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 2. Build a report pivoting categories as columns and months as rows with variance.
--    Inputs: For sql-50 Exercise 2, read from `expenses`, and `budgets`. Build the answer toward `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-50 Exercise 2, expected output: one row per budget month and one variance column per known category. The final columns are `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`. The final order is `month DESC`.
--    Verify: For sql-50 Exercise 2, independently aggregate `expenses`, and `budgets` by `month`; require one output row for every distinct `month` tuple and compare `cogs`, `marketing`, and `payroll` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cogs`, `marketing`, and `payroll` for the existing `month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-50 Exercise 2, run `actual`, and `variance` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 3. Prediction: decide whether an absent budget row means zero budget or
--    unknown budget, and show how that policy changes COALESCE and variance.
--    Inputs: For sql-50 Exercise 3, read from `expenses`, and `budgets`. Build the answer toward `month`, `category`, `actual`, `budget`, and `comparison_status`; keep `month`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-50 Exercise 3, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `actual`, `budget`, and `comparison_status`. The final order is `month DESC, category`.
--    Verify: For sql-50 Exercise 3, project `month`, and `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `month`, and `category`, then assert the final `month`, `category`, `actual`, `budget`, and `comparison_status` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`, and `category`; verify the result gains exactly one row carrying that `month`, and `category` value.
--    Hint ladder, rung 1: For sql-50 Exercise 3, run `actual`, and `budget` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
-- 4. Construction: add YTD actual, budget, absolute variance, and variance
--    percentage per category using window frames.
--    Inputs: For sql-50 Exercise 4, read from `expenses`, `budgets`, and `month`. Build the answer toward `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`; keep `month`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-50 Exercise 4, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`. The final order is `month DESC, category`.
--    Verify: For sql-50 Exercise 4, choose one complete partition from `expenses`, `budgets`, and `month`; hand-calculate its first, middle, and final window values for `variance_ytd`, then verify output keys remain `month`, and `category`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-50 Exercise 4, run `monthly` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
-- 5. Debugging: repair a FULL JOIN whose month/category keys are coalesced only
--    in SELECT but not consistently reused in later windows.
--    Inputs: For sql-50 Exercise 5, complete the normalize joined keys before applying windows written analysis and support its claims with read-only evidence from `monthly.month`, and `monthly.category`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-50 Exercise 5, expected output: a completed the normalize joined keys before applying windows written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
--    Verify: For sql-50 Exercise 5, check the normalize joined keys before applying windows written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-50 Exercise 5, check the normalize joined keys before applying windows written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 6. Edge case: label new categories with actual spend but no budget separately
--    from overspend so stakeholders do not confuse missing plans with zero plans.
--    Inputs: For sql-50 Exercise 6, aggregate `expenses` and `budgets` independently to (`month`, `category`) before joining.
--    Expected result/shape: For sql-50 Exercise 6, expected output: one row per (`month`, `category`) found in either source, with `actual`, `budget`, and `status`.
--    Verify: For sql-50 Exercise 6, reconcile joined actual and budget totals to independent source totals. Test actual-only, budget-only, and zero-budget keys; a budget must never be multiplied by expense-row fanout.
--    Hint ladder, rung 1: Build unique `expense_monthly` and `budget_monthly` CTEs, then `FULL JOIN ... USING (month, category)`.

ROLLBACK;
