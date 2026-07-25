-- Day 13 solutions: date and time functions
SET search_path TO training, public;

-- Exercise 1: the prompt does not define a fiscal start month, so this answer
-- explicitly assumes fiscal quarters equal UTC calendar quarters.
WITH order_calendar AS (
  SELECT order_id,
         order_date,
         order_date AT TIME ZONE 'UTC' AS order_time_utc
  FROM orders
)
SELECT order_id,
       order_date,
       EXTRACT(year FROM order_time_utc)::int AS fiscal_year,
       EXTRACT(quarter FROM order_time_utc)::int AS fiscal_quarter
FROM order_calendar
ORDER BY order_date, order_id;

-- Exercise 2: days since the customer's most recent UTC order date.
SELECT c.customer_id,
       c.full_name,
       MAX(o.order_date) AS last_order_at,
       CURRENT_DATE - MAX((o.order_date AT TIME ZONE 'UTC')::date)
         AS days_since_last_order
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.full_name
ORDER BY days_since_last_order DESC NULLS LAST, c.customer_id;
