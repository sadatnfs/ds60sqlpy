# Day 05 solutions: CROSS and SELF JOINs: Combinatorics and Relationships to Self

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Five of these answers read `employees` or `departments`; Exercise 3 reads `expenses` and the calendar. Try each prompt first, then run the companion file:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day05_solutions.sql
```

The script sets `search_path` to `training, public` and ends in `ROLLBACK`. Counts to expect: 100, 97, 30, 72, 784 and 100 rows. Only Exercise 3's month values move with the date you run it. Each section mirrors a prompt in [day05_cross_self_joins.sql](../day05_cross_self_joins.sql); see the [solution-reading notes](../../STUDY-GUIDE.md#read-a-solution) for the general approach.

## Reading contract

- **Focus:** Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
- **Assumptions:** The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
- **Primary pitfall:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
- **Safety:** read-only from start to finish, and still wrapped in `BEGIN`/`ROLLBACK` so a test row you insert to probe an edge case is gone afterwards.

## Exercise 1: Query writing

**Prompt:** List every employee with their direct manager when present.

**Reasoning:** Self join employees and use a left join so top-level employees remain visible.

**Clause-by-clause reading:**

- `FROM employees AS e`: the person being described, 100 rows.
- `LEFT JOIN employees AS m ON m.employee_id = e.manager_id`: looks up that person's manager in the same table; a NULL `manager_id` finds nothing and leaves `m` empty.
- `SELECT ... m.employee_id AS manager_id, m.full_name AS manager_name`: both manager columns come from the second alias, so they are NULL together.
- `ORDER BY e.employee_id`: one row per person in ID order.

```sql
SELECT
  e.employee_id,
  e.full_name AS employee_name,
  m.employee_id AS manager_id,
  m.full_name AS manager_name
FROM
  employees AS e
  LEFT JOIN employees AS m ON m.employee_id = e.manager_id
ORDER BY
  e.employee_id;
```

**Expected shape:** One row per employee.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 1, self-join the 100 `employees` rows, aliasing the manager copy as `m`; 6 employees (1 through 6) have no `manager_id`, and the other 94 report to employee 1, 2, or 8. Return `employee_id`, `employee_name`, `manager_id`, and `manager_name`.
- **Expected result/shape:** For sql-05 Exercise 1, return 100 rows, one per employee; employees 1 through 6 show `NULL` manager columns, employee 7 reports to Employee 2, employee 8 to Employee 1, and the remaining 92 to Employee 8. The final columns are `employee_id`, `employee_name`, `manager_id`, and `manager_name`. The final order is `e.employee_id`.
- **Independent verification:** For sql-05 Exercise 1, confirm 100 distinct `employee_id` values and exactly 6 rows with `manager_name IS NULL`. Switch `LEFT JOIN` to an inner join and the count must fall to 94, losing exactly employees 1 through 6.
- **What prints:** 100 rows. Employees 1 to 6 have NULL `manager_id` and `manager_name`. Employee 7 reports to Employee 2, Employee 8 reports to Employee 1, and Employees 9 to 100 all report to Employee 8.
- **Count to compare:** `SELECT COUNT(*) FROM employees` is 100, and `COUNT(manager_id)` is 94. The result should have 6 NULL managers, the difference.
- **Inner join instead:** 94 rows, with the six department heads gone. Nothing errors, so the missing rows are easy to miss without the count above.
- **Why fanout cannot happen:** `employee_id` is the key of `m`, so each person matches at most one manager row.
- **Reading the top of the output:** Employees 1 to 6 come first only because the order is by `e.employee_id`; sorting by `manager_name` instead would move them to the end, since PostgreSQL places NULLs last in ascending order.

## Exercise 2: Query writing

**Prompt:** Find employees who manage nobody.

**Reasoning:** Left join candidate managers to reports and retain managers with no right-side match.

**Clause-by-clause reading:**

- `FROM employees AS e`: every person is a candidate.
- `LEFT JOIN employees AS report ON report.manager_id = e.employee_id`: attaches each person's direct reports. Employee 8 gets 92 rows here, Employees 1 and 2 one each, everyone else a single row of NULLs.
- `WHERE report.employee_id IS NULL`: keeps only the NULL-padded rows, meaning no report was found.
- `ORDER BY e.employee_id`.

```sql
SELECT
  e.employee_id,
  e.full_name
FROM
  employees AS e
  LEFT JOIN employees AS report ON report.manager_id = e.employee_id
WHERE
  report.employee_id IS NULL
ORDER BY
  e.employee_id;
```

**Expected shape:** One row per leaf employee.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 2, `LEFT JOIN` each of the 100 `employees` to the employees who report to them and keep rows with no report; only employees 1, 2, and 8 manage anyone.
- **Expected result/shape:** For sql-05 Exercise 2, return 97 rows, one per employee who manages nobody, from employee 3 to employee 100 with 1, 2, and 8 missing. The final columns are `employee_id`, and `full_name`. The final order is `e.employee_id`.
- **Independent verification:** For sql-05 Exercise 2, confirm `SELECT COUNT(DISTINCT manager_id) FROM employees` returns 3 and that 100 minus 3 equals the 97 rows. Inside a rolled-back transaction, make employee 100 report to employee 3; the result must drop to 96 rows because employee 3 is no longer a leaf.
- **What prints:** 97 rows, every employee except 1, 2 and 8. Employees 3 to 6 appear even though they also have no manager; having no boss and having no reports are separate facts.
- **The intermediate count:** without the `WHERE`, the left join gives 191 rows (97 single rows plus 1 + 1 + 92 report rows). The filter then removes the 94 matched rows.
- **Where the test belongs:** moving `report.employee_id IS NULL` into the `ON` clause makes the join match nothing, so all 100 people return.
- **Equivalent query:** `WHERE NOT EXISTS (SELECT 1 FROM employees r WHERE r.manager_id = e.employee_id)` gives the same 97 rows. `NOT IN` over `manager_id` gives 0, because that column contains NULLs.

## Exercise 3: Query writing

**Prompt:** Build a complete grid of six recent months and all expense categories.

**Reasoning:** Cross join two small declared dimensions; do not cross join raw fact tables.

**Clause-by-clause reading:**

- `months`: `generate_series` from the first day of the month five months ago to the first day of this month, one month apart, cast to `date`. Six rows.
- `categories`: `SELECT DISTINCT e.category FROM expenses`, five rows out of 10,000.
- `CROSS JOIN`: 5 times 6.
- `ORDER BY c.category, m.month_start`.

```sql
WITH months AS (
  SELECT
    generate_series(date_trunc('month', CURRENT_DATE) - INTERVAL '5 months', date_trunc('month', CURRENT_DATE), INTERVAL '1 month')::date AS month_start
),
categories AS (
  SELECT DISTINCT
    e.category
  FROM
    expenses AS e
)
SELECT
  c.category,
  m.month_start
FROM
  categories AS c
  CROSS JOIN months AS m
ORDER BY
  c.category,
  m.month_start;
```

**Expected shape:** Six rows per distinct expense category.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 3, cross join the 5 distinct `expenses` categories with a `generate_series` of 6 month starts, from five months before the current month through the current month.
- **Expected result/shape:** For sql-05 Exercise 3, return 30 rows, six month starts for each of `COGS`, `G&A`, `Infrastructure`, `Marketing`, and `Payroll`, whether or not the month has expenses. The final columns are `category`, and `month_start`. The final order is `c.category, m.month_start`.
- **Independent verification:** For sql-05 Exercise 3, confirm 30 distinct `(category, month_start)` pairs and that each category appears exactly 6 times. Widen the series to start eleven months back and the result must grow to 60 rows, 5 categories times 12 months.
- **What prints:** 30 rows, six months for each of COGS, G&A, Infrastructure, Marketing and Payroll. On the load used here (`CURRENT_DATE` in late November 2026) the months run from 2026-06-01 to 2026-11-01.
- **Purpose of the grid:** it holds no spending yet. Left joining monthly expense totals onto it later turns a missing month into a visible row with a NULL total, rather than no row.
- **The tempting shortcut:** crossing `expenses` itself with six months returns 60,000 rows that repeat each category thousands of times.
- **Edge case:** an expense with a new category adds six rows, one per month, not one.

## Exercise 4: Prediction

**Prompt:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.

**Reasoning:** Cross-join cardinality is the product of input row counts.

**Clause-by-clause reading:**

- `months`: `generate_series(1, 12)`, twelve numbered rows.
- `FROM departments AS d CROSS JOIN months AS m`: 6 times 12 combinations.
- `SELECT COUNT(*) AS department_month_combinations`: counts them without listing any column.

```sql
WITH months AS (
  SELECT
    generate_series(1, 12) AS month_number
)
SELECT
  COUNT(*) AS department_month_combinations
FROM
  departments AS d
  CROSS JOIN months AS m;
```

**Expected shape:** One row containing 72.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 4, cross join the 6 `departments` rows with `generate_series(1, 12)` and count the combinations; no department key is returned.
- **Expected result/shape:** For sql-05 Exercise 4, return exactly one row with `department_month_combinations` equal to 72. The final columns are `department_month_combinations`.
- **Independent verification:** For sql-05 Exercise 4, confirm 72 equals `SELECT COUNT(*) FROM departments` (6) times 12. Change the series to `generate_series(1, 6)` and the count must become 36, showing that a cross join multiplies the row counts.
- **What prints:** one row, 72. The prediction is pure arithmetic: 6 departments times 12 months.
- **Applying the add-a-row rule:** a seventh department raises the count to 84, twelve more, while the output stays one row.
- **Crossing the wrong table:** using `employees` instead of `departments` gives 1,200, a warning sign that the grain is people, not departments.
- **Equivalent check:** `SELECT (SELECT COUNT(*) FROM departments) * 12` returns 72 without building the combinations at all.

## Exercise 5: Debugging

**Prompt:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.

**Reasoning:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.

**Clause-by-clause reading:**

- `employees AS left_employee JOIN employees AS right_employee`: two copies of the same 100 people.
- `ON right_employee.department_id = left_employee.department_id`: pairs only colleagues in the same department.
- `AND left_employee.employee_id < right_employee.employee_id`: keeps each pair once, smaller ID on the left, and excludes pairing a person with themself.
- `ORDER BY` department, then first ID, then second ID.

```sql
SELECT
  left_employee.department_id,
  left_employee.employee_id AS first_employee_id,
  right_employee.employee_id AS second_employee_id
FROM
  employees AS left_employee
  JOIN employees AS right_employee ON right_employee.department_id = left_employee.department_id
    AND left_employee.employee_id < right_employee.employee_id
  ORDER BY
    left_employee.department_id,
    left_employee.employee_id,
    right_employee.employee_id;
```

**Expected shape:** One row per unordered same-department pair.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 5, self-join the 100 `employees` rows on `department_id`; departments 1 to 4 hold 17 employees each and departments 5 and 6 hold 16 each. Return `department_id`, `first_employee_id`, and `second_employee_id` as the composite pair key.
- **Expected result/shape:** For sql-05 Exercise 5, return 784 rows, one row per unordered same-department pair: 136 for each 17-person department and 120 for each 16-person department, starting with the pair 1 and 7 in department 1. The final columns are `department_id`, `first_employee_id`, and `second_employee_id`. The final order is `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
- **Independent verification:** For sql-05 Exercise 5, confirm `first_employee_id < second_employee_id` on all 784 rows and that 4 * 136 + 2 * 120 equals 784. Joining on `department_id` alone returns 1,668 rows, which includes 100 self-pair rows and every mirror pair; replacing `<` with `<>` returns 1,568 rows, exactly twice 784.
- **What prints:** 784 rows, starting with department 1, employees 1 and 7. Departments 1 to 4 have 17 people each (136 pairs) and departments 5 and 6 have 16 (120 pairs): 4 times 136 plus 2 times 120.
- **Seeing the bug:** with only the department condition you get 1,668 rows, which includes 100 self-pairs and every pair twice. Switching to `<>` removes the self-pairs and leaves 1,568, still double.
- **Proof query:** `SELECT department_id, COUNT(*) FROM (your query) GROUP BY 1` should show 136 or 120 for each department.
- **Edge case:** a new hire in department 5 adds 16 rows, one pair with each existing colleague.

## Exercise 6: Extension

**Prompt:** Show each employee, their manager, and their manager's manager.

**Reasoning:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.

**Clause-by-clause reading:**

- `employees AS e`: the person.
- `LEFT JOIN employees AS manager ON manager.employee_id = e.manager_id`: one level up.
- `LEFT JOIN employees AS grandmanager ON grandmanager.employee_id = manager.manager_id`: two levels up, joined from the manager alias rather than from `e`.
- `ORDER BY e.employee_id`.

```sql
SELECT
  e.employee_id,
  e.full_name AS employee_name,
  manager.full_name AS manager_name,
  grandmanager.full_name AS grandmanager_name
FROM
  employees AS e
  LEFT JOIN employees AS manager ON manager.employee_id = e.manager_id
  LEFT JOIN employees AS grandmanager ON grandmanager.employee_id = manager.manager_id
ORDER BY
  e.employee_id;
```

**Expected shape:** One row per employee with up to two ancestor columns.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 6, join `employees` to itself twice with `LEFT JOIN`, first for the manager and then for the manager's manager; only employee 8's 92 reports have a two-level chain.
- **Expected result/shape:** For sql-05 Exercise 6, return 100 rows, one per employee: 94 show a `manager_name`, and 92 show `grandmanager_name` Employee 1, because they report to Employee 8, who reports to Employee 1. The final columns are `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`. The final order is `e.employee_id`.
- **Independent verification:** For sql-05 Exercise 6, confirm 100 rows, 94 non-`NULL` `manager_name` values, and 92 non-`NULL` `grandmanager_name` values. Employee 7 must show Employee 2 with no grandmanager, and making either join an inner join must cut the result to 94 or 92 rows.
- **What prints:** 100 rows. Employees 9 to 100 show manager Employee 8 and grandmanager Employee 1. Employees 7 and 8 have a manager but no grandmanager, because their managers (2 and 1) sit at the top. Employees 1 to 6 have neither.
- **Counting the levels:** 94 rows have a manager and 92 have a grandmanager.
- **Inner joins instead:** the result shrinks to those 92 rows, hiding the top two levels of the hierarchy.
- **Wrong anchor:** joining `grandmanager` on `e.manager_id` repeats the manager in both columns. Each step must start from the alias one level below.

## Final self-check

- Why does Example 1 include Brazil even though no Brazilian customer has ordered?
- What row count does Exercise 5 give with `<`, with `<>`, and with neither?
- Why does `NOT IN (SELECT manager_id FROM employees)` return nothing?
- Which alias must the grandmanager join start from, and why?
- How would Exercise 3's months change if you ran it next month?
