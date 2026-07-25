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

ROLLBACK;
