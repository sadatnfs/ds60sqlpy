# Day 08 — Solutions (Scalar and Inline Subqueries)

We compare scalar subqueries to join-based rewrites, and demonstrate set comparisons with ANY. Line-by-line explanations and pitfalls included.

Setup
- Schema: training; tables: customers, orders, products (plus optional promotions/events)
- Rule of thumb: Prefer pre-aggregated subqueries JOINed back over row-by-row scalar subqueries for performance and clarity

Exercise 1 — Last order date per customer (scalar subquery vs JOIN)

Scalar subquery form
```sql
SELECT c.customer_id,
       c.full_name,
       (
         SELECT MAX(o.order_date)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS last_order_date
FROM customers c
ORDER BY last_order_date DESC NULLS LAST
LIMIT 200;
```
Explanation
- The parent SELECT scans customers; for each row, the scalar subquery runs to compute MAX(order_date).
- This is simple to write and logically clear, but on large tables it can be slower (N subqueries).
- ORDER BY ... NULLS LAST pushes customers with no orders to the bottom.
Pitfalls
- Correlated subqueries that cannot use an index (due to functions, casts) can be expensive.

Preferred JOIN form
```sql
WITH last_orders AS (
  SELECT o.customer_id, MAX(o.order_date) AS last_order_date
  FROM orders o
  GROUP BY o.customer_id
)
SELECT c.customer_id,
       c.full_name,
       lo.last_order_date
FROM customers c
LEFT JOIN last_orders lo ON lo.customer_id = c.customer_id
ORDER BY lo.last_order_date DESC NULLS LAST
LIMIT 200;
```
Line-by-line
- last_orders pre-aggregates to one row per customer; a LEFT JOIN preserves customers without orders (NULL last_order_date).
- The planner can optimize a single grouped scan better than many correlated lookups.
- Same result set semantics as the scalar subquery, typically faster.

Exercise 2 — Orders whose total exceeds ANY of the top-decile totals
```sql
WITH ranked AS (
  SELECT o.order_id,
         o.total_amount,
         NTILE(10) OVER (ORDER BY o.total_amount DESC) AS decile
  FROM orders o
), top_decile AS (
  SELECT r.total_amount
  FROM ranked r
  WHERE r.decile = 1
)
SELECT o.order_id, o.total_amount
FROM orders o
WHERE o.total_amount > ANY (SELECT td.total_amount FROM top_decile td)
ORDER BY o.total_amount DESC
LIMIT 100;
```
Explanation
- NTILE(10) assigns deciles by total_amount; decile=1 is the top 10%.
- ANY compares a value to a set; “> ANY (set)” is equivalent to “> MIN(set)”. Here, picking ANY with the top decile essentially means greater than the minimum of that decile.
- You could also compute a cutoff with percentile_cont(0.9) and compare directly; the ANY form highlights set semantics.
Pitfalls
- Be careful with NULLs in the set — comparison to NULL yields UNKNOWN; filter NULLs in top_decile if needed.
- If you intended “greater than ALL of the top decile” (i.e., strictly above the entire top decile), use > ALL instead.
