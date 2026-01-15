-- Day 27 - Solutions: Pivoting/Unpivoting (Crosstabs and Conditional Aggregation)
-- Assumes: orders(order_id, order_date), order_items(order_id, product_id, unit_price, quantity, discount), products(product_id, category)

/*
Exercise 1) Pivot monthly revenue into columns Jan..Dec for the latest year using conditional aggregation (portable).
Why: Conditional SUM produces fixed columns without requiring extensions.
*/
WITH lines AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS m,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS rev
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE DATE_TRUNC('year', o.order_date) = DATE_TRUNC('year', CURRENT_DATE)
  GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=1  THEN rev END),2) AS jan,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=2  THEN rev END),2) AS feb,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=3  THEN rev END),2) AS mar,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=4  THEN rev END),2) AS apr,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=5  THEN rev END),2) AS may,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=6  THEN rev END),2) AS jun,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=7  THEN rev END),2) AS jul,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=8  THEN rev END),2) AS aug,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=9  THEN rev END),2) AS sep,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=10 THEN rev END),2) AS oct,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=11 THEN rev END),2) AS nov,
       ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM m)=12 THEN rev END),2) AS dec
FROM lines;

/*
Exercise 2) Pivot top 5 categories as columns (others as 'Other') using conditional aggregation.
Why: Bucket long tail into 'Other' to keep schema stable.
*/
WITH cat_rev AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS rev
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
), top5 AS (
  SELECT category
  FROM cat_rev
  ORDER BY rev DESC
  LIMIT 5
), labeled AS (
  SELECT CASE WHEN p.category IN (SELECT category FROM top5) THEN p.category ELSE 'Other' END AS cat,
         DATE_TRUNC('month', o.order_date)::date AS m,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS rev
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT m,
       ROUND(SUM(CASE WHEN cat = (SELECT category FROM top5 OFFSET 0 LIMIT 1) THEN rev END),2) AS c1,
       ROUND(SUM(CASE WHEN cat = (SELECT category FROM top5 OFFSET 1 LIMIT 1) THEN rev END),2) AS c2,
       ROUND(SUM(CASE WHEN cat = (SELECT category FROM top5 OFFSET 2 LIMIT 1) THEN rev END),2) AS c3,
       ROUND(SUM(CASE WHEN cat = (SELECT category FROM top5 OFFSET 3 LIMIT 1) THEN rev END),2) AS c4,
       ROUND(SUM(CASE WHEN cat = (SELECT category FROM top5 OFFSET 4 LIMIT 1) THEN rev END),2) AS c5,
       ROUND(SUM(CASE WHEN cat = 'Other' THEN rev END),2) AS other
FROM labeled
GROUP BY m
ORDER BY m;

/*
Exercise 3) Unpivot a wide KPI table into (key, metric_name, metric_value).
Why: UNION ALL or JSONB functions can normalize wide data; UNION ALL is portable.
*/
-- Suppose daily_kpis(day, revenue, orders, customers)
SELECT day, 'revenue'  AS metric, revenue  AS value FROM daily_kpis
UNION ALL
SELECT day, 'orders'   AS metric, orders   AS value FROM daily_kpis
UNION ALL
SELECT day, 'customers' AS metric, customers AS value FROM daily_kpis
ORDER BY day, metric
LIMIT 500;
