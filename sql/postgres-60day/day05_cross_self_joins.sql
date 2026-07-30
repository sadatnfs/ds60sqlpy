-- Day 5: CROSS JOINs and Self-joins
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
-- Assumptions: The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
-- Pitfall: An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
-- Predict row grain and NULL/order behavior before executing each example.

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
ORDER BY manager NULLS FIRST,
         m.employee_id NULLS FIRST,
         employee,
         e.employee_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every employee with their direct manager when present.
--    Hint: Self join employees and use a left join so top-level employees remain visible.
-- 2. [Query writing] Find employees who manage nobody.
--    Hint: Left join candidate managers to reports and retain managers with no right-side match.
-- 3. [Query writing] Build a complete grid of six recent months and all expense categories.
--    Hint: Cross join two small declared dimensions; do not cross join raw fact tables.
-- 4. [Prediction] Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
--    Hint: Cross-join cardinality is the product of input row counts.
-- 5. [Debugging] List unique employee pairs in the same department without self-pairs or mirrored duplicates.
--    Hint: Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
-- 6. [Extension] Show each employee, their manager, and their manager's manager.
--    Hint: Use two independently aliased left self joins; NULLs indicate the hierarchy ends.

ROLLBACK;
