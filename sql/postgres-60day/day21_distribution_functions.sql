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
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Calculate salary percent rank within each department.
--    Hint: Partition by department and rank on salary alone so tied salaries share rank.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Calculate cumulative distribution of product price within category.
--    Hint: Partition by category and order on price.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Compare percent rank and cumulative distribution for tied values 10, 10, and 20.
--    Hint: Tied values share rank and cumulative endpoint, but the two functions use different formulas.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Audit the row count in each customer spend decile rather than assuming exact equality.
--    Hint: NTILE bucket sizes differ by at most one when row count is not divisible by ten.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Return customers in the top stored-spend decile with their spend and population share.
--    Hint: Filter an outer query after assigning deciles; state that bucket 1 is highest because ordering is descending.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
