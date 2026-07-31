-- Day 59 solution: integrated stakeholder analytics
-- SOLUTION READING MAP — sql-59: Final Capstone Part2
-- Explanation: sql/postgres-60day/solutions/day59_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day59_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
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

-- Exercise 1: an executable grain map makes transitions reviewable. The LTV
-- pipeline starts at order rows, aggregates to customer, then summarizes by
-- cohort/segment; joining a lower grain after that would change the metric.
SELECT *
FROM (
  VALUES
    ('order_values', 'one row per order', 'customer_id + order_id'),
    ('customer_ltv', 'one row per customer', 'customer_id'),
    ('cohort_segment_summary', 'one row per cohort/segment',
     'cohort_month + segment')
) AS grain_map(step_name, row_grain, key_columns);

-- Exercise 2: start with every customer so buyers without matching event
-- records remain visible. Each denominator is the preceding funnel population.
WITH activity AS (
  SELECT c.customer_id,
         BOOL_OR(e.event_type = 'page_view') AS viewed,
         BOOL_OR(e.event_type = 'add_to_cart') AS added,
         BOOL_OR(e.event_type = 'checkout') AS checked_out,
         EXISTS (
           SELECT 1 FROM orders o
           WHERE o.customer_id = c.customer_id
             AND o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
         ) AS bought
  FROM customers c
  LEFT JOIN events e
    ON e.customer_id = c.customer_id
   AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY c.customer_id
), counts AS (
  SELECT COUNT(*) FILTER (WHERE viewed) AS viewers,
         COUNT(*) FILTER (WHERE added) AS adders,
         COUNT(*) FILTER (WHERE checked_out) AS checkouts,
         COUNT(*) FILTER (WHERE bought) AS buyers,
         COUNT(*) FILTER (WHERE bought AND NOT viewed) AS buyers_without_view
  FROM activity
)
SELECT *,
       ROUND(adders::numeric / NULLIF(viewers, 0), 4) AS view_to_add,
       ROUND(checkouts::numeric / NULLIF(adders, 0), 4) AS add_to_checkout,
       ROUND(buyers::numeric / NULLIF(checkouts, 0), 4) AS checkout_to_buy
FROM counts;

-- Exercise 3: reconcile candidate revenue measures at order grain before a
-- stakeholder chooses one. Differences are evidence, not values to hide.
WITH lines AS (
  SELECT order_id,
         SUM(quantity * unit_price * (1 - discount)) AS line_revenue
  FROM order_items GROUP BY order_id
), paid AS (
  SELECT order_id, SUM(amount) AS paid_amount
  FROM payments GROUP BY order_id
)
SELECT o.order_id,
       o.total_amount AS stored_order_total,
       l.line_revenue,
       p.paid_amount,
       o.total_amount - l.line_revenue AS header_minus_lines,
       p.paid_amount - o.total_amount AS paid_minus_header
FROM orders o
LEFT JOIN lines l USING (order_id)
LEFT JOIN paid p USING (order_id)
ORDER BY o.order_id
LIMIT 50;

-- Exercise 4: each purchase gets the latest qualifying campaign or the direct
-- bucket. Starting from orders guarantees the buckets reconcile to purchases.
SELECT COALESCE(t.campaign, '(direct)') AS attribution_bucket,
       COUNT(*) AS purchases
FROM orders o
LEFT JOIN LATERAL (
  SELECT e.metadata->>'campaign' AS campaign
  FROM events e
  WHERE e.customer_id = o.customer_id
    AND e.event_time >= o.order_date - interval '7 days'
    AND e.event_time < o.order_date
    AND e.metadata ? 'campaign'
  ORDER BY e.event_time DESC, e.event_id DESC
  LIMIT 1
) t ON true
GROUP BY COALESCE(t.campaign, '(direct)')
ORDER BY purchases DESC, attribution_bucket;

-- Exercise 5: the date-leading index matches the bounded-date scan, while the
-- customer-leading index better supports one customer's ordered history.
CREATE INDEX idx_orders_date_customer_day59_solution
  ON orders(order_date, customer_id) INCLUDE (total_amount);
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, SUM(total_amount) AS revenue
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY customer_id;

-- Exercise 6: a metric contract is data, not an undocumented assumption.
SELECT *
FROM (
  VALUES (
    'viewer_to_buyer_rate',
    'one row for the 90-day reporting window',
    'distinct customers with an order',
    'distinct customers with a page_view',
    'UTC timestamps; trailing 90 days',
    'NULL when denominator is zero',
    'test/internal events excluded only when explicitly labeled',
    'analytics owner'
  )
) AS metric_contract(
  metric_name, grain, numerator, denominator, time_window,
  null_policy, exclusions, owner
);

-- Exercise 7: basket pairs use distinct product/order membership. Minimum
-- together count controls noise; deterministic ties use product IDs.
WITH baskets AS (
  SELECT DISTINCT order_id, product_id FROM order_items
), totals AS (
  SELECT COUNT(DISTINCT order_id)::numeric AS all_baskets FROM baskets
), product_baskets AS (
  SELECT product_id, COUNT(*)::numeric AS baskets
  FROM baskets GROUP BY product_id
), pairs AS (
  SELECT a.product_id AS product_a, b.product_id AS product_b,
         COUNT(*)::numeric AS together
  FROM baskets a JOIN baskets b
    ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p.product_a, p.product_b, p.together,
       ROUND(p.together / t.all_baskets, 4) AS support,
       ROUND(p.together / a.baskets, 4) AS confidence_a_to_b,
       ROUND((p.together * t.all_baskets)
             / NULLIF(a.baskets * b.baskets, 0), 4) AS lift
FROM pairs p CROSS JOIN totals t
JOIN product_baskets a ON a.product_id = p.product_a
JOIN product_baskets b ON b.product_id = p.product_b
WHERE p.together >= 2
ORDER BY lift DESC, together DESC, product_a, product_b
LIMIT 20;

-- Exercise 8: named controls make cross-domain sign-off machine-readable.
SELECT 'customers' AS control_name, COUNT(*)::numeric AS observed_value
FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'stored_order_revenue', ROUND(SUM(total_amount), 2) FROM orders
UNION ALL
SELECT 'line_revenue',
       ROUND(SUM(quantity * unit_price * (1 - discount)), 2) FROM order_items
UNION ALL
SELECT 'payments', ROUND(SUM(amount), 2) FROM payments
ORDER BY control_name;

ROLLBACK;
