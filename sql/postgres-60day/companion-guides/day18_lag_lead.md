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

## Practice assumptions and review method

- **Focus:** Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
- **Assumptions:** Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
- **Failure to watch for:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Show each order with the previous order timestamp for that customer.
   **Progressive hint:** Partition by customer and order by timestamp plus ID.
   **Expected shape:** One row per order; first customer order has NULL previous timestamp.
2. **Query writing:** Calculate days since each customer's previous order.
   **Progressive hint:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
   **Expected shape:** One row per order with nullable interval/days.
3. **Query writing:** Show each promotion with the next promotion start date for the same product.
   **Progressive hint:** Partition by product and define a stable chronological order.
   **Expected shape:** One row per promotion; last product promotion has NULL next date.
4. **Prediction:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
   **Progressive hint:** NULL means there is no prior observation; preserve that semantic state.
   **Expected shape:** One row per customer's first order.
5. **Debugging:** Compute month-over-month stored-revenue change after aggregating to month grain.
   **Progressive hint:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
   **Expected shape:** One row per month with nullable first change.
6. **Extension:** Compare each product price with the next higher price in its category.
   **Progressive hint:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
   **Expected shape:** One row per product with nullable next price.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- LAG/LEAD: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW
