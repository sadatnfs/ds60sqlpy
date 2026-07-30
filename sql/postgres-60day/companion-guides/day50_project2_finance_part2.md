# Day 50 — Finance/Operations Project, Part 2: Budget Variance

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 49 — revenue forecasting](day49_project2_finance_part1.md)
- **Artifacts:** [learner SQL](../day50_project2_finance_part2.sql) ·
  [solution reasoning](../solutions/day50_solutions.md) ·
  [executable solution](../solutions/day50_solutions.sql)

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
2. Pivot monthly category variance.
3. Define absent-budget policy before using `COALESCE`.
4. Add category YTD actual, budget, variance, and variance percentage.
5. Normalize joined keys before applying windows.
6. Label unbudgeted spend separately from ordinary overspend.

Test actual-only, budget-only, and zero-budget toy rows.

## Self-check

- Are missing and zero values kept semantically distinct?
- Does every pivot row reconcile with the long-form variance rows?

## Next step

Continue to [Day 51 — cash flow](day51_project2_finance_part3.md).

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

## Practice — match the learner prompts exactly

1. Add prior-year actual and year-over-year percentage by category, plus
   `actual > budget * 1.15` as the requested overspend flag.
2. Return one row per month with actual-minus-budget variance columns for the
   five known categories.

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
