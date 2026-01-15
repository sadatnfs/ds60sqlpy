-- Day 17: ROW_NUMBER, RANK, DENSE_RANK
BEGIN;
SET search_path TO training, public;

-- Rank customers by lifetime revenue (ties vs gaps)
WITH cust_rev AS (
  SELECT c.customer_id,
         c.full_name,
         COALESCE(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),0) AS revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id, c.full_name
)
SELECT customer_id,
       full_name,
       revenue,
       ROW_NUMBER() OVER (ORDER BY revenue DESC) AS row_num,
       RANK()       OVER (ORDER BY revenue DESC) AS rank_pos,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_pos
FROM cust_rev
ORDER BY revenue DESC
LIMIT 30;

-- Rank employees by salary within department
SELECT e.department_id,
       d.name AS department,
       e.employee_id,
       e.full_name,
       e.salary,
       RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_rank
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id
ORDER BY department, dept_rank
LIMIT 50;

-- Exercises
-- 1) Rank products by revenue within category; compare RANK vs DENSE_RANK differences.
-- 2) Top 3 customers per country by lifetime revenue.

ROLLBACK;
