-- Day 41 solutions: complex aggregations
-- SOLUTION READING MAP — sql-41: Complex Aggregations
-- Explanation: sql/postgres-60day/solutions/day41_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day41_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
SET search_path TO training, public;

-- Exercise 1: six category dashboard metrics over useful windows.
WITH lines AS (
  SELECT p.category,
         o.order_id,
         o.customer_id,
         o.order_date,
         oi.quantity,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
)
SELECT category,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ), 2) AS revenue_30d,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ), 2) AS revenue_90d,
       COUNT(DISTINCT order_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS orders_30d,
       SUM(quantity) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS units_30d,
       COUNT(DISTINCT customer_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ) AS customers_90d,
       ROUND(
         SUM(revenue) FILTER (
           WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
         )
         / NULLIF(
             COUNT(DISTINCT order_id) FILTER (
               WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
             ),
             0
           ),
         2
       ) AS revenue_per_order_30d
FROM lines
GROUP BY category
ORDER BY revenue_30d DESC NULLS LAST, category;

-- Exercise 2: top five product names by revenue for each country.
WITH product_revenue AS (
  SELECT c.country,
         p.product_id,
         p.name,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM customers c
  JOIN orders o USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY c.country, p.product_id, p.name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
SELECT country,
       string_agg(name, ', ' ORDER BY product_rank) AS top_five_products
FROM ranked
WHERE product_rank <= 5
GROUP BY country
ORDER BY country;

-- Exercise 3: explicit grouping sets omit country/category detail. CUBE emits
-- detail, each one-column subtotal, and the grand total. GROUPING packs the
-- omitted dimensions into a right-to-left bit mask: category is bit 0 and
-- country is bit 1.
WITH lines AS (
  SELECT c.country, p.category,
         oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), cube_rows AS (
  SELECT country,
         category,
         SUM(revenue) AS revenue,
         GROUPING(country, category) AS grouping_mask
  FROM lines
  GROUP BY CUBE (country, category)
)
SELECT country,
       category,
       revenue,
       grouping_mask,
       CASE grouping_mask
         WHEN 0 THEN 'detail'
         WHEN 1 THEN 'country subtotal'
         WHEN 2 THEN 'category subtotal'
         WHEN 3 THEN 'grand total'
       END AS grouping_level
FROM cube_rows
ORDER BY grouping_mask, country, category;

-- Exercise 4: FILTER states each metric population next to its measure.
SELECT c.country,
       COUNT(*) AS orders,
       COUNT(*) FILTER (WHERE o.status = 'paid') AS paid_orders,
       SUM(o.total_amount) FILTER (WHERE o.status = 'paid') AS paid_revenue,
       SUM(o.total_amount) FILTER (WHERE o.status = 'returned') AS returned_revenue,
       COUNT(DISTINCT o.customer_id) AS customers
FROM orders o
JOIN customers c USING (customer_id)
GROUP BY c.country
ORDER BY c.country;

-- Exercise 5: GROUPING distinguishes generated subtotal NULL from a stored
-- NULL. The controlled NULL row makes both cases observable even though the
-- course customers table normally requires a country.
WITH country_input AS (
  SELECT country
  FROM customers
  UNION ALL
  SELECT NULL::text
)
SELECT CASE WHEN GROUPING(country) = 1 THEN 'ALL COUNTRIES'
            ELSE COALESCE(country, '(stored null)') END AS country_label,
       GROUPING(country) AS is_subtotal,
       COUNT(*) AS customers
FROM country_input
GROUP BY GROUPING SETS ((country), ())
ORDER BY is_subtotal, country_label;

-- Exercise 6: array_agg over no rows is NULL; COALESCE needs the same text[]
-- result type to implement the chosen empty-array display policy.
SELECT COALESCE(array_agg(email) FILTER (WHERE false), '{}'::text[])
         AS empty_email_array
FROM customers;
