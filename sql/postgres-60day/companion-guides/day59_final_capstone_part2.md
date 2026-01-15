# Day 59 — Final Capstone (Part 2) — Modeling and KPIs (Companion Guide)

Objectives
- Model cleaned data into facts/dims suitable for analytics
- Build core KPIs and cohort/retention/LTV views
- Validate with reconciliation and spot checks

Steps
- Build dim_customer (SCD choice), dim_country, dim_segment
- Build fact_order/fact_order_item; compute revenue (qty × price × (1−discount))
- Views: daily_kpis, cohort_retention, ltv_curves using windows and aggregates

Quality
- Reconcile total revenue against orders/items; exception report for mismatches
- Null checks and category validation against dims

Deliverables
- Schema DDL and KPI view definitions

Stretch goals
- Parameterize KPI views by date range and segments
- Materialize heavy KPIs for dashboards
