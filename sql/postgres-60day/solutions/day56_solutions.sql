-- Day 56 solutions: CUBE, payment method, and percentiles
SET search_path TO training, public;

WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS paid_amount
  FROM payments
  GROUP BY order_id, method
), ranked_payment AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY order_id ORDER BY paid_amount DESC, method
         ) AS payment_rank
  FROM payment_by_method
), primary_payment AS (
  SELECT order_id, method
  FROM ranked_payment
  WHERE payment_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(fp.method, 'unpaid') AS payment_method,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN customers c USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  LEFT JOIN primary_payment fp USING (order_id)
), cube_two AS (
  SELECT country, category, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category)
), cube_three AS (
  SELECT country, category, payment_method, SUM(revenue) AS revenue
  FROM line
  GROUP BY CUBE (country, category, payment_method)
)
-- Exercise 1: quantify the row-count increase.
SELECT (SELECT COUNT(*) FROM cube_two) AS two_dimension_rows,
       (SELECT COUNT(*) FROM cube_three) AS three_dimension_rows;

-- Exercise 2: p50 and p90 category-attributable order values per month.
WITH category_orders AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         p.category,
         o.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY date_trunc('month', o.order_date), p.category, o.order_id
)
SELECT month,
       category,
       ROUND(
         percentile_cont(0.50) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p50_order_value,
       ROUND(
         percentile_cont(0.90) WITHIN GROUP (ORDER BY order_value)::numeric,
         2
       ) AS p90_order_value
FROM category_orders
GROUP BY month, category
ORDER BY month DESC, category;
