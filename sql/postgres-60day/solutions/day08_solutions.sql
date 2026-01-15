-- Day 08 - Solutions: Scalar and Inline Subqueries
-- Assumes: customers, orders, products, promotions

/*
Exercise 1) Add last_order_date per customer via scalar subquery; then rewrite as a LEFT JOIN.
Why: Scalar subquery is straightforward but runs per-row; a join on a pre-aggregated subquery is often faster and clearer.
*/
-- Scalar subquery form
SELECT c.customer_id,
       c.full_name,
       (
         SELECT MAX(o.order_date)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS last_order_date
FROM customers c
ORDER BY last_order_date DESC NULLS LAST
LIMIT 200;

-- Join form (preferred)
WITH last_orders AS (
  SELECT o.customer_id, MAX(o.order_date) AS last_order_date
  FROM orders o
  GROUP BY o.customer_id
)
SELECT c.customer_id,
       c.full_name,
       lo.last_order_date
FROM customers c
LEFT JOIN last_orders lo ON lo.customer_id = c.customer_id
ORDER BY lo.last_order_date DESC NULLS LAST
LIMIT 200;

/*
Exercise 2) Use ANY to filter orders whose total exceeds ANY top 10% order totals.
Why: ANY compares against a set; we build a top-decile cutoff and compare.
*/
WITH ranked AS (
  SELECT o.order_id,
         o.total_amount,
         NTILE(10) OVER (ORDER BY o.total_amount DESC) AS decile
  FROM orders o
), top_decile AS (
  SELECT r.total_amount
  FROM ranked r
  WHERE r.decile = 1
)
SELECT o.order_id, o.total_amount
FROM orders o
WHERE o.total_amount > ANY (SELECT td.total_amount FROM top_decile td)
ORDER BY o.total_amount DESC
LIMIT 100;

-- End of Day 08 solutions
