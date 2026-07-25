-- Day 18 solutions: LAG and LEAD
SET search_path TO training, public;

-- Exercise 1: dense product-month revenue, so LAG is the preceding calendar
-- month rather than merely the preceding month that happened to have sales.
WITH month_bounds AS (
  SELECT date_trunc('month', MIN(order_date) AT TIME ZONE 'UTC')::date AS first_month,
         date_trunc('month', MAX(order_date) AT TIME ZONE 'UTC')::date AS last_month
  FROM orders
), months AS (
  SELECT generated_month::date AS sales_month
  FROM month_bounds
  CROSS JOIN LATERAL generate_series(
    first_month, last_month, interval '1 month'
  ) AS g(generated_month)
), monthly_sales AS (
  SELECT oi.product_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS sales_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN orders o USING (order_id)
  GROUP BY oi.product_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
), dense_product_months AS (
  SELECT p.product_id,
         p.name,
         m.sales_month,
         COALESCE(ms.revenue, 0) AS revenue
  FROM products p
  CROSS JOIN months m
  LEFT JOIN monthly_sales ms
    ON ms.product_id = p.product_id
   AND ms.sales_month = m.sales_month
)
SELECT product_id,
       name,
       sales_month,
       ROUND(revenue, 2) AS monthly_sales,
       ROUND(
         LAG(revenue) OVER (PARTITION BY product_id ORDER BY sales_month),
         2
       ) AS previous_month_sales
FROM dense_product_months
ORDER BY product_id, sales_month;

-- Exercise 2: LEAD over distinct salaries makes "higher" strict.
WITH distinct_department_salaries AS (
  SELECT DISTINCT department_id, salary
  FROM employees
), salary_steps AS (
  SELECT department_id,
         salary,
         LEAD(salary) OVER (
           PARTITION BY department_id ORDER BY salary
         ) AS next_higher_salary
  FROM distinct_department_salaries
)
SELECT d.name AS department,
       e.employee_id,
       e.full_name,
       e.salary,
       ss.next_higher_salary,
       ss.next_higher_salary - e.salary AS gap_to_next_higher
FROM employees e
JOIN departments d USING (department_id)
JOIN salary_steps ss
  ON ss.department_id = e.department_id
 AND ss.salary = e.salary
ORDER BY department, e.salary, e.employee_id;
