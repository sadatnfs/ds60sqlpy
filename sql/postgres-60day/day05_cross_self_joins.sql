-- Day 5: CROSS JOINs and Self-joins
BEGIN;
SET search_path TO training, public;

-- CROSS JOIN: all category-country pairs with counts
WITH cats AS (
  SELECT DISTINCT category FROM products
), ctries AS (
  SELECT DISTINCT country FROM customers
)
SELECT cats.category, ctries.country
FROM cats CROSS JOIN ctries
ORDER BY 1,2;

-- Self-join: employee-manager hierarchy
SELECT e.employee_id, e.full_name AS employee, m.full_name AS manager
FROM employees e
LEFT JOIN employees m ON m.employee_id = e.manager_id
ORDER BY manager NULLS FIRST, employee
LIMIT 50;

-- Exercises
-- 1) Create a CROSS JOIN between top 5 categories and top 5 countries by revenue.
-- 2) Show 3-level hierarchy employee -> manager -> manager's manager.

ROLLBACK;
