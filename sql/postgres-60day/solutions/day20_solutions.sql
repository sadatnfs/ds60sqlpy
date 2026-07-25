-- Day 20 solutions: FIRST_VALUE and LAST_VALUE
SET search_path TO training, public;

-- Exercise 1: current-month product revenue compared with first observed month.
WITH monthly AS (
  SELECT p.product_id,
         date_trunc('month', o.order_date)::date AS month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM products p
  JOIN order_items oi ON oi.product_id = p.product_id
  JOIN orders o ON o.order_id = oi.order_id
  GROUP BY p.product_id, date_trunc('month', o.order_date)
), windowed AS (
  SELECT product_id,
         month,
         revenue,
         FIRST_VALUE(revenue) OVER (
           PARTITION BY product_id
           ORDER BY month
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         ) AS first_month_revenue
  FROM monthly
), firsts AS (
  SELECT DISTINCT product_id, first_month_revenue FROM windowed
), current_month AS (
  SELECT product_id, revenue
  FROM monthly
  WHERE month = date_trunc('month', CURRENT_DATE)::date
)
SELECT p.product_id,
       p.name,
       ROUND(COALESCE(cm.revenue, 0), 2) AS current_month_revenue,
       ROUND(f.first_month_revenue, 2) AS first_month_revenue,
       ROUND(COALESCE(cm.revenue, 0) - f.first_month_revenue, 2)
         AS change_from_first_month
FROM products p
LEFT JOIN firsts f USING (product_id)
LEFT JOIN current_month cm USING (product_id)
ORDER BY p.product_id;

-- Exercise 2: salary versus the earliest-hired employee's salary in a department.
-- This is only a simulation: the course schema has no salary-history table.
SELECT d.name AS department,
       e.employee_id,
       e.full_name,
       e.hire_date,
       e.salary,
       FIRST_VALUE(e.salary) OVER (
         PARTITION BY e.department_id
         ORDER BY e.hire_date, e.employee_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS earliest_hire_salary,
       e.salary - FIRST_VALUE(e.salary) OVER (
         PARTITION BY e.department_id
         ORDER BY e.hire_date, e.employee_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS difference
FROM employees e
JOIN departments d ON d.department_id = e.department_id
ORDER BY department, e.hire_date, e.employee_id;
