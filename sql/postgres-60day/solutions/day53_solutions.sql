-- Day 53 solutions: SCD Type 2 and temporal fact lookup
BEGIN;
SET search_path TO dwh, training, public;

DO $require_day52$
BEGIN
  IF to_regclass('dwh.dim_customer') IS NULL THEN
    RAISE EXCEPTION 'Run day52_solutions.sql before Day 53';
  END IF;
END
$require_day52$;

-- Exercise 2: audit metadata on both changing dimensions.
ALTER TABLE dim_customer
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE dim_product
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- A deterministic customer change effective 30 days ago.
CREATE TEMP TABLE staged_customer_change AS
SELECT customer_id,
       full_name,
       country,
       CASE WHEN segment = 'gold' THEN 'silver' ELSE 'gold' END AS segment,
       (CURRENT_DATE - 30) AS effective_date
FROM dim_customer
WHERE customer_id = 1
  AND is_current;

UPDATE dim_customer dc
SET valid_to = s.effective_date - 1,
    is_current = FALSE,
    updated_by = 'day53_solution',
    updated_at = CURRENT_TIMESTAMP
FROM staged_customer_change s
WHERE dc.customer_id = s.customer_id
  AND dc.is_current;

INSERT INTO dim_customer(
  customer_id, full_name, country, segment, country_sk,
  valid_from, valid_to, is_current, updated_by, updated_at
)
SELECT s.customer_id,
       s.full_name,
       s.country,
       s.segment,
       co.country_sk,
       s.effective_date,
       NULL,
       TRUE,
       'day53_solution',
       CURRENT_TIMESTAMP
FROM staged_customer_change s
JOIN dim_country co ON co.country_code = s.country;

-- Exercise 1: rebuild a fact-key mapping by choosing the dimension versions
-- whose validity intervals contain each order date.
CREATE TEMP TABLE fact_sales_temporal_solution AS
SELECT o.order_id,
       oi.order_item_id,
       dd.date_key,
       dc.customer_sk,
       dp.product_sk,
       oi.quantity,
       oi.unit_price,
       oi.discount,
       oi.unit_price * oi.quantity * (1 - oi.discount) AS amount
FROM training.orders o
JOIN training.order_items oi USING (order_id)
JOIN dim_date dd ON dd.date_actual = o.order_date::date
JOIN dim_customer dc
  ON dc.customer_id = o.customer_id
 AND o.order_date::date >= dc.valid_from
 AND o.order_date::date <= COALESCE(dc.valid_to, 'infinity'::date)
JOIN dim_product dp
  ON dp.product_id = oi.product_id
 AND o.order_date::date >= dp.valid_from
 AND o.order_date::date <= COALESCE(dp.valid_to, 'infinity'::date);

SELECT (SELECT COUNT(*) FROM fact_sales_temporal_solution) AS mapped_fact_rows,
       (SELECT COUNT(*) FROM training.order_items) AS source_item_rows,
       (SELECT COUNT(*) FROM dim_customer WHERE customer_id = 1) AS customer_versions;

-- Exercise 3: date-grain closed intervals cannot represent two ordered changes
-- on one date without an invalid or overlapping range. Surface that limitation.
SELECT customer_id, valid_from, valid_to,
       (valid_to IS NOT NULL AND valid_to < valid_from) AS invalid_range
FROM dim_customer
WHERE customer_id = 1
ORDER BY valid_from;

-- Exercise 4: each pair is compared once. Inclusive validity ranges overlap
-- when neither ends before the other begins.
SELECT a.customer_id,
       a.customer_sk AS version_a,
       b.customer_sk AS version_b,
       a.valid_from AS a_from,
       a.valid_to AS a_to,
       b.valid_from AS b_from,
       b.valid_to AS b_to
FROM dim_customer a
JOIN dim_customer b
  ON b.customer_id = a.customer_id
 AND b.customer_sk > a.customer_sk
 AND a.valid_from <= COALESCE(b.valid_to, 'infinity'::date)
 AND b.valid_from <= COALESCE(a.valid_to, 'infinity'::date)
ORDER BY a.customer_id, version_a, version_b;

-- Exercise 5: an unchanged current source should produce zero differences;
-- this is the idempotency gate before closing/inserting a new version.
SELECT COUNT(*) AS unchanged_rows_that_would_version
FROM dim_customer dc
JOIN training.customers c USING (customer_id)
WHERE dc.is_current
  AND (
    dc.full_name IS DISTINCT FROM c.full_name
    OR dc.country IS DISTINCT FROM c.country
    OR dc.segment IS DISTINCT FROM COALESCE(c.segment, 'standard')
  );

-- Exercise 6: timestamp-effective ranges support same-day ordering, but require
-- source effective timestamps (or a source sequence), not load time guesses.
SELECT '[2026-01-15 09:00+00,2026-01-15 12:00+00)'::tstzrange
         AS first_version,
       '[2026-01-15 12:00+00,infinity)'::tstzrange AS second_version;

ROLLBACK;
