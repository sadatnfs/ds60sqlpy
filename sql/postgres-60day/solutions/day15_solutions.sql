-- Day 15 solution: Phase 1 multidimensional report extension
SET search_path TO training, public;

-- The deliverable adds product category and one primary payment method.
-- Selecting one primary method per order avoids multiplying line revenue.
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
  SELECT o.order_id,
         c.customer_id,
         date_trunc('month', o.order_date)::date AS month,
         COALESCE(c.segment, 'standard') AS segment,
         c.country,
         p.category,
         COALESCE(fp.method, 'unpaid') AS payment_method,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN primary_payment fp ON fp.order_id = o.order_id
)
SELECT month,
       segment,
       country,
       category,
       payment_method,
       ROUND(SUM(line_revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT customer_id) AS active_customers,
       ROUND(SUM(line_revenue) / NULLIF(COUNT(DISTINCT customer_id), 0), 2)
         AS revenue_per_active_customer
FROM line
GROUP BY month, segment, country, category, payment_method
ORDER BY month DESC, revenue DESC
LIMIT 500;

-- Reconciliation: the added dimensions must not change total revenue.
WITH expected AS (
  SELECT ROUND(SUM(total_amount), 2) AS revenue FROM orders
), actual AS (
  SELECT ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
  FROM order_items oi
)
SELECT expected.revenue AS order_total_revenue,
       actual.revenue AS dimensional_line_revenue,
       actual.revenue - expected.revenue AS difference
FROM expected CROSS JOIN actual;
