-- Day 17: ROW_NUMBER, RANK, DENSE_RANK
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
-- 2. [Query writing] Rank products by price within category using both `RANK` and `DENSE_RANK`.
--    Hint: Rank only on price so equal prices tie; order the final display by product ID.
-- 3. [Query writing] Return the three highest-priced products per category, including price ties.
--    Hint: Compute `DENSE_RANK` in a CTE and filter outside.
-- 4. [Prediction] Compare row number, rank, and dense rank on values 100, 100, and 90.
--    Hint: Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
-- 5. [Debugging] Return exactly one latest order per customer even when timestamps tie.
--    Hint: Use row number with the unique order ID as final tie-breaker.
-- 6. [Extension] Rank employee salaries within department and show only the top two distinct salary levels.
--    Hint: Dense rank includes all employees tied at either of the top two salary values.

ROLLBACK;
