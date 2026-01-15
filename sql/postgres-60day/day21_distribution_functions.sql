-- Day 21: NTILE and PERCENT_RANK
BEGIN;
SET search_path TO training, public;

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
       NTILE(4) OVER (ORDER BY revenue DESC) AS revenue_quartile,
       ROUND(PERCENT_RANK() OVER (ORDER BY revenue),4) AS pct_rank
FROM cust_rev
ORDER BY revenue DESC
LIMIT 50;

-- Exercises
-- 1) Bucket products into deciles by units sold in last 90 days.
-- 2) Compute percentile rank of each order by total_amount within customer.

ROLLBACK;
