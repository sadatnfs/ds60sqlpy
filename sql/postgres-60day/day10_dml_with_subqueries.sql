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
--    Inputs: Use `order_items`, `products` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 must make “Query writing: Materialize category net revenue into a temporary table with INSERT ... SELECT” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `oi`, `p`, `revenue`, `insert`.
--    Verify: For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `oi`, `p`, `revenue`, `insert`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Declare the temporary schema and aggregate source rows before inserting.
-- 2. [Query writing] Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
--    Hint: Select departments by key, round exact numeric salary, and inspect `RETURNING`.
--    Inputs: Use `employees`, `departments` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Give Sales and Engineering employees a 5% demonstration raise and return affected rows” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `e`, `d`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, `departments`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Select departments by key, round exact numeric salary, and inspect RETURNING.
-- 3. [Query writing] Delete orders older than one year only when no payment exists, returning candidate keys.
--    Hint: Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
--    Inputs: Use `orders`, `payments` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Query writing: Delete orders older than one year only when no payment exists, returning candidate keys” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `o`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `payments`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Use correlated NOT EXISTS; foreign-key cascades remain rollback-protected.
-- 4. [Prediction] Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
--    Hint: A primary key supplies the conflict target; the second statement updates rather than inserts.
--    Inputs: Use `tmp_category_revenue`, `order_items`, `products`, `employees`, `departments` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 must make “Prediction: Run an upsert twice against a temporary key-value table and prove only one row exists for the key” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`.
--    Verify: For Exercise 4, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: A primary key supplies the conflict target; the second statement updates rather than inserts.
-- 5. [Debugging] Preview and update a bounded product set while reconciling selected and returned key counts.
--    Hint: Store candidate keys in a temporary table and update only through that reviewed set.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 must make “Debugging: Preview and update a bounded product set while reconciling selected and returned key counts” observable through the exact DDL/DML command tag plus one row per product or product grouping requested; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `p`, `candidate`, `candidate_count`, `updated_count`.
--    Verify: For Exercise 5, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `p`, `candidate`, `candidate_count`, `updated_count`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Store candidate keys in a temporary table and update only through that reviewed set.
-- 6. [Extension] Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
--    Hint: Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
--    Inputs: Use `products` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Stage product prices and update only rows whose incoming price is nonnegative and actually differs” observable through the exact DDL/DML command tag plus one row per product or product grouping requested; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `p`, `stage`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `p`, `stage`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Use UPDATE ... FROM, validate the stage predicate, and compare with IS DISTINCT FROM.

ROLLBACK;
