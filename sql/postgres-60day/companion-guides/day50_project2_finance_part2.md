# Day 50: Finance/Operations Project, Part 2: Budget Variance

## How to run this lesson

Launch `./classroom`, pick PostgreSQL lesson **sql-50**, then **Whole SQL
lesson (psql)**. Your copy lives at
`.learning/sql/sql-50/lesson/workspace/sql/postgres-60day/day50_project2_finance_part2.sql`
and reads `expenses` and `budgets` in `advanced_sql_training` between `BEGIN`
and `ROLLBACK`. Running it through `psql` prints two 100-row results: a
budget-versus-actual comparison and a rolling three-month view, both newest
month first. Setup details are in the
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom), and the
[notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is
optional.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 49; revenue forecasting](day49_project2_finance_part1.md) Day 49 already turned expense rows into monthly series; today the same months meet a budget.
- **Artifacts:** [learner SQL](../day50_project2_finance_part2.sql) ·
  [solution reasoning](../solutions/day50_solutions.md) ·
  [executable solution](../solutions/day50_solutions.sql)

## A beginner's mental model for this lesson

Two tables describe the same months from opposite sides. `expenses` holds
10,000 individual payments, about 80 per month and category. `budgets` holds
one planned amount per month and category, 125 rows in all. Comparing them
row against row is wrong: joining raw expenses to a budget row repeats that
budget once per expense. Each side is first summed to one row per
`(month, category)`, and only then are the two sides joined.

**Variance** in this course is `actual - budget`, so a positive number means
overspend. On a fresh load, COGS and Payroll stay under budget in every month,
while G&A, Infrastructure and Marketing overspend in almost every month. A
**budget-only row** is a month and category with a plan but no spending; its
mirror is spending with no plan. A `FULL JOIN` keeps both kinds, and the
course data happens to contain neither, so you test them by adding rows. A
**static pivot** turns the five known category names into five columns,
which only works while that list stays fixed.

The calendar has a trap: the first and last of the 25 months are partial, so
comparing them with full months distorts both variance and year-over-year
change. Read each query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both examples build the same two monthly summaries and differ in what they do
after the join.

### Example 1

```sql
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
```

**How to read it:** `monthly_exp` and `monthly_budget` each return 125 rows, one per month and
category. The `FULL OUTER JOIN` matches them on both keys, `COALESCE` picks
whichever side has the key, and missing amounts display as 0. `NULLIF(b.budget,
0)` makes the percentage `NULL` rather than an error if a budget is zero.

**Expected result/shape:** 100 of the 125 joined rows, newest month first. The top row is COGS for the
current partial month: budget 576,000.00, actual 335,159.36, variance
-240,840.64 and `variance_pct` -0.4181 on a fresh load. The columns appear as
`category`, `month`, `budget`, `actual`, `variance`, `variance_pct`.

### Example 2

```sql
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
```

**How to read it:** After the same join, the window `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`
adds each category's current month to the two before it. Despite the `_ma3`
names these are three-month totals, not averages; divide by 3 for a mean.

**Expected result/shape:** 100 rows of `category`, `month`, `actual_ma3` and `budget_ma3`. COGS in the
latest month shows 1,174,789.21 actual against 1,854,000.00 budget on a fresh
load. Each category's two oldest months have fewer than three rows in the
frame, so their totals are smaller.

## Learning objectives

- Align actual and budget values without discarding one-sided periods.
- Calculate absolute and percentage variance and pivot controlled categories.

## Vocabulary and concepts

- **Variance:** actual minus budget under this course's declared convention.
- **Budget-only row:** a period/category with budget but no represented actual.
- **Static pivot:** fixed output columns for a controlled category domain.

## Worked example / walkthrough

Aggregate actuals and budgets independently at `(month, category)`, full-join
those stable relations, and retain both raw values. Derive absolute variance and
guard percentage variance with `NULLIF(budget, 0)`; only then pivot the five
known categories.

## Exercises

Complete these in the [learner SQL](../day50_project2_finance_part2.sql):

1. Calculate YoY variance and flag >15% overspend.
   **Inputs/evidence:** For sql-50 Exercise 1, sum the 10,000 `expenses` rows by `date_trunc('month', expense_date)` and `category` in `actual`, sum the 125 `budgets` rows by `period` and `category` in `budget`, `FULL OUTER JOIN` them `USING (month, category)` with missing amounts set to 0, and take `LAG(actual, 12)` within each category for the prior year.
   **Expected result/shape:** For sql-50 Exercise 1, expected output: 125 rows, one per month and category (25 months from 2024-11-01 to 2026-11-01 times 5 categories), including any period found on only one side of the actual/budget comparison. The final columns are `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`. The final order is `month DESC, category`.
   **Verify:** For sql-50 Exercise 1, confirm 125 distinct (`month`, `category`) pairs, 71 rows with the flag true, and 65 rows with a `prior_year_actual` (the first 12 months of each category have none). Recompute the top row by hand: 2026-11 COGS spent 335,159.36 against 398,788.03 in 2025-11 (-0.1596) and a 576,000.00 budget (-0.4181), so the flag is false. Then, in a transaction, insert a `Travel` expense of 1,000 on 2026-11-15: a 126th row appears with `budget_variance_pct` `NULL` but the flag true, because the missing budget became 0; `ROLLBACK`.
   **Data check:** 125 rows on a fresh load. 71 carry `overspent_by_more_than_15_pct = true`, none of them COGS or Payroll. Only 65 rows have a `prior_year_actual`, since the first 12 months have nothing to compare with. The month one year after the partial first month shows year-over-year changes above 4.5 (450%), a calendar artifact rather than real growth.
2. Pivot monthly category variance.
   **Inputs/evidence:** For sql-50 Exercise 2, sum `expenses` by month and category in `actual`, start `variance` from the 125 `budgets` rows with a `LEFT JOIN` to `actual`, compute `actual - budget` per row, and spread it into one column per category with `SUM(variance) FILTER (WHERE category = ...)`.
   **Expected result/shape:** For sql-50 Exercise 2, expected output: 25 rows, one per budget month from 2026-11-01 down to 2024-11-01, with one variance column per known category. The final columns are `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`. The final order is `month DESC`.
   **Verify:** For sql-50 Exercise 2, confirm 25 distinct months and that the five columns of each row add up to that month's total spend minus its total budget: for 2026-11, -240,840.64 + 135,537.59 - 342,178.22 + 41,001.63 + 175,254.25 = -231,225.39, the same as `SUM(expenses.amount) - SUM(budgets.amount)` for that month. Then, in a transaction, insert a `Travel` expense of 1,000 on 2026-11-15 and rerun: the pivot is unchanged at 25 rows, so the November reconciliation is now off by exactly 1,000.00, because spending without a budget row never enters `variance`; `ROLLBACK`.
   **Data check:** 25 rows, one per budget month. The `cogs` and `payroll` columns are negative in every row, and the latest row repeats Example 1's variances: -240,840.64 for COGS and 135,537.59 for Marketing. Adding the five columns of any row should equal that month's total spend minus its total budget.
3. Define absent-budget policy before using `COALESCE`.
   **Inputs/evidence:** For sql-50 Exercise 3, build the same 125-row `actual` and `budget` summaries, `FULL JOIN` them `USING (month, category)`, keep `a.actual` and `b.budget` without `COALESCE`, and label each row from which side's key is `NULL`.
   **Expected result/shape:** For sql-50 Exercise 3, expected output: 125 rows, one per `month` and `category`, every one labeled `comparable` on the course data. The final columns are `month`, `category`, `actual`, `budget`, and `comparison_status`. The final order is `month DESC, category`.
   **Verify:** For sql-50 Exercise 3, confirm 125 rows, all `comparable`, with no `NULL` in `actual` or `budget`. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01: a 126th row appears at the top labeled `no actual` with `actual` shown as `NULL`, not 0. Roll back and insert a `Travel` expense of 1,000 on 2026-11-15 instead: its row is labeled `missing budget` with `budget` `NULL`; `ROLLBACK`.
   **Data check:** All 125 rows say `comparable`. Insert a budget for a month after the last expense and one new row appears at the top, `no actual`, with `actual` shown as `NULL`, not 0. An expense in a category with no budget would instead produce `missing budget`.
4. Add category YTD actual, budget, variance, and variance percentage.
   **Inputs/evidence:** For sql-50 Exercise 4, build `monthly` from the 125-row expense and budget summaries with a `FULL JOIN` and coalesced `month` and `category`, then run three running `SUM` windows partitioned by `category` and `EXTRACT(year FROM month)` and ordered by `month`.
   **Expected result/shape:** For sql-50 Exercise 4, expected output: 125 rows, one per `month` and `category`, in 15 partitions (5 categories times the years 2024, 2025, and 2026). The final columns are `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`. The final order is `month DESC, category`.
   **Verify:** For sql-50 Exercise 4, hand-check COGS: the 2024 partition has only two rows, so 2024-11 shows 72,384.36 against 654,000.00 and 2024-12 shows 545,878.91 against 1,266,000.00; 2025-01 restarts at 430,421.17 against 570,000.00; and 2026-11 shows 4,508,769.63 against 6,600,000.00, a `variance_ytd` of -2,091,230.37, equal to summing that year's COGS rows directly. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01: that row shows `budget_ytd` 7,200,000.00 but `actual_ytd` and `variance_ytd` unchanged from November, because `actual - budget` is `NULL` on a one-sided row; `ROLLBACK`.
   **Data check:** Partitions are a category within a calendar year, so the totals restart every January. On a fresh load the first year holds only two months. In the latest month, COGS shows 4,508,769.63 spent against 6,600,000.00 budgeted, a `variance_ytd` of -2,091,230.37, which you can check by summing that year's rows from Exercise 3.
5. Normalize joined keys before applying windows.
   **Inputs/evidence:** For sql-50 Exercise 5, write a short note on why every window and filter must use the coalesced keys `monthly.month` and `monthly.category` from Exercise 4 instead of `a.month` or `a.category` from one side of the `FULL JOIN`; Exercise 4's `monthly` CTE is the repaired query, so cite its results as evidence and mark anything you did not run as an assumption.
   **Expected result/shape:** For sql-50 Exercise 5, expected output: a written note with six fields, `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`, whose `evidence` quotes the 125 rows of `monthly` with zero `NULL` months and zero `NULL` categories.
   **Verify:** For sql-50 Exercise 5, show that the broken and repaired forms agree today: partitioning by `a.category, EXTRACT(year FROM a.month)` returns the same 125 rows and totals as Exercise 4, because every key matches. Then, in a transaction, insert a COGS budget of 600,000 for 2026-12-01 and run both: the repaired form gives that row a `budget_ytd` of 7,200,000.00, while the broken form puts it in a `NULL` partition with 600,000.00, so it never joins the COGS total; `ROLLBACK`, and name the `fallback` and `rollback_limit` entries that cover this case.
   **Data check:** The `monthly` relation has 125 rows and no `NULL` month or category, so a window on either side's own key would give the same numbers today. Add a budget-only row and partition by `a.category` instead of the coalesced key: that row falls into a `NULL` partition and its budget never reaches its category's totals.
6. Label unbudgeted spend separately from ordinary overspend.
   **Inputs/evidence:** For sql-50 Exercise 6, aggregate `expenses` and `budgets` independently to (`month`, `category`) before joining.
   **Expected result/shape:** For sql-50 Exercise 6, expected output: 125 rows, one per (`month`, `category`) found in either source, with `actual`, `budget`, and `status`, ordered by `month, category` (oldest first); 72 rows are `overspend` and 53 are `within budget`.
   **Verify:** For sql-50 Exercise 6, reconcile the totals: `actual` sums to 50,483,850.00 and `budget` to 51,198,000.00, the same as `SUM(amount)` on each source table, while joining raw `expenses` to `budgets` instead sums the budget to 4,098,331,000.00 because each plan repeats once per expense (13 to 96 times). Then, in a transaction, test each missing case: a `Travel` expense on 2026-11-15 gives `unbudgeted spend`, a COGS budget for 2026-12-01 gives `budget without spend`, and setting the 2026-11 G&A budget to 0 gives `zero budget`; `ROLLBACK` after each.
   **Data check:** 125 rows: 72 `overspend` and 53 `within budget`. Summed `actual` is 50,483,850.00 and summed `budget` is 51,198,000.00, matching `SUM(amount)` on each source table. Insert an expense dated after the last budget period and one `unbudgeted spend` row appears.

Test actual-only, budget-only, and zero-budget toy rows.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Preserve actual-only and budget-only rows before deciding how to display missing values.
- **Budgets about 80 times too large:** raw `expenses` were joined to
  `budgets`, so each budget row repeated once per expense. Sum both sides to
  `(month, category)` before the join.
- **Year-over-year change of +450% or -16%:** the first and last months are
  partial. Compare full months, or say clearly that the latest month is
  month-to-date.
- **A pivot row that does not add up:** a category spelled differently from
  the `FILTER` text, or a sixth category, silently falls out of the pivot.
  Reconcile each pivot row with the long-form rows from Exercise 3.
- **A "moving average" three times too big:** Example 2 sums three months.
  Divide by the number of rows in the frame if you need a mean.
- More recovery steps are in the
  [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Are missing and zero values kept semantically distinct?
- Does every pivot row reconcile with the long-form variance rows?

## Next step

Continue to [Day 51; cash flow](day51_project2_finance_part3.md).

## Deep dive and reference

## Project focus

- Align monthly actual expenses with monthly budgets.
- Add year-over-year and greater-than-15% overspend indicators.
- Pivot known expense categories into report columns.

## How the learner script uses the current schema

Actuals come from `expenses(expense_date, category, amount)`. Budgets come from
`budgets(period, category, amount)`, where `period` is the first day of a month.
The starter uses a full outer join so months/categories present on only one side
remain visible, then demonstrates rolling three-row totals.

The setup categories are `COGS`, `Marketing`, `Payroll`, `Infrastructure`, and
`G&A`.

## Practice map

Exercise 1 adds year-over-year change and a 15% overspend flag, Exercise 2
pivots variance into one column per category, Exercises 3 and 6 label
one-sided and zero-budget rows, and Exercise 4 builds year-to-date totals. Exercise 5 is written: argue for one canonical key before any window. The
learner script repeats each prompt unchanged.

## Metric semantics

- Variance is `actual - budget`; positive means overspend.
- Percentage variance uses budget as denominator and must guard zero budgets.
- A 12-row `LAG` assumes every category has a complete monthly series. Build a
  month/category spine when gaps are possible.
- A static pivot is appropriate only while the category set is controlled.

## Validation and limits

- Preserve actual-only and budget-only rows before deciding how to display
  missing values.
- Reconcile each pivot row to the long-form monthly variance.
- Do not silently label a missing budget as zero-percent variance.
- Report both absolute currency variance and percentage; either alone can
  mislead.

## Ask an AI tutor about this lesson

Budget variance is a good topic for a tutor's questions: ask it to quiz you on
which status a hand-made row should get before you insert it. Start with the
prompt below; the
[study guide on tutors](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) covers
the ground rules.

```text
Tutor me through sql-50: Finance Project, Part 2: Budget Variance.

I have completed the direct catalog prerequisite: `sql-49`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day50_project2_finance_part2.md
- Answer-free learner SQL: sql/postgres-60day/day50_project2_finance_part2.sql

Key terms to teach in context: Variance, Budget-only row, Static pivot. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate actuals and budgets independently at `(month, category)`, full-join those stable relations, and retain both raw values. Derive absolute variance and guard percentage variance with `NULLIF(budget, 0)`; only then pivot the five known categories.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-50/ working copy. Never point setup, reset, DDL, or DML
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
