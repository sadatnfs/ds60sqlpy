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

## Practice assumptions and review method

- **Focus:** Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.
- **Assumptions:** `PERCENT_RANK` ranges from 0 to 1 using rank; `CUME_DIST` is the fraction at or below the current value; `NTILE` balances row counts.
- **Failure to watch for:** A percentile rank is not a probability or causal score, and `NTILE(10)` does not guarantee equal value ranges.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Assign customers to four stored-spend buckets.
   **Progressive hint:** Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.
   **Expected shape:** One row per ordering customer with bucket 1–4.
2. **Query writing:** Calculate salary percent rank within each department.
   **Progressive hint:** Partition by department and rank on salary alone so tied salaries share rank.
   **Expected shape:** One row per employee with values from 0 to 1.
3. **Query writing:** Calculate cumulative distribution of product price within category.
   **Progressive hint:** Partition by category and order on price.
   **Expected shape:** One row per product with cume_dist in (0, 1].
4. **Prediction:** Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
   **Progressive hint:** Tied values share rank and cumulative endpoint, but the two functions use different formulas.
   **Expected shape:** Three rows making tie behavior visible.
5. **Debugging:** Audit the row count in each customer spend decile rather than assuming exact equality.
   **Progressive hint:** NTILE bucket sizes differ by at most one when row count is not divisible by ten.
   **Expected shape:** Up to 10 bucket rows with counts.
6. **Extension:** Return customers in the top stored-spend decile with their spend and population share.
   **Progressive hint:** Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
   **Expected shape:** Customers in decile 1.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Distribution: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW
