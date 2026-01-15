-- Day 54: Project 3 - Data Warehouse Design (Part 3)
-- Topics: Aggregation tables and DQ checks in DWH
BEGIN;
SET search_path TO dwh, training, public;

-- Aggregate tables (star-schema rollups)
CREATE TABLE agg_sales_category_month (
  year    INT NOT NULL,
  month   INT NOT NULL,
  category TEXT NOT NULL,
  revenue NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, category)
);

CREATE TABLE agg_sales_customer_month (
  year     INT NOT NULL,
  month    INT NOT NULL,
  customer_sk INT NOT NULL,
  revenue  NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, customer_sk)
);

-- Initial full builds (would normally be incremental)
INSERT INTO agg_sales_category_month(year, month, category, revenue)
SELECT dd.year,
       dd.month,
       dp.category,
       ROUND(SUM(fs.amount),2) AS revenue
FROM fact_sales fs
JOIN dim_date dd    ON dd.date_key = fs.date_key
JOIN dim_product dp ON dp.product_sk = fs.product_sk
GROUP BY dd.year, dd.month, dp.category;

INSERT INTO agg_sales_customer_month(year, month, customer_sk, revenue)
SELECT dd.year,
       dd.month,
       fs.customer_sk,
       ROUND(SUM(fs.amount),2) AS revenue
FROM fact_sales fs
JOIN dim_date dd ON dd.date_key = fs.date_key
GROUP BY dd.year, dd.month, fs.customer_sk;

-- Example incremental refresh for a given month (delete + insert)
-- WITH target AS (
--   SELECT 2026 AS y, 1 AS m
-- )
-- DELETE FROM agg_sales_category_month a
-- USING target t
-- WHERE a.year = t.y AND a.month = t.m;
-- INSERT INTO agg_sales_category_month(year, month, category, revenue)
-- SELECT t.y, t.m, dp.category, ROUND(SUM(fs.amount),2)
-- FROM fact_sales fs
-- JOIN dim_date dd ON dd.date_key = fs.date_key
-- JOIN dim_product dp ON dp.product_sk = fs.product_sk
-- JOIN target t ON dd.year = t.y AND dd.month = t.m
-- GROUP BY dp.category, t.y, t.m;

-- Data Quality checks: reconciling aggregates to facts
-- 1) Compare monthly category revenue between agg and base
WITH base AS (
  SELECT dd.year, dd.month, dp.category, ROUND(SUM(fs.amount),2) AS rev
  FROM fact_sales fs
  JOIN dim_date dd ON dd.date_key = fs.date_key
  JOIN dim_product dp ON dp.product_sk = fs.product_sk
  GROUP BY dd.year, dd.month, dp.category
), diff AS (
  SELECT b.year, b.month, b.category,
         b.rev AS base_rev,
         a.revenue AS agg_rev,
         ROUND(coalesce(a.revenue,0) - coalesce(b.rev,0),2) AS delta
  FROM base b
  FULL OUTER JOIN agg_sales_category_month a
    ON a.year = b.year AND a.month = b.month AND a.category = b.category
)
SELECT * FROM diff WHERE delta <> 0 ORDER BY year DESC, month DESC, category;

-- 2) Check for orphan SKs in agg_sales_customer_month
SELECT a.customer_sk
FROM agg_sales_customer_month a
LEFT JOIN dim_customer dc ON dc.customer_sk = a.customer_sk
WHERE dc.customer_sk IS NULL
LIMIT 10;

-- Exercises
-- 1) Add an agg table agg_sales_product_month and validate it.
-- 2) Create a stored procedure to refresh a given y, m across all aggs.

ROLLBACK;
