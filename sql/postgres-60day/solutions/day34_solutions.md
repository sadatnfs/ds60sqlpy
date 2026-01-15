# Day 34 — Solutions (Query Optimization: Patterns and Anti‑patterns)

We optimize queries by reducing rows early, leveraging indexes, avoiding unnecessary work, and structuring joins/aggregations safely. We use EXPLAIN to confirm improvements.

Setup
- Tables: orders, order_items, customers, products
- Tools: EXPLAIN (ANALYZE, BUFFERS), ANALYZE, proper indexes

Exercise 1 — Push predicates early and avoid function-wrapped columns
```sql
-- Anti-pattern: wrapping column prevents index use
SELECT *
FROM orders
WHERE date(order_date) = CURRENT_DATE;  -- bad

-- Better: time range predicate
SELECT *
FROM orders
WHERE order_date >= date_trunc('day', CURRENT_DATE)
  AND order_date <  date_trunc('day', CURRENT_DATE) + interval '1 day';
```
Why
- Sargable predicates let the planner use an index on (order_date). Wrapping the column forces a full scan.

Exercise 2 — Pre-aggregate before joining 1:N tables
```sql
-- Anti-pattern: join raw order_items then group at the end, duplicating rows across joins
SELECT c.country,
       SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
FROM orders o
JOIN customers c ON c.customer_id=o.customer_id
JOIN order_items oi ON oi.order_id=o.order_id
GROUP BY c.country;

-- Better: aggregate to order level first; join smaller result set
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
)
SELECT c.country,
       SUM(ol.order_revenue) AS revenue
FROM orders o
JOIN customers c ON c.customer_id=o.customer_id
JOIN order_lines ol ON ol.order_id=o.order_id
GROUP BY c.country;
```
Benefits
- Fewer rows flow through the customer join; avoids accidental fanout if other 1:N joins are added later.

Exercise 3 — Replace correlated subqueries with JOINs or pre-aggregations
```sql
-- Anti-pattern: N-times scalar subquery
SELECT c.customer_id,
       (SELECT MAX(o.order_date) FROM orders o WHERE o.customer_id=c.customer_id) AS last_order
FROM customers c;

-- Better: pre-aggregate once and left join
WITH last_orders AS (
  SELECT customer_id, MAX(order_date) AS last_order
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id, lo.last_order
FROM customers c
LEFT JOIN last_orders lo ON lo.customer_id=c.customer_id;
```
Why
- Reduces repeated work; enables planner to choose efficient join strategies.

Exercise 4 — Avoid SELECT * and unnecessary DISTINCT
```sql
-- Anti-pattern: SELECT * and DISTINCT to mask duplicates
SELECT DISTINCT *
FROM orders o
JOIN order_items oi ON oi.order_id=o.order_id
WHERE o.order_date >= CURRENT_DATE - interval '7 days';

-- Better: project needed columns, fix duplication at source (pre-aggregate or keys)
WITH order_lines AS (
  SELECT order_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY order_id
)
SELECT o.order_id, o.customer_id, ol.order_revenue
FROM orders o
JOIN order_lines ol USING (order_id)
WHERE o.order_date >= CURRENT_DATE - interval '7 days';
```
Why
- DISTINCT is expensive and often hides a logical modeling problem.

Exercise 5 — Use appropriate join strategies and indexes
```sql
-- Verify join keys are indexed (FK side)
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.order_id, c.country
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_date >= CURRENT_DATE - interval '90 days';
```
Interpretation
- Expect Hash Join or Nested Loop + Index depending on sizes; ensure no Seq Scan on the large side.

Checklist
- Sargable predicates; no function-wrapped columns in WHERE/ON
- Pre-aggregate before many joins; avoid fanout
- Replace correlated subqueries with JOINs/CTEs
- Project only needed columns; avoid SELECT * and DISTINCT as band-aids
- Confirm with EXPLAIN; add/adjust indexes to match query shapes
