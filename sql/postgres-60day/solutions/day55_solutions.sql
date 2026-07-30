-- Day 55 solutions: BI drill-down and subtotal design
SET search_path TO training, public;

WITH line AS (
  SELECT c.country,
         p.category,
         o.status,
         p.product_id,
         p.name,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), rollup_rows AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY ROLLUP (country, category)
), cube_rows AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
)
-- Exercise 1: CUBE adds category-only subtotals that ROLLUP omits.
SELECT (SELECT COUNT(*) FROM rollup_rows) AS rollup_row_count,
       (SELECT COUNT(*) FROM cube_rows) AS cube_row_count;

WITH line AS (
  SELECT c.country,
         p.category,
         o.status,
         p.product_id,
         p.name,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
), product_revenue AS (
  SELECT country,
         category,
         status,
         product_id,
         name,
         SUM(revenue) AS revenue
  FROM line
  GROUP BY country, category, status, product_id, name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country, category, status
           ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
-- Exercise 2: status-aware top-five drill-down.
SELECT country,
       category,
       status,
       product_id,
       name,
       ROUND(revenue, 2) AS revenue,
       product_rank
FROM ranked
WHERE product_rank <= 5
ORDER BY country, category, status, product_rank;

-- Exercise 3: GROUPING's bit mask documents each ROLLUP level: detail (0),
-- category subtotal within country (1), and grand total (3).
WITH line AS (
  SELECT c.country, p.category,
         oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
)
SELECT country, category, SUM(revenue) AS revenue,
       GROUPING(country, category) AS grouping_mask
FROM line
GROUP BY ROLLUP (country, category)
ORDER BY grouping_mask, country, category;

-- Exercise 4: PostgreSQL's GROUPING(args) returns the stable bit mask used as
-- both machine-readable level ID and source for display labels.
WITH line AS (
  SELECT c.country, p.category,
         oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
)
SELECT GROUPING(country, category) AS level_id,
       CASE GROUPING(country, category)
         WHEN 0 THEN 'country/category detail'
         WHEN 1 THEN 'country subtotal'
         WHEN 3 THEN 'grand total'
       END AS level_name,
       country, category, SUM(revenue) AS revenue
FROM line
GROUP BY ROLLUP (country, category)
ORDER BY level_id, country, category;

-- Exercise 5: ROW_NUMBER and product_id as the final sort key guarantee no more
-- than five deterministic products per group even when revenue ties.
WITH revenue AS (
  SELECT c.country, p.product_id, p.name,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY c.country, p.product_id, p.name
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY country ORDER BY revenue DESC, product_id
  ) AS position
  FROM revenue
)
SELECT * FROM ranked WHERE position <= 5 ORDER BY country, position;

-- Exercise 6: grouping flag and stored-member label are separate columns, so
-- a real unknown value can never masquerade as the ALL subtotal.
SELECT CASE WHEN GROUPING(country) = 1 THEN 'ALL'
            ELSE COALESCE(country, '(unknown member)') END AS display_country,
       GROUPING(country) AS is_generated_total,
       COUNT(*) AS customers
FROM customers
GROUP BY GROUPING SETS ((country), ())
ORDER BY is_generated_total, display_country;
