-- Day 51: Project 2 - Financial/Operational Analysis (Part 3)
-- BEGINNER WORKFLOW — sql-51: Project2 Finance Part3
-- Guide: sql/postgres-60day/companion-guides/day51_project2_finance_part3.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-51/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: payments, expenses, budgets.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Cash flow projections; budget vs actual with rolling periods
BEGIN;
SET search_path TO training, public;

-- Net cash flow per month = customer payments - expenses
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

-- Budget vs actual on expenses with rolling windows
WITH exp AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), j AS (
  SELECT COALESCE(b.category, e.category) AS category,
         COALESCE(b.month, e.month) AS month,
         COALESCE(b.budget,0) AS budget,
         COALESCE(e.actual,0) AS actual
  FROM bud b FULL JOIN exp e ON e.month = b.month AND e.category = b.category
)
SELECT category,
       month,
       actual,
       budget,
       ROUND(actual - budget, 2) AS variance,
       SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
       SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
FROM j
ORDER BY month DESC, category
LIMIT 120;

-- Exercises
-- 1. Compute operating margin: (cash_in - COGS - Payroll - Infrastructure - G&A) / cash_in.
--    Inputs: Use only the declared lesson objects (payments, expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Project next 3 months net cash as the average of last 12 matching months (seasonal naive).
--    Inputs: Use only the declared lesson objects (payments, expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: compare cash-basis payments with order revenue and explain why
--    timing differences make them unsuitable for one unlabeled margin metric.
--    Inputs: Use only the declared lesson objects (payments, expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 4. Construction: produce monthly beginning cash, inflows, outflows, net cash,
--    and ending cash with a running window.
--    Inputs: Use only the declared lesson objects (payments, expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: preserve months with expenses but no payments by replacing an
--    inner join with a calendar spine and left joins.
--    Inputs: Use only the declared lesson objects (payments, expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: keep operating margin NULL when cash_in is zero and provide a
--    separate status column explaining why the ratio is undefined.
--    Inputs: Use only the declared lesson objects (payments, expenses, budgets) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
