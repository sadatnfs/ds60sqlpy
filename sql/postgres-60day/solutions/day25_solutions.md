# Day 25 — Solutions: Multiple CTEs and Hierarchies

This day focuses on composing several named stages. Each CTE has one job and an
explicit grain, which makes the result easier to test.

## Exercise 1 — Three-level report with department aggregates

Assumption: “three-level” means employee, direct manager, and manager's manager.
The department metrics are calculated once and attached to every employee row.

```sql
SET search_path TO training, public;

WITH department_metrics AS (
  SELECT department_id,
         COUNT(*) AS department_headcount,
         ROUND(SUM(salary), 2) AS department_payroll,
         ROUND(AVG(salary), 2) AS department_avg_salary
  FROM employees
  GROUP BY department_id
), three_levels AS (
  SELECT e.department_id,
         e.employee_id,
         e.full_name AS employee,
         m.full_name AS manager,
         gm.full_name AS managers_manager
  FROM employees e
  LEFT JOIN employees m ON m.employee_id = e.manager_id
  LEFT JOIN employees gm ON gm.employee_id = m.manager_id
)
SELECT d.name AS department,
       t.employee_id,
       t.employee,
       t.manager,
       t.managers_manager,
       dm.department_headcount,
       dm.department_payroll,
       dm.department_avg_salary
FROM three_levels t
JOIN departments d ON d.department_id = t.department_id
JOIN department_metrics dm ON dm.department_id = t.department_id
ORDER BY department,
         managers_manager NULLS FIRST,
         manager NULLS FIRST,
         employee;
```

Expected shape: one row per employee, enriched with up to two ancestors and
department-wide metrics. Top-level employees have `NULL` manager names.

## Exercise 2 — Filter, enrich, aggregate, present

The prompt intentionally leaves the business question open. This answer reports
orders and net revenue by country and category for the last 180 days.

```sql
SET search_path TO training, public;

WITH filtered_orders AS (
  SELECT order_id,
         customer_id,
         order_date
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
), enriched_lines AS (
  SELECT fo.order_id,
         fo.order_date::date AS order_day,
         c.country,
         p.category,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS line_revenue
  FROM filtered_orders fo
  JOIN customers c ON c.customer_id = fo.customer_id
  JOIN order_items oi ON oi.order_id = fo.order_id
  JOIN products p ON p.product_id = oi.product_id
), aggregated AS (
  SELECT country,
         category,
         COUNT(DISTINCT order_id) AS orders,
         SUM(line_revenue) AS revenue
  FROM enriched_lines
  GROUP BY country, category
)
SELECT country,
       category,
       orders,
       ROUND(revenue, 2) AS revenue,
       ROUND(revenue / NULLIF(orders, 0), 2) AS revenue_per_order
FROM aggregated
ORDER BY revenue DESC, country, category;
```

Expected shape: one row per observed country-category pair. An order spanning
multiple categories contributes to each category's distinct order count, so
category order counts are not additive across categories.

## Pitfalls

- Keep each stage's grain visible: employee, order, order line, or grouped
  country-category.
- Use `LEFT JOIN` for optional hierarchy levels; an inner self-join would drop
  executives and employees without a second-level ancestor.
- Do not sum `orders.total_amount` after joining to order items; that repeats an
  order total once per line.
