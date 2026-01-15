-- Day 01 - Solutions: SELECT, WHERE, ORDER BY, LIMIT/OFFSET
-- Schema assumption: training schema from 00_setup.sql with tables customers, products, orders, order_items, payments
-- Note: Run `SET search_path TO training, public;` at the start of your session if needed.

/*
Exercise 1) List the 20 newest orders with customer_id and total_amount.
Key ideas:
- ORDER BY must be on a timestamp that increases with recency (order_date)
- Use DESC for newest first, and NULLS LAST to push any missing dates to the bottom
- LIMIT 20 to only return the first 20 rows after sorting
Why: Without ORDER BY, SQL does not guarantee any particular row order.
*/
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders o
ORDER BY 4 DESC
LIMIT 20;

/*
Exercise 2) Find top 10 most expensive products created in the last 90 days.
Key ideas:
- Use a sargable date filter: created_at >= now() - interval '90 days'
- ORDER BY price DESC to surface most expensive items
- LIMIT 10 for the top N
Why: Wrapping created_at in a function (e.g., date(created_at)) can block index usage; comparisons keep it sargable.
*/
SELECT p.product_id,
       p.name,
       p.category,
       p.price,
       p.created_at
FROM products p
WHERE p.created_at >= now() - interval '90 days'
ORDER BY p.price DESC, p.created_at DESC
LIMIT 10;

/*
Exercise 3) Show customers from GB or DE created within the last year, newest first.
Key ideas:
- Use IN ('GB','DE') to match either country; prefer upper-cased standardized codes
- Use a 1-year interval with a sargable predicate
- Secondary sort by full_name for deterministic ordering within same created_at
Why: Deterministic ordering avoids nondeterminism when timestamps tie.
*/
SELECT c.customer_id,
       c.full_name,
       c.email,
       c.country,
       c.created_at
FROM customers c
WHERE c.country IN ('GB','DE')
  AND c.created_at >= now() - interval '1 year'
ORDER BY c.created_at DESC, c.full_name ASC
LIMIT 100; -- limit optional for UX in UIs

-- End of Day 01 solutions
