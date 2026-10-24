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
--    Inputs: For sql-51 Exercise 1, read from `payments`, and `expenses`. Build the answer toward `month`, `cash_in`, `operating_cost`, and `operating_margin`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-51 Exercise 1, expected output: one row per month appearing in either payments or operating expenses. The final columns are `month`, `cash_in`, `operating_cost`, and `operating_margin`. The final order is `month DESC`.
--    Verify: For sql-51 Exercise 1, project `month` plus the raw source columns from `payments`, and `expenses` at each join stage; record row count and distinct `month`, then assert the final `month`, `cash_in`, `operating_cost`, and `operating_margin` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
--    Hint ladder, rung 1: For sql-51 Exercise 1, run `cash`, and `operating_expense` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 2. Project next 3 months net cash as the average of last 12 matching months (seasonal naive).
--    Inputs: For sql-51 Exercise 2, read from `payments`, `expenses`, `h.month`, and `f.forecast_month`. Build the answer toward `forecast_month`, `projected_net_cash`, and `matching_historical_months`; keep `forecast_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-51 Exercise 2, expected output: exactly three future month rows. The count column shows how much history supports each estimate; a `NULL` projection means there was none. The final columns are `forecast_month`, `projected_net_cash`, and `matching_historical_months`. The final order is `f.forecast_month`.
--    Verify: For sql-51 Exercise 2, independently aggregate `payments`, `expenses`, `h.month`, and `f.forecast_month` by `forecast_month`; require one output row for every distinct `forecast_month` tuple and compare `projected_net_cash`, and `matching_historical_months` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `projected_net_cash`, and `matching_historical_months` for the existing `forecast_month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-51 Exercise 2, run `cash`, `expense`, `historical`, and `future` one at a time. Record each CTE's row count and `forecast_month` uniqueness before the next stage uses it.
-- 3. Prediction: compare cash-basis payments with order revenue and explain why
--    timing differences make them unsuitable for one unlabeled margin metric.
--    Inputs: For sql-51 Exercise 3, read from `orders`, and `payments`. Build the answer toward `month`, `booked_order_revenue`, and `cash_received`; keep `cash_received` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-51 Exercise 3, expected output: one row per `cash_received`. The final columns are `month`, `booked_order_revenue`, and `cash_received`. The final order is `month`.
--    Verify: For sql-51 Exercise 3, independently aggregate `orders`, and `payments` by `cash_received`; require one output row for every distinct `cash_received` tuple and compare `booked_order_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `booked_order_revenue` for the existing `cash_received` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-51 Exercise 3, start with the first relation in `orders`, and `payments`; after each join, record total rows and distinct `cash_received` so the exact fanout or loss is visible.
-- 4. Construction: produce monthly beginning cash, inflows, outflows, net cash,
--    and ending cash with a running window.
--    Inputs: For sql-51 Exercise 4, read from `payments`, and `expenses`. Build the answer toward `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-51 Exercise 4, expected output: one row per `month`. The final columns are `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`. The final order is `month`.
--    Verify: For sql-51 Exercise 4, choose one complete partition from `payments`, and `expenses`; hand-calculate its first, middle, and final window values for `beginning_cash`, `cash_in`, and `cash_out`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-51 Exercise 4, run `flow`, and `balances` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 5. Debugging: preserve months with expenses but no payments by replacing an
--    inner join with a calendar spine and left joins.
--    Inputs: For sql-51 Exercise 5, read from `payments`, and `expenses`. Build the answer toward `month`, `cash_in`, and `cash_out`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-51 Exercise 5, expected output: one row per `month`. The final columns are `month`, `cash_in`, and `cash_out`. The final order is `m.month`.
--    Verify: For sql-51 Exercise 5, project `month` plus the raw source columns from `payments`, and `expenses` at each join stage; record row count and distinct `month`, then assert the final `month`, `cash_in`, and `cash_out` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
--    Hint ladder, rung 1: For sql-51 Exercise 5, run `bounds`, `months`, `cash`, and `costs` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 6. Edge case: keep operating margin NULL when cash_in is zero and provide a
--    separate status column explaining why the ratio is undefined.
--    Inputs: For sql-51 Exercise 6, read from `toy`. Build the answer toward `month`, `operating_margin`, and `margin_status`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-51 Exercise 6, expected output: one row per `month`. The final columns are `month`, `operating_margin`, and `margin_status`.
--    Verify: For sql-51 Exercise 6, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `operating_margin`, and `margin_status` against `toy`. Repeat with `NULL` in `month`, and `operating_margin` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-51 Exercise 6, select `month` from `toy` before adding derived columns.

ROLLBACK;
