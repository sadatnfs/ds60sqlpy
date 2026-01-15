# Day 01 — Solutions (SELECT, WHERE, ORDER BY, LIMIT/OFFSET)

This write-up explains each exercise solution line by line, why it’s written that way, and common pitfalls for beginners.

Setup
- Schema: training (from 00_setup.sql). If needed: `SET search_path TO training, public;`
- Tables used: customers, products, orders, order_items

Exercise 1 — 20 newest orders with customer_id and total_amount
```sql
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders o
ORDER BY 4 DESC
LIMIT 20;
```
Explanation
- SELECT: We choose the exact columns we need. Avoid SELECT * in production; it returns unnecessary data and can break downstream consumers if schema changes.
- FROM orders o: We alias orders to o for brevity and to prepare for joins later.
- ORDER BY 4 DESC: Sort by the 4th select item (order_date) in descending order so the newest is first. You can also write `ORDER BY o.order_date DESC` for clarity.
- LIMIT 20: After sorting, keep only the first 20 rows.
Pitfalls
- Assuming order without ORDER BY. SQL does not guarantee ordering unless specified.
- Sorting by a text-formatted date instead of a real timestamp column.

Exercise 2 — Top 10 most expensive products created in last 90 days
```sql
SELECT p.product_id,
       p.name,
       p.category,
       p.price,
       p.created_at
FROM products p
WHERE p.created_at >= now() - interval '90 days'
ORDER BY p.price DESC, p.created_at DESC
LIMIT 10;
```
Explanation
- WHERE created_at >= now() - interval '90 days': Filters rows before ordering, which is efficient and index-friendly (sargable).
- ORDER BY price DESC, created_at DESC: Break ties by preferring newer products if equal price.
- LIMIT 10: Return just the top 10.
Pitfalls
- Wrapping created_at in a function (e.g., date(created_at)) on the left side of the comparison can prevent index use.

Exercise 3 — GB/DE customers from last year, newest first, secondary sort by name
```sql
SELECT c.customer_id,
       c.full_name,
       c.email,
       c.country,
       c.created_at
FROM customers c
WHERE c.country IN ('GB','DE')
  AND c.created_at >= now() - interval '1 year'
ORDER BY c.created_at DESC, c.full_name ASC
LIMIT 100; -- optional for UI
```
Explanation
- country IN ('GB','DE'): Use IN for a small set of exact matches.
- AND created_at >= now() - interval '1 year': Time window filter.
- ORDER BY created_at DESC, full_name ASC: Deterministic ordering when timestamps tie.
Pitfalls
- Case-sensitive vs. insensitive comparisons—make sure country codes are standardized.

Check your understanding
- Why does ORDER BY come after WHERE and how does that affect performance?
- What happens if you forget ORDER BY and rely on insertion order?

Further tips
- Prefer keyset pagination for large lists (WHERE created_at < :last_seen ORDER BY created_at DESC) over OFFSET for better performance.
