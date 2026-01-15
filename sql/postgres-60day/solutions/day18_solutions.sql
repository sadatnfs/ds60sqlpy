-- Day 18 - Solutions: LAG/LEAD and Intra-Row Comparisons
-- Assumes: orders(order_id, customer_id, order_date, total_amount)

/*
Exercise 1) Compute revenue delta and growth rate day-to-day.
Why: Pre-aggregate to daily revenue; LAG to get prior value; protect division by zero with NULLIF.
*/
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT d,
       revenue,
       (revenue - LAG(revenue) OVER (ORDER BY d)) AS delta,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY d))
         / NULLIF(LAG(revenue) OVER (ORDER BY d), 0)
       , 4) AS growth_rate
FROM daily
ORDER BY d DESC
LIMIT 60;

/*
Exercise 2) For each customer, compute days between orders and flag gaps > 60 days.
Why: Partition by customer, order by date; LAG and AGE/diff in days; CASE to flag large gaps.
*/
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS prev_order,
       EXTRACT(DAY FROM (o.order_date - LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date))) AS days_since_prev,
       CASE WHEN o.order_date - LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) > INTERVAL '60 days'
            THEN TRUE ELSE FALSE END AS gap_gt_60
FROM orders o
ORDER BY o.customer_id, o.order_date
LIMIT 200;

/*
Exercise 3) For each product, compute the difference in price from the previous listing.
Why: Use LAG over product_id partition ordered by effective date (if available) or updated_at.
*/
-- Assuming products_price_history(product_id, price, effective_at)
SELECT product_id,
       effective_at,
       price,
       price - LAG(price) OVER (PARTITION BY product_id ORDER BY effective_at) AS price_delta
FROM products_price_history
ORDER BY product_id, effective_at
LIMIT 200;

-- End of Day 18 solutions
