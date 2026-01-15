# Day 42 — Data Quality and Validation in SQL (Companion Guide)

Learning objectives
- Encode business rules with constraints (NOT NULL, CHECK, UNIQUE, FK, EXCLUDE)
- Detect anomalies with profiling queries and schema tests
- Build reproducible validation suites you can run in CI

Why this matters
Analytics and downstream apps depend on trustworthy data. Catching schema drift, out‑of‑range values, referential breaks, or malformed text early prevents expensive rework and bad decisions.

Core concepts and deep dive
- Declarative integrity
  - NOT NULL for mandatory fields; CHECK for ranges/enums; UNIQUE for keys; FOREIGN KEY for referential integrity; EXCLUDE for complex constraints (ranges, overlaps)
  - DEFERRABLE INITIALLY DEFERRED for multi‑row invariants within a transaction
- Profiling queries (templates)
  - Completeness: SELECT COUNT(*) FILTER (WHERE col IS NULL)/COUNT(*) AS null_rate FROM t
  - Valid ranges/categories: SELECT col, COUNT(*) FROM t GROUP BY 1 ORDER BY 2 DESC
  - Uniqueness: SELECT key, COUNT(*) FROM t GROUP BY 1 HAVING COUNT(*)>1
  - Referentials: SELECT child.key FROM child c LEFT JOIN parent p USING(key) WHERE p.key IS NULL
  - Pattern checks: SELECT COUNT(*) FROM t WHERE NOT (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
- JSONB and semi‑structured
  - Enforce presence of required keys with CHECK (payload ? 'field')
  - Expression indexes for (payload->>'field')::int to support fast validation queries
- Time consistency
  - CHECK (starts_at < ends_at); EXCLUDE USING gist (period WITH &&) to prevent overlapping bookings
- Repeatable validation
  - Package checks as a view or stored procedure returning a table of (check_name, status, failing_rows)
  - Run validations after ingestion; fail the job if critical thresholds are exceeded

Design patterns
- Staging → conformance → serving layers: validate in staging, reject/fix bad rows before promoting
- Small dimension tables for valid categories (FK from facts) to block typos

Pitfalls
- Relying only on application‑level checks; enforce in the database too
- Turning every check into a constraint; some rules evolve—keep them in validation jobs first
- Costly full‑table scans for validation; sample or validate deltas on large fact tables

Practice exercises
1) Add CHECK constraints to enforce non‑negative quantities/amounts and valid enumerations
2) Write a validation view that reports null_rate, duplicate keys, and invalid patterns for customers
3) Create a small valid_countries table and add a FK from customers(country)

Further reading
- Constraints: https://www.postgresql.org/docs/current/ddl-constraints.html
- Exclusion constraints: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION
- JSONB operators: https://www.postgresql.org/docs/current/functions-json.html
