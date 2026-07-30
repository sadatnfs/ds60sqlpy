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

## Practice assumptions and review method

- **Focus:** Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
- **Assumptions:** Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
- **Failure to watch for:** Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Show each order with the customer's average order total.
   **Progressive hint:** Partition by customer ID and keep one output row per order.
   **Expected shape:** One row per order.
2. **Query writing:** Show each employee salary with department average, minimum, and maximum.
   **Progressive hint:** Partition all three window aggregates by department.
   **Expected shape:** One row per employee.
3. **Query writing:** Calculate every order's share of its customer's stored revenue.
   **Progressive hint:** Use a partition total denominator and guard it with `NULLIF`.
   **Expected shape:** One row per order with shares summing near one per customer.
4. **Prediction:** Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.
   **Progressive hint:** Grouping collapses to one row per customer; a window preserves every order row.
   **Expected shape:** Two labeled count rows.
5. **Debugging:** Return orders above their customer average without placing a window function in `WHERE`.
   **Progressive hint:** Compute the window value in a CTE, then filter the named column outside.
   **Expected shape:** Order rows above their customer mean.
6. **Extension:** Show order count and revenue context at both customer and country levels in the same row.
   **Progressive hint:** Use different partitions for independent analytical contexts.
   **Expected shape:** One row per order with customer and country totals.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Postgres windows: https://www.postgresql.org/docs/current/tutorial-window.html
- Frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
