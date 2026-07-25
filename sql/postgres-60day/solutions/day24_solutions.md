# Day 24 — Solutions: Recursive CTEs

Recursive CTEs have an anchor term, a recursive term, and a stopping condition.
The employee hierarchy uses `manager_id` as the parent pointer.

## Exercise 1 — Every manager's direct and indirect reports

The literal prompt says “for each manager,” so this solution seeds every direct
manager-report edge and then walks downward. `path` both documents the route and
prevents a bad cycle from recursing forever.

```sql
SET search_path TO training, public;

WITH RECURSIVE reporting_lines AS (
  SELECT m.employee_id AS manager_id,
         e.employee_id AS report_id,
         e.full_name AS report_name,
         1 AS depth,
         ARRAY[m.employee_id, e.employee_id] AS path
  FROM employees m
  JOIN employees e ON e.manager_id = m.employee_id

  UNION ALL

  SELECT rl.manager_id,
         e.employee_id,
         e.full_name,
         rl.depth + 1,
         rl.path || e.employee_id
  FROM reporting_lines rl
  JOIN employees e ON e.manager_id = rl.report_id
  WHERE NOT e.employee_id = ANY(rl.path)
)
SELECT m.employee_id AS manager_id,
       m.full_name AS manager_name,
       rl.report_id,
       rl.report_name,
       rl.depth,
       rl.path
FROM reporting_lines rl
JOIN employees m ON m.employee_id = rl.manager_id
ORDER BY manager_id, depth, report_id;
```

Expected shape: one row per ancestor-descendant pair. `depth = 1` is a direct
report; larger depths are indirect reports. A report can correctly appear under
several managers along its chain.

To answer a question about one manager instead, add a root-manager predicate to
the anchor term; the maintained executable solution intentionally answers the
literal all-managers prompt shown above.

## Exercise 2 — Generate 1 through 100 and sum the sequence

```sql
SET search_path TO training, public;

WITH RECURSIVE numbers(n) AS (
  VALUES (1)

  UNION ALL

  SELECT n + 1
  FROM numbers
  WHERE n < 100
)
SELECT SUM(n) AS sum_1_to_100
FROM numbers;
```

Expected result: `5050`.

## Additional hierarchy diagnostic

The executable answer includes this useful check: count employees at each
depth from all roots.

```sql
SET search_path TO training, public;

WITH RECURSIVE org AS (
  SELECT e.employee_id,
         e.manager_id,
         0 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees e
  WHERE e.manager_id IS NULL

  UNION ALL

  SELECT c.employee_id,
         c.manager_id,
         org.depth + 1,
         org.path || c.employee_id
  FROM employees c
  JOIN org ON c.manager_id = org.employee_id
  WHERE NOT c.employee_id = ANY(org.path)
)
SELECT depth,
       COUNT(*) AS employees_at_depth
FROM org
GROUP BY depth
ORDER BY depth;
```

## Pitfalls

- Use `UNION ALL`; `UNION` performs duplicate elimination on every iteration
  and is not a substitute for a deliberate cycle check.
- Put the stop condition in the recursive term. The number generator would run
  indefinitely without `n < 100`.
- This schema permits multiple roots (`manager_id IS NULL`), so do not assume
  the organization has exactly one top-level employee.
