# Day 17 — Solutions (Ranking Functions: ROW_NUMBER, RANK, DENSE_RANK)

We select top‑k within partitions, deduplicate by earliest record, and rank customers by LTV per country. Key differences between ROW_NUMBER, RANK, and DENSE_RANK are highlighted.

Setup
- Tables: products, order_items, orders, customers
- When Postgres lacks QUALIFY, filter ranks in an outer SELECT or CTE

Exercise 1 — Top 3 products by revenue per category (ties included)
```sql
WITH prod_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.product_id
), ranked AS (
  SELECT category, product_id, revenue,
         DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT category, product_id, ROUND(revenue,2) AS revenue
FROM ranked
WHERE rnk <= 3
ORDER BY category, revenue DESC;
```
Reasoning
- DENSE_RANK keeps consecutive ranks with ties; you might get >3 products if multiple tie for rank 3.
- Use ROW_NUMBER if you need exactly 3 rows per category (break ties deterministically with a secondary sort key).

Exercise 2 — Deduplicate customers by normalized email, keep earliest created_at
```sql
WITH normalized AS (
  SELECT c.customer_id, LOWER(TRIM(c.email)) AS norm_email, c.created_at
  FROM customers c
), numbered AS (
  SELECT customer_id, norm_email, created_at,
         ROW_NUMBER() OVER (PARTITION BY norm_email ORDER BY created_at ASC, customer_id ASC) AS rn
  FROM normalized
)
SELECT customer_id, norm_email, created_at
FROM numbered
WHERE rn = 1
ORDER BY created_at;
```
Explanation
- ROW_NUMBER assigns a unique ordinal within each email group. Ordering by created_at then customer_id ensures reproducibility.
- The final WHERE rn=1 picks the keeper row per normalized email.

Exercise 3 — Top 10 customers by lifetime revenue within each country
```sql
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, SUM(order_value) AS lifetime_revenue
  FROM order_values
  GROUP BY customer_id
), ranked AS (
  SELECT c.country,
         c.customer_id,
         ROUND(l.lifetime_revenue,2) AS ltv,
         RANK() OVER (PARTITION BY c.country ORDER BY l.lifetime_revenue DESC) AS rnk
  FROM customers c
  JOIN ltv l ON l.customer_id = c.customer_id
)
SELECT *
FROM ranked
WHERE rnk <= 10
ORDER BY country, rnk, ltv DESC;
```
Notes
- Postgres doesn’t support QUALIFY; emulate it by wrapping the windowed SELECT and filtering rnk in the outer query, as shown.
- RANK introduces gaps when ties occur; DENSE_RANK would keep contiguous ranks.
