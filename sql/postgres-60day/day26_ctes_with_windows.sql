-- Day 26: CTEs with Window Functions
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
-- Assumptions: Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
-- Pitfall: Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
-- Predict row grain and NULL/order behavior before executing each example.

WITH line AS (
  SELECT o.order_id, o.customer_id, o.order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), ranked AS (
  SELECT line.*,
         RANK() OVER (
           PARTITION BY customer_id
           ORDER BY order_total DESC
         ) AS rnk
  FROM line
)
SELECT customer_id, order_id, order_date, order_total, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY customer_id, rnk, order_total DESC, order_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate monthly stored revenue and its prior-month value/change.
--    Hint: Aggregate to month in a CTE, then lag the monthly measure.
-- 2. [Query writing] Rank product categories by net revenue within each UTC order month.
--    Hint: Aggregate month/category first, then rank the stable aggregate.
-- 3. [Query writing] Return the top three category revenue levels per month.
--    Hint: Rank in one CTE and filter the window result outside.
-- 4. [Prediction] Calculate each category's cumulative share of monthly revenue in descending contribution order.
--    Hint: Divide running category revenue by the full monthly total; use explicit frames.
-- 5. [Debugging] Calculate a three-month moving average after building a dense month calendar.
--    Hint: Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
-- 6. [Extension] Reconcile the final cumulative monthly revenue with the independent order total.
--    Hint: Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.

ROLLBACK;
