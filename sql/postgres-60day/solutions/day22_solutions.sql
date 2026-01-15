-- Day 22 - Solutions: Advanced Windows (Named windows, exclusion, performance)
-- Assumes: orders(order_id, customer_id, order_date, total_amount), order_items

/*
Exercise 1) Compute leave-one-out average order amount per customer.
Why: Exclude current row from window sum/count.
Portable approach: (sum - x)/(count - 1). Postgres also has EXCLUDE CURRENT ROW in frames.
*/
SELECT o.customer_id,
       o.order_id,
       o.total_amount,
       ROUND(
         (SUM(o.total_amount) OVER (PARTITION BY o.customer_id)
          - o.total_amount)
         / NULLIF((COUNT(*) OVER (PARTITION BY o.customer_id) - 1), 0)
       , 2) AS loo_avg
FROM orders o
ORDER BY o.customer_id, o.order_date
LIMIT 200;

/*
Exercise 2) Produce, in one query, both per-category and global running totals using named windows.
Why: WINDOW clause avoids repeating specs; two different partitions used in same SELECT.
*/
WITH daily_cat AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY DATE_TRUNC('day', o.order_date), p.category
)
SELECT d,
       category,
       revenue,
       ROUND(SUM(revenue) OVER w_cat, 2)    AS cat_running,
       ROUND(SUM(revenue) OVER w_global, 2) AS global_running
FROM daily_cat
WINDOW w_cat AS (PARTITION BY category ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
       w_global AS (ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
ORDER BY d DESC, category
LIMIT 200;
