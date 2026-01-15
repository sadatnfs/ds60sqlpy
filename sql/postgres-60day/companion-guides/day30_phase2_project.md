# Day 30 — Phase 2 Project: Windows, CTEs, and Pivoting (Companion Guide)

Goal
- Deliver a multi-faceted analysis that combines CTE pipelines, window functions, and reshaping (pivot/unpivot) into a coherent report.

What you’ll build
- CTE staging of order lines → monthly/category aggregates → windowed KPIs (rolling, shares) → pivot to presentation shape.
- Clear validation section using totals checks and EXPLAIN for hot queries.

Guidance
1) Stage order-level revenue in order_lines (per order_id) to avoid fanout when joining customers/products.
2) Pre-aggregate to monthly by category/country; index predicates on (category, month) or (country, month) if needed.
3) Apply windows for cumulative/rolling metrics; prefer ROWS frames.
4) Shape output: conditional aggregation or crosstab for months across columns.
5) Add a DQ slice: count NULL categories, detect outliers via z-scores, and list zero-sales products.

Quality checklist
- Correctness: row counts/base totals trace back to source.
- Performance: no unnecessary DISTINCT; appropriate indexes considered.
- Reproducibility: parameters (date range, segments) easy to change.

Stretch goals
- Parameterize categories to include as columns; move the rest into an "Other" bucket.
- Persist a materialized view for the monthly summary and compare performance.
