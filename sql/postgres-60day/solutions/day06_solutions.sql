-- Day 06 - Solutions: Set Operations (UNION, INTERSECT, EXCEPT)
-- Assumes: orders, customers, products, order_items

/*
Exercise 1) Build Q1 vs Q2 cohort sets and compute intersection and exclusive members.
Why: Use INTERSECT/EXCEPT to derive overlaps and exclusives between time-based cohorts.
*/
WITH q1 AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= DATE_TRUNC('year', CURRENT_DATE)
    AND o.order_date <  DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '3 months'
), q2 AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '3 months'
    AND o.order_date <  DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '6 months'
)
-- Intersection (both Q1 and Q2)
SELECT 'intersection' AS set_type, customer_id FROM (
  SELECT customer_id FROM q1
  INTERSECT
  SELECT customer_id FROM q2
) i
UNION ALL
-- Exclusive Q1 only
SELECT 'q1_only' AS set_type, customer_id FROM (
  SELECT customer_id FROM q1
  EXCEPT
  SELECT customer_id FROM q2
) q1_only
UNION ALL
-- Exclusive Q2 only
SELECT 'q2_only' AS set_type, customer_id FROM (
  SELECT customer_id FROM q2
  EXCEPT
  SELECT customer_id FROM q1
) q2_only
ORDER BY set_type, customer_id
LIMIT 500;

/*
Exercise 2) Combine top sellers by category across two months using UNION ALL and then rank.
Why: UNION ALL concatenates without de-dup; then rank within (category, month) to pick top-k.
*/
WITH month_cat AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         p.category,
         oi.product_id,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
    AND o.order_date <  DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
  GROUP BY DATE_TRUNC('month', o.order_date), p.category, oi.product_id
), ranked AS (
  SELECT month,
         category,
         product_id,
         revenue,
         DENSE_RANK() OVER (PARTITION BY month, category ORDER BY revenue DESC) AS rnk
  FROM month_cat
)
SELECT month, category, product_id, revenue
FROM ranked
WHERE rnk <= 3
ORDER BY month, category, revenue DESC;

/*
Exercise 3) Find products present in catalog but not in any order_items.
Why: Use EXCEPT (or LEFT JOIN IS NULL) to find keys missing from the fact table.
*/
SELECT p.product_id
FROM products p
EXCEPT
SELECT DISTINCT oi.product_id
FROM order_items oi
ORDER BY product_id
LIMIT 200;

-- End of Day 06 solutions
