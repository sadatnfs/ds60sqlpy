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

## Exercises

Complete the prompts in the [learner SQL](../day19_running_aggregates.sql).
Report both row count and earliest date in each moving frame so its meaning is
auditable.

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

Exercises from the learner script
1) Compute a 30-day moving revenue sum and average.
2) For each category and product, compute cumulative quantity sold by product
   order date.

For a literal 30-calendar-day frame, first create a dense daily calendar and
fill missing revenue with zero, then use `ROWS BETWEEN 29 PRECEDING AND CURRENT
ROW`. On raw observed days, 30 rows need not equal 30 calendar days.

Further reading
- Window frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
