# Day 19 — Running Aggregates and Moving Windows (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 18 — LAG and LEAD](day18_lag_lead.md)
- **Artifacts:** [learner SQL](../day19_running_aggregates.sql) ·
  [solution reasoning](../solutions/day19_solutions.md) ·
  [executable solution](../solutions/day19_solutions.sql)

## Learning objectives

- Calculate cumulative and moving aggregates with explicit frames.
- Explain whether a frame counts observations, peer groups, or elapsed time.

## Vocabulary and concepts

- **Cumulative aggregate:** a summary from the partition start through the
  current row.
- **Moving window:** a bounded frame around or before the current row.
- **Observation:** one row at the grain supplied to the window calculation.

## Worked example / walkthrough

Aggregate orders to daily revenue, then apply
`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`. This includes at most seven observed
order dates, not automatically seven calendar days. Compare it with a
date-spined input that includes zero-revenue days.

## Practice assumptions and review method

- **Focus:** Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
- **Assumptions:** Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
- **Failure to watch for:** Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate cumulative stored revenue across all orders.
   **Progressive hint:** Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.
   **Expected shape:** One row per order with nondecreasing cumulative revenue.
2. **Query writing:** Calculate each customer's cumulative stored spend.
   **Progressive hint:** Partition by customer and reset the explicit row frame for every customer.
   **Expected shape:** One row per order.
3. **Query writing:** Calculate a trailing seven-order average within each customer.
   **Progressive hint:** A seven-row frame is based on observations, not seven calendar days.
   **Expected shape:** One row per order with up to seven observations in its frame.
4. **Prediction:** Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
   **Progressive hint:** `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
   **Expected shape:** Three rows making the peer difference visible.
5. **Debugging:** Reset a running expense total at each category and month.
   **Progressive hint:** Partition by both reset keys and order by date plus expense ID.
   **Expected shape:** One row per expense.
6. **Extension:** Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
   **Progressive hint:** Select the last ordered cumulative value and compare it with an independent aggregate.
   **Expected shape:** One row with zero difference.

## Self-check

- Does the input grain match the period named in the metric?
- Are ties and missing dates treated deliberately rather than by a default
  frame?

## Next step

Continue to [Day 20 — first, last, and Nth values](day20_first_last_value.md).

## Deep dive and reference

Learning objectives
- Compute cumulative sums/averages and moving windows
- Choose ROWS vs RANGE frames and understand their semantics
- Build KPI baselines and rolling signals

Why this matters
Rolling and cumulative metrics stabilize noisy data and reveal trends and seasonality.

Core concepts and deep dive
- Cumulative: SUM(x) OVER (ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW).
- Moving average: AVG(x) OVER (ORDER BY t ROWS BETWEEN n PRECEDING AND CURRENT ROW).
- RANGE vs ROWS: RANGE groups peers by value; ROWS counts physical rows — prefer ROWS for exact ‘last N rows/days after aggregation’.
- Partitioned cumulatives: add PARTITION BY to reset per key (e.g., customer_id, category).

Patterns
- Rolling 7/28-day revenue; cumulative MTD/QTD/ YTD by combining date_trunc and partitions.
- Baseline with stddev bands using STDDEV_SAMP over the same frame for anomaly z-scores.

Pitfalls
- Applying window over raw transactional rows when you intended daily aggregates; pre-aggregate first.
- Filtering on a windowed column in the same SELECT; wrap in subquery to allow WHERE on computed value.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Window frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
