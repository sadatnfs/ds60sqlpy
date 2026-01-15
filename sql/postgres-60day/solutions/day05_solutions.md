# Day 05 — Solutions (CROSS and SELF JOINs)

We generate within-table comparisons safely and compute co-purchases.

Exercise 1 — Two closest order gaps per customer
```sql
WITH ordered AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         LAG(o.order_date)  OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS prev_dt,
         LEAD(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS next_dt
  FROM orders o
), gaps AS (
  SELECT customer_id,
         order_id,
         CASE WHEN prev_dt IS NOT NULL THEN EXTRACT(EPOCH FROM (order_date - prev_dt)) END AS gap_from_prev,
         CASE WHEN next_dt IS NOT NULL THEN EXTRACT(EPOCH FROM (next_dt - order_date)) END AS gap_to_next
  FROM ordered
), flattened AS (
  SELECT customer_id, order_id, 'prev' AS gap_side, gap_from_prev AS gap_seconds FROM gaps WHERE gap_from_prev IS NOT NULL
  UNION ALL
  SELECT customer_id, order_id, 'next' AS gap_side, gap_to_next  AS gap_seconds FROM gaps WHERE gap_to_next  IS NOT NULL
), ranked AS (
  SELECT customer_id, order_id, gap_side, gap_seconds,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY gap_seconds, order_id) AS rn
  FROM flattened
)
SELECT customer_id, order_id, gap_side, gap_seconds
FROM ranked
WHERE rn <= 2
ORDER BY customer_id, rn;
```
Explanation
- LAG/LEAD compute neighbor timestamps per customer; EXTRACT(EPOCH FROM interval) yields a comparable numeric.
- Flatten both directions into a single list of gaps, then rank ascending per customer and keep top 2.

Exercise 2 — Unique product pairs and co-purchases within category
```sql
WITH lines AS (
  SELECT oi.order_id, oi.product_id, p.category
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
)
SELECT l1.category,
       l1.product_id AS product_id_a,
       l2.product_id AS product_id_b,
       COUNT(*) AS co_purchases
FROM lines l1
JOIN lines l2
  ON l1.order_id = l2.order_id
 AND l1.product_id < l2.product_id
GROUP BY l1.category, l1.product_id, l2.product_id
ORDER BY co_purchases DESC, l1.category
LIMIT 200;
```
Why it works
- Self‑join on the same order_id pairs items bought together. The strict inequality enforces (a,b) once and excludes (a,a).

Exercise 3 — Employee → manager → director chain via self-joins
```sql
SELECT e.employee_id AS employee_id,
       e.first_name || ' ' || e.last_name AS employee_name,
       m.employee_id AS manager_id,
       m.first_name || ' ' || m.last_name AS manager_name,
       d.employee_id AS director_id,
       d.first_name || ' ' || d.last_name AS director_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
LEFT JOIN employees d ON m.manager_id = d.employee_id
ORDER BY employee_id
LIMIT 200;
```
Notes
- LEFT JOINs preserve employees without managers or directors (top of hierarchy). Add more levels similarly.
Pitfalls
- CROSS JOINs explode row counts; use only on small sets or with immediate filters.
