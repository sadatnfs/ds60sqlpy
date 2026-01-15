# Day 52 — Solutions (Project 3: DWH Design, Part 1 — Star Schema & Initial Loads)

We extend the star schema with a country dimension and build a payments fact. The solutions below are written step‑by‑step for beginners and mirror the day’s SQL.

Important
- These examples assume you are experimenting inside a transaction; replace ROLLBACK with COMMIT when you want to persist.
- We use schema dwh; ensure search_path includes dwh for these examples.

Exercise 1 — Add dim_country and link customers to it
Goal
- Normalize country into its own dimension dim_country with a surrogate key (country_sk).
- Link dim_customer rows to dim_country via a foreign key.

Step 1: Create the new dimension
```sql
-- A minimal country dimension. You may add region/iso3, etc.
CREATE TABLE IF NOT EXISTS dwh.dim_country (
  country_sk   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  country_code TEXT NOT NULL UNIQUE
);
```
Notes
- GENERATED ALWAYS AS IDENTITY auto‑generates the surrogate key.
- country_code stores your existing two‑letter code (e.g., 'US').

Step 2: Seed dim_country from the OLTP source
```sql
INSERT INTO dwh.dim_country(country_code)
SELECT DISTINCT UPPER(TRIM(country))
FROM training.customers
WHERE country IS NOT NULL
  AND TRIM(country) <> ''
ON CONFLICT (country_code) DO NOTHING;
```
Notes
- DISTINCT to avoid duplicates; UPPER/TRIM to standardize.
- ON CONFLICT avoids duplicate inserts if you re‑run.

Step 3: Add a foreign key column to dim_customer and populate it
```sql
-- Add the new column; allow NULL during backfill
ALTER TABLE dwh.dim_customer ADD COLUMN IF NOT EXISTS country_sk INT;

-- Backfill by matching the current country attribute to dim_country
UPDATE dwh.dim_customer dc
SET country_sk = c.country_sk
FROM dwh.dim_country c
WHERE UPPER(TRIM(dc.country)) = c.country_code
  AND dc.is_current; -- backfill only current rows for now
```
Notes
- We keep the old textual country column for human readability; country_sk is the normalized link.
- If you need historical conformance (country changes over time), treat it via SCD rules in Day 53.

Step 4: Add a foreign key and optional index
```sql
ALTER TABLE dwh.dim_customer
  ADD CONSTRAINT fk_dim_customer_country
  FOREIGN KEY (country_sk) REFERENCES dwh.dim_country(country_sk);

-- Helpful for joins on country_sk
CREATE INDEX IF NOT EXISTS ix_dim_customer_country_sk ON dwh.dim_customer(country_sk);
```

Validation
```sql
-- Spot‑check: every current customer should now have a country_sk
SELECT COUNT(*) AS missing_country_sk
FROM dwh.dim_customer
WHERE is_current AND country_sk IS NULL;
```

Exercise 2 — Build a fact_payments table
Goal
- Capture customer payments at day grain with links to date and customer dimensions.

Step 1: Create fact_payments
```sql
CREATE TABLE IF NOT EXISTS dwh.fact_payments (
  payment_id   INT NOT NULL,
  date_key     INT NOT NULL REFERENCES dwh.dim_date(date_key),
  customer_sk  INT NOT NULL REFERENCES dwh.dim_customer(customer_sk),
  amount       NUMERIC(12,2) NOT NULL,
  method       TEXT,
  PRIMARY KEY (payment_id)
);
```
Notes
- payment_id from OLTP ensures idempotent loads (no duplicate payments).
- date_key maps to the business date of the payment (derived below).

Step 2: Initial load from training.payments
```sql
WITH src AS (
  SELECT p.payment_id,
         p.customer_id,
         p.amount,
         p.method,
         p.payment_date::date AS d
  FROM training.payments p
), keys AS (
  SELECT s.*, 
         (EXTRACT(year FROM s.d)::int * 10000
        + EXTRACT(month FROM s.d)::int * 100
        + EXTRACT(day  FROM s.d)::int) AS date_key,
         dc.customer_sk
  FROM src s
  JOIN dwh.dim_customer dc ON dc.customer_id = s.customer_id AND dc.is_current
)
INSERT INTO dwh.fact_payments(payment_id, date_key, customer_sk, amount, method)
SELECT payment_id, date_key, customer_sk, amount, method
FROM keys
ON CONFLICT (payment_id) DO NOTHING; -- idempotent
```
Notes
- date_key is computed yyyymmdd to match dim_date.
- We join to the current dim_customer row; for historical conformance, see Day 53’s date‑keyed SCD lookup.

Validation
```sql
-- Totals should match source (within rounding if any)
SELECT ROUND(SUM(amount),2) AS fact_total
FROM dwh.fact_payments;

SELECT ROUND(SUM(amount),2) AS src_total
FROM training.payments;
```

Going further
- Add indexes on (customer_sk, date_key) for common filters.
- Partition fact tables by date for maintenance at large scale.
