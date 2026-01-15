-- Day 59: Final Capstone - Integrated Data Challenge (Part 2)
-- Focus: Complex business logic, performance requirements, stakeholder queries
BEGIN;
SET search_path TO training, public;

-- 1) Business KPI Suite (multi-level calculations)
-- a) LTV by cohort and segment
WITH order_values AS (
  SELECT o.customer_id, o.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value,
         o.order_date
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id, o.order_date
), ltv AS (
  SELECT customer_id,
         date_trunc('month', MIN(order_date))::date AS first_order_month,
         SUM(order_value) AS ltv
  FROM order_values
  GROUP BY customer_id
), cohort AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month,
         COALESCE(c.segment,'standard') AS segment
  FROM customers c
)
SELECT cohort.segment,
       cohort.cohort_month,
       ROUND(AVG(ltv.ltv),2) AS avg_ltv,
       COUNT(*) AS customers
FROM ltv
JOIN cohort ON cohort.customer_id = ltv.customer_id
GROUP BY cohort.segment, cohort.cohort_month
ORDER BY cohort.cohort_month DESC, avg_ltv DESC
LIMIT 100;

-- b) Conversion funnel from events -> orders (last 90 days)
WITH ev AS (
  SELECT e.customer_id,
         MAX(CASE WHEN e.event_type='page_view'  THEN 1 ELSE 0 END) AS page_view,
         MAX(CASE WHEN e.event_type='add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
         MAX(CASE WHEN e.event_type='checkout'   THEN 1 ELSE 0 END) AS checkout
  FROM events e
  WHERE e.event_time >= now() - interval '90 days'
  GROUP BY e.customer_id
), buyers AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= now() - interval '90 days'
)
SELECT 
  SUM(page_view)    AS viewers,
  SUM(add_to_cart)  AS adders,
  SUM(checkout)     AS checkouts,
  (SELECT COUNT(*) FROM buyers) AS buyers
FROM ev;

-- c) Top product pairs revenue (market basket)
WITH items AS (
  SELECT order_id, product_id FROM order_items GROUP BY order_id, product_id
), pairs AS (
  SELECT a.product_id AS p1, b.product_id AS p2, COUNT(*) AS together
  FROM items a
  JOIN items b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p1.name AS product_a, p2.name AS product_b, together
FROM pairs
JOIN products p1 ON p1.product_id = pairs.p1
JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY together DESC
LIMIT 20;

-- 2) Performance Aids (indexes/partitioning hints) - run EXPLAIN before/after
-- Note: These DDLs are rolled back unless you COMMIT intentionally
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_date ON payments(order_id, payment_date);

EXPLAIN ANALYZE
SELECT o.customer_id, SUM(o.total_amount)
FROM orders o
WHERE o.order_date >= now() - interval '180 days'
GROUP BY o.customer_id
ORDER BY SUM(o.total_amount) DESC
LIMIT 50;

-- 3) Stakeholder Views
-- a) Finance: Budget vs Actual YTD by category
WITH ytd_exp AS (
  SELECT date_trunc('year', expense_date)::date AS yr,
         category,
         SUM(amount) AS actual
  FROM expenses
  WHERE expense_date >= date_trunc('year', now())
  GROUP BY 1,2
), ytd_bud AS (
  SELECT date_trunc('year', period)::date AS yr,
         category,
         SUM(amount) AS budget
  FROM budgets
  WHERE period >= date_trunc('year', now())
  GROUP BY 1,2
)
SELECT COALESCE(b.category, e.category) AS category,
       COALESCE(b.yr, e.yr) AS year,
       COALESCE(b.budget,0) AS budget_ytd,
       COALESCE(e.actual,0) AS actual_ytd,
       ROUND(COALESCE(e.actual,0) - COALESCE(b.budget,0),2) AS variance
FROM ytd_bud b
FULL OUTER JOIN ytd_exp e ON e.yr=b.yr AND e.category=b.category
ORDER BY category;

-- b) Marketing: Campaign-assisted purchases (within 7 days)
WITH first_purchase AS (
  SELECT o.customer_id, MIN(o.order_date) AS first_buy
  FROM orders o
  GROUP BY o.customer_id
), touch AS (
  SELECT e.customer_id, e.event_time, COALESCE(e.metadata->>'campaign','none') AS campaign
  FROM events e
)
SELECT t.campaign,
       COUNT(DISTINCT t.customer_id) AS assisted_customers
FROM touch t
JOIN first_purchase fp ON fp.customer_id = t.customer_id
WHERE t.event_time BETWEEN fp.first_buy - interval '7 days' AND fp.first_buy
GROUP BY t.campaign
ORDER BY assisted_customers DESC
LIMIT 20;

-- 4) Large-scale considerations
-- For 100M+ rows, favor partitioning by time on orders/events, and use partial indexes on recent partitions.
-- Ensure queries constrain partition key (order_date, event_time) to enable pruning.

ROLLBACK;
