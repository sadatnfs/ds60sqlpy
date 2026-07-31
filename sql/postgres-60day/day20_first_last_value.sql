-- Day 20: FIRST_VALUE and LAST_VALUE
-- BEGINNER WORKFLOW — sql-20: First Last Value
-- Guide: sql/postgres-60day/companion-guides/day20_first_last_value.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-20/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
-- Assumptions: First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
-- Pitfall: The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
-- Predict row grain and NULL/order behavior before executing each example.

-- First and last order amount per customer
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       FIRST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS first_order_amount,
       LAST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS last_order_amount
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 100;

-- Compare current to first/last
WITH per_cust AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount,
         FIRST_VALUE(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         ) AS first_amt
  FROM orders o
)
SELECT *, ROUND(total_amount - first_amt, 2) AS delta_from_first
FROM per_cust
ORDER BY customer_id, order_date, order_id
LIMIT 100;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show every order with the customer's first and last order timestamps.
--    Hint: Use one full-partition frame from unbounded preceding through unbounded following.
--    Inputs: For sql-20 Exercise 1, read from `orders`. Compute `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-20 Exercise 1, expected output: One row per order with constant first/last values per customer. The final columns are `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-20 Exercise 1, evaluate each of `order_date`, `first_order_date`, and `last_order_date` in a separate control `SELECT` over `orders`; require one final row and compare every value. Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-20 Exercise 1, check `o.customer_id, o.order_date, o.order_id` before applying the row cap.
-- 2. [Query writing] Show each product with the cheapest and most expensive price in its category.
--    Hint: Order by price and use a full frame; values tie without needing row identity.
--    Inputs: For sql-20 Exercise 2, read from `products`. Compute `product_id`, `category`, `price`, `category_min_price`, and `category_max_price` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-20 Exercise 2, expected output: One row per product. The final columns are `product_id`, `category`, `price`, `category_min_price`, and `category_max_price`. The final order is `p.category, p.price, p.product_id`.
--    Verify: For sql-20 Exercise 2, evaluate each of `category_min_price`, and `category_max_price` in a separate control `SELECT` over `products`; require one final row and compare every value. Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.
--    Hint ladder, rung 1: For sql-20 Exercise 2, check `p.category, p.price, p.product_id` before applying the row cap.
-- 3. [Query writing] Compare every payment with the first and last payment amount for its order.
--    Hint: Partition by order, order by timestamp/payment ID, and keep the full frame.
--    Inputs: For sql-20 Exercise 3, read from `payments`. Compute `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-20 Exercise 3, expected output: One row per payment. The final columns are `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount`. The final order is `p.order_id, p.payment_date, p.payment_id`.
--    Verify: For sql-20 Exercise 3, evaluate each of `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` in a separate control `SELECT` over `payments`; require one final row and compare every value. Tie two rows on `p.order_id` and give them different `p.payment_id` values; verify `p.order_id, p.payment_date, p.payment_id` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-20 Exercise 3, check `p.order_id, p.payment_date, p.payment_id` before applying the row cap.
-- 4. [Prediction] Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
--    Hint: The default ends at the current row; explicit following reaches the true last row.
--    Inputs: For sql-20 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `value`, `default_last_value`, and `partition_last_value`; keep `value` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-20 Exercise 4, expected output: Three rows showing default current value and full-frame 30. The final columns are `value`, `default_last_value`, and `partition_last_value`. The final order is `value`.
--    Verify: For sql-20 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `value`, `default_last_value`, and `partition_last_value`, then verify output keys remain `value`. Use a one-row partition and a partition tied on `value`; verify `value` and `value` preserve the intended first/last row.
--    Hint ladder, rung 1: For sql-20 Exercise 4, inspect one window partition before projecting; then check `value` before applying the row cap.
-- 5. [Debugging] Return one first and one last order per customer without using window output as an accidental duplicate report.
--    Hint: Compute first/last IDs with full-frame windows, then select distinct customer-level output.
--    Inputs: For sql-20 Exercise 5, read from `orders`. Compute `customer_id`, `first_order_id`, and `last_order_id` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-20 Exercise 5, expected output: One row per customer with orders. The final columns are `customer_id`, `first_order_id`, and `last_order_id`. The final order is `customer_id`.
--    Verify: For sql-20 Exercise 5, evaluate each of `first_order_id`, and `last_order_id` in a separate control `SELECT` over `orders`; require one final row and compare every value. Tie two rows on `customer_id` and give them different `customer_id` values; verify `customer_id` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-20 Exercise 5, run `annotated` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 6. [Extension] Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
--    Hint: `DISTINCT ON` keeps the first row under its mandatory leading order keys.
--    Inputs: For sql-20 Exercise 6, read from `orders`. Build the answer toward `customer_id`, `order_id`, `order_date`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-20 Exercise 6, expected output: At most one latest order per customer. The final columns are `customer_id`, `order_id`, `order_date`, and `total_amount`. The final order is `o.customer_id, o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-20 Exercise 6, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `customer_id`, `order_id`, `order_date`, and `total_amount` against `orders`. Tie two rows on `o.customer_id` and give them different `o.order_id DESC` values; verify `o.customer_id, o.order_date DESC, o.order_id DESC` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-20 Exercise 6, check `o.customer_id, o.order_date DESC, o.order_id DESC` before applying the row cap.

ROLLBACK;
