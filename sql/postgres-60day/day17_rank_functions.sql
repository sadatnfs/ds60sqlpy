-- Day 17: ROW_NUMBER, RANK, DENSE_RANK
-- BEGINNER WORKFLOW - sql-17: ROW_NUMBER, RANK and DENSE_RANK
-- Guide: sql/postgres-60day/companion-guides/day17_rank_functions.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-17.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    c.customer_id,
    c.full_name,
    COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0) AS revenue
  FROM
    customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    c.customer_id,
    c.full_name
)
SELECT
  customer_id,
  full_name,
  revenue,
  ROW_NUMBER() OVER (ORDER BY revenue DESC, customer_id) AS row_num,
  RANK() OVER (ORDER BY revenue DESC) AS rank_pos,
  DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank_pos
FROM
  cust_rev
ORDER BY
  revenue DESC,
  customer_id
LIMIT 30;

-- Rank employees by salary within department
SELECT
  e.department_id,
  d.name AS department,
  e.employee_id,
  e.full_name,
  e.salary,
  RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS dept_rank
FROM
  employees e
  LEFT JOIN departments d ON d.department_id = e.department_id
ORDER BY
  department NULLS LAST,
  dept_rank,
  e.salary DESC,
  e.employee_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Number each customer's orders from newest to oldest.
--    Hint: Partition by customer and use order date plus order ID as a unique descending order.
--    Inputs: For sql-17 Exercise 1, number each of the 4,362 `orders` rows with `ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, o.order_id DESC)`; the 438 buyers have 4 to 16 orders each.
--    Expected result/shape: For sql-17 Exercise 1, return 4,362 rows, one per order, where each customer's numbers run from 1 up to that customer's order count; customer 1's orders 5, 4, 3, 2, and 1 get numbers 1 to 5, and the 33 customers with 16 orders, such as customer 12, reach 16. The final columns are `order_id`, `customer_id`, `order_date`, and `recency_number`. The final order is `o.customer_id, recency_number`.
--    Verify: For sql-17 Exercise 1, confirm that exactly 438 rows have `recency_number` 1, the maximum is 16, and each customer's maximum equals `COUNT(*)` from `orders` grouped by `customer_id`. All `order_date` values are distinct, so inside a rolled-back transaction copy order 5's `order_date` onto order 3; customer 1 must then number orders 5, 3, 4, 2, 1 as 1 to 5, because `o.order_id DESC` breaks the tie.
--    Hint ladder, rung 1: For sql-17 Exercise 1, inspect one window partition before projecting; then check `o.customer_id, recency_number` before applying the row cap.
-- 2. [Query writing] Rank products by price within category using both `RANK` and `DENSE_RANK`.
--    Hint: Rank only on price so equal prices tie; order the final display by product ID.
--    Inputs: For sql-17 Exercise 2, rank the 300 `products` within each of the 6 categories (50 products each) by `p.price DESC`, once with `RANK()` and once with `DENSE_RANK()`.
--    Expected result/shape: For sql-17 Exercise 2, return 300 rows, one per product; `Apparel` starts with product 295 at 119.15, 289 at 116.93, and 283 at 114.71 ranked 1, 2, and 3, and both rank columns end at 50 in every category. The final columns are `product_id`, `category`, `price`, `price_rank`, and `dense_price_rank`. The final order is `p.category, p.price DESC, p.product_id`.
--    Verify: For sql-17 Exercise 2, confirm 300 rows and zero rows where `price_rank <> dense_price_rank`, since every category has 50 distinct prices. Inside a rolled-back transaction, set product 289's price to 119.15; `Apparel` must then show products 289 and 295 at rank 1 and dense rank 1, product 283 at rank 3 but dense rank 2, and product 277 at rank 4 but dense rank 3.
--    Hint ladder, rung 1: For sql-17 Exercise 2, inspect one window partition before projecting; then check `p.category, p.price DESC, p.product_id` before applying the row cap.
-- 3. [Query writing] Return the three highest-priced products per category, including price ties.
--    Hint: Compute `DENSE_RANK` in a CTE and filter outside.
--    Inputs: For sql-17 Exercise 3, apply `DENSE_RANK() OVER (PARTITION BY p.category ORDER BY p.price DESC)` inside the `ranked` CTE, then keep `price_rank <= 3` in the outer query.
--    Expected result/shape: For sql-17 Exercise 3, return 18 rows, three per category for the 6 categories; `Apparel` keeps products 295, 289, and 283, and `Books` keeps 300 at 121.00, 294 at 118.78, and 288 at 116.56. The final columns are `product_id`, `name`, `category`, `price`, and `price_rank`. The final order is `category, price_rank, product_id`.
--    Verify: For sql-17 Exercise 3, confirm 18 rows, no `price_rank` above 3, and that each kept price is among the three highest from `SELECT category, price FROM products ORDER BY category, price DESC`. Inside a rolled-back transaction, set product 289's price to 119.15; the result must grow to 19 rows, with `Apparel` returning 289 and 295 at rank 1, 283 at rank 2, and 277 at rank 3.
--    Hint ladder, rung 1: For sql-17 Exercise 3, run `ranked` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
-- 4. [Prediction] Compare row number, rank, and dense rank on values 100, 100, and 90.
--    Hint: Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
--    Inputs: For sql-17 Exercise 4, rank the three-row `VALUES` fixture `(1, 100), (2, 100), (3, 90)` by `score DESC` with `ROW_NUMBER()` (tie broken by `sample_id`), `RANK()`, and `DENSE_RANK()`.
--    Expected result/shape: For sql-17 Exercise 4, expected output: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2. The final columns are `sample_id`, `score`, `row_number_value`, `rank_value`, and `dense_rank_value`. The final order is `sample_id`.
--    Verify: For sql-17 Exercise 4, check by hand that samples 1 and 2 tie at 100, so only `row_number_value` separates them (1 and 2), while sample 3 gets 3, 3, and 2. Add `(4, 90)` to the fixture; the four rows must read 1/1/1, 2/1/1, 3/3/2, and 4/3/2.
--    Hint ladder, rung 1: For sql-17 Exercise 4, inspect one window partition before projecting; then check `sample_id` before applying the row cap.
-- 5. [Debugging] Return exactly one latest order per customer even when timestamps tie.
--    Hint: Use row number with the unique order ID as final tie-breaker.
--    Inputs: For sql-17 Exercise 5, number orders with `ROW_NUMBER()` partitioned by `o.customer_id` and ordered by `o.order_date DESC, o.order_id DESC` in the `numbered` CTE, then keep `recency_number = 1`.
--    Expected result/shape: For sql-17 Exercise 5, return 438 rows, one latest order per buyer, with no rows for the 62 customers who never ordered; customer 1's row is order 5 for 105.84 and customer 500's is order 4362 for 951.76. The final columns are `order_id`, `customer_id`, `order_date`, and `total_amount`. The final order is `customer_id`.
--    Verify: For sql-17 Exercise 5, confirm 438 distinct `customer_id` values and that all 438 rows match `SELECT customer_id, MAX(order_date) FROM orders GROUP BY customer_id` on both columns; the kept orders total 252375.44. Inside a rolled-back transaction, copy order 5's `order_date` onto order 3; customer 1 must still return order 5, because `o.order_id DESC` breaks the tie.
--    Hint ladder, rung 1: For sql-17 Exercise 5, run `numbered` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. [Extension] Rank employee salaries within department and show only the top two distinct salary levels.
--    Hint: Dense rank includes all employees tied at either of the top two salary values.
--    Inputs: For sql-17 Exercise 6, apply `DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC)` to the 100 `employees` rows in the `ranked` CTE, then keep `salary_rank <= 2`.
--    Expected result/shape: For sql-17 Exercise 6, return 12 rows, two per department for the 6 departments; department 1 keeps employee 97 at 47681.43 and employee 91 at 47206.29, and department 4 keeps employee 100 at 47919.00 and employee 94 at 47443.86. The final columns are `employee_id`, `full_name`, `department_id`, `salary`, and `salary_rank`. The final order is `department_id, salary_rank, employee_id`.
--    Verify: For sql-17 Exercise 6, confirm 12 rows and that each department's two salaries are its two highest from `SELECT department_id, salary FROM employees ORDER BY department_id, salary DESC`; no department has a salary tie. Inside a rolled-back transaction, set employee 91's salary to 47681.43; the result must grow to 13 rows, with employees 91 and 97 at rank 1 and employee 85 (46731.15) at rank 2 in department 1.
--    Hint ladder, rung 1: For sql-17 Exercise 6, run `ranked` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
ROLLBACK;
