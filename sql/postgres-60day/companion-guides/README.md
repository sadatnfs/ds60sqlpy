# Companion Guides — PostgreSQL Advanced SQL 60-Day Curriculum

This folder contains narrative, text-only companion guides for each daily SQL script in `../`. Use these as pre-reads and references while you run the matching `.sql` files against the `advanced_sql_training` database created by `00_setup.sql`.

Conventions
- Scripts and guides begin with safe transaction blocks (BEGIN/ROLLBACK). Replace ROLLBACK with COMMIT if you want to persist changes.
- All examples assume `search_path` includes the `training` schema created by setup.
- Tables you will commonly see: customers, products, orders, order_items, payments, employees, departments, expenses, budgets, promotions, events (JSONB), xml_docs, and helper views.

Index (high-level)
- 00_setup — schema and seed data overview
- 01–07 core SQL & joins; 08–15 subqueries, DML, CASE, strings/dates/numerics; week 1 project
- 16–22 windows; 23–30 CTEs, pivoting, JSON/XML, patterns; week 2 project
- 31–37 plans, indexes, optimization, partitioning; 38–45 transactions/locks/ops; phase 3 project
- 46–48 Project 1 (e‑commerce): LTV, cohorts, funnels, payback
- 49–51 Project 2 (finance): positions/P&L, risk, reconciliation
- 52–54 Project 3 (DWH): modeling, SCD, aggregates/marts
- 55–57 Project 4 (BI): semantic views, RLS, caching/refresh
- 58–60 Final capstone: ingest/clean, model/KPIs, package/hand‑off
