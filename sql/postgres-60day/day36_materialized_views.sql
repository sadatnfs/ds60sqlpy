-- Day 36: Materialized Views & Caching
BEGIN;
SET search_path TO training, public;

-- Materialized view for category revenue by month
CREATE MATERIALIZED VIEW mv_category_month_revenue AS
SELECT p.category,
       date_trunc('month', o.order_date)::date AS month,
       SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
GROUP BY p.category, date_trunc('month', o.order_date);

-- Query the MV
SELECT * FROM mv_category_month_revenue ORDER BY month DESC, revenue DESC LIMIT 50;

-- Refresh when needed (will be rolled back)
REFRESH MATERIALIZED VIEW mv_category_month_revenue;

-- Exercises
-- 1. Create a MV for weekly revenue by country.
-- 2. Compare query time against base tables vs MV.
-- 3. Prediction: insert a temporary order after the materialized view is built.
--    Predict whether the view changes before REFRESH, then verify.
-- 4. Construction: add a unique index that would make a concurrent refresh
--    structurally possible; explain why this lesson still uses ordinary refresh.
-- 5. Debugging: compare SUM(orders.total_amount) with line-item revenue and
--    identify which business definition the materialized view actually stores.
-- 6. Edge case: query a month/category combination with no source rows and
--    explain why a materialized aggregate has no automatic zero-valued row.

ROLLBACK;
