-- Day 54 solutions: aggregate tables and refresh procedure
-- SOLUTION READING MAP — sql-54: Project3 DWH Part3 Aggregations
-- Explanation: sql/postgres-60day/solutions/day54_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day54_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
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

-- Exercise 3: list loaded periods. A late fact for any listed closed period
-- requires refreshing that period, not only the newest one.
SELECT dd.year, dd.month,
       COUNT(*) AS fact_rows,
       MAX(dd.date_actual) AS latest_fact_date
FROM fact_sales fs
JOIN dim_date dd USING (date_key)
GROUP BY dd.year, dd.month
ORDER BY dd.year DESC, dd.month DESC;

-- Exercise 4: the procedure's DELETE + INSERT statements share this surrounding
-- transaction. The prior call already refreshed one month atomically.
SELECT year, month, COUNT(*) AS category_rows, SUM(revenue) AS revenue
FROM agg_sales_category_month
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- Exercise 5: FULL JOIN plus COALESCE in the delta exposes a row missing from
-- either side instead of allowing NULL arithmetic to hide it.
WITH aggregate_total AS (
  SELECT year, month, SUM(revenue) AS revenue
  FROM agg_sales_category_month GROUP BY year, month
), fact_total AS (
  SELECT dd.year, dd.month, ROUND(SUM(fs.amount), 2) AS revenue
  FROM fact_sales fs JOIN dim_date dd USING (date_key)
  GROUP BY dd.year, dd.month
)
SELECT COALESCE(a.year, f.year) AS year,
       COALESCE(a.month, f.month) AS month,
       a.revenue AS aggregate_revenue,
       f.revenue AS fact_revenue,
       COALESCE(a.revenue, 0) - COALESCE(f.revenue, 0) AS difference
FROM aggregate_total a
FULL JOIN fact_total f USING (year, month)
WHERE a.revenue IS DISTINCT FROM f.revenue
ORDER BY year, month;

-- Exercise 6: snapshot, rerun the same latest-month refresh, then compare both
-- directions. An empty difference proves row/value idempotency.
CREATE TEMP TABLE aggregate_snapshot_before AS
SELECT * FROM agg_sales_category_month;
DO $refresh_latest_month_again$
DECLARE
  latest_year int;
  latest_month int;
BEGIN
  SELECT dd.year, dd.month INTO latest_year, latest_month
  FROM fact_sales fs JOIN dim_date dd USING (date_key)
  ORDER BY dd.year DESC, dd.month DESC LIMIT 1;
  CALL refresh_sales_aggregates_solution(latest_year, latest_month);
END
$refresh_latest_month_again$;
SELECT 'before_minus_after' AS side, * FROM (
  SELECT * FROM aggregate_snapshot_before
  EXCEPT
  SELECT * FROM agg_sales_category_month
) a
UNION ALL
SELECT 'after_minus_before', * FROM (
  SELECT * FROM agg_sales_category_month
  EXCEPT
  SELECT * FROM aggregate_snapshot_before
) b;

ROLLBACK;
