-- Day 5: CROSS JOINs and Self-joins
-- BEGINNER WORKFLOW — sql-05: Cross Self Joins
-- Guide: sql/postgres-60day/companion-guides/day05_cross_self_joins.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-05/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: products, customers, employees.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-05 Exercise 1, read from `employees`. Build the answer toward `employee_id`, `employee_name`, `manager_id`, and `manager_name`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-05 Exercise 1, expected output: One row per employee. The final columns are `employee_id`, `employee_name`, `manager_id`, and `manager_name`. The final order is `e.employee_id`.
--    Verify: For sql-05 Exercise 1, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `employee_name`, `manager_id`, and `manager_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
--    Hint ladder, rung 1: For sql-05 Exercise 1, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 2. [Query writing] Find employees who manage nobody.
--    Hint: Left join candidate managers to reports and retain managers with no right-side match.
--    Inputs: For sql-05 Exercise 2, read from `employees`. Build the answer toward `employee_id`, and `full_name`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-05 Exercise 2, expected output: One row per leaf employee. The final columns are `employee_id`, and `full_name`. The final order is `e.employee_id`.
--    Verify: For sql-05 Exercise 2, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, and `full_name` values match those staged rows without unintended fanout or loss. Add one row for which `(report.employee_id IS NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.
--    Hint ladder, rung 1: For sql-05 Exercise 2, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 3. [Query writing] Build a complete grid of six recent months and all expense categories.
--    Hint: Cross join two small declared dimensions; do not cross join raw fact tables.
--    Inputs: For sql-05 Exercise 3, read from `expenses`. Build the answer toward `category`, and `month_start`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-05 Exercise 3, expected output: Six rows per distinct expense category. The final columns are `category`, and `month_start`. The final order is `c.category, m.month_start`.
--    Verify: For sql-05 Exercise 3, project `category` plus the raw source columns from `expenses` at each join stage; record row count and distinct `category`, then assert the final `category`, and `month_start` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
--    Hint ladder, rung 1: For sql-05 Exercise 3, run `months`, and `categories` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 4. [Prediction] Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
--    Hint: Cross-join cardinality is the product of input row counts.
--    Inputs: For sql-05 Exercise 4, read from `departments`. Build the answer toward `department_month_combinations`; keep `department_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-05 Exercise 4, expected output: One row containing 72. The final columns are `department_month_combinations`.
--    Verify: For sql-05 Exercise 4, project `department_id` plus the raw source columns from `departments` at each join stage; record row count and distinct `department_id`, then assert the final `department_month_combinations` values match those staged rows without unintended fanout or loss. Add one source row with a new `department_id`; verify the result gains exactly one row carrying that `department_id` value.
--    Hint ladder, rung 1: For sql-05 Exercise 4, run `months` one at a time. Record each CTE's row count and `department_id` uniqueness before the next stage uses it.
-- 5. [Debugging] List unique employee pairs in the same department without self-pairs or mirrored duplicates.
--    Hint: Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
--    Inputs: For sql-05 Exercise 5, read from `employees` twice at employee grain. Build the answer toward `department_id`, `first_employee_id`, and `second_employee_id`; keep all three columns visible as the composite pair key.
--    Expected result/shape: For sql-05 Exercise 5, expected output: One row per unordered same-department pair. The final columns are `department_id`, `first_employee_id`, and `second_employee_id`. The final order is `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
--    Verify: For sql-05 Exercise 5, assert `first_employee_id < second_employee_id` for every row, require uniqueness of (`department_id`, `first_employee_id`, `second_employee_id`), and anti-check for both self-pairs and mirrored `(a, b)` / `(b, a)` pairs. For each department with `n` employees, independently require `n * (n - 1) / 2` result rows.
--    Hint ladder, rung 1: For sql-05 Exercise 5, start with the first relation in `employees`; after each join, record total rows and distinct `department_id` so the exact fanout or loss is visible.
-- 6. [Extension] Show each employee, their manager, and their manager's manager.
--    Hint: Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
--    Inputs: For sql-05 Exercise 6, read from `employees`. Build the answer toward `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-05 Exercise 6, expected output: One row per employee with up to two ancestor columns. The final columns are `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`. The final order is `e.employee_id`.
--    Verify: For sql-05 Exercise 6, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
--    Hint ladder, rung 1: For sql-05 Exercise 6, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.

ROLLBACK;
