# Day 35 — Solutions (Avoiding Pitfalls: NULLs, Casting, Time Zones, Precision)

We catalog common SQL pitfalls that cause silent logic errors or poor performance, and show robust patterns for correctness. Topics: three‑valued logic with NULLs, implicit casting, integer division, time zone drift, and duplicates from joins.

Setup
- Tables: customers(email, created_at), orders(order_id, customer_id, order_date, total_amount), order_items(...)
- Guiding principle: be explicit — types, time zones, join keys, and aggregations

Exercise 1 — NULL logic: IS NULL vs = NULL; outer joins and filters
```sql
-- Wrong: comparisons to NULL are UNKNOWN (not TRUE)
SELECT 1 WHERE NULL = NULL;   -- returns no rows

-- Correct: IS NULL / IS NOT NULL
SELECT customer_id FROM customers WHERE email IS NULL;

-- LEFT JOIN + filter pitfall
-- Wrong: WHERE p.status='completed' turns LEFT into INNER (drops NULL-extended rows)
SELECT c.customer_id
FROM customers c
LEFT JOIN payments p ON p.customer_id=c.customer_id
WHERE p.status='completed';   -- inner semantics

-- Correct: put right-side predicate in ON when preserving unmatched rows
SELECT c.customer_id
FROM customers c
LEFT JOIN payments p
  ON p.customer_id=c.customer_id AND p.status='completed';
```
Takeaways
- Use IS NULL; move right‑side predicates into ON for LEFT joins when you need to preserve NULL‑extended rows.

Exercise 2 — Integer division, casting, and precision
```sql
-- Integer division truncates
SELECT 1/2  AS i_div, 1.0/2  AS f_div;  -- 0 vs 0.5

-- Cast to numeric/float before division; round at presentation edge
SELECT ROUND(SUM(revenue)::numeric / NULLIF(COUNT(*),0), 2) AS aov
FROM (
  SELECT (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi
) t;
```
Notes
- Keep internal arithmetic at full precision; round only in final SELECT.

Exercise 3 — Implicit casts and sargability
```sql
-- Non-sargable implicit cast: forces full scan
SELECT * FROM orders WHERE order_date::date = CURRENT_DATE;

-- Sargable window with explicit bounds
SELECT * FROM orders
WHERE order_date >= date_trunc('day', CURRENT_DATE)
  AND order_date <  date_trunc('day', CURRENT_DATE) + interval '1 day';

-- Mismatched types: text vs numeric
SELECT * FROM orders WHERE order_id = '123'; -- avoid relying on implicit cast; use correct type
```
Why it matters
- Sargable predicates enable index usage; implicit casts on the column side disable it. Match types explicitly.

Exercise 4 — Time zones and drift
```sql
-- Store timestamps in UTC (timestamptz) and convert at edges
SELECT order_id,
       order_date AT TIME ZONE 'UTC' AS utc_time,
       order_date AT TIME ZONE 'America/Los_Angeles' AS pacific_time
FROM orders
WHERE order_date >= now() - interval '1 day';

-- Define day windows with care for local midnight
WITH bounds AS (
  SELECT timezone('America/New_York', date_trunc('day', now())) AS start_local
)
SELECT *
FROM orders
WHERE order_date >= (SELECT start_local FROM bounds) AT TIME ZONE 'America/New_York'
  AND order_date <  ((SELECT start_local FROM bounds) + interval '1 day') AT TIME ZONE 'America/New_York';
```
Tips
- Be explicit about zones when slicing by “business day.” Prefer storing UTC and convert only for I/O.

Exercise 5 — Duplicates from joins and DISTINCT misuse
```sql
-- Anti-pattern: DISTINCT to hide duplicated rows from a 1:N join
SELECT DISTINCT o.order_id, c.customer_id
FROM orders o JOIN customers c USING (customer_id)
JOIN order_items oi USING (order_id);

-- Better: reduce to 1:1 before joining or aggregate on the N-side first
WITH order_lines AS (
  SELECT order_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY order_id
)
SELECT o.order_id, c.customer_id, ol.order_revenue
FROM orders o
JOIN customers c USING (customer_id)
JOIN order_lines ol USING (order_id);
```
Why
- DISTINCT is expensive and can mask logic errors. Fix multiplicity at source with grouping or keys.

Exercise 6 — CASE and ELSE
```sql
-- Missing ELSE yields NULL for unmatched rows; handle explicitly when needed
SELECT CASE WHEN total_amount >= 100 THEN 'VIP' ELSE 'REG' END AS tier
FROM orders;
```
Checklist
- IS NULL/IS NOT NULL over = NULL
- Cast intentionally; avoid integer division surprises
- Sargable predicates; no function/cast on columns in WHERE/ON
- Time windows defined with timezone awareness
- Fix join multiplicity; avoid DISTINCT as a band‑aid
