-- Day 17 - Solutions: Ranking Functions (ROW_NUMBER, RANK, DENSE_RANK)
-- Assumes: orders(order_id, customer_id, order_date, total_amount), products, order_items

/*
Exercise 1) Get top 3 products by revenue per category with DENSE_RANK (ties included).
Why: DENSE_RANK allows ties so you may get >3 rows when multiple products share the same revenue.
*/
WITH prod_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.product_id
), ranked AS (
  SELECT category, product_id, revenue,
         DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT category, product_id, ROUND(revenue,2) AS revenue
FROM ranked
WHERE rnk <= 3
ORDER BY category, revenue DESC;

/*
Exercise 2) De-duplicate customers by email keeping the earliest created_at using ROW_NUMBER.
Why: ROW_NUMBER gives exactly one row per partition when ordered by created_at.
*/
WITH normalized AS (
  SELECT c.customer_id, LOWER(TRIM(c.email)) AS norm_email, c.created_at
  FROM customers c
), numbered AS (
  SELECT customer_id, norm_email, created_at,
         ROW_NUMBER() OVER (PARTITION BY norm_email ORDER BY created_at ASC, customer_id ASC) AS rn
  FROM normalized
)
SELECT customer_id, norm_email, created_at
FROM numbered
WHERE rn = 1
ORDER BY created_at;

/*
Exercise 3) Rank customers by lifetime revenue within each country; return the top 10 per country.
Why: RANK vs DENSE_RANK choice depends on whether you want gaps; using RANK here is fine when you truly want ordinal position.
*/
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, SUM(order_value) AS lifetime_revenue
  FROM order_values
  GROUP BY customer_id
)
SELECT c.country,
       c.customer_id,
       ROUND(l.lifetime_revenue,2) AS ltv,
       RANK() OVER (PARTITION BY c.country ORDER BY l.lifetime_revenue DESC) AS rnk
FROM customers c
JOIN ltv l ON l.customer_id = c.customer_id
QUALIFY rnk <= 10; -- If QUALIFY not supported, wrap and filter rnk<=10 in outer SELECT
