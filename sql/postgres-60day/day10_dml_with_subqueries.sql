-- Day 10: INSERT/UPDATE/DELETE with Subqueries (safe via ROLLBACK)
-- BEGINNER WORKFLOW — sql-10: DML with Subqueries
-- Guide: sql/postgres-60day/companion-guides/day10_dml_with_subqueries.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-10/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: tmp_category_revenue, order_items, products, employees, departments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.
-- Assumptions: Every exercise runs inside the disposable course transaction. Savepoints isolate demonstrations so one answer does not change the next.
-- Pitfall: Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
-- Predict row grain and NULL/order behavior before executing each example.

-- Example: Insert promotional budget rollups into a temp table
CREATE TEMP TABLE tmp_category_revenue AS
SELECT p.category, ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category;

SELECT category, revenue
FROM tmp_category_revenue
ORDER BY revenue DESC, category;

-- Example: Update salaries by department performance (demo only).
-- Capture RETURNING in a data-modifying CTE so the evidence can be sorted.
WITH changed AS (
  UPDATE employees AS e
  SET salary = e.salary * 1.05
  WHERE e.department_id IN (
    SELECT d.department_id
    FROM departments AS d
    WHERE d.name IN ('Sales','Engineering')
  )
  RETURNING e.employee_id, e.department_id, e.salary
)
SELECT employee_id, department_id, salary
FROM changed
ORDER BY employee_id;

-- Example: Delete unpaid old orders (demo only)
WITH deleted AS (
  DELETE FROM orders AS o
  WHERE o.order_date < now() - interval '365 days'
    AND NOT EXISTS (
      SELECT 1
      FROM payments AS p
      WHERE p.order_id = o.order_id
    )
  RETURNING o.order_id
)
SELECT order_id
FROM deleted
ORDER BY order_id;

-- All changes will be rolled back below

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Materialize category net revenue into a temporary table with `INSERT ... SELECT`.
--    Hint: Declare the temporary schema and aggregate source rows before inserting.
--    Inputs: For sql-10 Exercise 1, read the target keys from `exercise_category_revenue`, `order_items`, and `products` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-10 Exercise 1, expected output: One temporary row per product category. The final columns are `category`. The final order is `revenue DESC, category`.
--    Verify: For sql-10 Exercise 1, materialize the intended `category` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_category_revenue`, `order_items`, and `products` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `category` values in both cases.
--    Hint ladder, rung 1: For sql-10 Exercise 1, start with the first relation in `exercise_category_revenue`, `order_items`, and `products`; after each join, record total rows and distinct `category` so the exact fanout or loss is visible.
-- 2. [Query writing] Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
--    Hint: Select departments by key, round exact numeric salary, and inspect `RETURNING`.
--    Inputs: For sql-10 Exercise 2, read the target keys from `employees`, and `departments` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-10 Exercise 2, expected output: Affected employee rows only; no change persists. The final columns are `returning`, `update`, `from`, and `where`.
--    Verify: For sql-10 Exercise 2, materialize the intended `employee_id` target set first; require the command tag/`RETURNING` set to match it, then query `employees`, and `departments` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `employee_id` values in both cases.
--    Hint ladder, rung 1: For sql-10 Exercise 2, materialize the intended `employee_id` target set first; require the command tag/`RETURNING` set to match it, then query `employees`, and `departments` again and prove rollback or idempotent retry.
-- 3. [Query writing] Delete orders older than one year only when no payment exists, returning candidate keys.
--    Hint: Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
--    Inputs: For sql-10 Exercise 3, read the target keys from `orders`, and `payments` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-10 Exercise 3, expected output: Deleted-candidate order rows, then fully restored state. The final columns are `from`, `where`, and `returning`.
--    Verify: For sql-10 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `payments` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
--    Hint ladder, rung 1: For sql-10 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `payments` again and prove rollback or idempotent retry.
-- 4. [Prediction] Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
--    Hint: A primary key supplies the conflict target; the second statement updates rather than inserts.
--    Inputs: For sql-10 Exercise 4, read the target keys from `exercise_feed` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-10 Exercise 4, expected output: One row for `source_a` with the second value. The final columns are `source_key`, and `source_value`. The final order is `source_key`.
--    Verify: For sql-10 Exercise 4, materialize the intended `source_key` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_feed` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `source_key` values in both cases.
--    Hint ladder, rung 1: For sql-10 Exercise 4, materialize the intended `source_key` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_feed` again and prove rollback or idempotent retry.
-- 5. [Debugging] Preview and update a bounded product set while reconciling selected and returned key counts.
--    Hint: Store candidate keys in a temporary table and update only through that reviewed set.
--    Inputs: For sql-10 Exercise 5, read the target keys from `products`, and `exercise_product_candidates` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-10 Exercise 5, expected output: One summary row with equal candidate and updated counts. The final columns are `product_id`. The final order is `p.product_id`.
--    Verify: For sql-10 Exercise 5, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `products`, and `exercise_product_candidates` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.
--    Hint ladder, rung 1: For sql-10 Exercise 5, run `updated` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
-- 6. [Extension] Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
--    Hint: Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
--    Inputs: For sql-10 Exercise 6, read the target keys from `exercise_price_stage`, `products`, and `stage.new_price` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-10 Exercise 6, expected output: Returned rows only for valid changed products. The final columns are `product_id`. The final order is `p.product_id`.
--    Verify: For sql-10 Exercise 6, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_price_stage`, `products`, and `stage.new_price` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.
--    Hint ladder, rung 1: For sql-10 Exercise 6, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_price_stage`, `products`, and `stage.new_price` again and prove rollback or idempotent retry.

ROLLBACK;
