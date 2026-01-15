# Day 54 — Solutions (Project 3: DWH Design, Part 3 — Aggregations & DQ Checks)

Today you build aggregate tables from the star schema and validate them with data quality (DQ) reconciliations. The exercises ask you to add a product‑month aggregate and create a refresh procedure. Below are line‑by‑line, beginner‑friendly solutions.

Reference rollups from lesson (annotated)
```sql
INSERT INTO agg_sales_category_month(year, month, category, revenue)
SELECT dd.year,
       dd.month,
       dp.category,
       ROUND(SUM(fs.amount),2) AS revenue
FROM fact_sales fs
JOIN dim_date dd    ON dd.date_key = fs.date_key
JOIN dim_product dp ON dp.product_sk = fs.product_sk
GROUP BY dd.year, dd.month, dp.category;
```
Notes
- Join facts to dimensions to expose reporting attributes (year, month, category).
- SUM(fs.amount) collapses row‑level facts to a monthly aggregate. ROUND for presentation.

Exercise 1 — Add agg_sales_product_month and validate it
Goal
- Create an aggregate at (year, month, product_sk) grain and cross‑check it matches base facts.

A) Table DDL
```sql
CREATE TABLE IF NOT EXISTS dwh.agg_sales_product_month (
  year       INT NOT NULL,
  month      INT NOT NULL,
  product_sk INT NOT NULL,
  revenue    NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, product_sk)
);
```
Line‑by‑line
- year/month ints make it easy to filter and partition.
- product_sk links back to dim_product; PK enforces uniqueness per month/product.

B) Initial full build
```sql
INSERT INTO dwh.agg_sales_product_month(year, month, product_sk, revenue)
SELECT dd.year,
       dd.month,
       fs.product_sk,
       ROUND(SUM(fs.amount),2) AS revenue
FROM dwh.fact_sales fs
JOIN dwh.dim_date dd ON dd.date_key = fs.date_key
GROUP BY dd.year, dd.month, fs.product_sk;
```
Notes
- We don’t join dim_product here because the grain is already product_sk; add it if you need attributes (e.g., category) in the aggregate.

C) Validation — reconcile to base facts at the same grain
```sql
WITH base AS (
  SELECT dd.year, dd.month, fs.product_sk, ROUND(SUM(fs.amount),2) AS rev
  FROM dwh.fact_sales fs
  JOIN dwh.dim_date dd ON dd.date_key = fs.date_key
  GROUP BY dd.year, dd.month, fs.product_sk
), diff AS (
  SELECT COALESCE(b.year, a.year)  AS year,
         COALESCE(b.month, a.month) AS month,
         COALESCE(b.product_sk, a.product_sk) AS product_sk,
         COALESCE(a.revenue,0) AS agg_rev,
         COALESCE(b.rev,0)     AS base_rev,
         ROUND(COALESCE(a.revenue,0) - COALESCE(b.rev,0), 2) AS delta
  FROM base b
  FULL OUTER JOIN dwh.agg_sales_product_month a
    ON a.year=b.year AND a.month=b.month AND a.product_sk=b.product_sk
)
SELECT * FROM diff
WHERE delta <> 0
ORDER BY year DESC, month DESC, product_sk
LIMIT 50;
```
Line‑by‑line
- base: recompute from fact to compare against the aggregate.
- FULL OUTER JOIN: catch missing rows on either side (a build bug or grain mismatch).
- delta: any nonzero value indicates a discrepancy to investigate.

Exercise 2 — Stored procedure to refresh a given year/month
Goal
- Idempotently rebuild aggregates for a target period (y, m) across multiple agg tables.

Solution (PL/pgSQL)
```sql
CREATE OR REPLACE PROCEDURE dwh.refresh_month(y INT, m INT)
LANGUAGE plpgsql
AS $$
BEGIN
  -- 1) Category aggregate --------------------------------------------------
  DELETE FROM dwh.agg_sales_category_month a
  WHERE a.year = y AND a.month = m;

  INSERT INTO dwh.agg_sales_category_month(year, month, category, revenue)
  SELECT dd.year, dd.month, dp.category, ROUND(SUM(fs.amount),2)
  FROM dwh.fact_sales fs
  JOIN dwh.dim_date dd    ON dd.date_key = fs.date_key
  JOIN dwh.dim_product dp ON dp.product_sk = fs.product_sk
  WHERE dd.year = y AND dd.month = m
  GROUP BY dd.year, dd.month, dp.category;

  -- 2) Customer aggregate --------------------------------------------------
  DELETE FROM dwh.agg_sales_customer_month a
  WHERE a.year = y AND a.month = m;

  INSERT INTO dwh.agg_sales_customer_month(year, month, customer_sk, revenue)
  SELECT dd.year, dd.month, fs.customer_sk, ROUND(SUM(fs.amount),2)
  FROM dwh.fact_sales fs
  JOIN dwh.dim_date dd ON dd.date_key = fs.date_key
  WHERE dd.year = y AND dd.month = m
  GROUP BY dd.year, dd.month, fs.customer_sk;

  -- 3) Product aggregate ---------------------------------------------------
  DELETE FROM dwh.agg_sales_product_month a
  WHERE a.year = y AND a.month = m;

  INSERT INTO dwh.agg_sales_product_month(year, month, product_sk, revenue)
  SELECT dd.year, dd.month, fs.product_sk, ROUND(SUM(fs.amount),2)
  FROM dwh.fact_sales fs
  JOIN dwh.dim_date dd ON dd.date_key = fs.date_key
  WHERE dd.year = y AND dd.month = m
  GROUP BY dd.year, dd.month, fs.product_sk;
END;
$$;
```
How to run and verify
```sql
CALL dwh.refresh_month(2026, 1);
-- Quick spot check for the refreshed slice
SELECT * FROM dwh.agg_sales_product_month WHERE year=2026 AND month=1 ORDER BY revenue DESC LIMIT 10;
```

Best practices
- Wrap refreshes in a transaction if you refresh multiple months at once.
- Consider partitioning aggregates by (year, month) for fast delete/insert.
- Maintain foreign keys only when necessary; aggregates often omit them for speed.
