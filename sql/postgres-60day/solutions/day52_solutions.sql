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

-- Persist the solution-owned warehouse state for the next two solution days.
COMMIT;
