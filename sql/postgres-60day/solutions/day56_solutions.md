# Day 56 — Solutions (Project 4: Complex BI, Part 2 — Percentiles, Ranking, CUBE)

We compute distribution percentiles, top‑N splits, and multi‑dimensional subtotals. Below are step‑by‑step solutions to the exercises with line‑by‑line explanations.

Reference (annotated)
```sql
-- p50/p90/p99 of order values per country‑month
WITH orders_m AS (
  SELECT c.country,
         date_trunc('month', o.order_date)::date AS month,
         o.total_amount AS amt
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
)
SELECT country,
       month,
       PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM orders_m
GROUP BY country, month
ORDER BY month DESC, country
LIMIT 200;
```
Explanation
- orders_m: bring values (amt) to the group we’ll summarize over (country, month).
- PERCENTILE_CONT: continuous quantile; requires ORDER BY value inside WITHIN GROUP.

Exercise 1 — Add payment method to the CUBE and measure row count increase
Goal
- Expand CUBE to include payment_method and quantify how many extra subtotal rows appear.

Solution
```sql
WITH line AS (
  SELECT c.country,
         p.category,
         pm.method AS payment_method,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN payments pm ON pm.order_id = o.order_id
), base AS (
  SELECT COUNT(*) AS n_cube2
  FROM (
    SELECT 1
    FROM line
    GROUP BY CUBE(country, category)
  ) t
), expanded AS (
  SELECT COUNT(*) AS n_cube3
  FROM (
    SELECT 1
    FROM line
    GROUP BY CUBE(country, category, payment_method)
  ) t
)
SELECT n_cube2, n_cube3, (n_cube3 - n_cube2) AS extra_rows
FROM base CROSS JOIN expanded;
```
Line‑by‑line
- base: number of grouping sets produced by a 2‑dimensional CUBE.
- expanded: same but with a 3rd dimension (payment_method).
- Difference shows added subtotal combinations.

Exercise 2 — Compute p50/p90 of order values per category‑month
Goal
- Replace “country” with “category” and summarize distribution by month.

Solution
```sql
WITH orders_cat AS (
  SELECT p.category,
         date_trunc('month', o.order_date)::date AS month,
         o.total_amount AS amt
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT category,
       month,
       ROUND(PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY amt)::numeric, 2)  AS p50,
       ROUND(PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY amt)::numeric, 2)  AS p90
FROM orders_cat
GROUP BY category, month
ORDER BY month DESC, category
LIMIT 200;
```
Notes
- We join through order_items to expose product category for each order’s amount. If order totals already reflect all items, grouping by order is fine.

Top‑N within dimension (reference)
```sql
WITH prod_rev AS (
  SELECT c.country,
         p.category,
         p.product_id,
         p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT * FROM ranked WHERE rnk <= 5
ORDER BY country, category, rnk;
```
Explanation
- RANK gives ties the same rank. Use ROW_NUMBER to break ties deterministically.
