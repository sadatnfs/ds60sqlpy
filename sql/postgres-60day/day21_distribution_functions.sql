-- Day 21: NTILE and PERCENT_RANK
-- BEGINNER WORKFLOW - sql-21: Distribution Functions
-- Guide: sql/postgres-60day/companion-guides/day21_distribution_functions.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-21.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    c.customer_id,
    COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0) AS revenue
  FROM
    customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    c.customer_id
)
SELECT
  customer_id,
  revenue,
  -- NTILE must assign tied rows to physical buckets; customer_id makes
  -- that assignment reproducible without changing PERCENT_RANK tie rules.
  NTILE(4) OVER (ORDER BY revenue DESC, customer_id) AS revenue_quartile,
  ROUND((PERCENT_RANK() OVER (ORDER BY revenue))::numeric, 4) AS pct_rank
FROM
  cust_rev
ORDER BY
  revenue DESC,
  customer_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Assign customers to four stored-spend buckets.
--    Hint: Aggregate to customer grain first, then apply `NTILE(4)` with a stable tie-breaker.
--    Inputs: For sql-21 Exercise 1, read `orders`, total `total_amount` per `customer_id` in the `customer_spend` CTE, then apply `NTILE(4)` over that customer-grain relation ordered by spend descending with `customer_id` as the tie-breaker; `order_id` does not survive the aggregation.
--    Expected result/shape: For sql-21 Exercise 1, expected output: 438 rows, one per customer who has at least one order (the other 62 of the 500 customers have none), with quartiles of 110, 110, 109, and 109 customers. The final columns are `customer_id`, `stored_spend`, and `spend_quartile`. The final order is `spend_quartile, stored_spend DESC, customer_id`.
--    Verify: For sql-21 Exercise 1, confirm the row count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` (438) and that grouping the result by `spend_quartile` returns counts 110, 110, 109, 109 with quartile 1 running from 9502.21 down to 7133.41 and quartile 4 from 3522.32 down to 962.26; the seed has 18 pairs of customers with identical spend (for example 51 and 428 at 8970.66), and each pair lands in the same quartile with the lower `customer_id` first.
--    Hint ladder, rung 1: For sql-21 Exercise 1, run `customer_spend` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 2. [Query writing] Calculate salary percent rank within each department.
--    Hint: Partition by department and rank on salary alone so tied salaries share rank.
--    Inputs: For sql-21 Exercise 2, read the 100 rows of `employees`, partition by `department_id`, and order each partition by `salary` alone so that equal salaries would share a rank; keep `employee_id` because the result stays at employee grain.
--    Expected result/shape: For sql-21 Exercise 2, expected output: 100 rows, one per employee, with `salary_percent_rank` from 0 to 1 inside each of the six departments (four of 17 employees and two of 16). The final columns are `employee_id`, `department_id`, `salary`, and `salary_percent_rank`. The final order is `e.department_id, e.salary, e.employee_id`.
--    Verify: For sql-21 Exercise 2, in department 1 (17 employees, no tied salaries) check the formula (rank - 1) / (rows - 1): employee 1 at 40079.19 returns 0, employee 7 at 40554.33 returns 0.0625 (1/16), employee 49 returns 0.5, and employee 97 at 47681.43 returns 1; in 16-employee department 5 the second row returns 1/15 (0.0667). Then run the window on `VALUES (9, 50000), (8, 100), (8, 100), (8, 200)` and expect 0 for the one-row department and 0, 0, 1 for the tied salaries.
--    Hint ladder, rung 1: For sql-21 Exercise 2, inspect one window partition before projecting; then check `e.department_id, e.salary, e.employee_id` before applying the row cap.
-- 3. [Query writing] Calculate cumulative distribution of product price within category.
--    Hint: Partition by category and order on price.
--    Inputs: For sql-21 Exercise 3, read the 300 rows of `products`, partition by `category`, and order by `price`; keep `product_id` because each product stays one row.
--    Expected result/shape: For sql-21 Exercise 3, expected output: 300 rows, one per product, 50 per category, with `price_cume_dist` in (0, 1]. The final columns are `product_id`, `category`, `price`, and `price_cume_dist`. The final order is `p.category, p.price, p.product_id`.
--    Verify: For sql-21 Exercise 3, in `Apparel` (50 products, no repeated prices) check rows at or below / partition rows: product 1 at 10.37 returns 0.02, product 7 at 12.59 returns 0.04, product 145 at 63.65 returns 0.5, and product 295 at 119.15 returns 1; confirm `MAX(price_cume_dist)` is exactly 1 in each of the six categories, and that a one-row partition such as `VALUES (9, 50000)` returns 1, not 0.
--    Hint ladder, rung 1: For sql-21 Exercise 3, inspect one window partition before projecting; then check `p.category, p.price, p.product_id` before applying the row cap.
-- 4. [Prediction] Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
--    Hint: Tied values share rank and cumulative endpoint, but the two functions use different formulas.
--    Inputs: For sql-21 Exercise 4, read only the three-row inline `VALUES` fixture `(1, 10), (2, 10), (3, 20)` with columns `row_id` and `value`; compute both functions over the whole fixture ordered by `value`.
--    Expected result/shape: For sql-21 Exercise 4, expected output: three rows, one per `row_id`, where the two rows tied at 10 share both results. The final columns are `row_id`, `value`, `percent_rank_value`, and `cume_dist_value`. The final order is `row_id`.
--    Verify: For sql-21 Exercise 4, expect rows 1 and 2 to return `percent_rank_value` 0 and `cume_dist_value` 0.6667 (two of three rows are at or below 10), and row 3 to return 1 and 1; then change row 2 to 15 and confirm the results become 0, 0.5, 1 for percent rank and 0.3333, 0.6667, 1 for cumulative distribution, because the tie is gone.
--    Hint ladder, rung 1: For sql-21 Exercise 4, inspect one window partition before projecting; then check `row_id` before applying the row cap.
-- 5. [Debugging] Audit the row count in each customer spend decile rather than assuming exact equality.
--    Hint: NTILE bucket sizes differ by at most one when row count is not divisible by ten.
--    Inputs: For sql-21 Exercise 5, read `orders`, total spend per `customer_id`, assign `NTILE(10)` over the 438 customer totals ordered by spend descending and `customer_id`, then count customers per decile.
--    Expected result/shape: For sql-21 Exercise 5, expected output: 10 rows, deciles 1 to 8 holding 44 customers and deciles 9 and 10 holding 43, because 438 = 10 x 43 + 8 and `NTILE` gives the remainder to the first buckets. The final columns are `decile`, and `customers`. The final order is `decile`.
--    Verify: For sql-21 Exercise 5, confirm `SUM(customers)` equals `SELECT COUNT(DISTINCT customer_id) FROM orders` (438) and that the counts differ by at most one; then run `NTILE(4)` over `generate_series(1, 3)` and confirm it returns only buckets 1, 2, and 3, showing that a bucket can be empty when there are fewer rows than buckets.
--    Hint ladder, rung 1: For sql-21 Exercise 5, run `spend`, and `bucketed` one at a time. Record each CTE's row count and `decile` uniqueness before the next stage uses it.
-- 6. [Extension] Return customers in the top stored-spend decile with their spend and population share.
--    Hint: Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
--    Inputs: For sql-21 Exercise 6, read `orders`, total spend per `customer_id`, assign `NTILE(10)` and `COUNT(*) OVER ()` in the `bucketed` CTE, and only then filter to `decile = 1`, so the population is counted before the filter.
--    Expected result/shape: For sql-21 Exercise 6, expected output: the 44 customers of decile 1, from customer 181 at 9502.21 down to 8190.44, each carrying `population` 438. The final columns are `customer_id`, `total_spend`, `decile`, and `population`. The final order is `total_spend DESC, customer_id`.
--    Verify: For sql-21 Exercise 6, confirm 44 rows, every `decile` equals 1, every `population` equals 438, and no customer appears twice; the first three rows are customers 181 (9502.21), 12 (9244.27), and 25 (9196.96). Customers 51 and 428 tie at 8970.66 and both appear, 51 first; the next spend below the cut, 8168.74, belongs to decile 2. Computing `COUNT(*) OVER ()` in the outer query after the filter instead returns 44, which is why `population` is taken inside `bucketed`.
--    Hint ladder, rung 1: For sql-21 Exercise 6, run `spend`, and `bucketed` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
ROLLBACK;
