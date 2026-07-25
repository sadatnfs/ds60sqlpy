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

## Exercises

Complete the prompts in the [learner SQL](../day26_ctes_with_windows.sql). For
the top-five exercise, compare `ROW_NUMBER` with `RANK` on a tied value.

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

Exercises from the learner script
1) Build a multi-stage CTE that computes monthly totals and then
   month-over-month growth with `LAG`.
2) For each product, return its top five orders by that product's net line
   value using a CTE plus a window rank.

Filter a window rank in an outer query because PostgreSQL has no `QUALIFY`
clause. Use `ROW_NUMBER` for at most five rows per product or a tie-aware rank
when the requirement allows more than five.

Further reading
- CTEs: https://www.postgresql.org/docs/current/queries-with.html
- Windows: https://www.postgresql.org/docs/current/tutorial-window.html
