# Day 54 — Project 3: Data Warehouse (Part 3) — Aggregate Tables and Marts (Companion Guide)

Objectives
- Build aggregate fact tables for common queries (daily revenue by segment, category)
- Schedule refreshes and manage incremental updates
- Document lineage and quality checks

Aggregates
- daily_revenue(dim keys..., day, revenue, orders, customers)
- Use INSERT INTO ... SELECT ... FROM fact_order_item GROUP BY ... for full rebuild
- For incremental loads, restrict by day >= :last_loaded_day; handle late arriving facts

Indexes and MVs
- Consider MATERIALIZED VIEW for complex rollups; add unique index and CONCURRENT refresh
- Add indexes on (day, segment/category) for common filters

Quality
- Reconcile aggregates to detail fact totals by day; exception on mismatch > threshold
- Track row counts per day to detect gaps

Pitfalls
- Double counting due to joining to dims at detail level after aggregation; join dims before aggregate or via keys only
- Incremental logic missing late corrections; periodically run a backfill window

Deliverables
- One or more aggregate tables with refresh script and validation queries

Stretch goals
- Aggregate by week (ISO), month; use date_dim to drive calendar completeness
- Partition large aggregate tables by month for faster maintenance
