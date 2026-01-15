-- Day 03 - Solutions: INNER JOINs and Predicate Placement
-- Assumes: orders, order_items, products, customers, payments

/*
Exercise 1) Join orders to customers to compute revenue by customer country for the last 90 days.
Why: Join facts (orders + items) correctly by aggregating line revenue per order to avoid double counting when adding dimensions.
*/
WITH order_revenue AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_date >= now() - interval '90 days'
  GROUP BY o.order_id, o.customer_id
)
SELECT c.country,
       ROUND(SUM(orv.order_revenue),2) AS revenue_90d
FROM order_revenue orv
JOIN customers c ON c.customer_id = orv.customer_id
GROUP BY c.country
ORDER BY revenue_90d DESC;

/*
Exercise 2) Join order_items to products and compute gross margin per category.
Why: Margin = (price - cost) * quantity after discount; aggregate by category.
*/
SELECT p.category,
       ROUND(SUM( (oi.unit_price - p.cost) * oi.quantity * (1 - oi.discount) ), 2) AS gross_margin
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY gross_margin DESC;

/*
Exercise 3) Detect and fix a fanout when joining orders and payments (1:N on both sides) by aggregating first.
Why: Joining orders (1:N items) to payments (1:N) directly multiplies rows. Pre-aggregate each side to 1 row per order_id.
*/
WITH order_totals AS (
  SELECT o.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id
),
payments_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_amount
  FROM payments p
  GROUP BY p.order_id
)
SELECT o.order_id,
       ROUND(o.order_revenue,2) AS order_revenue,
       ROUND(pt.paid_amount,2) AS paid_amount,
       ROUND(o.order_revenue - COALESCE(pt.paid_amount,0),2) AS balance
FROM order_totals o
LEFT JOIN payments_totals pt ON pt.order_id = o.order_id
ORDER BY o.order_id
LIMIT 100;

-- End of Day 03 solutions
