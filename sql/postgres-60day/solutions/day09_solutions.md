# Day 09 — Solutions (Correlated Subqueries, EXISTS/NOT EXISTS)

We use EXISTS as a semi-join, NOT EXISTS as an anti-join, and show why NOT IN can be incorrect in the presence of NULLs. Step-by-step explanations and pitfalls included.

Setup
- Schema: training; tables: customers, orders, order_items, products, events
- Rule of thumb: Prefer EXISTS/NOT EXISTS over IN/NOT IN when the subquery can contain NULLs or when you only need to test existence

Exercise 1 — Customers with a return/refund event (EXISTS)
```sql
SELECT c.customer_id,
       c.full_name,
       c.email
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM events e
  WHERE e.customer_id = c.customer_id
    AND (
      e.kind = 'refund' OR e.kind = 'return'
      -- If payload is JSONB with type in payload->>'event', you can use:
      -- (e.payload->>'event') IN ('refund','return')
    )
)
ORDER BY c.customer_id
LIMIT 200;
```
Line-by-line
- EXISTS: returns true if the subquery finds at least one row; the SELECT list inside EXISTS is ignored, so `SELECT 1` is idiomatic.
- Correlation: `e.customer_id = c.customer_id` ties the inner query to the current customer row.
- Why EXISTS: stops on first match; avoids duplicates and is robust to NULLs inside events.

Exercise 2 — Categories with no orders in the last 30 days (NOT EXISTS)
```sql
WITH window AS (
  SELECT CURRENT_DATE - INTERVAL '30 days' AS start_dt
)
SELECT DISTINCT p.category
FROM products p
WHERE NOT EXISTS (
  SELECT 1
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE oi.product_id = p.product_id
    AND o.order_date >= (SELECT start_dt FROM window)
)
ORDER BY p.category;
```
Explanation
- NOT EXISTS is an anti-join: it keeps a row from the outer query only if the subquery matches zero rows.
- Place the date filter in the subquery so that only recent orders disqualify a category.
- DISTINCT prevents duplicate categories if multiple products map to the same category.

Exercise 3 — Why NOT IN can be wrong with NULLs; fix with NOT EXISTS
Bad pattern (can exclude all rows if subquery has NULL)
```sql
SELECT c.customer_id, c.email
FROM customers c
WHERE c.email NOT IN (
  SELECT email
  FROM customers
  WHERE country = 'GB' -- might include NULL emails
);
```
Correct pattern with NOT EXISTS
```sql
SELECT c.customer_id, c.email
FROM customers c
WHERE NOT EXISTS (
  SELECT 1
  FROM customers gb
  WHERE gb.country = 'GB'
    AND gb.email = c.email
);
```
Why
- If the subquery of NOT IN returns any NULL, every comparison `x NOT IN (.., NULL, ..)` becomes UNKNOWN (i.e., false), yielding 0 rows.
- NOT EXISTS compares equality row-by-row and does not misbehave in the presence of NULLs.

Checks and tips
- When using IN/NOT IN, ensure the subquery column is declared NOT NULL or explicitly `WHERE email IS NOT NULL` inside the subquery.
- EXISTS is also often faster than `IN (SELECT ...)` for large subqueries, depending on indexes and planner choices.
