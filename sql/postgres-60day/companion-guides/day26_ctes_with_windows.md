# Day 26 — CTEs with Window Functions: Layered Analytics (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 25 — multiple CTEs and hierarchies](day25_multiple_ctes_hierarchies.md)
- **Artifacts:** [learner SQL](../day26_ctes_with_windows.sql) ·
  [solution reasoning](../solutions/day26_solutions.md) ·
  [executable solution](../solutions/day26_solutions.sql)

## Learning objectives

- Pre-aggregate to the correct grain before calculating ranks, shares, or
  changes.
- Filter a window result through an outer query in PostgreSQL.

## Vocabulary and concepts

- **Layered analytics:** successive relational stages with progressively richer
  measures.
- **Window input grain:** the meaning of one row before `OVER (...)` is applied.
- **QUALIFY alternative:** an outer `SELECT` that filters a computed window
  column.

## Worked example / walkthrough

Create monthly totals in one CTE, add `LAG(total)` in the next, and calculate
growth in the outer query with a guarded denominator. Keeping the ratio outside
the `LAG` layer makes the prior value visible and lets you inspect both values
before interpreting the percentage.

## Practice assumptions and review method

- **Focus:** Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
- **Assumptions:** Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
- **Failure to watch for:** Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate monthly stored revenue and its prior-month value/change.
   **Progressive hint:** Aggregate to month in a CTE, then lag the monthly measure.
   **Expected shape:** One row per observed month.
2. **Query writing:** Rank product categories by net revenue within each UTC order month.
   **Progressive hint:** Aggregate month/category first, then rank the stable aggregate.
   **Expected shape:** One row per observed month/category.
3. **Query writing:** Return the top three category revenue levels per month.
   **Progressive hint:** Rank in one CTE and filter the window result outside.
   **Expected shape:** Top three revenue ranks for each observed month.
4. **Prediction:** Calculate each category's cumulative share of monthly revenue in descending contribution order.
   **Progressive hint:** Divide running category revenue by the full monthly total; use explicit frames.
   **Expected shape:** One row per month/category with final share equal to one.
5. **Debugging:** Calculate a three-month moving average after building a dense month calendar.
   **Progressive hint:** Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
   **Expected shape:** A continuous chronological month series.
6. **Extension:** Reconcile the final cumulative monthly revenue with the independent order total.
   **Progressive hint:** Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
   **Expected shape:** One row with zero difference.

## Self-check

- Does every window operate over the intended pre-aggregated relation?
- Is window filtering performed in an outer query rather than an invalid
  same-level `WHERE`?

## Next step

Continue to [Day 27 — pivoting and unpivoting](day27_pivot_unpivot.md).

## Deep dive and reference

Learning objectives
- Combine CTE staging with window calculations for clarity and speed
- Decide which grain to aggregate at before applying windows
- Build multi-stage pipelines for advanced KPIs (shares, ranks, rolling metrics)

Why this matters
Complex analytics often need a staging step (pre-aggregations) before windowing. Getting the grain right avoids wrong answers and large sorts, and it yields maintainable queries.

Core concepts and deep dive
- Pre-aggregate, then window: compute daily/category totals in a CTE, then run windows over that smaller set.
- Windows across aggregates: once at daily grain, you can apply running totals, moving averages, and shares cheaply.
- Multiple windows: define named window specs to compute per-partition and global metrics in the same SELECT.

Patterns
- WITH daily AS (... GROUP BY day, key) SELECT day, key, SUM(x) OVER (PARTITION BY key ORDER BY day) ... FROM daily.
- Shares of total: x / NULLIF(SUM(x) OVER (PARTITION BY key),0) and x / NULLIF(SUM(x) OVER(),0).

Pitfalls
- Windowing raw rows creates noisy and heavy computations; pre-aggregate first.
- Filtering on windowed values in the same SELECT; wrap in another SELECT to filter.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- CTEs: https://www.postgresql.org/docs/current/queries-with.html
- Windows: https://www.postgresql.org/docs/current/tutorial-window.html
