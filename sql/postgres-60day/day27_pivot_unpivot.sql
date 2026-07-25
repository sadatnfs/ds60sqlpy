-- Day 27: PIVOT / UNPIVOT (PostgreSQL approaches)
BEGIN;
SET search_path TO training, public;

-- Approach 1: Conditional aggregation (portable)
SELECT p.category,
       ROUND(SUM(CASE WHEN date_part('month', o.order_date)=1 THEN oi.quantity ELSE 0 END),2) AS jan_qty,
       ROUND(SUM(CASE WHEN date_part('month', o.order_date)=2 THEN oi.quantity ELSE 0 END),2) AS feb_qty,
       ROUND(SUM(CASE WHEN date_part('month', o.order_date)=3 THEN oi.quantity ELSE 0 END),2) AS mar_qty
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.order_date >= date_trunc('year', now())
GROUP BY p.category
ORDER BY p.category;

-- Approach 2: crosstab (requires the optional tablefunc extension; an
-- authorized database role must install it before this query is used)
-- SELECT * FROM crosstab(
--   $$
--   SELECT p.category::text AS rowid,
--          date_part('month', o.order_date)::int AS bucket,
--          SUM(oi.quantity)::numeric AS value
--   FROM order_items oi
--   JOIN orders o ON o.order_id = oi.order_id
--   JOIN products p ON p.product_id = oi.product_id
--   WHERE o.order_date >= date_trunc('year', now())
--   GROUP BY p.category, date_part('month', o.order_date)
--   ORDER BY 1,2
--   $$,
--   $$ SELECT m FROM generate_series(1,12) AS t(m) $$
-- ) AS ct(category text, m1 numeric, m2 numeric, m3 numeric, m4 numeric, m5 numeric, m6 numeric, m7 numeric, m8 numeric, m9 numeric, m10 numeric, m11 numeric, m12 numeric);

-- UNPIVOT-like using UNION ALL
SELECT category, 'jan' AS month, jan_qty FROM (
  SELECT p.category,
         SUM(CASE WHEN date_part('month', o.order_date)=1 THEN oi.quantity ELSE 0 END) AS jan_qty
  FROM order_items oi JOIN orders o ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
) s
UNION ALL
SELECT category, 'feb', feb_qty FROM (
  SELECT p.category,
         SUM(CASE WHEN date_part('month', o.order_date)=2 THEN oi.quantity ELSE 0 END) AS feb_qty
  FROM order_items oi JOIN orders o ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
) s2;

-- Exercises
-- 1) Pivot revenue by payment method across last 4 quarters.
-- 2) Unpivot budget table into category, period, amount rows.

ROLLBACK;
