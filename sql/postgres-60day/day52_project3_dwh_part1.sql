-- Day 52: Project 3 - Data Warehouse Design (Part 1)
-- BEGINNER WORKFLOW - sql-52: Project 3 DWH Part 1
-- Guide: sql/postgres-60day/companion-guides/day52_project3_dwh_part1.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-52.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: dim_date, dim_customer, dim_product, fact_sales, training.orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. This stateful lesson ends with COMMIT and preserves only the course-owned dwh schema.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Topics: Star schema design (facts/dimensions) and initial loads
BEGIN;
SET search_path TO training, public;

-- This three-day project is intentionally stateful. Re-running Day 52 resets
-- only the course-owned dwh schema, then commits it for Days 53 and 54.
DROP SCHEMA IF EXISTS dwh CASCADE;

CREATE SCHEMA dwh;

SET search_path TO dwh, training, public;

-- Dimension tables (surrogate keys)
CREATE TABLE dim_date (
  date_key INT PRIMARY KEY, -- yyyymmdd
  date_actual DATE NOT NULL,
  year INT NOT NULL,
  quarter INT NOT NULL,
  month INT NOT NULL,
  day INT NOT NULL,
  day_name TEXT NOT NULL,
  is_weekend BOOLEAN NOT NULL
);

CREATE SEQUENCE dim_customer_sk_seq;

CREATE TABLE dim_customer (
  customer_sk INT PRIMARY KEY DEFAULT nextval('dim_customer_sk_seq'),
  customer_id INT NOT NULL, -- business key
  full_name TEXT,
  country TEXT,
  segment TEXT,
  valid_from DATE NOT NULL,
  valid_to DATE,
  is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE SEQUENCE dim_product_sk_seq;

CREATE TABLE dim_product (
  product_sk INT PRIMARY KEY DEFAULT nextval('dim_product_sk_seq'),
  product_id INT NOT NULL, -- business key
  name TEXT,
  category TEXT,
  price NUMERIC(10, 2),
  cost NUMERIC(10, 2),
  valid_from DATE NOT NULL,
  valid_to DATE,
  is_current BOOLEAN NOT NULL DEFAULT TRUE
);

-- Fact table
CREATE TABLE fact_sales (
  order_id INT NOT NULL,
  order_item_id INT NOT NULL,
  date_key INT NOT NULL REFERENCES dim_date (date_key),
  customer_sk INT NOT NULL REFERENCES dim_customer (customer_sk),
  product_sk INT NOT NULL REFERENCES dim_product (product_sk),
  quantity INT NOT NULL,
  unit_price NUMERIC(10, 2) NOT NULL,
  discount NUMERIC(5, 2) NOT NULL,
  amount NUMERIC(12, 2) NOT NULL
);

-- Populate dim_date for every source order plus a useful planning horizon.
-- Deriving the bounds from the source prevents old facts from missing a date key.
WITH bounds AS (
  SELECT
    LEAST (MIN(order_date)::date, (CURRENT_DATE - interval '2 years')::date) AS start_date,
    GREATEST (MAX(order_date)::date, (CURRENT_DATE + interval '1 year')::date) AS end_date
  FROM
    training.orders
),
cal AS (
  SELECT
    generate_series(start_date, end_date, interval '1 day')::date AS d
  FROM
    bounds)
INSERT INTO dim_date (date_key, date_actual, year, quarter, month, day, day_name, is_weekend)
SELECT
  extract(year from d)::int * 10000 + extract(month from d)::int * 100 + extract(day from d)::int,
  d,
  extract(year from d)::int,
  extract(quarter from d)::int,
  extract(month from d)::int,
  extract(day from d)::int,
  to_char(d, 'Dy'),
  (extract(isodow from d)::int >= 6)
FROM
  cal;

-- Initial load for customer dimension (Type 2 structure; initial current rows)
INSERT INTO dim_customer (customer_id, full_name, country, segment, valid_from, valid_to, is_current)
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  COALESCE(c.segment, 'standard') AS segment,
  c.created_at::date,
  NULL,
  TRUE
FROM
  training.customers c;

-- Initial load for product dimension
INSERT INTO dim_product (product_id, name, category, price, cost, valid_from, valid_to, is_current)
SELECT
  p.product_id,
  p.name,
  p.category,
  p.price,
  p.cost,
  p.created_at::date,
  NULL,
  TRUE
FROM
  training.products p;

-- Load fact from existing orders/items (map to dims using current rows)
WITH oi AS (
  SELECT
    oi.order_item_id,
    oi.order_id,
    o.order_date::date AS od,
    o.customer_id,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    (oi.unit_price * oi.quantity * (1 - oi.discount)) AS amount
  FROM
    training.order_items oi
    JOIN training.orders o ON o.order_id = oi.order_id
),
keys AS (
  SELECT
    oi.*,
    (extract(year from oi.od)::int * 10000 + extract(month from oi.od)::int * 100 + extract(day from oi.od)::int) AS date_key,
    dc.customer_sk,
    dp.product_sk
  FROM
    oi
    JOIN dim_customer dc ON dc.customer_id = oi.customer_id
      AND dc.is_current
    JOIN dim_product dp ON dp.product_id = oi.product_id
      AND dp.is_current)
  INSERT INTO fact_sales (order_id, order_item_id, date_key, customer_sk, product_sk, quantity, unit_price, discount, amount)
  SELECT
    order_id,
    order_item_id,
    date_key,
    customer_sk,
    product_sk,
    quantity,
    unit_price,
    discount,
    amount
  FROM
    keys;

-- Sample star query
SELECT
  dd.year,
  dd.month,
  dp.category,
  ROUND(SUM(fs.amount), 2) AS revenue
FROM
  fact_sales fs
  JOIN dim_date dd ON dd.date_key = fs.date_key
  JOIN dim_product dp ON dp.product_sk = fs.product_sk
GROUP BY
  dd.year,
  dd.month,
  dp.category
ORDER BY
  dd.year DESC,
  dd.month DESC,
  revenue DESC
LIMIT 50;

-- Exercises
-- 1. Add dim_country and link customers to it.
--    Inputs: For sql-52 Exercise 1, create `dim_country(country_sk, country_code)` with one row per distinct `training.customers.country`, add `country_sk` to `dim_customer` as a foreign key to it, backfill it from the text `country`, and make it `NOT NULL` before the final `COMMIT`.
--    Expected result/shape: For sql-52 Exercise 1, expected output: `INSERT 0 8` for the country codes, `UPDATE 500` for the backfill, and `ALTER TABLE` for the `NOT NULL` change, so every customer-dimension version has exactly one `country_sk`. Days 53 and 54 run against this committed state, and Day 53's SCD2 inserts must keep it.
--    Verify: For sql-52 Exercise 1, right after the backfill, confirm that `SELECT COUNT(*) FROM dim_country` is 8, that no `dim_customer` row has a NULL `country_sk`, and that joining `dim_customer` to `dim_country` on `country_sk` gives `country_code = country` on every row; after a savepoint, an `INSERT` into `dim_customer` without `country_sk` must fail with SQLSTATE `23502`, then roll back to the savepoint.
--    Hint ladder, rung 1: For sql-52 Exercise 1, load `dim_country` and backfill `country_sk` before you add `NOT NULL`; `SET NOT NULL` fails while any row is still NULL.
-- 2. Build a second fact table fact_payments linked to dim_date and dim_customer.
--    Inputs: For sql-52 Exercise 2, create `fact_payments` with one row per `training.payments` row, keyed by `payment_id`, and load it by joining each payment to its order, to `dim_date` on the payment date, and to the `dim_customer` version valid on that date.
--    Expected result/shape: For sql-52 Exercise 2, expected output: `INSERT 0 3836`, one fact row per source payment, then a check row with `countries` 8, `fact_payment_rows` 3836, and `source_payment_rows` 3836. The fact columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`.
--    Verify: For sql-52 Exercise 2, confirm that `fact_payment_rows` equals `source_payment_rows` (3836) and that `SELECT SUM(amount) FROM fact_payments` equals `SELECT SUM(amount) FROM training.payments` (1831900.81); a join that lost payments would lower the count, and a join to every customer version would raise it.
--    Hint ladder, rung 1: For sql-52 Exercise 2, join `training.payments` to `orders`, `dim_date`, and `dim_customer` one table at a time and check that the row count stays 3836 after each join.
-- 3. Prediction: identify the grain of fact_sales and explain why order_id alone
--    cannot be its primary key.
--    Inputs: For sql-52 Exercise 3, read from `fact_sales` and count its rows, its distinct `order_id` values, and its distinct `order_item_id` values.
--    Expected result/shape: For sql-52 Exercise 3, expected output: one row with `fact_rows` 13085, `orders` 4362, and `distinct_order_items` 13085, which shows that `fact_sales` has one row per order line and that `order_id` alone does not identify a row. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
--    Verify: For sql-52 Exercise 3, confirm that `fact_rows` and `distinct_order_items` both equal `SELECT COUNT(*) FROM training.order_items` (13085) while `orders` is only 4362; `SELECT order_id FROM fact_sales GROUP BY order_id HAVING COUNT(*) > 1` returns 3490 orders, which proves that `order_id` repeats.
--    Hint ladder, rung 1: For sql-52 Exercise 3, compare `COUNT(*)` with `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT order_item_id)`; the key is the column whose distinct count equals the row count.
-- 4. Construction: add unknown (-1) members to dimensions and route an
--    intentionally unmatched source key to them during a test load.
--    Inputs: For sql-52 Exercise 4, add an unknown member with surrogate key -1 to `dim_country`, `dim_customer`, and `dim_product`, then route a source row whose `customer_id` (-999) has no dimension match to that member with `COALESCE(dc.customer_sk, -1)` after a `LEFT JOIN`.
--    Expected result/shape: For sql-52 Exercise 4, expected output: three `INSERT 0 1` commands and one row whose `routed_customer_sk` is -1. The final columns are `routed_customer_sk`.
--    Verify: For sql-52 Exercise 4, confirm that `SELECT customer_sk FROM dim_customer WHERE customer_sk = -1` returns one row and that the routing query returns -1 for `customer_id` -999; replace -999 with 1 and confirm that it returns that customer's real `customer_sk` (1) instead.
--    Hint ladder, rung 1: For sql-52 Exercise 4, insert the unknown members first and query each one by its -1 key before you test the routing `LEFT JOIN`.
-- 5. Debugging: prove that fact_sales amount reconciles to source line-item
--    revenue and investigate any row-count or amount difference.
--    Inputs: For sql-52 Exercise 5, compare `fact_sales` with `training.order_items`: the two row counts, the total fact `amount`, and the source line total `ROUND(SUM(quantity * unit_price * (1 - discount)), 2)`.
--    Expected result/shape: For sql-52 Exercise 5, expected output: one row with `fact_rows` and `source_rows` both 13085, `fact_amount` 2355648.13, and `source_amount` 2355647.12; the 1.01 gap comes from rounding each fact line to cents. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
--    Verify: For sql-52 Exercise 5, confirm equal row counts, then recompute the source with the fact's rounding rule, `SELECT SUM(ROUND(quantity * unit_price * (1 - discount), 2)) FROM training.order_items`, and expect 2355648.13, exactly `fact_amount`; a gap that remains after that would be a real load error.
--    Hint ladder, rung 1: For sql-52 Exercise 5, count rows first, then compare totals; when the totals differ, check whether the fact rounds each line before summing.
-- 6. Edge case: document how a late-arriving payment date outside dim_date's
--    generated range should fail, extend, or map according to an explicit policy.
--    Inputs: For sql-52 Exercise 6, left join the 3,836 `training.payments` rows to `dwh.dim_date` on `d.date_actual = p.payment_date::date` and keep only the payments with no calendar row (`d.date_key IS NULL`); the calendar runs from two years before today to one year after today (2023-02-13 to 2027-11-25 on our run).
--    Expected result/shape: For sql-52 Exercise 6, expected output: zero rows on the course data, because every payment date falls inside the calendar; a late payment would appear as one row per `payment_id`. The final columns are `payment_id` and `payment_date` (the `::date` cast keeps the source column name). The final order is `p.payment_id`.
--    Verify: For sql-52 Exercise 6, confirm that the left join without the `WHERE` returns 3,836 rows and 3,836 distinct `payment_id` values, so the calendar adds no fanout, and that the `NOT EXISTS` form also returns 0 rows. Then, in a transaction, insert a payment for order 1 dated 2028-01-01: the query returns exactly that new `payment_id` with `payment_date` 2028-01-01, and the unfiltered join rises to 3,837 rows; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-52 Exercise 6, find `MIN` and `MAX` of `date_actual` in `dim_date` and of `payment_date::date` in `training.payments` before you write the anti-join; when the payments sit inside the calendar, zero rows is the correct answer.
COMMIT;
