# Day 05 solutions — CROSS and SELF JOINs: Combinatorics and Relationships to Self

These answers align one-for-one with [day05_cross_self_joins.sql](../day05_cross_self_joins.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
- **Assumptions:** The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
- **Primary pitfall:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List every employee with their direct manager when present.

**Reasoning:** Self join employees and use a left join so top-level employees remain visible.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.full_name AS employee_name,
       m.employee_id AS manager_id,
       m.full_name AS manager_name
FROM employees AS e
LEFT JOIN employees AS m
  ON m.employee_id = e.manager_id
ORDER BY e.employee_id;
```

**Expected shape:** One row per employee.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Find employees who manage nobody.

**Reasoning:** Left join candidate managers to reports and retain managers with no right-side match.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.full_name
FROM employees AS e
LEFT JOIN employees AS report
  ON report.manager_id = e.employee_id
WHERE report.employee_id IS NULL
ORDER BY e.employee_id;
```

**Expected shape:** One row per leaf employee.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Build a complete grid of six recent months and all expense categories.

**Reasoning:** Cross join two small declared dimensions; do not cross join raw fact tables.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH months AS (
  SELECT generate_series(
           date_trunc('month', CURRENT_DATE) - INTERVAL '5 months',
           date_trunc('month', CURRENT_DATE),
           INTERVAL '1 month'
         )::date AS month_start
), categories AS (
  SELECT DISTINCT e.category
  FROM expenses AS e
)
SELECT c.category,
       m.month_start
FROM categories AS c
CROSS JOIN months AS m
ORDER BY c.category, m.month_start;
```

**Expected shape:** Six rows per distinct expense category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.

**Reasoning:** Cross-join cardinality is the product of input row counts.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.

```sql
WITH months AS (
  SELECT generate_series(1, 12) AS month_number
)
SELECT COUNT(*) AS department_month_combinations
FROM departments AS d
CROSS JOIN months AS m;
```

**Expected shape:** One row containing 72.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.

**Reasoning:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT left_employee.department_id,
       left_employee.employee_id AS first_employee_id,
       right_employee.employee_id AS second_employee_id
FROM employees AS left_employee
JOIN employees AS right_employee
  ON right_employee.department_id = left_employee.department_id
 AND left_employee.employee_id < right_employee.employee_id
ORDER BY left_employee.department_id,
         left_employee.employee_id,
         right_employee.employee_id;
```

**Expected shape:** One row per unordered same-department pair.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Show each employee, their manager, and their manager's manager.

**Reasoning:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.full_name AS employee_name,
       manager.full_name AS manager_name,
       grandmanager.full_name AS grandmanager_name
FROM employees AS e
LEFT JOIN employees AS manager
  ON manager.employee_id = e.manager_id
LEFT JOIN employees AS grandmanager
  ON grandmanager.employee_id = manager.manager_id
ORDER BY e.employee_id;
```

**Expected shape:** One row per employee with up to two ancestor columns.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
