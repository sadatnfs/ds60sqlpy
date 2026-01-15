# 00 — Setup: Schema, Seed Data, and How to Run Safely (Companion Guide)

Purpose
- Create a self-contained training schema named training with realistic tables and data.
- Ensure every day’s script can be run and reverted safely via BEGIN/ROLLBACK.

What this script does
- Sets search_path to training so unqualified names like orders refer to training.orders.
- Creates core tables:
  - customers(id, name, email, created_at, status, segment, …)
  - products(id, sku, name, category, price, cost, active, …)
  - orders(id, customer_id, order_date, status, total, …)
  - order_items(id, order_id, product_id, qty, unit_price, discount)
  - payments(id, order_id, payment_date, method, amount, status)
- Organization tables:
  - employees(id, first_name, last_name, title, department_id, manager_id, hired_at)
  - departments(id, name)
- Analytics helpers:
  - events(id, customer_id, occurred_at, kind, payload JSONB)
  - expenses(id, dt, department_id, amount, category)
  - budgets(id, period, department_id, amount)
  - promotions(id, code, starts_at, ends_at, pct_off)
  - xml_docs(id, doc XML)
- Seeds thousands of rows across these tables with consistent FK relationships.
- Adds representative indexes and constraints (PKs, FKs, unique, check constraints).

How to run and reset safely
- Scripts are wrapped in a transaction (BEGIN … ROLLBACK). Replace ROLLBACK with COMMIT to make changes persistent.
- Re-running 00_setup.md is idempotent in spirit: if you need to reset the schema completely, drop and recreate the database or drop schema training cascade; then run 00_setup.sql again.

Naming and conventions used throughout the curriculum
- Lower_snake_case identifiers, singular table names for entities; associative tables as needed.
- Surrogate primary keys (bigint/serial/identity) with FK constraints.
- Timestamps use timestamptz (UTC) unless otherwise noted.
- Monetary values use numeric(12,2) for precision; avoid float for currency.

Data volumes (approx.)
- customers: 10–50k
- products: 1–5k
- orders: 100–500k
- order_items: 300k–1.5M
- events: 500k+ (JSONB heavy)
- employees: few hundred (org hierarchy)

Tips
- Use EXPLAIN ANALYZE early to build intuition about performance.
- When writing queries, qualify ambiguous columns (e.g., o.id vs oi.id) and alias tables consistently.

Validation checklist after running setup
- SELECT count(*) from each table to confirm non-zero row counts.
- Check foreign keys by joining e.g., order_items → orders → customers should all match.
- SELECT payload->>'event' as e, count(*) FROM events GROUP BY 1 ORDER BY 2 DESC; should show variety of event kinds.
