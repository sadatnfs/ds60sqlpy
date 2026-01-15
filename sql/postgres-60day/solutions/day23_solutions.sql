-- Day 23 - Solutions: CTEs Introduction
-- Assumes: orders, order_items, products, customers

/*
Exercise 1) Create a monthly_revenue CTE and select top 3 months.
*/
WITH monthly_revenue AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT month, ROUND(revenue,2) AS revenue
FROM monthly_revenue
ORDER BY revenue DESC
LIMIT 3;

/*
Exercise 2) Create a CTE filtering Electronics category orders, then aggregate by country.
*/
WITH electronics AS (
  SELECT o.order_id,
         o.customer_id,
         o.order_date,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_rev
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE p.category = 'Electronics'
)
SELECT c.country,
       ROUND(SUM(e.line_rev),2) AS revenue
FROM electronics e
JOIN customers c ON c.customer_id = e.customer_id
GROUP BY c.country
ORDER BY revenue DESC
LIMIT 200;
