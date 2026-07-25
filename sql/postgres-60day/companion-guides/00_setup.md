# 00 — Setup: Schema, Seed Data, and How to Run Safely (Companion Guide)

Purpose
- Create a self-contained training schema named training with realistic tables and data.
- Provide stable, varied data for joins, windows, time series, JSONB, XML, and projects.

What this script does
- Drops and recreates the course-owned `training` schema, then sets `search_path` so unqualified names such as `orders` resolve to `training.orders`.
- Creates core tables:
  - `customers(customer_id, full_name, email, country, created_at, segment, attributes)`
  - `products(product_id, name, category, price, cost, created_at)`
  - `orders(order_id, customer_id, order_date, status, total_amount)`
  - `order_items(order_item_id, order_id, product_id, quantity, unit_price, discount)`
  - `payments(payment_id, order_id, payment_date, amount, method)`
- Organization tables:
  - `employees(employee_id, full_name, manager_id, department_id, hire_date, salary)`
  - `departments(department_id, name)`
- Analytics helpers:
  - `events(event_id, customer_id, event_time, event_type, metadata JSONB)`
  - `expenses(expense_id, category, amount, expense_date)`
  - `budgets(budget_id, category, period, amount)`
  - `promotions(promotion_id, product_id, start_date, end_date, discount_rate)`
  - `xml_docs(doc_id, payload XML, created_at)`
- Seeds deterministic relationships and categories. Dates are relative to
  `CURRENT_DATE`, so “last N days” lessons stay live without making repeated
  setup runs structurally random.
- Adds primary-key, foreign-key, unique, and check constraints.

How to run and reset safely
- Run setup and its executable invariant checks from the repository root:
  `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql`,
  then run the same command with `00_verify.sql`.
- Re-running `00_setup.sql` drops and recreates the disposable `training` schema. Never run it against a database that contains data you care about.
- Most lesson scripts use `BEGIN` and `ROLLBACK`. The stated exception is the
  Days 52–54 warehouse project: Day 52 resets and commits the course-owned
  `dwh` schema for Days 53 and 54, so run those lessons in order.

Naming and conventions used throughout the curriculum
- Lower_snake_case identifiers, singular table names for entities; associative tables as needed.
- Surrogate primary keys (bigint/serial/identity) with FK constraints.
- Timestamps use timestamptz (UTC) unless otherwise noted.
- Monetary values use numeric(12,2) for precision; avoid float for currency.

Deterministic data volumes
- customers: 500
- products: 300
- orders: 4,362 across 438 customers; BR is intentionally an event-only market
- order_items: 13,085, covering 275 products; 25 products intentionally remain unsold
- payments: 3,836, including fully paid, partially paid, and split-payment examples
- events: 20,000
- employees: 100
- expenses: 10,000
- budgets: 125
- promotions: 200
- XML documents: 1,000

Tips
- Use EXPLAIN ANALYZE early to build intuition about performance.
- When writing queries, qualify ambiguous columns (e.g., o.id vs oi.id) and alias tables consistently.

Validation checklist after running setup
- Run `00_verify.sql`; a broken count, coverage rule, chronology rule, total, or
  foreign-key relationship raises an error and stops `psql`.
- Inspect variety with
  `SELECT event_type, metadata->>'device', count(*) FROM events GROUP BY 1, 2 ORDER BY 3 DESC;`.
- Re-run setup followed by verify whenever you want a known-clean training
  dataset.
