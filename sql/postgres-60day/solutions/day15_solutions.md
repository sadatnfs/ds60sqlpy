# Day 15 — Solutions (Phase 1 Project: Multi‑Dimensional Revenue Report)

We build a monthly revenue report segmented by customer segment, country, and product category while avoiding fanout. We also reconcile totals two different ways to validate the result.

Setup
- Facts: orders(order_date, total_amount, customer_id), order_items(unit_price, quantity, discount, order_id, product_id)
- Dimensions: customers(customer_id, segment, country), products(product_id, category)
- Principle: Pre‑aggregate line revenue to the order level before joining other 1:N tables to avoid multiplicative duplication

Exercise — Monthly revenue by segment × country × category
```sql
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
```
Line‑by‑line
- order_lines: One row per order with its line‑item revenue. This collapses the 1:N order↔items relationship so later joins don’t multiply rows.
- enriched: Joins each order to exactly one row from customers (1:1), and selects a single dominant category per order via a subquery (ARRAY_AGG ordered by line revenue desc). In a data warehouse with order↔category many‑to‑many, you’d model a bridge table and decide how to attribute revenue (e.g., split proportionally).
- DATE_TRUNC('month')::date: Buckets orders into months and casts to date for tidy output.
- COALESCE(segment,'standard'): Normalizes NULL segments to a default bucket so GROUP BY includes them explicitly.
- Final SELECT: Aggregates measures and computes AOV = revenue / orders. NULLIF protects against divide‑by‑zero.
Pitfalls and alternatives
- Fanout: Joining raw order_items again after order_lines will double count. Keep to the rolled‑up grain or carefully aggregate before joining.
- Category attribution: If you need multi‑category attribution, replace the “pick one category” logic with a proportional split CTE using each item’s revenue share within the order.

Validation — Reconcile monthly revenue computed two ways
```sql
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
```
Explanation
- by_lines: Sums reconstructed revenue from items.
- by_orders: Sums order totals. Differences often reflect taxes/shipping/returns/discount rounding or definition drift.
- diff: Provides a quick QA signal. Investigate material gaps before publishing the main report.
