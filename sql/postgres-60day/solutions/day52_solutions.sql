-- Day 52 solutions: warehouse dimensions and a payment fact
-- This solution intentionally prepares persistent course-owned dwh state for
-- Days 53 and 54. The included lesson resets only dwh and commits its base.
SET search_path TO training, public;
\ir ../day52_project3_dwh_part1.sql

BEGIN;
SET search_path TO dwh, training, public;

-- Exercise 1: normalize country into its own dimension.
CREATE TABLE dim_country (
  country_sk int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  country_code text NOT NULL UNIQUE
);

INSERT INTO dim_country(country_code)
SELECT DISTINCT country
FROM training.customers
ORDER BY country;

ALTER TABLE dim_customer
  ADD COLUMN country_sk int REFERENCES dim_country(country_sk);

UPDATE dim_customer dc
SET country_sk = co.country_sk
FROM dim_country co
WHERE co.country_code = dc.country;

ALTER TABLE dim_customer
  ALTER COLUMN country_sk SET NOT NULL;

-- Exercise 2: payment fact linked to date and customer dimensions.
CREATE TABLE fact_payments (
  payment_id bigint PRIMARY KEY,
  order_id int NOT NULL,
  date_key int NOT NULL REFERENCES dim_date(date_key),
  customer_sk int NOT NULL REFERENCES dim_customer(customer_sk),
  amount numeric(12,2) NOT NULL,
  method text NOT NULL
);

INSERT INTO fact_payments(payment_id, order_id, date_key, customer_sk, amount, method)
SELECT p.payment_id,
       p.order_id,
       dd.date_key,
       dc.customer_sk,
       p.amount,
       p.method
FROM training.payments p
JOIN training.orders o USING (order_id)
JOIN dim_date dd ON dd.date_actual = p.payment_date::date
JOIN dim_customer dc
  ON dc.customer_id = o.customer_id
 AND p.payment_date::date >= dc.valid_from
 AND p.payment_date::date <= COALESCE(dc.valid_to, 'infinity'::date);

SELECT (SELECT COUNT(*) FROM dim_country) AS countries,
       (SELECT COUNT(*) FROM fact_payments) AS fact_payment_rows,
       (SELECT COUNT(*) FROM training.payments) AS source_payment_rows;

-- Exercise 3: fact_sales has one row per source order_item. order_id repeats for
-- multi-line orders, while order_item_id is the unique source-grain key.
SELECT COUNT(*) AS fact_rows,
       COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT order_item_id) AS distinct_order_items
FROM fact_sales;

-- Exercise 4: reserve -1 as an explicit unknown member in every referenced
-- dimension. This is a policy alternative to rejecting an unmatched fact.
INSERT INTO dim_country(country_sk, country_code)
  OVERRIDING SYSTEM VALUE VALUES (-1, '(unknown)');
INSERT INTO dim_customer(
  customer_sk, customer_id, full_name, country, segment, country_sk,
  valid_from, valid_to, is_current
) VALUES (
  -1, -1, '(unknown)', '(unknown)', '(unknown)', -1,
  date '1900-01-01', NULL, TRUE
);
INSERT INTO dim_product(
  product_sk, product_id, name, category, price, cost,
  valid_from, valid_to, is_current
) VALUES (
  -1, -1, '(unknown)', '(unknown)', 0, 0,
  date '1900-01-01', NULL, TRUE
);
SELECT COALESCE(dc.customer_sk, -1) AS routed_customer_sk
FROM (VALUES (-999)) AS source(customer_id)
LEFT JOIN dim_customer dc USING (customer_id);

-- Exercise 5: row and amount controls prove both completeness and measure
-- reconciliation at the declared line-item grain.
SELECT (SELECT COUNT(*) FROM fact_sales) AS fact_rows,
       (SELECT COUNT(*) FROM training.order_items) AS source_rows,
       (SELECT ROUND(SUM(amount), 2) FROM fact_sales) AS fact_amount,
       (
         SELECT ROUND(SUM(quantity * unit_price * (1 - discount)), 2)
         FROM training.order_items
       ) AS source_amount;

-- Exercise 6: report any payment date outside the current date dimension.
-- This solution chooses fail-and-extend, rather than silently mapping a real
-- date to unknown, because accounting date is analytically significant.
SELECT p.payment_id, p.payment_date::date
FROM training.payments p
LEFT JOIN dim_date d ON d.date_actual = p.payment_date::date
WHERE d.date_key IS NULL
ORDER BY p.payment_id;

-- Persist the solution-owned warehouse state for the next two solution days.
COMMIT;
