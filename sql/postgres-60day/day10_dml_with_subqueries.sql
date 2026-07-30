-- Day 10: INSERT/UPDATE/DELETE with Subqueries (safe via ROLLBACK)
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
-- 2. [Query writing] Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
--    Hint: Select departments by key, round exact numeric salary, and inspect `RETURNING`.
-- 3. [Query writing] Delete orders older than one year only when no payment exists, returning candidate keys.
--    Hint: Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
-- 4. [Prediction] Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
--    Hint: A primary key supplies the conflict target; the second statement updates rather than inserts.
-- 5. [Debugging] Preview and update a bounded product set while reconciling selected and returned key counts.
--    Hint: Store candidate keys in a temporary table and update only through that reviewed set.
-- 6. [Extension] Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
--    Hint: Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.

ROLLBACK;
