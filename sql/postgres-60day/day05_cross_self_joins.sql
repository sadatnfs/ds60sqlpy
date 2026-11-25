-- Day 5: CROSS JOINs and Self-joins
-- BEGINNER WORKFLOW - sql-05: Cross Self Joins
-- Guide: sql/postgres-60day/companion-guides/day05_cross_self_joins.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-05.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT DISTINCT
    category
  FROM
    products
),
ctries AS (
  SELECT DISTINCT
    country
  FROM
    customers
)
SELECT
  cats.category,
  ctries.country
FROM
  cats
  CROSS JOIN ctries
ORDER BY
  1,
  2;

-- Self-join: employee-manager hierarchy
SELECT
  e.employee_id,
  e.full_name AS employee,
  m.full_name AS manager
FROM
  employees e
  LEFT JOIN employees m ON m.employee_id = e.manager_id
ORDER BY
  manager NULLS FIRST,
  m.employee_id NULLS FIRST,
  employee,
  e.employee_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every employee with their direct manager when present.
--    Hint: Self join employees and use a left join so top-level employees remain visible.
--    Inputs: For sql-05 Exercise 1, self-join the 100 `employees` rows, aliasing the manager copy as `m`; 6 employees (1 through 6) have no `manager_id`, and the other 94 report to employee 1, 2, or 8. Return `employee_id`, `employee_name`, `manager_id`, and `manager_name`.
--    Expected result/shape: For sql-05 Exercise 1, return 100 rows, one per employee; employees 1 through 6 show `NULL` manager columns, employee 7 reports to Employee 2, employee 8 to Employee 1, and the remaining 92 to Employee 8. The final columns are `employee_id`, `employee_name`, `manager_id`, and `manager_name`. The final order is `e.employee_id`.
--    Verify: For sql-05 Exercise 1, confirm 100 distinct `employee_id` values and exactly 6 rows with `manager_name IS NULL`. Switch `LEFT JOIN` to an inner join and the count must fall to 94, losing exactly employees 1 through 6.
--    Hint ladder, rung 1: For sql-05 Exercise 1, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 2. [Query writing] Find employees who manage nobody.
--    Hint: Left join candidate managers to reports and retain managers with no right-side match.
--    Inputs: For sql-05 Exercise 2, `LEFT JOIN` each of the 100 `employees` to the employees who report to them and keep rows with no report; only employees 1, 2, and 8 manage anyone.
--    Expected result/shape: For sql-05 Exercise 2, return 97 rows, one per employee who manages nobody, from employee 3 to employee 100 with 1, 2, and 8 missing. The final columns are `employee_id`, and `full_name`. The final order is `e.employee_id`.
--    Verify: For sql-05 Exercise 2, confirm `SELECT COUNT(DISTINCT manager_id) FROM employees` returns 3 and that 100 minus 3 equals the 97 rows. Inside a rolled-back transaction, make employee 100 report to employee 3; the result must drop to 96 rows because employee 3 is no longer a leaf.
--    Hint ladder, rung 1: For sql-05 Exercise 2, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 3. [Query writing] Build a complete grid of six recent months and all expense categories.
--    Hint: Cross join two small declared dimensions; do not cross join raw fact tables.
--    Inputs: For sql-05 Exercise 3, cross join the 5 distinct `expenses` categories with a `generate_series` of 6 month starts, from five months before the current month through the current month.
--    Expected result/shape: For sql-05 Exercise 3, return 30 rows, six month starts for each of `COGS`, `G&A`, `Infrastructure`, `Marketing`, and `Payroll`, whether or not the month has expenses. The final columns are `category`, and `month_start`. The final order is `c.category, m.month_start`.
--    Verify: For sql-05 Exercise 3, confirm 30 distinct `(category, month_start)` pairs and that each category appears exactly 6 times. Widen the series to start eleven months back and the result must grow to 60 rows, 5 categories times 12 months.
--    Hint ladder, rung 1: For sql-05 Exercise 3, run `months`, and `categories` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 4. [Prediction] Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
--    Hint: Cross-join cardinality is the product of input row counts.
--    Inputs: For sql-05 Exercise 4, cross join the 6 `departments` rows with `generate_series(1, 12)` and count the combinations; no department key is returned.
--    Expected result/shape: For sql-05 Exercise 4, return exactly one row with `department_month_combinations` equal to 72. The final columns are `department_month_combinations`.
--    Verify: For sql-05 Exercise 4, confirm 72 equals `SELECT COUNT(*) FROM departments` (6) times 12. Change the series to `generate_series(1, 6)` and the count must become 36, showing that a cross join multiplies the row counts.
--    Hint ladder, rung 1: For sql-05 Exercise 4, run `months` one at a time. Record each CTE's row count and `department_id` uniqueness before the next stage uses it.
-- 5. [Debugging] List unique employee pairs in the same department without self-pairs or mirrored duplicates.
--    Hint: Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
--    Inputs: For sql-05 Exercise 5, self-join the 100 `employees` rows on `department_id`; departments 1 to 4 hold 17 employees each and departments 5 and 6 hold 16 each. Return `department_id`, `first_employee_id`, and `second_employee_id` as the composite pair key.
--    Expected result/shape: For sql-05 Exercise 5, return 784 rows, one row per unordered same-department pair: 136 for each 17-person department and 120 for each 16-person department, starting with the pair 1 and 7 in department 1. The final columns are `department_id`, `first_employee_id`, and `second_employee_id`. The final order is `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
--    Verify: For sql-05 Exercise 5, confirm `first_employee_id < second_employee_id` on all 784 rows and that 4 * 136 + 2 * 120 equals 784. Joining on `department_id` alone returns 1,668 rows, which includes 100 self-pair rows and every mirror pair; replacing `<` with `<>` returns 1,568 rows, exactly twice 784.
--    Hint ladder, rung 1: For sql-05 Exercise 5, start with the first relation in `employees`; after each join, record total rows and distinct `department_id` so the exact fanout or loss is visible.
-- 6. [Extension] Show each employee, their manager, and their manager's manager.
--    Hint: Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
--    Inputs: For sql-05 Exercise 6, join `employees` to itself twice with `LEFT JOIN`, first for the manager and then for the manager's manager; only employee 8's 92 reports have a two-level chain.
--    Expected result/shape: For sql-05 Exercise 6, return 100 rows, one per employee: 94 show a `manager_name`, and 92 show `grandmanager_name` Employee 1, because they report to Employee 8, who reports to Employee 1. The final columns are `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`. The final order is `e.employee_id`.
--    Verify: For sql-05 Exercise 6, confirm 100 rows, 94 non-`NULL` `manager_name` values, and 92 non-`NULL` `grandmanager_name` values. Employee 7 must show Employee 2 with no grandmanager, and making either join an inner join must cut the result to 94 or 92 rows.
--    Hint ladder, rung 1: For sql-05 Exercise 6, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
ROLLBACK;
