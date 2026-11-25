# Day 51: Finance/Operations Project, Part 3: Cash Flow

## How to run this lesson

Open **sql-51** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit
`.learning/sql/sql-51/lesson/workspace/sql/postgres-60day/day51_project2_finance_part3.sql`.
The script reads `payments`, `expenses` and `budgets` in
`advanced_sql_training` between `BEGIN` and `ROLLBACK`. A clean `psql` run
prints up to 36 months of net and cumulative cash, newest first, then up to
120 category-month rows comparing actual spend with budget, then your
exercises. Payment and expense dates are generated relative to the load date,
so month labels move over time while totals stay the same. See the
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) for the
launcher and recovery steps, and its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
for the optional notebook.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 50; budget variance](day50_project2_finance_part2.md) Day 50 compared expenses with budgets by category; today expenses meet the cash that customers actually paid.
- **Artifacts:** [learner SQL](../day51_project2_finance_part3.sql) ·
  [solution reasoning](../solutions/day51_solutions.md) ·
  [executable solution](../solutions/day51_solutions.sql)

## A beginner's mental model for this lesson

Cash flow is two monthly series that come from different tables. Cash in is
`payments.amount`, 3,836 payments totaling about 1.83 million spread over
roughly four years. Cash out is `expenses.amount`, 10,000 expense rows in five
categories (COGS, G&A, Infrastructure, Marketing and Payroll, about 10.1
million each) that only cover the last two years. The two series therefore do
not have the same months, and the gap is the whole lesson: summarize each
table to one row per month on its own, then combine the summaries with a
`FULL OUTER JOIN` so a month that appears on only one side is kept with a zero
on the other.

Cash is not revenue. `orders.total_amount` sums to about 2.36 million, but
roughly a fifth of orders are still `placed` without a payment, and 149
payments land in a later month than their order. A running total such as
cumulative cash is a window over the monthly rows, so it must be computed
after the monthly grain is fixed. Read each CTE in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both excerpts come from the learner script and run inside its transaction.

### Example 1

```sql
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
```

**How to read it:** `pay_m` and `exp_m` each reduce one table to one row per month. `joined`
combines them with `FULL OUTER JOIN`, taking the month from whichever side has
it and turning a missing side into 0. The final `SELECT` computes net cash and
a running `SUM(...) OVER (ORDER BY month)`.

**Expected result/shape:** 36 rows, newest month first. The cumulative column is computed over every
month before `LIMIT` trims the list, so the newest row carries a balance of
about -48.65 million: expenses close to 2 million in a full month swamp
cash in of 30,000 to 126,000. Older rows before expenses begin show small positive net cash.

### Example 2

```sql
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
```

**How to read it:** `exp` and `bud` reduce expenses and budgets to (month, category).
`j` full-joins them on both keys. The two window columns are three-row
rolling sums per category, ordered by month.

**Expected result/shape:** 120 rows, newest month first and alphabetical by category within a month, so
24 months of five categories. Despite the `_ma3` names, `actual_ma3` and
`budget_ma3` are three-month sums, not averages; divide by 3 if you need a
moving average, and remember the first two months of each category sum fewer
than three rows.

## Learning objectives

- Separate cash movement from booked order revenue.
- Project three future months under a precisely stated seasonal-average rule.

## Vocabulary and concepts

- **Cash-in:** received payment amount by payment date.
- **Cash-out:** expense amount by expense date.
- **Seasonal average:** an average of prior observations matching the target
  calendar period, distinct from a single seasonal-naive lag.

## Worked example / walkthrough

Aggregate payments and expenses independently by month, full-join the two
series, and calculate net and cumulative cash. For a future target month, join
historical net cash on calendar month, average the matches, and return the
supporting observation count beside the projection.

## Exercises

Complete these in the [learner SQL](../day51_project2_finance_part3.sql):

1. Calculate policy-defined monthly operating margin.
   **Inputs/evidence:** For sql-51 Exercise 1, sum `payments.amount` by payment month in `cash`, sum `expenses.amount` by expense month for the four operating categories (COGS, Payroll, Infrastructure, G&A, not Marketing) in `operating_expense`, and `FULL OUTER JOIN` the two `USING (month)`.
   **Expected result/shape:** For sql-51 Exercise 1, expected output: 46 rows, one per month appearing in either payments or operating expenses (2023-02-01 to 2026-11-01). The final columns are `month`, `cash_in`, `operating_cost`, and `operating_margin`. The final order is `month DESC`.
   **Verify:** For sql-51 Exercise 1, confirm 46 distinct months, and that the 21 months before expenses begin (2023-02 to 2024-10) show `operating_cost` 0.00 and a margin of exactly 1.0000. Recompute the top row: 2026-11 has 76,045.60 cash in and 1,362,737.02 operating cost (that month's 1,712,274.61 of expenses minus 349,537.59 of Marketing), so the margin is -16.9200. Then, in a transaction, delete the 77 payments from 2025-03: that month stays with `cash_in` 0.00, cost 1,747,681.27, and a `NULL` margin instead of a division error; `ROLLBACK`.
   **Data check:** Expect one row per month from either side, newest first. Recent months show an `operating_margin` around -12 to -17, and the first full expense months fall near -60, because operating cost (all categories except Marketing) runs well over a million against at most about 126,000 of cash in. Months before expenses begin show cost 0 and a margin of exactly 1.0000, which says more about missing data than about profit.
2. Project three months of seasonal-naive net cash.
   **Inputs/evidence:** For sql-51 Exercise 2, build monthly net cash in `historical` from a `FULL OUTER JOIN` of payment and expense totals, generate the next three calendar months after `CURRENT_DATE` in `future`, and `LEFT JOIN` each one to the earlier months with the same calendar month number.
   **Expected result/shape:** For sql-51 Exercise 2, expected output: exactly three rows, one per future `forecast_month` (2026-12-01, 2027-01-01, and 2027-02-01 when run in November 2026). The count column shows how much history supports each estimate; a `NULL` projection means there was none. The final columns are `forecast_month`, `projected_net_cash`, and `matching_historical_months`. The final order is `forecast_month`.
   **Verify:** For sql-51 Exercise 2, run in November 2026, confirm the counts 3, 3, and 4, then recompute the first row by hand: the Decembers 2023, 2024, and 2025 have net cash 11,201.99, -2,102,060.09, and -2,062,784.20, whose mean is -1,384,547.43. February averages four months (2023 to 2026), so it is -941,106.45. Then, in a transaction, insert a 100.00 payment dated 2026-12-02 and rerun: the December projection does not change, because `h.month < f.forecast_month` keeps a month out of its own forecast; `ROLLBACK`.
   **Data check:** Expect exactly three rows, the next three calendar months. Each shows how many past years supplied that calendar month, usually 3 or 4. The averages mix years with no expense data (small positive net cash) and years with full expenses (large negative), so treat them as a demonstration of the method.
3. Explain cash-basis versus order-revenue timing.
   **Inputs/evidence:** For sql-51 Exercise 3, read from `orders` and `payments`; sum `total_amount` by order month as `booked_order_revenue` and left join the payments summed by payment month as `cash_received`, using `COALESCE(..., 0)` for months without payments.
   **Expected result/shape:** For sql-51 Exercise 3, expected output: one row per order month, ordered by `month`; `cash_received` is lower than `booked_order_revenue` in most months because unpaid orders bring no cash. The final columns are `month`, `booked_order_revenue`, and `cash_received`. The final order is `month`.
   **Verify:** For sql-51 Exercise 3, confirm 46 unique months, that `SUM(booked_order_revenue)` is 2,355,646.89 and `SUM(cash_received)` is 1,831,900.81 (the same as `SELECT SUM(amount) FROM payments`), and that cash is lower than bookings in 45 months and equal only in 2023-02 (1,203.26). Then, in a transaction, insert a 100.00 payment dated 2026-12-02: the result keeps 46 rows and the same cash total, now 100.00 short of `payments`, because the query starts from order months and drops a payment-only month; `ROLLBACK`.
   **Data check:** Expect one row per order month. Booked revenue exceeds cash received in every month except the first, where they match, because unpaid `placed` orders bring no cash and some payments arrive a month late.
4. Produce beginning cash, flows, net cash, and ending cash.
   **Inputs/evidence:** For sql-51 Exercise 4, stack the 3,836 payments (as `cash_in`) and the 10,000 expenses (as `cash_out`) with `UNION ALL`, group them to monthly totals in `flow`, add a running `SUM(cash_in - cash_out) OVER (ORDER BY month)` in `balances`, and read the previous ending balance with `LAG(ending_cash, 1, 0)`.
   **Expected result/shape:** For sql-51 Exercise 4, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, starting from a declared opening balance of 0. The final columns are `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`. The final order is `month`.
   **Verify:** For sql-51 Exercise 4, hand-check the first two rows: 2023-02 begins at 0 and ends at 1,203.26, and 2023-03 begins at 1,203.26 and ends at 2,350.50. Confirm with `LAG` that every `beginning_cash` equals the previous row's `ending_cash`, and that the last `ending_cash`, -48,651,949.19, equals 1,831,900.81 of payments minus 50,483,850.00 of expenses. There is one window with no `PARTITION BY`, so nothing resets; in a transaction, delete the 77 payments from 2025-03 and confirm that month keeps its row with `cash_in` 0 and every later ending balance drops by 38,915.28; `ROLLBACK`.
   **Data check:** Expect one row per month in date order. Each `beginning_cash` equals the previous row's `ending_cash`, and the first row starts at 0 by declaration. Ending cash stays positive while there are no expenses and then falls to about -48.65 million in the latest month.
5. Preserve expense-only/payment-only months with a calendar spine.
   **Inputs/evidence:** For sql-51 Exercise 5, find the first and last dates across `payments` and `expenses` in `bounds`, expand them into calendar months with `generate_series` in `months`, and `LEFT JOIN` the monthly totals `cash` and `costs` to that spine.
   **Expected result/shape:** For sql-51 Exercise 5, expected output: 46 rows, one per calendar `month` from 2023-02-01 to 2026-11-01, with 0 where a side has no rows. The final columns are `month`, `cash_in`, and `cash_out`. The final order is `month`.
   **Verify:** For sql-51 Exercise 5, confirm 46 months and show the bug being repaired: an inner join of `cash` and `costs` returns only 25 rows (2024-11 to 2026-11), losing the 21 months that have payments but no expenses. Then, in a transaction, delete the 77 payments from 2025-03 and rerun: the spine still returns 46 rows, with 2025-03 showing `cash_in` 0 and `cash_out` 2,154,691.38; `ROLLBACK`.
   **Data check:** On the course data payments cover every month in the range, so the spine returns the same months as the full outer join; the value of the spine shows when a month has neither payments nor expenses. Delete one month of payments in a rolled-back transaction and the month should remain with `cash_in` 0.
6. Keep zero-cash-in margin NULL with an explanatory status.
   **Inputs/evidence:** For sql-51 Exercise 6, use the two-row `VALUES` list `toy` (2026-01 with 0 cash in and 100 cost; 2026-02 with 500 in and 300 cost) instead of the course tables, divide through `NULLIF(cash_in, 0)`, and label the result with a `CASE`.
   **Expected result/shape:** For sql-51 Exercise 6, expected output: 2 rows, one per `toy` month: 2026-01-01 with a `NULL` margin and `undefined: zero cash in`, and 2026-02-01 with 0.4 and `defined`. The final columns are `month`, `operating_margin`, and `margin_status`.
   **Verify:** For sql-51 Exercise 6, confirm the two rows above and that the first raises no division-by-zero error. Then add a third `toy` row, `(date '2026-03-01', NULL, 100)`: its margin is also `NULL`, but the status says `defined`, because `cash_in = 0` is unknown for a `NULL` and falls to `ELSE`, so a `WHEN cash_in IS NULL` branch is needed to tell missing cash from zero cash.
   **Data check:** The solution uses a two-row `VALUES` example, not the course tables: the month with zero cash in returns a `NULL` margin and the status `undefined: zero cash in`, while 500 in and 300 cost gives 0.4 and `defined`.

Show all three forecast months even without matching history.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Use a full outer join so payment-only
  and expense-only months remain visible. With an inner join every month
  before expenses begin disappears, and the cumulative balance starts in the
  wrong place.
- **Totals that are too large:** payments and expenses were joined row to row
  before summing, multiplying each payment by every expense in the month.
  Aggregate each table to months first.
- **Margin of 1.0000 or a division error:** a month with no cost or no cash.
  Keep `NULLIF(cash_in, 0)` and show a status rather than hiding the case.
- **Cash and booked revenue mixed:** `orders.total_amount` is not cash. Label
  which one a column measures.
- More recovery steps are in the
  [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Do monthly net totals reconcile to payments minus expenses over the same
  represented period?
- Is the forecast definition, and its behavior with one or zero historical
  matches, explicit?

## Next step

Continue to [Day 52; star-schema warehouse](day52_project3_dwh_part1.md).

## Deep dive and reference

## Project focus

- Calculate monthly cash-in, cash-out, net cash flow, and cumulative cash.
- Define an operating-margin metric from selected expense categories.
- Project net cash for the next three months.

## How the learner script uses the current schema

Cash-in comes from `payments.payment_date` and `payments.amount`; cash-out comes
from `expenses.expense_date` and `expenses.amount`. This is cash movement, not
booked `orders.total_amount`. The starter also aligns monthly budgets and
actuals at category grain.

## Practice map

Exercises 1 and 6 define and protect an operating margin, Exercise 2 builds a
seasonal projection that shows its own evidence, Exercise 3 sets booked
revenue beside cash, and Exercises 4 and 5 produce a balance sheet style
roll-forward and a gap-free month list. The learner SQL repeats the same
numbered prompts.

## Ambiguous forecast wording

The learner says “average of last 12 matching months (seasonal naive).”
Seasonal naive usually means the single value from 12 months earlier, while
“average” implies several observations. The reference answer interprets
matching months as the same calendar month across prior years and averages the
available values. State this assumption and return the supporting history count.

## Validation and limits

- Use a full outer join so payment-only and expense-only months remain visible.
- Guard margin when cash-in is zero.
- Treat expense-category classification as course policy, not accounting advice.
- A one-observation seasonal average is only a naive estimate.
- Reconcile monthly net cash to total payments minus total expenses over the
  same represented period.

## Ask an AI tutor about this lesson

A tutor can talk through what a negative margin of -15 means for a business,
but the cash figures must come from your own queries. To use one, paste this
prompt and follow the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-51: Finance Project, Part 3: Cash Flow.

I have completed the direct catalog prerequisite: `sql-50`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day51_project2_finance_part3.md
- Answer-free learner SQL: sql/postgres-60day/day51_project2_finance_part3.sql

Key terms to teach in context: Cash-in, Cash-out, Seasonal average. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate payments and expenses independently by month, full-join the two series, and calculate net and cumulative cash. For a future target month, join historical net cash on calendar month, average the matches, and return the supporting observation count beside the projection.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-51/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
