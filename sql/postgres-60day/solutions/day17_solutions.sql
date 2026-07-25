-- Day 17 solutions: ranking functions
SET search_path TO training, public;

-- Exercise 1: product revenue ranks within category.
-- RANK leaves gaps after ties; DENSE_RANK does not.
WITH product_revenue AS (
  SELECT p.category,
         p.product_id,
         p.name,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM products p
  JOIN order_items oi ON oi.product_id = p.product_id
  GROUP BY p.category, p.product_id, p.name
)
SELECT category,
       product_id,
       name,
       ROUND(revenue, 2) AS revenue,
       RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS revenue_rank,
       DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC)
         AS dense_revenue_rank
FROM product_revenue
ORDER BY category, revenue DESC, product_id;

-- Exercise 2: top three customers per country by lifetime revenue.
WITH lifetime AS (
  SELECT c.country,
         c.customer_id,
         c.full_name,
         COALESCE(SUM(o.total_amount), 0) AS lifetime_revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  GROUP BY c.country, c.customer_id, c.full_name
), ranked AS (
  SELECT *,
         DENSE_RANK() OVER (
           PARTITION BY country
           ORDER BY lifetime_revenue DESC
         ) AS country_rank
  FROM lifetime
)
SELECT country,
       customer_id,
       full_name,
       ROUND(lifetime_revenue, 2) AS lifetime_revenue,
       country_rank
FROM ranked
WHERE country_rank <= 3
ORDER BY country, country_rank, customer_id;
