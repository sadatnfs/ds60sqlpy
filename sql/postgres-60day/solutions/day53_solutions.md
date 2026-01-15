# Day 53 — Solutions (Project 3: DWH Design, Part 2 — SCD Type 2)

Today we practice Slowly Changing Dimensions (SCD Type 2) for customers and products. We close the current version and insert a new one when attributes change, then show how facts should join to the correct historical version by date.

Reference from lesson (annotated)
```sql
-- Demo of detecting changed customers and applying SCD2
WITH current_dim AS (
  SELECT dc.*
  FROM dim_customer dc
  WHERE dc.is_current
), diffs AS (
  SELECT s.customer_id,
         s.full_name,
         s.country,
         s.segment
  FROM changed_customers s
  JOIN current_dim dc ON dc.customer_id = s.customer_id
  WHERE coalesce(s.full_name,'') <> coalesce(dc.full_name,'')
     OR coalesce(s.country,'')   <> coalesce(dc.country,'')
     OR coalesce(s.segment,'')   <> coalesce(dc.segment,'')
), closed AS (
  UPDATE dim_customer dc
  SET valid_to = CURRENT_DATE - 1,
      is_current = FALSE
  FROM diffs d
  WHERE dc.customer_id = d.customer_id
    AND dc.is_current
  RETURNING dc.customer_id
)
INSERT INTO dim_customer(customer_id, full_name, country, segment, valid_from, valid_to, is_current)
SELECT d.customer_id, d.full_name, d.country, d.segment, CURRENT_DATE, NULL, TRUE
FROM diffs d;
```
Line‑by‑line notes
- current_dim: only the active version participates in change detection.
- diffs: row‑by‑row attribute comparison vs source to find changes.
- closed: end‑date the current version (yesterday) and flip is_current.
- INSERT: add a new current row starting today.

Exercise 1 — Join facts to the correct SCD version using the fact date
Prompt
- For a fact row at date_key (derived from order_date), you must join to the dimensional version valid at that date: valid_from ≤ fact_date ≤ COALESCE(valid_to, infinity).

Solution (rebuild fact_sales joins to SCD2 by date)
```sql
-- We assume:
--  - dim_date(date_key INT -> date_actual DATE)
--  - orders + order_items exist in training schema
--  - dim_customer and dim_product are SCD2 with (valid_from, valid_to, is_current)

WITH oi AS (
  SELECT oi.order_item_id,
         oi.order_id,
         o.order_date::date AS od,
         o.customer_id,
         oi.product_id,
         oi.quantity,
         oi.unit_price,
         oi.discount,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS amount
  FROM training.order_items oi
  JOIN training.orders o ON o.order_id = oi.order_id
), keys AS (
  SELECT oi.*,
         -- yyyymmdd date key
         (EXTRACT(year FROM oi.od)::int * 10000
        + EXTRACT(month FROM oi.od)::int * 100
        + EXTRACT(day  FROM oi.od)::int) AS date_key
  FROM oi
), with_scds AS (
  SELECT k.order_id,
         k.order_item_id,
         k.date_key,
         dc.customer_sk,
         dp.product_sk,
         k.quantity,
         k.unit_price,
         k.discount,
         k.amount
  FROM keys k
  JOIN dwh.dim_date dd ON dd.date_key = k.date_key
  JOIN dwh.dim_customer dc
    ON dc.customer_id = k.customer_id
   AND dd.date_actual BETWEEN dc.valid_from AND COALESCE(dc.valid_to, 'infinity')::date
  JOIN dwh.dim_product dp
    ON dp.product_id = k.product_id
   AND dd.date_actual BETWEEN dp.valid_from AND COALESCE(dp.valid_to, 'infinity')::date
)
-- Insert into fact (idempotency and PK handling omitted for brevity)
INSERT INTO dwh.fact_sales(order_id, order_item_id, date_key, customer_sk, product_sk, quantity, unit_price, discount, amount)
SELECT order_id, order_item_id, date_key, customer_sk, product_sk, quantity, unit_price, discount, amount
FROM with_scds;
```
Line‑by‑line notes
- keys: compute date_key once at the row grain.
- Join to dim_date to convert key → actual date for interval comparison.
- BETWEEN valid_from and valid_to: selects the correct version; COALESCE(...,'infinity') handles open‑ended rows.

Performance tips
- Index SCD tables for version lookups: (customer_id, valid_from, valid_to) and (product_id, valid_from, valid_to).
- Keep dim_date(date_key PK, date_actual UNIQUE) for fast resolution.

Exercise 2 — Add audit columns to SCD tables
Prompt
- Track who and when made SCD changes.

Solution (DDL + simple defaults)
```sql
ALTER TABLE dwh.dim_customer
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now(),
  ADD COLUMN IF NOT EXISTS updated_by text NOT NULL DEFAULT current_user;

ALTER TABLE dwh.dim_product
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now(),
  ADD COLUMN IF NOT EXISTS updated_by text NOT NULL DEFAULT current_user;
```
Notes
- Defaults stamp the actor/time for inserts. For UPDATEs (closing rows), stamp explicitly:
```sql
UPDATE dwh.dim_customer dc
SET valid_to = CURRENT_DATE - 1,
    is_current = FALSE,
    updated_at = now(),
    updated_by = current_user
WHERE ... ;
```
Optional: trigger to auto‑update updated_at on any change
```sql
CREATE OR REPLACE FUNCTION dwh.touch_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at := now();
  NEW.updated_by := current_user;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_touch_dim_customer ON dwh.dim_customer;
CREATE TRIGGER trg_touch_dim_customer
BEFORE UPDATE ON dwh.dim_customer
FOR EACH ROW EXECUTE FUNCTION dwh.touch_updated_at();
```

Validation queries
```sql
-- 1) Show customers with >1 version (SCD2 working)
SELECT customer_id, COUNT(*) AS versions
FROM dwh.dim_customer
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY versions DESC, customer_id
LIMIT 20;

-- 2) Sample fact rows and confirm date‑appropriate version
SELECT fs.order_id, fs.order_item_id, dd.date_actual, dc.valid_from, dc.valid_to, dc.is_current
FROM dwh.fact_sales fs
JOIN dwh.dim_customer dc ON dc.customer_sk = fs.customer_sk
JOIN dwh.dim_date dd ON dd.date_key = fs.date_key
ORDER BY dd.date_actual DESC
LIMIT 20;
```
