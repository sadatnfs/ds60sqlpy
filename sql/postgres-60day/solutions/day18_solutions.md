# Day 18 solutions — LAG and LEAD

These answers match the exercises in [Day 18](../day18_lag_lead.sql).

## Exercise 1 — Monthly product sales and the previous month

This solution interprets “sales” as discounted revenue. It builds a dense month calendar so `LAG` means the immediately previous calendar month, even when a product had no sales then.

```sql
WITH month_bounds AS (
  SELECT
    DATE_TRUNC('month', MIN(o.order_date) AT TIME ZONE 'UTC')::date AS first_month,
    DATE_TRUNC('month', MAX(o.order_date) AT TIME ZONE 'UTC')::date AS last_month
  FROM training.orders AS o
),
months AS (
  SELECT generated_month::date AS sales_month
  FROM month_bounds AS mb
  CROSS JOIN LATERAL GENERATE_SERIES(
    mb.first_month,
    mb.last_month,
    INTERVAL '1 month'
  ) AS g(generated_month)
),
monthly_sales AS (
  SELECT
    oi.product_id,
    DATE_TRUNC(
      'month',
      o.order_date AT TIME ZONE 'UTC'
    )::date AS sales_month,
    SUM(
      oi.unit_price * oi.quantity * (1 - oi.discount)
    ) AS revenue
  FROM training.order_items AS oi
  JOIN training.orders AS o
    ON o.order_id = oi.order_id
  GROUP BY
    oi.product_id,
    DATE_TRUNC('month', o.order_date AT TIME ZONE 'UTC')::date
),
dense_product_months AS (
  SELECT
    p.product_id,
    p.name,
    m.sales_month,
    COALESCE(ms.revenue, 0) AS revenue
  FROM training.products AS p
  CROSS JOIN months AS m
  LEFT JOIN monthly_sales AS ms
    ON ms.product_id = p.product_id
   AND ms.sales_month = m.sales_month
)
SELECT
  product_id,
  name,
  sales_month,
  ROUND(revenue, 2) AS monthly_sales,
  ROUND(
    LAG(revenue) OVER (
      PARTITION BY product_id
      ORDER BY sales_month
    ),
    2
  ) AS previous_month_sales
FROM dense_product_months
ORDER BY product_id, sales_month;
```

Without the `months` CTE, `LAG` would mean “previous month with a row,” which can skip inactive calendar months.

## Exercise 2 — Next higher salary within each department

```sql
WITH distinct_department_salaries AS (
  SELECT DISTINCT
    e.department_id,
    e.salary
  FROM training.employees AS e
),
salary_steps AS (
  SELECT
    dds.department_id,
    dds.salary,
    LEAD(dds.salary) OVER (
      PARTITION BY dds.department_id
      ORDER BY dds.salary
    ) AS next_higher_salary
  FROM distinct_department_salaries AS dds
)
SELECT
  d.name AS department,
  e.employee_id,
  e.full_name,
  e.salary,
  ss.next_higher_salary,
  ss.next_higher_salary - e.salary AS gap_to_next_higher
FROM training.employees AS e
JOIN training.departments AS d
  ON d.department_id = e.department_id
JOIN salary_steps AS ss
  ON ss.department_id = e.department_id
 AND ss.salary = e.salary
ORDER BY d.name, e.salary, e.employee_id;
```

Using distinct salary values makes “higher” strict: a same-salary colleague is not treated as the next step. The highest salary in each department has no higher value, so `LEAD` returns `NULL`.

## Check yourself

- The first month for each product has no previous-month value.
- After that, every dense product-month row compares with the immediately preceding calendar month.
- The highest salary in each department has a null `next_higher_salary`.
