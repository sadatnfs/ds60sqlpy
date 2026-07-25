-- Day 59 solution: integrated stakeholder analytics
BEGIN;
SET search_path TO training, public;

-- A reconciled KPI suite at customer grain.
WITH customer_ltv AS (
  SELECT c.customer_id,
         c.country,
         COALESCE(c.segment, 'standard') AS segment,
         date_trunc('month', c.created_at)::date AS cohort_month,
         COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id, c.country, c.segment, date_trunc('month', c.created_at)
)
SELECT cohort_month,
       segment,
       COUNT(*) AS customers,
       ROUND(AVG(ltv), 2) AS avg_ltv,
       ROUND(SUM(ltv), 2) AS total_ltv
FROM customer_ltv
GROUP BY cohort_month, segment
ORDER BY cohort_month DESC, total_ltv DESC;

-- Conversion funnel with rates and a stable customer denominator.
WITH activity AS (
  SELECT c.customer_id,
         BOOL_OR(e.event_type = 'page_view') AS viewed,
         BOOL_OR(e.event_type = 'add_to_cart') AS added,
         BOOL_OR(e.event_type = 'checkout') AS checked_out,
         EXISTS (
           SELECT 1
           FROM orders o
           WHERE o.customer_id = c.customer_id
             AND o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
         ) AS bought
  FROM customers c
  LEFT JOIN events e
    ON e.customer_id = c.customer_id
   AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY c.customer_id
)
SELECT COUNT(*) FILTER (WHERE viewed) AS viewers,
       COUNT(*) FILTER (WHERE added) AS adders,
       COUNT(*) FILTER (WHERE checked_out) AS checkouts,
       COUNT(*) FILTER (WHERE bought) AS buyers,
       ROUND(
         COUNT(*) FILTER (WHERE bought)::numeric
           / NULLIF(COUNT(*) FILTER (WHERE viewed), 0),
         4
       ) AS viewer_to_buyer_rate
FROM activity;

-- Finance stakeholder view: YTD budget versus actual.
WITH actual AS (
  SELECT category, SUM(amount) AS actual
  FROM expenses
  WHERE expense_date >= date_trunc('year', CURRENT_DATE)
  GROUP BY category
), budget AS (
  SELECT category, SUM(amount) AS budget
  FROM budgets
  WHERE period >= date_trunc('year', CURRENT_DATE)
  GROUP BY category
)
SELECT COALESCE(a.category, b.category) AS category,
       ROUND(COALESCE(b.budget, 0), 2) AS budget,
       ROUND(COALESCE(a.actual, 0), 2) AS actual,
       ROUND(COALESCE(a.actual, 0) - COALESCE(b.budget, 0), 2) AS variance
FROM actual a
FULL OUTER JOIN budget b USING (category)
ORDER BY category;

-- Performance evidence: add a candidate index and inspect the actual plan.
CREATE INDEX idx_orders_customer_date_day59_solution
  ON orders(customer_id, order_date) INCLUDE (total_amount);

EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, SUM(total_amount) AS revenue
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 50;

ROLLBACK;
