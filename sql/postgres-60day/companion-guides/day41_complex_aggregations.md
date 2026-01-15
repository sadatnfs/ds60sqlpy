# Day 41 — Complex Aggregations and Advanced GROUP BY (Companion Guide)

Learning objectives
- Master conditional aggregation and FILTER to compute many metrics in one pass
- Combine grouping sets (ROLLUP/CUBE) with windowed post-aggregations
- Use ordered-set aggregates (percentiles) alongside classic stats
- Structure multi-stage aggregates safely to avoid fanout and miscounts

Why this matters
Real reports mix totals, subtotals, rates, and percentiles. Efficiently computing all of them in one query reduces compute and keeps logic consistent.

Core concepts and deep dive
- Conditional aggregation
  - SUM(CASE WHEN status='completed' THEN amount ELSE 0 END) AS completed_amt
  - COUNT(*) FILTER (WHERE status='refunded') AS refunds  -- clearer and faster in Postgres
- Multi-metric patterns
  - Compute counts, sums, distinct customers, and conversion rates without extra joins using FILTER/CASE
  - Example metrics per month: orders, distinct customers, revenue, AOV, refund_rate, on-time_rate
- Grouping sets, ROLLUP, CUBE
  - Generate grand totals and subtotals across dimensions; detect with GROUPING() to label subtotal rows
  - Present results with a stable ordering: subtotals after detail rows
- Ordered-set aggregates and stats
  - PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY order_amount) AS p50
  - p90/p95 for tails; combine with STDDEV_SAMP/VAR_POP for dispersion
- Post-aggregation windows
  - After GROUP BY at a desired grain (e.g., month), apply window functions for running totals and shares across the grouped rows

Design patterns
- Stage details → aggregate to grain (CTE) → compute windows → add percentiles with GROUP BY + ordered-set
- Add safety via NULLIF in denominators and COALESCE for presentation

Pitfalls
- DISTINCT inside aggregates can be costly; prefer pre-dedup in a CTE when possible
- Mixed grains: ensure all columns in SELECT are group keys or aggregates at the current level
- Re-aggregating already-aggregated rows; wrap carefully or recompute at the correct grain

Practice exercises
1) Build a monthly KPI table with orders, revenue, distinct customers, AOV, refund_rate, on_time_rate in one query using FILTER.
2) Add p50/p90 order amounts alongside averages per month.
3) Extend with ROLLUP over (country, month) and label subtotal rows with GROUPING().

Further reading
- Aggregates and FILTER: https://www.postgresql.org/docs/current/functions-aggregate.html
- Ordered-set aggregates: https://www.postgresql.org/docs/current/functions-aggregate.html#FUNCTIONS-ORDEREDSET-TABLE
