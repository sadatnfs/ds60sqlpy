# Day 42 — Solutions (Data Quality and Validation)

We implement schema and semantic checks, row‐level constraints, uniqueness/foreign key tests, profiling metrics, and drift/contract validation for production data.

Setup
- Validation layers:
  - Schema: types, nullability, PK/FK, check constraints
  - Semantic: ranges, enumerations, business rules
  - Referential: FK integrity, orphan detection
  - Profiling: row counts, distincts, distributions, freshness
- Tooling: SQL first; optionally wire into dbt/evidently/great_expectations later

Exercise 1 — Enforce constraints (DDL)
```sql
-- Primary/unique keys
ALTER TABLE customers
  ADD CONSTRAINT customers_pk PRIMARY KEY (customer_id);
ALTER TABLE customers
  ADD CONSTRAINT email_unique UNIQUE (email);

-- Foreign keys
ALTER TABLE orders
  ADD CONSTRAINT orders_customer_fk FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id);

-- Value ranges / enumerations
ALTER TABLE orders
  ADD CONSTRAINT total_amount_nonneg CHECK (total_amount >= 0);

-- NOT NULL
ALTER TABLE products
  ALTER COLUMN name SET NOT NULL;
```
Why
- Fail fast at the database edge; prevents bad data from persisting.

Exercise 2 — Referential integrity audits
```sql
-- Orphan orders (no matching customer)
SELECT o.order_id
FROM orders o
LEFT JOIN customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL
LIMIT 100;

-- Products missing categories
SELECT p.product_id
FROM products p
LEFT JOIN categories c ON c.category_id = p.category_id
WHERE c.category_id IS NULL
LIMIT 100;
```
Action
- Fix sources or add FKs; log exceptions.

Exercise 3 — Uniqueness and duplicates
```sql
-- Duplicate emails after normalization
SELECT lower(trim(email)) AS norm_email, COUNT(*)
FROM customers
GROUP BY lower(trim(email))
HAVING COUNT(*) > 1
ORDER BY 2 DESC
LIMIT 100;
```
Remediation
- Choose a keeper by created_at; merge records; add UNIQUE on lower(email).

Exercise 4 — Profiling metrics and freshness
```sql
-- Daily counts and freshness
SELECT CURRENT_DATE                         AS as_of,
       (SELECT COUNT(*) FROM customers)      AS customers,
       (SELECT COUNT(*) FROM orders)         AS orders,
       (SELECT MAX(order_date) FROM orders)  AS max_order_ts,
       EXTRACT(EPOCH FROM (now() - (SELECT MAX(order_date) FROM orders)))/3600 AS hours_since_order;
```
Why
- Track basic health KPIs; alert when freshness thresholds exceed SLO.

Exercise 5 — Range and enum checks
```sql
-- Orders with out-of-range totals
SELECT order_id, total_amount
FROM orders
WHERE total_amount < 0 OR total_amount > 1000000
LIMIT 100;

-- Countries outside ISO allowlist (example)
WITH allow AS (
  SELECT unnest(ARRAY['US','CA','GB','DE','FR','AU']) AS code
)
SELECT DISTINCT c.country
FROM customers c
LEFT JOIN allow a ON a.code = c.country
WHERE a.code IS NULL
ORDER BY 1;
```
Action
- Correct sources; maintain reference tables (ISO codes) and validate by FK to reference.

Exercise 6 — Contract/drift checks (distributions)
```sql
-- Compare today vs last 30 days category mix
WITH today AS (
  SELECT p.category, COUNT(*) AS n
  FROM orders o
  JOIN order_items oi ON oi.order_id=o.order_id
  JOIN products p ON p.product_id=oi.product_id
  WHERE o.order_date::date = CURRENT_DATE
  GROUP BY p.category
), baseline AS (
  SELECT p.category, COUNT(*) AS n
  FROM orders o
  JOIN order_items oi ON oi.order_id=o.order_id
  JOIN products p ON p.product_id=oi.product_id
  WHERE o.order_date >= CURRENT_DATE - interval '30 days'
  GROUP BY p.category
)
SELECT COALESCE(t.category, b.category) AS category,
       t.n AS today,
       b.n AS last_30d
FROM today t
FULL JOIN baseline b USING (category)
ORDER BY 1;
```
Next steps
- Convert to PSI/chi‑square tests; threshold alerts in monitoring.

Checklist
- Enforce PK/FK/UNIQUE/NOT NULL/CHECK
- Scheduled integrity/profiling queries
- Reference tables + FKs for enumerations
- Distribution drift checks; publish dashboards and alerts
