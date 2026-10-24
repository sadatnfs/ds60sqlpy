-- Day 17: ROW_NUMBER, RANK, DENSE_RANK
-- BEGINNER WORKFLOW — sql-17: Rank Functions
-- Guide: sql/postgres-60day/companion-guides/day17_rank_functions.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-17/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, employees, departments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
-- Assumptions: All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
-- Pitfall: `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.
-- Predict row grain and NULL/order behavior before executing each example.

-- Rank customers by lifetime revenue (ties vs gaps)
WITH cust_rev AS (
  SELECT c.customer_id,
         c.full_name,
         COALESCE(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),0) AS revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id, c.full_name
)
SELECT customer_id,
       full_name,
       revenue,
       ROW_NUMBER() OVER (
         ORDER BY revenue DESC, customer_id
       ) AS row_num,
       RANK()       OVER (ORDER BY revenue DESC) AS rank_pos,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_pos
FROM cust_rev
ORDER BY revenue DESC, customer_id
LIMIT 30;

-- Rank employees by salary within department
SELECT e.department_id,
       d.name AS department,
       e.employee_id,
       e.full_name,
       e.salary,
       RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_rank
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id
ORDER BY department NULLS LAST,
         dept_rank,
         e.salary DESC,
         e.employee_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Number each customer's orders from newest to oldest.
--    Hint: Partition by customer and use order date plus order ID as a unique descending order.
--    Inputs: For sql-17 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `recency_number`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-17 Exercise 1, expected output: One row per order with sequence starting at one per customer. The final columns are `order_id`, `customer_id`, `order_date`, and `recency_number`. The final order is `o.customer_id, recency_number`.
--    Verify: For sql-17 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, then verify output keys remain `order_id`. Give two rows the same `o.customer_id` value and different `recency_number` values; verify `o.customer_id, recency_number` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-17 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, recency_number` before applying the row cap.
-- 2. [Query writing] Rank products by price within category using both `RANK` and `DENSE_RANK`.
--    Hint: Rank only on price so equal prices tie; order the final display by product ID.
--    Inputs: For sql-17 Exercise 2, read from `products`. Build the answer toward `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-17 Exercise 2, expected output: One row per product with two rank semantics. The final columns are `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`. The final order is `p.category, p.price DESC, p.product_id`.
--    Verify: For sql-17 Exercise 2, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `price_rank`, and `dense_price_rank`, then verify output keys remain `product_id`. Give two rows the same `p.category` value and different `p.product_id` values; verify `p.category, p.price DESC, p.product_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-17 Exercise 2, inspect one window partition before projecting; then check `p.category, p.price DESC, p.product_id` before applying the row cap.
-- 3. [Query writing] Return the three highest-priced products per category, including price ties.
--    Hint: Compute `DENSE_RANK` in a CTE and filter outside.
--    Inputs: For sql-17 Exercise 3, read from `products`. Build the answer toward `product_id`, `name`, `category`, `price`, and `price_rank`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-17 Exercise 3, expected output: At least three price levels per category where available. The final columns are `product_id`, `name`, `category`, `price`, and `price_rank`. The final order is `category, price_rank, product_id`.
--    Verify: For sql-17 Exercise 3, run an anti-check that counts rows where NOT ((price_rank <= 3)); require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `name`, `category`, `price`, and `price_rank` against `products`. Give two rows the same `category` value and different `product_id` values; verify `category, price_rank, product_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-17 Exercise 3, run `ranked` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
-- 4. [Prediction] Compare row number, rank, and dense rank on values 100, 100, and 90.
--    Hint: Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
--    Inputs: For sql-17 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`; keep `sample_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-17 Exercise 4, expected output: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2. The final columns are `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`. The final order is `sample_id`.
--    Verify: For sql-17 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `score`, `row_number_value`, `rank_value`, and `dense_rank_value`, then verify output keys remain `sample_id`. Give two rows the same `sample_id` value and different ``sample_id`` values; verify `sample_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-17 Exercise 4, inspect one window partition before projecting; then check `sample_id` before applying the row cap.
-- 5. [Debugging] Return exactly one latest order per customer even when timestamps tie.
--    Hint: Use row number with the unique order ID as final tie-breaker.
--    Inputs: For sql-17 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-17 Exercise 5, expected output: At most one row per customer. The final columns are `order_id`, `customer_id`, `order_date`, and `total_amount`. The final order is `customer_id`.
--    Verify: For sql-17 Exercise 5, run an anti-check that counts rows where NOT ((recency_number = 1)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `order_date`, and `total_amount` against `orders`. Give two rows the same `customer_id` value and different ``order_id`` values; verify `customer_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-17 Exercise 5, run `numbered` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. [Extension] Rank employee salaries within department and show only the top two distinct salary levels.
--    Hint: Dense rank includes all employees tied at either of the top two salary values.
--    Inputs: For sql-17 Exercise 6, read from `employees`. Build the answer toward `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-17 Exercise 6, expected output: Top two salary levels per department. The final columns are `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`. The final order is `department_id, salary_rank, employee_id`.
--    Verify: For sql-17 Exercise 6, run an anti-check that counts rows where NOT ((salary_rank <= 2)); require unique `employee_id` where the expected grain is one row per key and confirm the projected `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank` against `employees`. Give two rows the same `department_id` value and different `employee_id` values; verify `department_id, salary_rank, employee_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-17 Exercise 6, run `ranked` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.

ROLLBACK;
