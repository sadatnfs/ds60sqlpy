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
--    Inputs: Use `employees` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: List every employee with their direct manager when present” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `employee_name`, `manager_id`, `manager_name`, `e`, `m`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Self join employees and use a left join so top-level employees remain visible.
-- 2. [Query writing] Find employees who manage nobody.
--    Hint: Left join candidate managers to reports and retain managers with no right-side match.
--    Inputs: Use `employees` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Find employees who manage nobody” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `e`, `report`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Left join candidate managers to reports and retain managers with no right-side match.
-- 3. [Query writing] Build a complete grid of six recent months and all expense categories.
--    Hint: Cross join two small declared dimensions; do not cross join raw fact tables.
--    Inputs: Use `expenses` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Build a complete grid of six recent months and all expense categories” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `month_start`, `e`, `c`, `m`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `expenses`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Cross join two small declared dimensions; do not cross join raw fact tables.
-- 4. [Prediction] Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
--    Hint: Cross-join cardinality is the product of input row counts.
--    Inputs: Use `departments` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `month_number`, `department_month_combinations`, `d`, `m`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `departments`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Cross-join cardinality is the product of input row counts.
-- 5. [Debugging] List unique employee pairs in the same department without self-pairs or mirrored duplicates.
--    Hint: Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
--    Inputs: Use `employees` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: List unique employee pairs in the same department without self-pairs or mirrored duplicates” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `both`, `evidence`, `first_employee_id`, `second_employee_id`, `left_employee`, `right_employee`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Use left.employeeid < right.employeeid as both the join condition and uniqueness rule.
-- 6. [Extension] Show each employee, their manager, and their manager's manager.
--    Hint: Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
--    Inputs: Use `employees` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Show each employee, their manager, and their manager's manager” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `employee_name`, `manager_name`, `grandmanager_name`, `e`, `manager`, `grandmanager`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `employee_name`, `manager_name`, `grandmanager_name`, `e`, `manager`, `grandmanager`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Use two independently aliased left self joins; NULLs indicate the hierarchy ends.

ROLLBACK;
