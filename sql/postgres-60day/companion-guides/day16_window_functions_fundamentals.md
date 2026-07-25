# Day 16 — Window Functions Fundamentals: OVER, PARTITION BY, ORDER BY, Frames (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 15 — Phase 1 project](day15_phase1_project.md), including
  grouped aggregates and declared result grain
- **Artifacts:** [learner SQL](../day16_window_functions_fundamentals.sql) ·
  [solution reasoning](../solutions/day16_solutions.md) ·
  [executable solution](../solutions/day16_solutions.sql)

## Learning objectives

- Add partition-level and running metrics without collapsing detail rows.
- Choose an explicit `ROWS` frame when peer-aware `RANGE` behavior is not
  intended.

## Vocabulary and concepts

- **Window:** the related rows visible to a window function for one result row.
- **Partition:** an independent window group created by `PARTITION BY`.
- **Frame:** the ordered subset of a partition used for the current row.

## Worked example / walkthrough

Pre-aggregate net revenue to one row per category, then calculate
`SUM(revenue) OVER ()` beside each category. The ordinary aggregate establishes
the category grain; the window exposes the grand total without removing those
category rows.

## Exercises

Complete the prompts in the [learner SQL](../day16_window_functions_fundamentals.sql).
Create tied ordering values and compare the default frame with
`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.

## Self-check

- Does the result retain the intended number of detail rows?
- Can you state the partition, ordering, and frame for every window expression?

## Next step

Continue to [Day 17 — ranking functions](day17_rank_functions.md).

## Deep dive and reference

Learning objectives
- Understand what a window is and how window functions differ from aggregates
- Use OVER() with PARTITION BY and ORDER BY to compute per-row metrics without collapsing rows
- Control frames with ROWS/RANGE; grasp default frames and their impact
- Combine multiple window functions in the same SELECT

Why this matters
Window functions unlock powerful analytics: running totals, per-customer averages alongside each row, shares of totals, and rank-based features, all without subqueries that collapse results.

Core concepts and deep dive
- Window vs aggregate
  - Aggregates (SUM, AVG, COUNT) collapse groups into a single row.
  - Window functions compute values across a set of rows related to the current row, but keep one row per input row.
- OVER() clause
  - PARTITION BY defines independent windows (e.g., per customer or per category).
  - ORDER BY defines an order within each partition enabling running/lagged calculations.
  - You can define named windows via WINDOW w AS (PARTITION BY ... ORDER BY ...).
- Default frame
  - If you specify ORDER BY without an explicit frame, the default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.
  - RANGE groups peers with equal ORDER BY values; SUM(RANGE ...) may include more rows than expected when there are ties.
  - Prefer ROWS BETWEEN ... for precise row-count frames: ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW for cumulative sums, or ROWS BETWEEN 6 PRECEDING AND CURRENT ROW for 7-row rolling.
- Mixing GROUP BY and window functions
  - You may compute aggregates in a subquery/CTE then apply window functions to the aggregated rows, or vice versa. Know which level is appropriate for your metric.

Walkthrough of the day’s script
- Category share of total revenue: a CTE first produces one row per category,
  then `SUM(revenue) OVER ()` exposes the grand total without collapsing those
  category rows.
- Customer-level windows: AVG(total_amount) OVER (PARTITION BY customer_id) and COUNT(*) OVER (PARTITION BY customer_id) produce lifetime averages and counts joined to each order without GROUP BY.
- Rolling window: SUM(revenue) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) computes a 7-day moving total. Note the explicit ROWS frame to avoid RANGE pitfalls.

Patterns to master
- Running total: SUM(x) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
- Percent of partition: x / NULLIF(SUM(x) OVER (PARTITION BY k),0)
- Windowed average/stddev for anomaly detection

Pitfalls
- Mixing RANGE with non-unique ORDER BY can include ties; use ROWS for exact counts.
- Window functions run after WHERE but before ORDER BY LIMIT at the outermost level; to filter on a windowed value, wrap in a subquery.
- Performance: Heavy windows over millions of rows may spill; ensure indexes on partition/order keys.

Exercises from the learner script
1) For each order, show its total and the customer's lifetime total alongside
   it.
2) For each category, show each product's net line revenue and its share of
   category revenue.

The maintained answer also computes each order's share of customer lifetime
revenue as a useful extension. Include unsold products with a dimension-first
`LEFT JOIN` if the report must cover the entire catalog.

Further reading
- Postgres windows: https://www.postgresql.org/docs/current/tutorial-window.html
- Frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
