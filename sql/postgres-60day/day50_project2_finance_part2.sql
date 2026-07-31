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
--    Inputs: Use only the declared lesson objects (expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Build a report pivoting categories as columns and months as rows with variance.
--    Inputs: Use only the declared lesson objects (expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: decide whether an absent budget row means zero budget or
--    unknown budget, and show how that policy changes COALESCE and variance.
--    Inputs: Use only the declared lesson objects (expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: add YTD actual, budget, absolute variance, and variance
--    percentage per category using window frames.
--    Inputs: Use only the declared lesson objects (expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: repair a FULL JOIN whose month/category keys are coalesced only
--    in SELECT but not consistently reused in later windows.
--    Inputs: Use only the declared lesson objects (expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: label new categories with actual spend but no budget separately
--    from overspend so stakeholders do not confuse missing plans with zero plans.
--    Inputs: Use only the declared lesson objects (expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
