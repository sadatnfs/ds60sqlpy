# Day 51 — Finance/Operations Project, Part 3: Cash Flow

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 50 — budget variance](day50_project2_finance_part2.md)
- **Artifacts:** [learner SQL](../day51_project2_finance_part3.sql) ·
  [solution reasoning](../solutions/day51_solutions.md) ·
  [executable solution](../solutions/day51_solutions.sql)

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
2. Project three months of seasonal-naive net cash.
3. Explain cash-basis versus order-revenue timing.
4. Produce beginning cash, flows, net cash, and ending cash.
5. Preserve expense-only/payment-only months with a calendar spine.
6. Keep zero-cash-in margin NULL with an explanatory status.

Show all three forecast months even without matching history.

## Self-check

- Do monthly net totals reconcile to payments minus expenses over the same
  represented period?
- Is the forecast definition—and its behavior with one or zero historical
  matches—explicit?

## Next step

Continue to [Day 52 — star-schema warehouse](day52_project3_dwh_part1.md).

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

## Practice — match the learner prompts exactly

1. Calculate monthly operating margin as:
   `(cash_in - COGS - Payroll - Infrastructure - G&A) / cash_in`.
   Marketing is deliberately excluded by the prompt.
2. Return the next three calendar months with projected net cash from historical
   matching months.

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
