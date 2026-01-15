# Day 40 — Analytic Functions (Advanced): Stats, Percentiles, Ratios (Companion Guide)

Learning objectives
- Compute rolling statistics with explicit ROWS frames and understand RANGE vs ROWS
- Use percentile functions (PERCENTILE_CONT/DISC) correctly with GROUP BY
- Derive ratio-to-total and z-scores within partitions for anomaly detection

Why this matters
Beyond simple windows, you’ll need robust statistics to quantify seasonality, volatility, and extremes. Correct frames and percentiles prevent subtle mistakes that mislead decisions.

Core concepts and deep dive
- Frame semantics
  - ORDER BY in OVER without an explicit frame defaults to RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW; peers with equal ORDER BY value are included
  - Prefer ROWS BETWEEN n PRECEDING AND CURRENT ROW for fixed-size windows (e.g., 7-day)
- Rolling statistics
  - AVG/STDDEV_SAMP over ROWS frames to capture local mean/volatility;
  - Use these to produce control-band z-scores: (x - avg_w)/NULLIF(std_w,0)
- Percentiles
  - PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY x) computes the continuous percentile across the set defined by GROUP BY
  - For partitioned percentiles, pre-aggregate into groups (e.g., by month) then compute percentiles per group
- Ratio to total
  - x / NULLIF(SUM(x) OVER (),0) for global share; x / NULLIF(SUM(x) OVER (PARTITION BY k),0) for within-group share

Walkthrough of the day’s script
- Daily revenue series then 15-day moving mean/variance with ROWS BETWEEN 14 PRECEDING AND CURRENT ROW — note the explicit frame
- Monthly order-amount percentiles (p50/p90/p99) using PERCENTILE_CONT with GROUP BY month
- Category revenue shares via SUM(revenue) OVER ()

Pitfalls
- Using RANGE when duplicates exist in ORDER BY can inflate frames; switch to ROWS
- Applying percentile functions without GROUP BY yields a single percentile across the whole set, not per period
- Dividing by total without NULLIF can raise divide-by-zero for empty partitions

Practice exercises
1) Compute 30-day rolling mean and stddev of daily revenue; flag days with |z|>2
2) Compute p25/p50/p75 of order amounts per category-month and compare dispersion
3) Calculate each product’s share of category revenue and rank by share

Further reading
- Window frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS
- Ordered-set aggregates: https://www.postgresql.org/docs/current/functions-aggregate.html#FUNCTIONS-ORDEREDSET-TABLE
