-- Day 41 solutions: complex aggregations
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
