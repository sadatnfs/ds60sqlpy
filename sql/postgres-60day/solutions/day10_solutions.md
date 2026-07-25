# Day 10 walkthrough — DML with subqueries

[Day 10](../day10_dml_with_subqueries.sql) contains three worked demonstrations and no separate exercise section. This walkthrough explains those demonstrations instead of inventing unrelated exercises.

> [!WARNING]
> Run the complete lesson against the disposable `advanced_sql_training` database. Keep `BEGIN` and `ROLLBACK`; the examples temporarily change course data.

## Demonstration 1 — Create a temporary revenue rollup

```sql
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE tmp_category_revenue AS
SELECT
  p.category,
  ROUND(
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
    2
  ) AS revenue
FROM order_items AS oi
JOIN products AS p
  ON p.product_id = oi.product_id
GROUP BY p.category;

SELECT *
FROM tmp_category_revenue
ORDER BY revenue DESC;

ROLLBACK;
```

`CREATE TEMP TABLE ... AS SELECT` materializes the grouped query for the current database session. Because the table is created inside this transaction, `ROLLBACK` removes it.

## Demonstration 2 — Update employees selected by a subquery

```sql
BEGIN;
SET search_path TO training, public;

UPDATE employees AS e
SET salary = e.salary * 1.05
WHERE e.department_id IN (
  SELECT d.department_id
  FROM departments AS d
  WHERE d.name IN ('Sales', 'Engineering')
)
RETURNING
  e.employee_id,
  e.full_name,
  e.department_id,
  e.salary;

ROLLBACK;
```

The subquery turns department names into the IDs stored by `employees`. `RETURNING` previews the changed rows without requiring a second query. The rollback restores every salary.

## Demonstration 3 — Delete old orders only when no payment exists

```sql
BEGIN;
SET search_path TO training, public;

DELETE FROM orders AS o
WHERE o.order_date < CURRENT_TIMESTAMP - INTERVAL '365 days'
  AND NOT EXISTS (
    SELECT 1
    FROM payments AS p
    WHERE p.order_id = o.order_id
  )
RETURNING o.order_id, o.customer_id, o.order_date;

ROLLBACK;
```

The correlated `NOT EXISTS` is the delete guard: an old order is eligible only if no payment row references it. `RETURNING` shows what would be deleted, and `ROLLBACK` restores those rows.

## Safety check

Run the lesson as a whole with stop-on-error behavior:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day10_dml_with_subqueries.sql
```

Do not remove `ROLLBACK` merely to see a persistent change. Persistence is not an objective of this lesson.
