# Day 21 — Distribution Functions: NTILE, PERCENT_RANK, CUME_DIST (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 20 — first, last, and Nth values](day20_first_last_value.md)
- **Artifacts:** [learner SQL](../day21_distribution_functions.sql) ·
  [solution reasoning](../solutions/day21_solutions.md) ·
  [executable solution](../solutions/day21_solutions.sql)

## Learning objectives

- Place ordered observations into buckets and relative distribution positions.
- Explain tie handling and small-partition limitations.

## Vocabulary and concepts

- **Quantile bucket:** one of N approximately equal row-count groups from
  `NTILE(N)`.
- **Percent rank:** relative rank from 0 through 1 based on rank position.
- **Cumulative distribution:** the fraction of rows less than or equal to the
  current peer group.

## Worked example / walkthrough

Apply `NTILE(4)`, `PERCENT_RANK`, and `CUME_DIST` to a five-row `VALUES` set
containing a tie. Observe that buckets need not have equal value ranges and that
peer-aware distribution functions treat equal ordering values together.

## Exercises

Complete the prompts in the [learner SQL](../day21_distribution_functions.sql).
Repeat one calculation on a partition smaller than the requested bucket count.

## Self-check

- Are the outputs described as row-position summaries rather than guaranteed
  business segments?
- Can you explain how ties affect each function?

## Next step

Continue to [Day 22 — advanced windows](day22_advanced_windows.md).

## Deep dive and reference

Learning objectives
- Bin ordered data into quantiles/tiles with NTILE
- Compute relative position within a partition via PERCENT_RANK and CUME_DIST
- Use distribution metrics for scoring, segmentation, and anomaly thresholds

Why this matters
Quantiles and ranks model relative standing robustly in skewed data and support thresholding without assuming normality.

Core concepts and deep dive
- NTILE(n) OVER (PARTITION BY k ORDER BY x): assigns tile indices 1..n with sizes as equal as possible.
- PERCENT_RANK() = (rank-1) / (count-1); 0 to 1 inclusive; undefined for single-row partitions (returns 0).
- CUME_DIST() = (number of rows with value <= current) / count; non-decreasing; useful for percentile-style thresholds.

Patterns
- Score bands: NTILE(10) deciles for customers by LTV.
- Top x% filters: WHERE CUME_DIST() OVER (...) >= 0.95 to flag extremes.
- Percentile thresholds: compute p95 within groups and join back.

Pitfalls
- Non-unique ORDER BY yields arbitrary rankings among ties; define tie policy.
- NTILE with small partitions creates imbalanced tiles; consider minimum partition size.

Exercises from the learner script
1) Bucket products into deciles by units sold during the last 90 days.
2) Compute each order's percentile rank by `total_amount` within its customer.

Aggregate to one row per product before `NTILE(10)` and retain unsold products
with a left join. `PERCENT_RANK` is ordered ascending in the maintained answer,
so 0 is the customer's lowest order and 1 is the highest when the partition has
more than one row.

Further reading
- Distribution: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW
