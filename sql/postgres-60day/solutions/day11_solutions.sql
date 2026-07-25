-- Day 11 solutions: CASE expressions
SET search_path TO training, public;

-- Exercise 1: lifetime-revenue tiers. Thresholds are explicit business rules.
WITH customer_revenue AS (
  SELECT c.customer_id,
         c.full_name,
         COALESCE(
           SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
           0
         ) AS lifetime_revenue
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  LEFT JOIN order_items oi USING (order_id)
  GROUP BY c.customer_id, c.full_name
)
SELECT customer_id,
       full_name,
       ROUND(lifetime_revenue, 2) AS lifetime_revenue,
       CASE
         WHEN lifetime_revenue >= 10000 THEN 'platinum'
         WHEN lifetime_revenue >= 5000 THEN 'gold'
         WHEN lifetime_revenue >= 1000 THEN 'silver'
         WHEN lifetime_revenue > 0 THEN 'bronze'
         ELSE 'no_orders'
       END AS revenue_tier
FROM customer_revenue
ORDER BY lifetime_revenue DESC, customer_id;

-- Exercise 2: UTC hour buckets. Explicit UTC makes output session-independent.
WITH order_hours AS (
  SELECT order_id,
         order_date,
         EXTRACT(hour FROM order_date AT TIME ZONE 'UTC')::int AS order_hour_utc
  FROM orders
)
SELECT order_id,
       order_date,
       order_hour_utc,
       CASE
         WHEN order_hour_utc >= 6 AND order_hour_utc < 12 THEN 'morning'
         WHEN order_hour_utc >= 12 AND order_hour_utc < 17 THEN 'afternoon'
         WHEN order_hour_utc >= 17 AND order_hour_utc < 22 THEN 'evening'
         ELSE 'night'
       END AS day_part
FROM order_hours
ORDER BY order_date, order_id;
