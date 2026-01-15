-- Day 25 - Solutions: Multiple CTEs and Hierarchies
-- Assumes: orders, order_items, products, customers, employees

/*
Exercise 1) 4-stage pipeline from order_items to a country-category monthly summary.
*/
WITH lines AS (
  SELECT oi.order_id, oi.product_id, (oi.unit_price*oi.quantity*(1-oi.discount)) AS line_rev
  FROM order_items oi
), enriched AS (
  SELECT l.order_id, p.category, l.line_rev
  FROM lines l JOIN products p ON p.product_id = l.product_id
), monthly AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         c.country,
         e.category,
         SUM(e.line_rev) AS revenue
  FROM orders o
  JOIN enriched e ON e.order_id = o.order_id
  JOIN customers c ON c.customer_id = o.customer_id
  GROUP BY DATE_TRUNC('month', o.order_date), c.country, e.category
)
SELECT month, country, category, ROUND(revenue,2) AS revenue
FROM monthly
ORDER BY month DESC, revenue DESC
LIMIT 500;

/*
Exercise 2) Employee tree with depth; join monthly revenue per employee’s accounts to compute team totals by level.
(Outline: depends on schema; example shows structure.)
*/
WITH RECURSIVE team AS (
  SELECT id, manager_id, 0 AS depth FROM employees WHERE id = 1
  UNION ALL
  SELECT e.id, e.manager_id, t.depth + 1 FROM employees e JOIN team t ON e.manager_id = t.id
), sales AS (
  SELECT account_owner_id AS id,
         DATE_TRUNC('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY account_owner_id, DATE_TRUNC('month', order_date)
)
SELECT t.depth, s.month, SUM(s.revenue) AS team_revenue
FROM team t JOIN sales s ON s.id = t.id
GROUP BY t.depth, s.month
ORDER BY s.month DESC, t.depth;
