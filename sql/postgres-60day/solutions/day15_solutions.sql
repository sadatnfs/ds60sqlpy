-- Day 15 - Solutions: Phase 1 Project — Multi-Dimensional Revenue Report
-- Assumes: orders(order_date,total_amount,customer_id), order_items(unit_price,quantity,discount,order_id,product_id),
--          customers(customer_id,segment,country), products(product_id,category)

/*
Goal: Produce monthly revenue report segmented by customer segment, country, and product category.
Why: Avoid fanout by aggregating line revenue to order level, then join exactly one row per dimension before final aggregates.
*/
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
), enriched AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         COALESCE(c.segment,'standard') AS segment,
         c.country,
         p.category,
         ol.order_revenue
  FROM orders o
  JOIN order_lines ol ON ol.order_id = o.order_id
  JOIN customers c    ON c.customer_id = o.customer_id
  JOIN (
    -- pick one category per order by highest revenue contribution (or join via a bridge if many-to-many is desired)
    SELECT oi.order_id,
           (ARRAY_AGG(p.category ORDER BY (oi.unit_price*oi.quantity*(1-oi.discount)) DESC))[1] AS category
    FROM order_items oi JOIN products p ON p.product_id = oi.product_id
    GROUP BY oi.order_id
  ) cat ON cat.order_id = o.order_id
  JOIN products p ON p.category = cat.category
)
SELECT month,
       segment,
       country,
       category,
       ROUND(SUM(order_revenue),2) AS revenue,
       COUNT(*) AS orders,
       ROUND(SUM(order_revenue) / NULLIF(COUNT(*),0),2) AS aov
FROM enriched
GROUP BY month, segment, country, category
ORDER BY month DESC, revenue DESC
LIMIT 500;

-- Validation: reconcile monthly revenue by two methods
WITH by_lines AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS rev
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY DATE_TRUNC('month', o.order_date)
), by_orders AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS rev
  FROM orders o
  GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT l.month, ROUND(l.rev,2) AS rev_by_lines, ROUND(o.rev,2) AS rev_by_orders,
       ROUND(l.rev - o.rev,2) AS diff
FROM by_lines l JOIN by_orders o USING (month)
ORDER BY l.month DESC;

-- End of Day 15 solutions
