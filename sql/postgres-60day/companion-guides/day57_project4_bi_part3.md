# Day 57 — Project 4: BI (Part 3) — Performance, Caching, and Dashboards (Companion Guide)

Objectives
- Optimize BI queries for responsiveness; pre‑aggregate where needed
- Use materialized views and cache invalidation strategies
- Design dashboard queries for incremental refresh

Techniques
- Pre‑aggregate to day/segment; JOIN to dims only on keys within views
- MATERIALIZED VIEW with CONCURRENT refresh; store last_refreshed timestamp
- Incremental refresh windows (last N days) for rolling dashboards

Operational
- Monitor BI workloads via pg_stat_statements; cap query timeouts
- Document refresh SLAs and fallbacks when cache stale

Pitfalls
- Overly dynamic pivoting in SQL causing recompile; prefer fixed schemas for BI
- Full table scans on dashboards; ensure date filters and matching indexes

Deliverables
- A refreshed MV powering a dashboard and the dashboard query templates

Stretch goals
- Use logical replication or read replicas for BI workloads
