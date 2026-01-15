# Day 55 — Project 4: BI and Semantic Layer (Part 1) — Metrics and Views (Companion Guide)

Objectives
- Define clear metric semantics (dimensions, filters, aggregations)
- Create BI‑friendly views that encapsulate join logic and flags
- Ensure compatibility with common BI tools (nullable dtypes, surrogate keys)

Metrics layer
- Document metrics: revenue, orders, AOV, active_customers, retention_rate
- For each metric, define: grain, formula, allowed dimensions, filters, null handling

BI views
- views.v_orders_enriched: orders joined to dims with clean flags (is_first_order, is_return)
- views.v_daily_kpis: daily aggregates with stable column names and dtypes

Pitfalls
- Hidden business logic in dashboards; centralize logic in SQL views
- Using raw IDs without human‑readable labels; join labels in views

Deliverables
- Metrics dictionary and at least two BI views

Stretch goals
- Explore dbt‑style semantic layer patterns (if applicable)
