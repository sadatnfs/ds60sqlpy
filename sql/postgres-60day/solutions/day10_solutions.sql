-- Day 10 worked solutions: DML with subqueries
BEGIN;
SET search_path TO training, public;

-- Worked INSERT ... SELECT: materialize category revenue in a temporary table.
CREATE TEMP TABLE tmp_category_revenue AS
SELECT p.category,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category;

SELECT * FROM tmp_category_revenue ORDER BY revenue DESC;

-- Worked UPDATE: give employees in two selected departments a 5% raise.
UPDATE employees e
SET salary = ROUND(e.salary * 1.05, 2)
WHERE EXISTS (
  SELECT 1
  FROM departments d
  WHERE d.department_id = e.department_id
    AND d.name IN ('Sales', 'Engineering')
)
RETURNING employee_id, full_name, salary;

-- Worked DELETE: remove only old orders for which no payment row exists.
-- NOT EXISTS is essential; deleting "old" orders alone would remove paid data.
DELETE FROM orders o
WHERE o.order_date < CURRENT_TIMESTAMP - interval '365 days'
  AND NOT EXISTS (
    SELECT 1
    FROM payments p
    WHERE p.order_id = o.order_id
  )
RETURNING o.order_id, o.order_date;

-- This answer is demonstrative and never persists its DML.
ROLLBACK;
