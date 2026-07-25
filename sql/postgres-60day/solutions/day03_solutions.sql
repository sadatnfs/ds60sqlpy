-- Day 03 solutions: INNER JOINs
SET search_path TO training, public;

-- Exercise 1: top 20 customers by item-level revenue.
SELECT c.customer_id,
       c.full_name,
       c.country,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id, c.full_name, c.country
ORDER BY revenue DESC, c.customer_id
LIMIT 20;

-- Exercise 2: last 100 orders whose course status is exactly "paid".
-- Limit orders first, then aggregate payments so split rows do not duplicate.
WITH latest_paid_orders AS (
  SELECT order_id, customer_id, order_date, total_amount
  FROM orders
  WHERE status = 'paid'
  ORDER BY order_date DESC, order_id DESC
  LIMIT 100
), payment_summary AS (
  SELECT p.order_id,
         string_agg(DISTINCT p.method, ', ' ORDER BY p.method) AS methods,
         SUM(p.amount) AS amount_paid
  FROM payments p
  JOIN latest_paid_orders lpo USING (order_id)
  GROUP BY p.order_id
)
SELECT lpo.order_id,
       lpo.customer_id,
       lpo.order_date,
       lpo.total_amount,
       ps.methods,
       ROUND(ps.amount_paid, 2) AS amount_paid
FROM latest_paid_orders lpo
LEFT JOIN payment_summary ps USING (order_id)
ORDER BY lpo.order_date DESC, lpo.order_id DESC;

-- Exercise 3: employees, departments, and optional manager names.
SELECT d.name AS department,
       e.employee_id,
       e.full_name AS employee,
       m.full_name AS manager
FROM employees e
JOIN departments d ON d.department_id = e.department_id
LEFT JOIN employees m ON m.employee_id = e.manager_id
ORDER BY d.name, manager NULLS FIRST, employee;
