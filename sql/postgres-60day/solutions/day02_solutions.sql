-- Day 02 - Solutions: Aggregations, GROUP BY, HAVING, Grouping Sets
-- Assumes tables: orders, order_items, products, customers in schema training

/*
Exercise 1) Compute revenue, orders, AOV (avg order value) by country and month; include a country subtotal and a grand total using ROLLUP.
Why: ROLLUP produces (country, month), then (country), then () grand total. GROUPING() identifies subtotal rows so we can label them.
*/
WITH order_totals AS (
  SELECT o.order_id,
         c.country,
         CAST(date_trunc('month', o.order_date) AS date) AS month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN customers c ON c.customer_id = o.customer_id
  GROUP BY o.order_id, c.country, date_trunc('month', o.order_date)
)
SELECT 
  CASE WHEN GROUPING(country)=1 THEN 'ALL_COUNTRIES' ELSE country END AS country,
  CASE WHEN GROUPING(month)=1 THEN NULL ELSE month END AS month,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(revenue),2)    AS revenue,
  ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT order_id),0), 2) AS aov
FROM order_totals
GROUP BY ROLLUP (country, month)
ORDER BY country NULLS FIRST, month NULLS FIRST;

/*
Exercise 2) For each product category, compute share of total revenue.
Why: Use a single pass with a window SUM() OVER () to compute the global total and divide each category’s revenue by it.
*/
WITH cat_rev AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT category,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (),0), 4) AS share_of_total
FROM cat_rev
ORDER BY revenue DESC;

/*
Exercise 3) Use FILTER to count refunds vs total shipments by region.
Note: The base schema does not include a shipments table; we’ll model “refunds” via an events table with payload kind='refund' and treat all orders as shipments for illustration.
Alternative: Count completed vs refunded orders using status on orders if available.
*/
-- Alternative with orders.status if present; adjust statuses to your schema
SELECT c.country AS region,
       SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) AS completed_orders,
       SUM(CASE WHEN o.status = 'refunded'  THEN 1 ELSE 0 END) AS refunded_orders,
       ROUND(
         SUM(CASE WHEN o.status = 'refunded' THEN 1 ELSE 0 END)::numeric
         / NULLIF(SUM(CASE WHEN o.status IN ('completed','refunded') THEN 1 ELSE 0 END), 0)
       , 4) AS refund_rate
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY refund_rate DESC;

-- End of Day 02 solutions
