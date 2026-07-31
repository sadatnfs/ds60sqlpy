-- Day 21: NTILE and PERCENT_RANK
-- BEGINNER WORKFLOW — sql-21: Distribution Functions
-- Guide: sql/postgres-60day/companion-guides/day21_distribution_functions.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-21/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use distribution windows to express relative position while documenting ties, small partitions, and bucket size.
-- Assumptions: `PERCENT_RANK` ranges from 0 to 1 using rank; `CUME_DIST` is the fraction at or below the current value; `NTILE` balances row counts.
-- Pitfall: A percentile rank is not a probability or causal score, and `NTILE(10)` does not guarantee equal value ranges.
-- Predict row grain and NULL/order behavior before executing each example.

-- Segment customers into quartiles by lifetime revenue
WITH cust_rev AS (
  SELECT c.customer_id,
         COALESCE(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),0) AS revenue
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
  LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY c.customer_id
)
SELECT customer_id,
       revenue,
       -- NTILE must assign tied rows to physical buckets; customer_id makes
       -- that assignment reproducible without changing PERCENT_RANK tie rules.
       NTILE(4) OVER (
         ORDER BY revenue DESC, customer_id
       ) AS revenue_quartile,
       ROUND((PERCENT_RANK() OVER (ORDER BY revenue))::numeric, 4) AS pct_rank
FROM cust_rev
ORDER BY revenue DESC, customer_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Assign customers to four stored-spend buckets.
--    Hint: Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.
--    Inputs: For sql-21 Exercise 1, read from `orders`. Build the answer toward `customer_id`, `stored_spend`, and `spend_quartile`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-21 Exercise 1, expected output: One row per ordering customer with bucket 1–4. The final columns are `customer_id`, `stored_spend`, and `spend_quartile`. The final order is `spend_quartile, stored_spend DESC, customer_id`.
--    Verify: For sql-21 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `customer_id`, `stored_spend`, and `spend_quartile`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-21 Exercise 1, run `customer_spend` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 2. [Query writing] Calculate salary percent rank within each department.
--    Hint: Partition by department and rank on salary alone so tied salaries share rank.
--    Inputs: For sql-21 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, and `salary_percent_rank`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-21 Exercise 2, expected output: One row per employee with values from 0 to 1. The final columns are `employee_id`, `department_id`, `salary`, and `salary_percent_rank`. The final order is `e.department_id, e.salary, e.employee_id`.
--    Verify: For sql-21 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `salary_percent_rank`, then verify output keys remain `employee_id`. Give two rows the same `e.department_id` value and different `e.employee_id` values; verify `e.department_id, e.salary, e.employee_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-21 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.salary, e.employee_id` before applying the row cap.
-- 3. [Query writing] Calculate cumulative distribution of product price within category.
--    Hint: Partition by category and order on price.
--    Inputs: For sql-21 Exercise 3, read from `products`. Build the answer toward `product_id`, `category`, `price`, and `price_cume_dist`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-21 Exercise 3, expected output: One row per product with cume_dist in (0, 1]. The final columns are `product_id`, `category`, `price`, and `price_cume_dist`. The final order is `p.category, p.price, p.product_id`.
--    Verify: For sql-21 Exercise 3, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `category`, `price`, and `price_cume_dist`, then verify output keys remain `product_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-21 Exercise 3, inspect one window partition before projecting; then check `p.category, p.price, p.product_id` before applying the row cap.
-- 4. [Prediction] Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
--    Hint: Tied values share rank and cumulative endpoint, but the two functions use different formulas.
--    Inputs: For sql-21 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`; keep `row_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-21 Exercise 4, expected output: Three rows making tie behavior visible. The final columns are `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`. The final order is `row_id`.
--    Verify: For sql-21 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `value`, `percent_rank_value`, and `cume_dist_value`, then verify output keys remain `row_id`. Give two rows the same `row_id` value and different ``row_id`` values; verify `row_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-21 Exercise 4, inspect one window partition before projecting; then check `row_id` before applying the row cap.
-- 5. [Debugging] Audit the row count in each customer spend decile rather than assuming exact equality.
--    Hint: NTILE bucket sizes differ by at most one when row count is not divisible by ten.
--    Inputs: For sql-21 Exercise 5, read from `orders`. Build the answer toward `decile`, and `customers`; keep `decile` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-21 Exercise 5, expected output: Up to 10 bucket rows with counts. The final columns are `decile`, and `customers`. The final order is `decile`.
--    Verify: For sql-21 Exercise 5, independently aggregate `orders` by `decile`; require one output row for every distinct `decile` tuple and compare `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customers` for the existing `decile` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-21 Exercise 5, run `spend`, and `bucketed` one at a time. Record each CTE's row count and `decile` uniqueness before the next stage uses it.
-- 6. [Extension] Return customers in the top stored-spend decile with their spend and population share.
--    Hint: Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
--    Inputs: For sql-21 Exercise 6, read from `orders`. Build the answer toward `customer_id`, `total_spend`, `decile`, and `population`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-21 Exercise 6, expected output: Customers in decile 1. The final columns are `customer_id`, `total_spend`, `decile`, and `population`. The final order is `total_spend DESC, customer_id`.
--    Verify: For sql-21 Exercise 6, run an anti-check that counts rows where NOT ((decile = 1)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `total_spend`, `decile`, and `population` against `orders`. Give two rows the same `total_spend DESC` value and different `customer_id` values; verify `total_spend DESC, customer_id` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-21 Exercise 6, run `spend`, and `bucketed` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.

ROLLBACK;
