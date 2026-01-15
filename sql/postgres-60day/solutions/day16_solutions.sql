-- Day 16 - Solutions: Window Functions Fundamentals (OVER, PARTITION BY, ORDER BY, Frames)
-- Assumes: orders(order_id, customer_id, order_date, total_amount), order_items(…)

/*
Exercise 1) For each order, show the customer’s lifetime revenue next to order_total and compute the ratio.
Why: PARTITION BY customer_id to get per-customer aggregates without collapsing rows; use ROWS UNBOUNDED PRECEDING for clarity.
*/
SELECT o.customer_id,
       o.order_id,
       o.total_amount AS order_total,
       ROUND(
         SUM(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         )
       , 2) AS customer_lifetime_rev,
       ROUND(
         o.total_amount / NULLIF(
           SUM(o.total_amount) OVER (PARTITION BY o.customer_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
         , 0)
       , 4) AS order_share_of_lifetime
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 200;

/*
Exercise 2) Compute a 30-day rolling average of daily revenue; discuss RANGE vs ROWS differences when multiple days share the same total.
Why: Pre-aggregate to daily grain, then apply a ROWS frame to get exactly the prior 29 rows plus current.
*/
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT d,
       revenue,
       ROUND(
         AVG(revenue) OVER (
           ORDER BY d
           ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
         )
       ,2) AS ma30_rows
FROM daily
ORDER BY d DESC
LIMIT 60;

/* Portable note:
- In portable SQL engines lacking explicit ROWS frames, the default frame may be RANGE … CURRENT ROW. In Postgres, prefer ROWS for fixed-size rolling windows to avoid peer expansion when duplicates in ORDER BY exist.
*/

/*
Exercise 3) For each category, compute product revenue and product share within the category.
Why: SUM() OVER (PARTITION BY category) provides the denominator per category.
*/
WITH prod_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.product_id
)
SELECT category,
       product_id,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY category),0), 4) AS share_in_category
FROM prod_rev
ORDER BY category, share_in_category DESC
LIMIT 300;

-- End of Day 16 solutions
