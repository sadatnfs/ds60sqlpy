-- Day 10: INSERT/UPDATE/DELETE with Subqueries (safe via ROLLBACK)
-- BEGINNER WORKFLOW - sql-10: DML with Subqueries
-- Guide: sql/postgres-60day/companion-guides/day10_dml_with_subqueries.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-10.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category;

SELECT
  category,
  revenue
FROM
  tmp_category_revenue
ORDER BY
  revenue DESC,
  category;

-- Example: Update salaries by department performance (demo only).
-- Capture RETURNING in a data-modifying CTE so the evidence can be sorted.
WITH changed AS (
  UPDATE
    employees AS e
  SET
    salary = e.salary * 1.05
  WHERE
    e.department_id IN (
      SELECT
        d.department_id
      FROM
        departments AS d
      WHERE
        d.name IN ('Sales', 'Engineering'))
    RETURNING
      e.employee_id,
      e.department_id,
      e.salary
)
SELECT
  employee_id,
  department_id,
  salary
FROM
  changed
ORDER BY
  employee_id;

-- Example: Delete unpaid old orders (demo only)
WITH deleted AS (
  DELETE FROM orders AS o
  WHERE o.order_date < now() - interval '365 days'
    AND NOT EXISTS (
      SELECT
        1
      FROM
        payments AS p
      WHERE
        p.order_id = o.order_id)
    RETURNING
      o.order_id
)
SELECT
  order_id
FROM
  deleted
ORDER BY
  order_id;

-- All changes will be rolled back below
-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Materialize category net revenue into a temporary table with `INSERT ... SELECT`.
--    Hint: Declare the temporary schema and aggregate source rows before inserting.
--    Inputs: For sql-10 Exercise 1, aggregate net revenue, `unit_price * quantity * (1 - discount)`, from `order_items` joined to `products` by `p.category`, and load it with `INSERT ... SELECT` into the temporary table `exercise_category_revenue (category text PRIMARY KEY, revenue numeric NOT NULL)`.
--    Expected result/shape: For sql-10 Exercise 1, expected output: the command tag `INSERT 0 6`, then six rows, one per product category, with columns `category` and `revenue` (rounded to 2 places), ordered by `revenue DESC, category`; `Sports` leads on the course seed.
--    Verify: For sql-10 Exercise 1, rerun the aggregate as a plain `SELECT` and compare each category's revenue with the stored row; confirm that `SELECT COUNT(DISTINCT p.category) FROM order_items oi JOIN products p ON p.product_id = oi.product_id` returns 6, and that the savepoint rollback leaves no `exercise_category_revenue` table.
--    Hint ladder, rung 1: For sql-10 Exercise 1, write and check the aggregate `SELECT` first; only then put `INSERT INTO ... (category, revenue)` in front of it.
-- 2. [Query writing] Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
--    Hint: Select departments by key, round exact numeric salary, and inspect `RETURNING`.
--    Inputs: For sql-10 Exercise 2, raise `salary` by 5% (rounded to 2 places) for employees whose `department_id` belongs to the `departments` named `Sales` or `Engineering`, selected with an `IN (SELECT ...)` subquery, inside a savepoint.
--    Expected result/shape: For sql-10 Exercise 2, expected output: the command tag `UPDATE 34` and 34 returned rows with columns `employee_id`, `full_name`, and `salary` (the new value); after `ROLLBACK TO SAVEPOINT`, no salary has changed.
--    Verify: For sql-10 Exercise 2, before the update, count the targets with `SELECT COUNT(*) FROM employees e JOIN departments d ON d.department_id = e.department_id WHERE d.name IN ('Sales', 'Engineering')` (34) and compare with the command tag; after the rollback, compare one returned `employee_id`'s salary with its original value.
--    Hint ladder, rung 1: For sql-10 Exercise 2, preview the target `employee_id` values with a `SELECT` that uses the same `WHERE` clause before you run the `UPDATE`.
-- 3. [Query writing] Delete orders older than one year only when no payment exists, returning candidate keys.
--    Hint: Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
--    Inputs: For sql-10 Exercise 3, delete orders with `order_date` older than one year that have no row in `payments`, using a correlated `NOT EXISTS`, inside a savepoint.
--    Expected result/shape: For sql-10 Exercise 3, expected output: a `DELETE` command tag and returned rows with columns `order_id`, `customer_id`, and `order_date`, all older than one year (362 rows on a freshly seeded database); after `ROLLBACK TO SAVEPOINT`, every order and its cascaded `order_items` are restored.
--    Verify: For sql-10 Exercise 3, count the candidates first with the same `WHERE` clause in a `SELECT COUNT(*)` and compare with the command tag; after the rollback, confirm that `SELECT COUNT(*) FROM orders` is back to 4,362 and that a deleted `order_id` exists again.
--    Hint ladder, rung 1: For sql-10 Exercise 3, write the `SELECT` that finds unpaid old orders first; `NOT EXISTS` is true exactly when the payment subquery returns no row.
-- 4. [Prediction] Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
--    Hint: A primary key supplies the conflict target; the second statement updates rather than inserts.
--    Inputs: For sql-10 Exercise 4, create the temporary table `exercise_feed (source_key text PRIMARY KEY, source_value numeric NOT NULL)` and run `INSERT ... ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value` twice for `source_a`, first with `10` and then with `12`.
--    Expected result/shape: For sql-10 Exercise 4, expected output: both statements print `INSERT 0 1`, and the final `SELECT` returns one row ordered by `source_key` with columns `source_key` and `source_value`: `('source_a', 12)`.
--    Verify: For sql-10 Exercise 4, confirm that `SELECT COUNT(*) FROM exercise_feed WHERE source_key = 'source_a'` returns 1 after the second run; add `RETURNING (xmax = 0) AS inserted` to each upsert to see `true` for the first run and `false` for the second.
--    Hint ladder, rung 1: For sql-10 Exercise 4, the conflict target names the unique key that decides between insert and update.
-- 5. [Debugging] Preview and update a bounded product set while reconciling selected and returned key counts.
--    Hint: Store candidate keys in a temporary table and update only through that reviewed set.
--    Inputs: For sql-10 Exercise 5, store the first five `Books` product keys in the temporary table `exercise_product_candidates`, then lower those products' `price` by 1% through a data-modifying CTE that updates only keys in that table.
--    Expected result/shape: For sql-10 Exercise 5, expected output: one summary row with columns `candidate_count` and `updated_count`, both `5`.
--    Verify: For sql-10 Exercise 5, list the candidate `product_id` values before the update and compare them with the keys returned by the `UPDATE`'s `RETURNING` clause; after `ROLLBACK TO SAVEPOINT`, confirm that each candidate's `price` equals its original value.
--    Hint ladder, rung 1: For sql-10 Exercise 5, update through the reviewed key table, then count both sides of the reconciliation in the same statement.
-- 6. [Extension] Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
--    Hint: Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
--    Inputs: For sql-10 Exercise 6, stage new prices for the first three products in the temporary table `exercise_price_stage`, then run `UPDATE products ... FROM exercise_price_stage` only where `stage.new_price >= 0` and `p.price IS DISTINCT FROM stage.new_price`.
--    Expected result/shape: For sql-10 Exercise 6, expected output: the command tag `UPDATE 3` and three returned rows ordered by `p.product_id` with columns `product_id` and `price`: `(1, 10.47)`, `(2, 10.85)`, and `(3, 11.22)` on the course seed.
--    Verify: For sql-10 Exercise 6, add a staged row with a negative price and one whose price equals the current price, rerun the update after a savepoint, and confirm that neither key is returned; then confirm the original prices after `ROLLBACK TO SAVEPOINT`.
--    Hint ladder, rung 1: For sql-10 Exercise 6, put every validation rule in the `WHERE` clause of the `UPDATE ... FROM`, so a rejected staged row can never reach `SET`.
ROLLBACK;
