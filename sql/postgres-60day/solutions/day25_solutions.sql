-- Day 25 solutions: multiple CTEs and hierarchies
SET search_path TO training, public;

-- Exercise 1: a three-level org report enriched with department aggregates.
WITH department_metrics AS (
  SELECT department_id,
         COUNT(*) AS department_headcount,
         ROUND(SUM(salary), 2) AS department_payroll,
         ROUND(AVG(salary), 2) AS department_avg_salary
  FROM employees
  GROUP BY department_id
), three_levels AS (
  SELECT e.department_id,
         e.employee_id,
         e.full_name AS employee,
         m.full_name AS manager,
         gm.full_name AS managers_manager
  FROM employees e
  LEFT JOIN employees m ON m.employee_id = e.manager_id
  LEFT JOIN employees gm ON gm.employee_id = m.manager_id
)
SELECT d.name AS department,
       t.employee_id,
       t.employee,
       t.manager,
       t.managers_manager,
       dm.department_headcount,
       dm.department_payroll,
       dm.department_avg_salary
FROM three_levels t
JOIN departments d ON d.department_id = t.department_id
JOIN department_metrics dm ON dm.department_id = t.department_id
ORDER BY department, managers_manager NULLS FIRST, manager NULLS FIRST, employee;

-- Exercise 2: filter -> enrich -> aggregate -> present.
WITH filtered_orders AS (
  SELECT *
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
), enriched_lines AS (
  SELECT fo.order_id,
         fo.order_date::date AS order_day,
         c.country,
         p.category,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM filtered_orders fo
  JOIN customers c ON c.customer_id = fo.customer_id
  JOIN order_items oi ON oi.order_id = fo.order_id
  JOIN products p ON p.product_id = oi.product_id
), aggregated AS (
  SELECT country,
         category,
         COUNT(DISTINCT order_id) AS orders,
         SUM(line_revenue) AS revenue
  FROM enriched_lines
  GROUP BY country, category
)
SELECT country,
       category,
       orders,
       ROUND(revenue, 2) AS revenue,
       ROUND(revenue / NULLIF(orders, 0), 2) AS revenue_per_order
FROM aggregated
ORDER BY revenue DESC, country, category;
