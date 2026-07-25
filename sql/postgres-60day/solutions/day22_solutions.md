# Day 22 — Solutions: Advanced Window Scenarios

These answers calculate an aggregate at the correct grain first and add window
rankings in a later query. That separation prevents line-item fanout from
distorting a rank.

## Exercise 1 — Category ranks by country and overall

Assumption: “overall category rank” means ranking each category by its revenue
across all countries, not ranking every country-category pair in one global
list.

```sql
SET search_path TO training, public;

WITH country_category AS (
  SELECT c.country,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM customers c
  JOIN orders o ON o.customer_id = c.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY c.country, p.category
), country_ranked AS (
  SELECT *,
         DENSE_RANK() OVER (
           PARTITION BY country
           ORDER BY revenue DESC
         ) AS rank_in_country
  FROM country_category
), overall_category AS (
  SELECT category,
         SUM(revenue) AS overall_revenue
  FROM country_category
  GROUP BY category
), overall_ranked AS (
  SELECT *,
         DENSE_RANK() OVER (
           ORDER BY overall_revenue DESC
         ) AS overall_category_rank
  FROM overall_category
)
SELECT cr.country,
       cr.category,
       ROUND(cr.revenue, 2) AS country_category_revenue,
       cr.rank_in_country,
       ROUND(o.overall_revenue, 2) AS overall_category_revenue,
       o.overall_category_rank
FROM country_ranked cr
JOIN overall_ranked o USING (category)
ORDER BY cr.country, cr.rank_in_country, cr.category;
```

Expected shape: one row per observed country-category pair. The overall revenue
and overall rank repeat for the same category in each country.

## Exercise 2 — Employee salary rank in department and company

```sql
SET search_path TO training, public;

SELECT d.name AS department,
       e.employee_id,
       e.full_name,
       e.salary,
       RANK() OVER (
         PARTITION BY e.department_id
         ORDER BY e.salary DESC
       ) AS department_salary_rank,
       RANK() OVER (
         ORDER BY e.salary DESC
       ) AS company_salary_rank
FROM employees e
JOIN departments d ON d.department_id = e.department_id
ORDER BY company_salary_rank, e.employee_id;
```

Expected shape: one row per employee. Rank `1` is the highest salary. `RANK`
leaves gaps after ties; use `DENSE_RANK` instead only if the requirement says
rank numbers must remain consecutive.

## Pitfalls

- A window function cannot directly rank a `SUM` at a different grain without
  first defining that grain in a CTE or subquery.
- Do not partition the company-wide rank; it deliberately has no
  `PARTITION BY`.
- The seeded employees all have departments, but a production report may need
  a `LEFT JOIN` to retain unassigned employees.
