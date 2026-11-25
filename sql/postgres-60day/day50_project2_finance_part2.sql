-- Day 50: Project 2 - Financial/Operational Analysis (Part 2)
-- BEGINNER WORKFLOW - sql-50: Project 2 Finance Part 2
-- Guide: sql/postgres-60day/companion-guides/day50_project2_finance_part2.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-50.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    1,
    2
),
monthly_budget AS (
  SELECT
    period AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  GROUP BY
    1,
    2
)
SELECT
  coalesce(b.category, e.category) AS category,
  coalesce(b.month, e.month) AS month,
  COALESCE(b.budget, 0) AS budget,
  COALESCE(e.actual, 0) AS actual,
  ROUND(COALESCE(e.actual, 0) - COALESCE(b.budget, 0), 2) AS variance,
  ROUND((COALESCE(e.actual, 0) - COALESCE(b.budget, 0)) / NULLIF (b.budget, 0), 4) AS variance_pct
FROM
  monthly_budget b
  FULL OUTER JOIN monthly_exp e ON e.month = b.month
  AND e.category = b.category
ORDER BY
  month DESC,
  category
LIMIT 100;

-- Rolling 3-month actuals and budget
WITH monthly AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    1,
    2
),
bud AS (
  SELECT
    period AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  GROUP BY
    1,
    2
),
joined AS (
  SELECT
    coalesce(b.category, m.category) AS category,
    coalesce(b.month, m.month) AS month,
    COALESCE(b.budget, 0) AS budget,
    COALESCE(m.actual, 0) AS actual
  FROM
    bud b
    FULL JOIN monthly m ON m.month = b.month
      AND m.category = b.category
)
  SELECT
    category,
    month,
    SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
    SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
  FROM
    joined
  ORDER BY
    month DESC,
    category
  LIMIT 100;

-- Exercises
-- 1. Compute YoY variance and highlight categories with >15% overspend.
--    Inputs: For sql-50 Exercise 1, sum the 10,000 `expenses` rows by `date_trunc('month', expense_date)` and `category` in `actual`, sum the 125 `budgets` rows by `period` and `category` in `budget`, `FULL OUTER JOIN` them `USING (month, category)` with missing amounts set to 0, and take `LAG(actual, 12)` within each category for the prior year.
--    Expected result/shape: For sql-50 Exercise 1, expected output: 125 rows, one per month and category (25 months from 2024-11-01 to 2026-11-01 times 5 categories), including any period found on only one side of the actual/budget comparison. The final columns are `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`. The final order is `month DESC, category`.
--    Verify: For sql-50 Exercise 1, confirm 125 distinct (`month`, `category`) pairs, 71 rows with the flag true, and 65 rows with a `prior_year_actual` (the first 12 months of each category have none). Recompute the top row by hand: 2026-11 COGS spent 335,159.36 against 398,788.03 in 2025-11 (-0.1596) and a 576,000.00 budget (-0.4181), so the flag is false. Then, in a transaction, insert a `Travel` expense of 1,000 on 2026-11-15: a 126th row appears with `budget_variance_pct` `NULL` but the flag true, because the missing budget became 0; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-50 Exercise 1, run `actual` (125 rows), `budget` (125 rows), `joined`, and `compared` one at a time, and check that `joined` still has 125 rows before any window runs, so the 12-row `LAG` lands on the same month a year earlier.
-- 2. Build a report pivoting categories as columns and months as rows with variance.
--    Inputs: For sql-50 Exercise 2, sum `expenses` by month and category in `actual`, start `variance` from the 125 `budgets` rows with a `LEFT JOIN` to `actual`, compute `actual - budget` per row, and spread it into one column per category with `SUM(variance) FILTER (WHERE category = ...)`.
--    Expected result/shape: For sql-50 Exercise 2, expected output: 25 rows, one per budget month from 2026-11-01 down to 2024-11-01, with one variance column per known category. The final columns are `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`. The final order is `month DESC`.
--    Verify: For sql-50 Exercise 2, confirm 25 distinct months and that the five columns of each row add up to that month's total spend minus its total budget: for 2026-11, -240,840.64 + 135,537.59 - 342,178.22 + 41,001.63 + 175,254.25 = -231,225.39, the same as `SUM(expenses.amount) - SUM(budgets.amount)` for that month. Then, in a transaction, insert a `Travel` expense of 1,000 on 2026-11-15 and rerun: the pivot is unchanged at 25 rows, so the November reconciliation is now off by exactly 1,000.00, because spending without a budget row never enters `variance`; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-50 Exercise 2, run `actual` (125 rows) and then `variance` (125 rows, one per budget row) before you pivot, and check that every `category` value in `variance` is one of the five names your `FILTER` clauses list.
-- 3. Prediction: decide whether an absent budget row means zero budget or
--    unknown budget, and show how that policy changes COALESCE and variance.
--    Inputs: For sql-50 Exercise 3, build the same 125-row `actual` and `budget` summaries, `FULL JOIN` them `USING (month, category)`, keep `a.actual` and `b.budget` without `COALESCE`, and label each row from which side's key is `NULL`.
--    Expected result/shape: For sql-50 Exercise 3, expected output: 125 rows, one per `month` and `category`, every one labeled `comparable` on the course data. The final columns are `month`, `category`, `actual`, `budget`, and `comparison_status`. The final order is `month DESC, category`.
--    Verify: For sql-50 Exercise 3, confirm 125 rows, all `comparable`, with no `NULL` in `actual` or `budget`. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01: a 126th row appears at the top labeled `no actual` with `actual` shown as `NULL`, not 0. Roll back and insert a `Travel` expense of 1,000 on 2026-11-15 instead: its row is labeled `missing budget` with `budget` `NULL`; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-50 Exercise 3, run `actual` and `budget` separately (125 rows each), then run the join with `a.category` and `b.category` both selected so you can see which side would be `NULL` on an unmatched row.
-- 4. Construction: add YTD actual, budget, absolute variance, and variance
--    percentage per category using window frames.
--    Inputs: For sql-50 Exercise 4, build `monthly` from the 125-row expense and budget summaries with a `FULL JOIN` and coalesced `month` and `category`, then run three running `SUM` windows partitioned by `category` and `EXTRACT(year FROM month)` and ordered by `month`.
--    Expected result/shape: For sql-50 Exercise 4, expected output: 125 rows, one per `month` and `category`, in 15 partitions (5 categories times the years 2024, 2025, and 2026). The final columns are `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`. The final order is `month DESC, category`.
--    Verify: For sql-50 Exercise 4, hand-check COGS: the 2024 partition has only two rows, so 2024-11 shows 72,384.36 against 654,000.00 and 2024-12 shows 545,878.91 against 1,266,000.00; 2025-01 restarts at 430,421.17 against 570,000.00; and 2026-11 shows 4,508,769.63 against 6,600,000.00, a `variance_ytd` of -2,091,230.37, equal to summing that year's COGS rows directly. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01: that row shows `budget_ytd` 7,200,000.00 but `actual_ytd` and `variance_ytd` unchanged from November, because `actual - budget` is `NULL` on a one-sided row; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-50 Exercise 4, run `monthly` alone (125 rows), then list the COGS rows for 2024 and 2025-01 with all three windows to see where the total restarts before you read the latest months.
-- 5. Debugging: repair a FULL JOIN whose month/category keys are coalesced only
--    in SELECT but not consistently reused in later windows.
--    Inputs: For sql-50 Exercise 5, write a short note on why every window and filter must use the coalesced keys `monthly.month` and `monthly.category` from Exercise 4 instead of `a.month` or `a.category` from one side of the `FULL JOIN`; Exercise 4's `monthly` CTE is the repaired query, so cite its results as evidence and mark anything you did not run as an assumption.
--    Expected result/shape: For sql-50 Exercise 5, expected output: a written note with six fields, `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`, whose `evidence` quotes the 125 rows of `monthly` with zero `NULL` months and zero `NULL` categories.
--    Verify: For sql-50 Exercise 5, show that the broken and repaired forms agree today: partitioning by `a.category, EXTRACT(year FROM a.month)` returns the same 125 rows and totals as Exercise 4, because every key matches. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01 and run both: the repaired form gives that row a `budget_ytd` of 7,200,000.00, while the broken form puts it in a `NULL` partition with 600,000.00, so it never joins the COGS total; `ROLLBACK`, and name the `fallback` and `rollback_limit` entries that cover this case.
--    Hint ladder, rung 1: For sql-50 Exercise 5, rerun Exercise 4's `monthly` and count its rows and its `NULL` keys first, then write the broken version with `a.category` in `PARTITION BY` so you can compare the two on the same data.
-- 6. Edge case: label new categories with actual spend but no budget separately
--    from overspend so stakeholders do not confuse missing plans with zero plans.
--    Inputs: For sql-50 Exercise 6, aggregate `expenses` and `budgets` independently to (`month`, `category`) before joining.
--    Expected result/shape: For sql-50 Exercise 6, expected output: 125 rows, one per (`month`, `category`) found in either source, with `actual`, `budget`, and `status`, ordered by `month, category` (oldest first); 72 rows are `overspend` and 53 are `within budget`.
--    Verify: For sql-50 Exercise 6, reconcile the totals: `actual` sums to 50,483,850.00 and `budget` to 51,198,000.00, the same as `SUM(amount)` on each source table, while joining raw `expenses` to `budgets` instead sums the budget to 4,098,331,000.00 because each plan repeats once per expense (13 to 96 times). Then, in a transaction, test each missing case: a `Travel` expense on 2026-11-15 gives `unbudgeted spend`, a COGS budget for 2026-12-01 gives `budget without spend`, and setting the 2026-11 G&A budget to 0 gives `zero budget`; `ROLLBACK` after each.
--    Hint ladder, rung 1: For sql-50 Exercise 6, build `expense_monthly` from the 10,000 `expenses` rows and `budget_monthly` from the 125 `budgets` rows, check that each returns 125 unique (`month`, `category`) rows, then `FULL JOIN ... USING (month, category)`.
ROLLBACK;
