-- Day 05 solutions: CROSS JOINs and self-joins
SET search_path TO training, public;

-- Exercise 1: all 25 combinations of the five leading categories and countries.
WITH category_revenue AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
  ORDER BY revenue DESC
  LIMIT 5
), country_revenue AS (
  SELECT c.country,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM customers c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.country
  ORDER BY revenue DESC
  LIMIT 5
)
SELECT cr.category,
       cor.country,
       ROUND(cr.revenue, 2) AS category_revenue,
       ROUND(cor.revenue, 2) AS country_revenue
FROM category_revenue cr
CROSS JOIN country_revenue cor
ORDER BY cr.revenue DESC, cor.revenue DESC;

-- Exercise 2: employee -> manager -> manager's manager.
SELECT e.employee_id,
       e.full_name AS employee,
       m.full_name AS manager,
       gm.full_name AS managers_manager
FROM employees e
LEFT JOIN employees m ON m.employee_id = e.manager_id
LEFT JOIN employees gm ON gm.employee_id = m.manager_id
ORDER BY gm.full_name NULLS FIRST, m.full_name NULLS FIRST, e.full_name;
