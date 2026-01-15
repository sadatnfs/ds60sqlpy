-- Day 09 - Solutions: Correlated Subqueries and EXISTS
-- Assumes: customers, orders, order_items, products, events (JSONB or simple table with kind)

/*
Exercise 1) List customers with a return/refund event using EXISTS against events.
Why: EXISTS is a semi-join that short-circuits on first match and handles NULLs cleanly.
*/
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

/*
Exercise 2) Find categories with no orders in the last 30 days using NOT EXISTS.
Why: NOT EXISTS is a robust anti-join; it avoids the pitfalls of NOT IN when NULLs are present.
*/
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

/*
Exercise 3) Demonstrate NOT IN vs NOT EXISTS when the subquery can produce NULL.
Why: NOT IN returns UNKNOWN (i.e., filters out everything) if the subquery contains NULLs. Prefer NOT EXISTS.
*/
-- Suppose some customers have NULL emails and we try to exclude all emails from a subquery that might include NULL
-- Bad pattern (can exclude all rows if subquery has NULL)
SELECT c.customer_id, c.email
FROM customers c
WHERE c.email NOT IN (
  SELECT email
  FROM customers
  WHERE country = 'GB' -- might include NULL emails
);

-- Correct pattern with NOT EXISTS
SELECT c.customer_id, c.email
FROM customers c
WHERE NOT EXISTS (
  SELECT 1
  FROM customers gb
  WHERE gb.country = 'GB'
    AND gb.email = c.email
);

-- End of Day 09 solutions
