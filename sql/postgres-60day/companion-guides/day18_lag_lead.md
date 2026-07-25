# Day 18 — LAG/LEAD and Intra-Row Comparisons (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 17 — ranking functions](day17_rank_functions.md)
- **Artifacts:** [learner SQL](../day18_lag_lead.sql) ·
  [solution reasoning](../solutions/day18_solutions.md) ·
  [executable solution](../solutions/day18_solutions.sql)

## Learning objectives

- Compare each row with an earlier or later row in the same ordered partition.
- Distinguish an offset in result rows from a duration in calendar time.

## Vocabulary and concepts

- **Offset:** the number of ordered rows traversed by `LAG` or `LEAD`.
- **Default value:** the value returned when the requested offset does not
  exist.
- **Calendar spine:** an explicit row for every required date or period.

## Worked example / walkthrough

At monthly grain, place `revenue` beside `LAG(revenue) OVER (ORDER BY month)`.
The first row has no predecessor and returns `NULL`. If a month is absent, the
previous row is not necessarily the previous calendar month, so build a month
spine before interpreting the difference as month-over-month.

## Exercises

Complete the prompts in the [learner SQL](../day18_lag_lead.sql). Remove one
period from a toy sequence and explain how the offset meaning changes.

## Self-check

- Is each window ordered uniquely enough to define “previous” or “next”?
- Are missing first/last offsets and zero denominators handled explicitly?

## Next step

Continue to [Day 19 — running aggregates](day19_running_aggregates.md).

## Deep dive and reference

Learning objectives
- Use LAG/LEAD to access prior/next row values within partitions
- Compute deltas, growth rates, and interval gaps
- Handle nulls and defaults with the third LAG/LEAD argument

Why this matters
Many metrics are changes over time: day-over-day growth, time since last purchase, step detection. LAG/LEAD express these cleanly and efficiently.

Core concepts and deep dive
- LAG(expr, offset, default) OVER (PARTITION BY k ORDER BY t): returns value offset rows before current; default substitutes for missing (e.g., first row).
- LEAD symmetric; often used for next timestamp to compute session gaps.
- Differences: expr - LAG(expr) for numeric deltas; AGE(ts, LAG(ts)) for time deltas.

Patterns
- DoD/YoY growth: (x - LAG(x)) / NULLIF(LAG(x),0).
- Sessionization: gap = ts - LAG(ts); new session if gap > interval '30 min'.
- Churn signal: last_order_date per customer and days_since_last.

Pitfalls
- Sorting by a non-unique timestamp yields unpredictable row pairing; add tiebreakers.
- Large partitions without indexes increase sort cost; index on (k, t) helps.

Exercises from the learner script
1) For each product, compute monthly sales and previous-month sales with `LAG`.
2) For each employee, show salary and the next higher salary within the
   department using `LEAD`.

“Sales” is ambiguous between units and revenue. The maintained answer uses net
line revenue and creates a dense product-month calendar, so `LAG` means the
previous calendar month even when it had zero sales. For exercise 2, window over
distinct department salaries in ascending order; otherwise duplicate salaries
make “next higher” non-strict.

Further reading
- LAG/LEAD: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW
