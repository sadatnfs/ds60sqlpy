-- Day 54 solutions: aggregate tables and refresh procedure
BEGIN;
SET search_path TO dwh, training, public;

DO $require_day52$
BEGIN
  IF to_regclass('dwh.fact_sales') IS NULL THEN
    RAISE EXCEPTION 'Run day52_solutions.sql before Day 54';
  END IF;
END
$require_day52$;

CREATE TABLE agg_sales_category_month (
  year int NOT NULL,
  month int NOT NULL,
  category text NOT NULL,
  revenue numeric(14,2) NOT NULL,
  units bigint NOT NULL,
  PRIMARY KEY (year, month, category)
);

CREATE TABLE agg_sales_customer_month (
  year int NOT NULL,
  month int NOT NULL,
  customer_sk int NOT NULL REFERENCES dim_customer(customer_sk),
  revenue numeric(14,2) NOT NULL,
  orders bigint NOT NULL,
  PRIMARY KEY (year, month, customer_sk)
);

-- Exercise 1: product-month aggregate.
CREATE TABLE agg_sales_product_month (
  year int NOT NULL,
  month int NOT NULL,
  product_sk int NOT NULL REFERENCES dim_product(product_sk),
  revenue numeric(14,2) NOT NULL,
  units bigint NOT NULL,
  orders bigint NOT NULL,
  PRIMARY KEY (year, month, product_sk)
);

-- Exercise 2: refresh all aggregate tables for one year/month.
CREATE OR REPLACE PROCEDURE refresh_sales_aggregates_solution(
  p_year int,
  p_month int
)
LANGUAGE plpgsql
AS $procedure$
BEGIN
  DELETE FROM agg_sales_category_month
  WHERE year = p_year AND month = p_month;
  DELETE FROM agg_sales_customer_month
  WHERE year = p_year AND month = p_month;
  DELETE FROM agg_sales_product_month
  WHERE year = p_year AND month = p_month;

  INSERT INTO agg_sales_category_month(year, month, category, revenue, units)
  SELECT dd.year,
         dd.month,
         dp.category,
         ROUND(SUM(fs.amount), 2),
         SUM(fs.quantity)
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  JOIN dim_product dp USING (product_sk)
  WHERE dd.year = p_year AND dd.month = p_month
  GROUP BY dd.year, dd.month, dp.category;

  INSERT INTO agg_sales_customer_month(year, month, customer_sk, revenue, orders)
  SELECT dd.year,
         dd.month,
         fs.customer_sk,
         ROUND(SUM(fs.amount), 2),
         COUNT(DISTINCT fs.order_id)
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  WHERE dd.year = p_year AND dd.month = p_month
  GROUP BY dd.year, dd.month, fs.customer_sk;

  INSERT INTO agg_sales_product_month(
    year, month, product_sk, revenue, units, orders
  )
  SELECT dd.year,
         dd.month,
         fs.product_sk,
         ROUND(SUM(fs.amount), 2),
         SUM(fs.quantity),
         COUNT(DISTINCT fs.order_id)
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  WHERE dd.year = p_year AND dd.month = p_month
  GROUP BY dd.year, dd.month, fs.product_sk;
END
$procedure$;

DO $refresh_latest_month$
DECLARE
  latest_year int;
  latest_month int;
BEGIN
  SELECT dd.year, dd.month
  INTO latest_year, latest_month
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  ORDER BY dd.year DESC, dd.month DESC
  LIMIT 1;

  CALL refresh_sales_aggregates_solution(latest_year, latest_month);
END
$refresh_latest_month$;

-- Product aggregate must reconcile to facts for the refreshed month.
WITH aggregate_total AS (
  SELECT year, month, SUM(revenue) AS revenue
  FROM agg_sales_product_month
  GROUP BY year, month
), fact_total AS (
  SELECT dd.year, dd.month, ROUND(SUM(fs.amount), 2) AS revenue
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  WHERE (dd.year, dd.month) IN (
    SELECT year, month FROM aggregate_total
  )
  GROUP BY dd.year, dd.month
)
SELECT a.year,
       a.month,
       a.revenue AS aggregate_revenue,
       f.revenue AS fact_revenue,
       a.revenue - f.revenue AS difference
FROM aggregate_total a
JOIN fact_total f USING (year, month);

ROLLBACK;
