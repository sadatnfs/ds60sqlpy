PostgreSQL Advanced SQL 60-Day Curriculum

Beginner-friendly setup and how to run each day (with fixes for common role/connection errors)

What you will do
- Install PostgreSQL (or use Docker)
- Create a training database once
- Load the sample schema/data once (00_setup.sql)
- Run one daily script at a time (day01 ... day60)
- By default, daily scripts ROLLBACK so your DB stays unchanged unless you COMMIT

Quick start by environment
- macOS (Homebrew) — simplest path (use your macOS username as the DB role):
  1) brew install postgresql@16
  2) brew services start postgresql@16
  3) psql -h localhost
     - CREATE DATABASE advanced_sql_training; \q
  4) psql -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  5) psql -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql

- macOS (Homebrew) — create canonical postgres superuser (fix for "role 'postgres' does not exist"):
  1) brew services start postgresql@16
  2) psql -h localhost
     - CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';
     - \q
  3) psql -U postgres -h localhost -c "CREATE DATABASE advanced_sql_training;"
  4) psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  5) psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql

- Docker (no local install):
  1) docker run --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
  2) docker exec -it pg psql -U postgres -c "CREATE DATABASE advanced_sql_training;"
  3) cat sql/postgres-60day/00_setup.sql | docker exec -i pg psql -U postgres -d advanced_sql_training
  4) cat sql/postgres-60day/day01_select_where_orderby.sql | docker exec -i pg psql -U postgres -d advanced_sql_training

- Linux (Debian/Ubuntu):
  1) sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib
  2) sudo service postgresql start
  3) sudo -u postgres psql -c "CREATE DATABASE advanced_sql_training;"
  4) psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  5) psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql

- Windows (installer):
  1) Install from https://www.postgresql.org/download/windows/ (remember superuser+password)
  2) Open "SQL Shell (psql)" and run:
     - CREATE DATABASE advanced_sql_training;
     - \q
  3) From Command Prompt/PowerShell:
     - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
     - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql

Run daily scripts one by one (safe by default)
- Example (no superuser specified):
  - psql -d advanced_sql_training -f sql/postgres-60day/day02_aggregates_groupby_having.sql
- Example (explicit postgres superuser):
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day02_aggregates_groupby_having.sql
- Docker example:
  - cat sql/postgres-60day/day02_aggregates_groupby_having.sql | docker exec -i pg psql -U postgres -d advanced_sql_training
- Safety: Each script starts with BEGIN; and ends with ROLLBACK; so the database returns to its prior state after running. Replace ROLLBACK with COMMIT to keep changes.

If you want changes to persist
- Two choices:
  1) Edit the day’s .sql and change the final ROLLBACK; to COMMIT; then run it.
  2) Copy the statements you want to keep into your own .sql file or into an interactive psql session and wrap with BEGIN; ... COMMIT;
- Note: DDL (e.g., CREATE MATERIALIZED VIEW, CREATE INDEX, CREATE TABLE) is also rolled back unless you COMMIT.

Using a GUI instead of psql (optional)
- pgAdmin:
  - Connect to localhost:5432, create advanced_sql_training (if not created), run 00_setup.sql, then each dayXX_*.sql
- DBeaver:
  - Create a PostgreSQL connection, create DB, run 00_setup.sql and each day script via SQL Editor

Common troubleshooting and fixes (applies to all calls)
- Error: psql: error: connection to server at "localhost" failed
  - Ensure the server is running:
    - macOS: brew services start postgresql@16
    - Linux: sudo service postgresql start
    - Docker: docker ps (ensure container named pg is up)
- Error: role "postgres" does not exist (macOS/Homebrew installs commonly)
  - Fix A (use your macOS username as DB role):
    - psql -h localhost
    - CREATE DATABASE advanced_sql_training; \q
    - psql -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  - Fix B (create canonical postgres superuser):
    - psql -h localhost
    - CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres'; \q
    - psql -U postgres -h localhost -c "CREATE DATABASE advanced_sql_training;"
    - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  - Fix C (CLI):
    - createuser -s postgres
- Error: createdb or psql: command not found
  - Install or add to PATH:
    - macOS: brew install postgresql@16
    - Windows: use "SQL Shell (psql)" or add PostgreSQL bin to PATH
    - Or use Docker flow above without installing psql locally
- Permission denied on COPY
  - Use client-side \copy or run from an accessible directory; the curriculum does not require server-side COPY by default
- Linter warnings about BEGIN/ROLLBACK
  - Many editors warn on transaction blocks at top level; scripts are meant for psql and work fine. Change ROLLBACK to COMMIT to persist when desired.

What 00_setup.sql creates
- Schema training (scripts set search_path to training)
- Core tables: customers, products, orders, order_items, payments
- Org tables: employees, departments
- Analytics helpers: events (JSONB), expenses, budgets, promotions
- XML sample: xml_docs
- Thousands of realistic rows for joins, windows, CTEs, JSON/XML, and performance labs

Daily script map (high level)
- Days 1–7: Core SQL & Joins
- Days 8–15: Subqueries, DML, CASE, string/date/number functions; Phase 1 project
- Days 16–22: Window functions; Days 23–30: CTEs, pivoting, JSON/XML, patterns; Phase 2 project
- Days 31–37: EXPLAIN/ANALYZE, indexing, optimization, partitioning
- Days 38–45: Transactions, locks, analytics, data quality, ops; Phase 3 optimization project
- Days 46–60: Capstone projects (e-commerce, finance, data warehouse, BI, integrated challenge)

Cheat sheet (copy/paste variants for all calls)
- macOS — use local user role:
  - psql -h localhost
  - CREATE DATABASE advanced_sql_training; \q
  - psql -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  - psql -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
- macOS — create postgres superuser:
  - psql -h localhost -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';"
  - psql -U postgres -h localhost -c "CREATE DATABASE advanced_sql_training;"
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
- Docker:
  - docker run --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
  - docker exec -it pg psql -U postgres -c "CREATE DATABASE advanced_sql_training;"
  - cat sql/postgres-60day/00_setup.sql | docker exec -i pg psql -U postgres -d advanced_sql_training
  - cat sql/postgres-60day/day01_select_where_orderby.sql | docker exec -i pg psql -U postgres -d advanced_sql_training
- Linux:
  - sudo -u postgres psql -c "CREATE DATABASE advanced_sql_training;"
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
- Windows:
  - Use SQL Shell (psql) to CREATE DATABASE advanced_sql_training; \q
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
  - psql -U postgres -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql

You’re ready to start. Begin with Day 1 and verify the sample queries return rows. If anything fails, use the fixes above for your environment or share your exact error and OS for a tailored command pair.
