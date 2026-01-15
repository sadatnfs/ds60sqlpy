-- Day 22: Advanced Window Function Scenarios
BEGIN;
SET search_path TO training, public;

-- Multi-level analysis: rank within partition, then across all
WITH prod_rev AS (
  SELECT p.product_id,
         p.name,
         p.category,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.product_id, p.name, p.category
)
SELECT *,
  RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
  RANK() OVER (ORDER BY revenue DESC) AS rank_overall
FROM prod_rev
ORDER BY category, rank_in_category
LIMIT 100;

-- Combine multiple windows in one query
SELECT o.customer_id,
       o.order_id,
       o.total_amount,
       AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS avg_per_customer,
       SUM(o.total_amount) OVER () AS total_revenue_all,
       RANK() OVER (PARTITION BY o.customer_id ORDER BY o.total_amount DESC) AS order_value_rank
FROM orders o
ORDER BY o.customer_id, order_value_rank
LIMIT 100;

-- Exercises
-- 1) For each country, rank categories by revenue and also compute overall category rank.
-- 2) For each employee, compute salary rank in department and across company.

ROLLBACK;
