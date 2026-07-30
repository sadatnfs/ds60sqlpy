-- Day 21: NTILE and PERCENT_RANK
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
-- 2. [Query writing] Calculate salary percent rank within each department.
--    Hint: Partition by department and rank on salary alone so tied salaries share rank.
-- 3. [Query writing] Calculate cumulative distribution of product price within category.
--    Hint: Partition by category and order on price.
-- 4. [Prediction] Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
--    Hint: Tied values share rank and cumulative endpoint, but the two functions use different formulas.
-- 5. [Debugging] Audit the row count in each customer spend decile rather than assuming exact equality.
--    Hint: NTILE bucket sizes differ by at most one when row count is not divisible by ten.
-- 6. [Extension] Return customers in the top stored-spend decile with their spend and population share.
--    Hint: Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.

ROLLBACK;
