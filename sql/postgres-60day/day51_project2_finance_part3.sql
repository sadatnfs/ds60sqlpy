-- Day 51: Project 2 - Financial/Operational Analysis (Part 3)
-- BEGINNER WORKFLOW - sql-51: Project 2 Finance Part 3
-- Guide: sql/postgres-60day/companion-guides/day51_project2_finance_part3.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-51.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    date_trunc('month', payment_date)::date AS month,
    SUM(amount) AS cash_in
  FROM
    payments
  GROUP BY
    1
),
exp_m AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    SUM(amount) AS cash_out
  FROM
    expenses
  GROUP BY
    1
),
joined AS (
  SELECT
    COALESCE(p.month, e.month) AS month,
    COALESCE(p.cash_in, 0) AS cash_in,
    COALESCE(e.cash_out, 0) AS cash_out
  FROM
    pay_m p
    FULL OUTER JOIN exp_m e ON e.month = p.month
)
SELECT
  month,
  ROUND(cash_in - cash_out, 2) AS net_cash_flow,
  SUM(ROUND(cash_in - cash_out, 2)) OVER (ORDER BY month) AS cumulative_cash
FROM
  joined
ORDER BY
  month DESC
LIMIT 36;

-- Budget vs actual on expenses with rolling windows
WITH exp AS (
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
j AS (
  SELECT
    COALESCE(b.category, e.category) AS category,
    COALESCE(b.month, e.month) AS month,
    COALESCE(b.budget, 0) AS budget,
    COALESCE(e.actual, 0) AS actual
  FROM
    bud b
    FULL JOIN exp e ON e.month = b.month
      AND e.category = b.category
)
  SELECT
    category,
    month,
    actual,
    budget,
    ROUND(actual - budget, 2) AS variance,
    SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
    SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
  FROM
    j
  ORDER BY
    month DESC,
    category
  LIMIT 120;

-- Exercises
-- 1. Compute operating margin: (cash_in - COGS - Payroll - Infrastructure - G&A) / cash_in.
--    Inputs: For sql-51 Exercise 1, sum `payments.amount` by payment month in `cash`, sum `expenses.amount` by expense month for the four operating categories (COGS, Payroll, Infrastructure, G&A, not Marketing) in `operating_expense`, and `FULL OUTER JOIN` the two `USING (month)`.
--    Expected result/shape: For sql-51 Exercise 1, expected output: 46 rows, one per month appearing in either payments or operating expenses (2023-02-01 to 2026-11-01). The final columns are `month`, `cash_in`, `operating_cost`, and `operating_margin`. The final order is `month DESC`.
--    Verify: For sql-51 Exercise 1, confirm 46 distinct months, and that the 21 months before expenses begin (2023-02 to 2024-10) show `operating_cost` 0.00 and a margin of exactly 1.0000. Recompute the top row: 2026-11 has 76,045.60 cash in and 1,362,737.02 operating cost (that month's 1,712,274.61 of expenses minus 349,537.59 of Marketing), so the margin is -16.9200. Then, in a transaction, delete the 77 payments from 2025-03: that month stays with `cash_in` 0.00, cost 1,747,681.27, and a `NULL` margin instead of a division error; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-51 Exercise 1, run `cash` (46 rows) and `operating_expense` (25 rows, from 2024-11) one at a time, then count the joined months; 46 means no expense month is missing a payment month.
-- 2. Project next 3 months net cash as the average of last 12 matching months (seasonal naive).
--    Inputs: For sql-51 Exercise 2, build monthly net cash in `historical` from a `FULL OUTER JOIN` of payment and expense totals, generate the next three calendar months after `CURRENT_DATE` in `future`, and `LEFT JOIN` each one to the earlier months with the same calendar month number.
--    Expected result/shape: For sql-51 Exercise 2, expected output: exactly three rows, one per future `forecast_month` (2026-12-01, 2027-01-01, and 2027-02-01 when run in November 2026). The count column shows how much history supports each estimate; a `NULL` projection means there was none. The final columns are `forecast_month`, `projected_net_cash`, and `matching_historical_months`. The final order is `forecast_month`.
--    Verify: For sql-51 Exercise 2, run in November 2026, confirm the counts 3, 3, and 4, then recompute the first row by hand: the Decembers 2023, 2024, and 2025 have net cash 11,201.99, -2,102,060.09, and -2,062,784.20, whose mean is -1,384,547.43. February averages four months (2023 to 2026), so it is -941,106.45. Then, in a transaction, insert a 100.00 payment dated 2026-12-02 and rerun: the December projection does not change, because `h.month < f.forecast_month` keeps a month out of its own forecast; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-51 Exercise 2, run `historical` (46 rows) and `future` (3 rows) separately, then run the join without `GROUP BY` and confirm it returns 10 rows, 3 + 3 + 4 matched history months.
-- 3. Prediction: compare cash-basis payments with order revenue and explain why
--    timing differences make them unsuitable for one unlabeled margin metric.
--    Inputs: For sql-51 Exercise 3, read from `orders` and `payments`; sum `total_amount` by order month as `booked_order_revenue` and left join the payments summed by payment month as `cash_received`, using `COALESCE(..., 0)` for months without payments.
--    Expected result/shape: For sql-51 Exercise 3, expected output: one row per order month, ordered by `month`; `cash_received` is lower than `booked_order_revenue` in most months because unpaid orders bring no cash. The final columns are `month`, `booked_order_revenue`, and `cash_received`. The final order is `month`.
--    Verify: For sql-51 Exercise 3, confirm 46 unique months, that `SUM(booked_order_revenue)` is 2,355,646.89 and `SUM(cash_received)` is 1,831,900.81 (the same as `SELECT SUM(amount) FROM payments`), and that cash is lower than bookings in 45 months and equal only in 2023-02 (1,203.26). Then, in a transaction, insert a 100.00 payment dated 2026-12-02: the result keeps 46 rows and the same cash total, now 100.00 short of `payments`, because the query starts from order months and drops a payment-only month; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-51 Exercise 3, aggregate `orders` and `payments` to month grain separately and compare their row counts before you join them.
-- 4. Construction: produce monthly beginning cash, inflows, outflows, net cash,
--    and ending cash with a running window.
--    Inputs: For sql-51 Exercise 4, stack the 3,836 payments (as `cash_in`) and the 10,000 expenses (as `cash_out`) with `UNION ALL`, group them to monthly totals in `flow`, add a running `SUM(cash_in - cash_out) OVER (ORDER BY month)` in `balances`, and read the previous ending balance with `LAG(ending_cash, 1, 0)`.
--    Expected result/shape: For sql-51 Exercise 4, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, starting from a declared opening balance of 0. The final columns are `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`. The final order is `month`.
--    Verify: For sql-51 Exercise 4, hand-check the first two rows: 2023-02 begins at 0 and ends at 1,203.26, and 2023-03 begins at 1,203.26 and ends at 2,350.50. Confirm with `LAG` that every `beginning_cash` equals the previous row's `ending_cash`, and that the last `ending_cash`, -48,651,949.19, equals 1,831,900.81 of payments minus 50,483,850.00 of expenses. There is one window with no `PARTITION BY`, so nothing resets; in a transaction, delete the 77 payments from 2025-03 and confirm that month keeps its row with `cash_in` 0 and every later ending balance drops by 38,915.28; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-51 Exercise 4, run `flow` (46 rows) and check that its `cash_in` and `cash_out` columns add up to the two table totals, then run `balances` and compare the last `ending_cash` with their difference.
-- 5. Debugging: preserve months with expenses but no payments by replacing an
--    inner join with a calendar spine and left joins.
--    Inputs: For sql-51 Exercise 5, find the first and last dates across `payments` and `expenses` in `bounds`, expand them into calendar months with `generate_series` in `months`, and `LEFT JOIN` the monthly totals `cash` and `costs` to that spine.
--    Expected result/shape: For sql-51 Exercise 5, expected output: 46 rows, one per calendar `month` from 2023-02-01 to 2026-11-01, with 0 where a side has no rows. The final columns are `month`, `cash_in`, and `cash_out`. The final order is `month`.
--    Verify: For sql-51 Exercise 5, confirm 46 months and show the bug being repaired: an inner join of `cash` and `costs` returns only 25 rows (2024-11 to 2026-11), losing the 21 months that have payments but no expenses. Then, in a transaction, delete the 77 payments from 2025-03 and rerun: the spine still returns 46 rows, with 2025-03 showing `cash_in` 0 and `cash_out` 2,154,691.38; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-51 Exercise 5, run `bounds` (one row: the first payment in February 2023 and the latest date, 2026-11-25 on our load), then `months` (46 rows), and only then join `cash` (46 rows) and `costs` (25 rows) to it.
-- 6. Edge case: keep operating margin NULL when cash_in is zero and provide a
--    separate status column explaining why the ratio is undefined.
--    Inputs: For sql-51 Exercise 6, use the two-row `VALUES` list `toy` (2026-01 with 0 cash in and 100 cost; 2026-02 with 500 in and 300 cost) instead of the course tables, divide through `NULLIF(cash_in, 0)`, and label the result with a `CASE`.
--    Expected result/shape: For sql-51 Exercise 6, expected output: 2 rows, one per `toy` month: 2026-01-01 with a `NULL` margin and `undefined: zero cash in`, and 2026-02-01 with 0.4 and `defined`. The final columns are `month`, `operating_margin`, and `margin_status`.
--    Verify: For sql-51 Exercise 6, confirm the two rows above and that the first raises no division-by-zero error. Then add a third `toy` row, `(date '2026-03-01', NULL, 100)`: its margin is also `NULL`, but the status says `defined`, because `cash_in = 0` is unknown for a `NULL` and falls to `ELSE`, so a `WHEN cash_in IS NULL` branch is needed to tell missing cash from zero cash.
--    Hint ladder, rung 1: For sql-51 Exercise 6, select `month`, `cash_in`, and `NULLIF(cash_in, 0)` from `toy` before you add the margin and the status.
ROLLBACK;
