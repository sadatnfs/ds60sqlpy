# Day 20 solutions — FIRST_VALUE and LAST_VALUE

These answers match the exercises in [Day 20](../day20_first_last_value.sql).

## Exercise 1 — Current-month revenue versus first-month revenue

This solution interprets “current month” as the calendar month containing `CURRENT_DATE`. Products without any sale have no first-sales month; products without a sale this month receive zero current-month revenue.

```sql
WITH monthly_sales AS (
  SELECT
    oi.product_id,
    DATE_TRUNC(
      'month',
      o.order_date AT TIME ZONE 'UTC'
    )::date AS sales_month,
    SUM(
      oi.unit_price * oi.quantity * (1 - oi.discount)
    ) AS month_revenue
  FROM training.order_items AS oi
  JOIN training.orders AS o
    ON o.order_id = oi.order_id
  GROUP BY
    oi.product_id,
    DATE_TRUNC('month', o.order_date AT TIME ZONE 'UTC')::date
),
sales_with_first AS (
  SELECT
    ms.*,
    FIRST_VALUE(ms.sales_month) OVER product_history AS first_sales_month,
    FIRST_VALUE(ms.month_revenue) OVER product_history AS first_month_revenue
  FROM monthly_sales AS ms
  WINDOW product_history AS (
    PARTITION BY ms.product_id
    ORDER BY ms.sales_month
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
),
product_summary AS (
  SELECT
    swf.product_id,
    MIN(swf.first_sales_month) AS first_sales_month,
    MAX(swf.first_month_revenue) AS first_month_revenue,
    COALESCE(
      MAX(swf.month_revenue) FILTER (
        WHERE swf.sales_month = DATE_TRUNC('month', CURRENT_DATE)::date
      ),
      0
    ) AS current_month_revenue
  FROM sales_with_first AS swf
  GROUP BY swf.product_id
)
SELECT
  p.product_id,
  p.name,
  ps.first_sales_month,
  ROUND(ps.first_month_revenue, 2) AS first_month_revenue,
  ROUND(COALESCE(ps.current_month_revenue, 0), 2) AS current_month_revenue,
  CASE
    WHEN ps.first_month_revenue IS NULL THEN NULL
    ELSE ROUND(
      COALESCE(ps.current_month_revenue, 0) - ps.first_month_revenue,
      2
    )
  END AS change_from_first_month
FROM training.products AS p
LEFT JOIN product_summary AS ps
  ON ps.product_id = p.product_id
ORDER BY p.product_id;
```

The full frame makes the first value available to every monthly row in a product partition. The outer product join retains the intentionally unsold products.

## Exercise 2 — Synthetic first-salary comparison

The course schema has one current salary per employee and no salary-history table. It cannot recover an employee’s original salary. Following the prompt, this simulation compares each employee with the salary of the earliest-hired employee in the same department.

```sql
WITH salary_reference AS (
  SELECT
    d.name AS department,
    e.department_id,
    e.employee_id,
    e.full_name,
    e.hire_date,
    e.salary,
    FIRST_VALUE(e.full_name) OVER department_hire_order
      AS earliest_hired_employee,
    FIRST_VALUE(e.salary) OVER department_hire_order
      AS earliest_hire_salary
  FROM training.employees AS e
  JOIN training.departments AS d
    ON d.department_id = e.department_id
  WINDOW department_hire_order AS (
    PARTITION BY e.department_id
    ORDER BY e.hire_date, e.employee_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
)
SELECT
  department,
  employee_id,
  full_name,
  hire_date,
  salary,
  earliest_hired_employee,
  earliest_hire_salary,
  salary - earliest_hire_salary AS difference_from_reference
FROM salary_reference
ORDER BY department, hire_date, employee_id;
```

This is a ranking-based reference, not salary history. A real answer to “first salary recorded” needs a table such as `employee_salary_history(employee_id, effective_at, salary)`.

## Check yourself

- An unsold product has `NULL` first-month revenue and zero current-month revenue.
- Every employee in a department sees the same earliest-hire reference.
- Do not describe the synthetic reference as an employee’s historical starting salary.
