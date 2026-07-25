-- Day 07 solutions: Week 1 reporting project
SET search_path TO training, public;

-- Exercise 1: revenue by country, category, and a primary payment method.
-- The method with the greatest paid amount wins; name breaks ties.
WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS paid_amount
  FROM payments p
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
  SELECT o.order_id,
         c.country,
         pr.category,
         COALESCE(fp.method, 'unpaid') AS payment_method,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products pr ON pr.product_id = oi.product_id
  LEFT JOIN primary_payment fp ON fp.order_id = o.order_id
  WHERE o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
)
SELECT country,
       category,
       payment_method,
       ROUND(SUM(line_revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders
FROM line
GROUP BY country, category, payment_method
ORDER BY revenue DESC, country, category, payment_method;

-- Exercise 2: add signup cohort month to the original country/category report.
WITH line AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month,
         c.country,
         p.category,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM customers c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
)
SELECT cohort_month,
       country,
       category,
       ROUND(SUM(line_revenue), 2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers
FROM line
GROUP BY cohort_month, country, category
ORDER BY cohort_month DESC, revenue DESC;
