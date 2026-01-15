-- Day 20 - Solutions: FIRST_VALUE, LAST_VALUE, NTH_VALUE
-- Assumes: orders(order_id, order_date, total_amount), order_items(...)

/*
Exercise 1) For each customer, compute spend vs their first order amount.
Why: FIRST_VALUE over a per-customer partition anchors to baseline order value; ensure the frame covers the whole partition.
*/
WITH per_order AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount AS order_total
  FROM orders o
)
SELECT customer_id,
       order_id,
       order_date,
       order_total,
       FIRST_VALUE(order_total) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS first_order_amt,
       ROUND(order_total / NULLIF(FIRST_VALUE(order_total) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ), 0), 4) AS vs_first_ratio
FROM per_order
ORDER BY customer_id, order_date, order_id
LIMIT 300;

/*
Exercise 2) For each month, attach the month’s last day revenue to each day.
Why: LAST_VALUE by month partition; must extend the frame to UNBOUNDED FOLLOWING to get true last value.
*/
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
), with_month AS (
  SELECT d,
         revenue,
         DATE_TRUNC('month', d)::date AS m
  FROM daily
)
SELECT d,
       revenue,
       LAST_VALUE(revenue) OVER (
         PARTITION BY m ORDER BY d
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS month_last_rev
FROM with_month
ORDER BY d DESC
LIMIT 60;

-- End of Day 20 solutions
