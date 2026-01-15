-- Day 21 - Solutions: Distribution Functions (NTILE, PERCENT_RANK, CUME_DIST)
-- Assumes: orders(order_id, customer_id, order_date, total_amount), order_items(...), products(...)

/*
Exercise 1) Assign quartiles to products by revenue within category; compute share per quartile.
Why: NTILE(4) partitions ordered revenue into nearly equal sized tiles; then aggregate by tile.
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
         NTILE(4) OVER (PARTITION BY category ORDER BY revenue DESC) AS quartile
  FROM prod_rev
)
SELECT category,
       quartile,
       ROUND(SUM(revenue),2) AS rev,
       ROUND(SUM(revenue) / NULLIF(SUM(SUM(revenue)) OVER (PARTITION BY category),0), 4) AS share_in_category
FROM ranked
GROUP BY category, quartile
ORDER BY category, quartile;

/*
Exercise 2) Identify orders above the 99th percentile by amount per month.
Why: PERCENTILE_CONT is an ordered-set aggregate; compute a per-month threshold, then filter.
*/
WITH monthly AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS m,
         o.order_id,
         o.total_amount
  FROM orders o
), thresholds AS (
  SELECT m,
         PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY total_amount) AS p99
  FROM monthly
  GROUP BY m
)
SELECT mo.m, mo.order_id, mo.total_amount
FROM monthly mo
JOIN thresholds t USING (m)
WHERE mo.total_amount >= t.p99
ORDER BY mo.m DESC, mo.total_amount DESC
LIMIT 200;

/*
Exercise 3) Use CUME_DIST to flag top-5% customers by lifetime revenue per country.
Why: CUME_DIST gives relative rank as a fraction in [0,1]; filter at >=0.95.
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
       CUME_DIST() OVER (PARTITION BY c.country ORDER BY l.lifetime_revenue) AS cd
FROM customers c
JOIN ltv l ON l.customer_id = c.customer_id
QUALIFY cd >= 0.95; -- If QUALIFY not supported, wrap and filter in outer SELECT
