-- Day 10: INSERT/UPDATE/DELETE with Subqueries (safe via ROLLBACK)
BEGIN;
SET search_path TO training, public;

-- Example: Insert promotional budget rollups into a temp table
CREATE TEMP TABLE tmp_category_revenue AS
SELECT p.category, ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category;

SELECT * FROM tmp_category_revenue ORDER BY revenue DESC;

-- Example: Update salaries by department performance (demo only)
UPDATE employees e
SET salary = salary * 1.05
WHERE department_id IN (
  SELECT department_id FROM departments WHERE name IN ('Sales','Engineering')
) RETURNING *;

-- Example: Delete unpaid old orders (demo only)
DELETE FROM orders o
WHERE o.order_date < now() - interval '365 days'
  AND NOT EXISTS (
    SELECT 1
    FROM payments p
    WHERE p.order_id = o.order_id
  )
RETURNING o.order_id;

-- All changes will be rolled back below
ROLLBACK;
