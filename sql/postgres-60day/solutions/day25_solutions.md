# Day 25 solutions: Multiple CTEs and Hierarchies in One Query


<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers read `employees` and `departments` only, inside
`BEGIN`/`ROLLBACK` with `search_path` set to `training`, so running the file
changes nothing. Run each CTE as its own `SELECT` first and compare its row
count with the notes below; the method is described in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day25_solutions.sql
```

## How these answers fit together

The hierarchy has 100 employees, 6 roots, 3 managers (employees 1, 2 and 8)
and 97 leaves. The answers ask for different grains over it: one row per depth,
per direct team, per root or leaf label, a single reachability check, one row
per manager's full subtree and one per department. Keep the company payroll of
4,399,909.50 in mind, since any per-employee breakdown should add back to it.
The learner file is
[day25_multiple_ctes_hierarchies.sql](../day25_multiple_ctes_hierarchies.sql).

## Reading contract

- **Focus:** Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.
- **Assumptions:** The employee graph can have multiple roots. Payroll uses exact salary numeric and each employee should contribute once per intended output grain.
- **Primary pitfall:** Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Build a root-based organization CTE and report headcount and payroll by depth.

**Reasoning:** Assign depth during recursion, then aggregate employee rows once.

```sql
WITH RECURSIVE organization AS (
  SELECT
    e.employee_id,
    e.manager_id,
    e.salary,
    0 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees AS e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    child.employee_id,
    child.manager_id,
    child.salary,
    parent.depth + 1,
    parent.path || child.employee_id
  FROM
    organization AS parent
    JOIN employees AS child ON child.manager_id = parent.employee_id
  WHERE
    NOT child.employee_id = ANY (parent.path))
SELECT
  depth,
  COUNT(*) AS headcount,
  ROUND(SUM(salary), 2) AS payroll
FROM
  organization
GROUP BY
  depth
ORDER BY
  depth;
```

**Expected shape:** One row per hierarchy depth.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 1, read `employees`: the recursive `organization` CTE starts at the 6 roots with `manager_id IS NULL`, carries each child's `salary` and `depth`, and guards against cycles with `path`; the outer query groups that CTE by `depth`.
- **Expected result/shape:** For sql-25 Exercise 1, expected output: exactly 3 rows, depth 0 with 6 people and 241662.99 payroll, depth 1 with 2 and 81187.85, and depth 2 with 92 and 4077058.66. The final columns are `depth`, `headcount`, and `payroll`. The final order is `depth`.
- **Independent verification:** For sql-25 Exercise 1, confirm the headcounts add to 100 and the payrolls to 4399909.50, matching `SELECT COUNT(*), ROUND(SUM(salary), 2) FROM employees`, and that the depth-1 payroll equals the two single-report payrolls in Exercise 2 (40633.52 + 40554.33); then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm only 5 people remain at depth 0 and 1 at depth 1.
- **Intermediate relation check:** `organization` returns 100 rows, one per employee, with `depth` 0 for the 6 roots, 1 for employees 7 and 8, and 2 for the 92 people under employee 8.
- **Clause check:** Grouping by `depth` gives three rows: 6 people with payroll 241,662.99, 2 with 81,187.85 and 92 with 4,077,058.66. Rounding happens once, after `SUM`, so the three payrolls add up to exactly 4,399,909.50.
- **Alternative/trade-off:** Carrying `salary` through the recursion avoids a second join to `employees` after the walk. Joining back by `employee_id` instead is also correct here, because the CTE holds each employee once.
- **Edge case:** Roots start at depth 0 in this answer, while the lesson's Example 1 starts them at 1. Both are fine as long as you say which you used; the headcounts per level do not change.

## Exercise 2: Query writing

**Prompt:** Report each manager's direct-report count and payroll.

**Reasoning:** Direct-team grain needs one self join, not full recursive descendants.

```sql
WITH direct_teams AS (
  SELECT
    e.manager_id,
    COUNT(*) AS direct_reports,
    SUM(e.salary) AS direct_report_payroll
  FROM
    employees AS e
  WHERE
    e.manager_id IS NOT NULL
  GROUP BY
    e.manager_id
)
SELECT
  manager.employee_id,
  manager.full_name,
  dt.direct_reports,
  ROUND(dt.direct_report_payroll, 2) AS direct_report_payroll
FROM
  direct_teams AS dt
  JOIN employees AS manager ON manager.employee_id = dt.manager_id
ORDER BY
  dt.direct_reports DESC,
  manager.employee_id;
```

**Expected shape:** One row per manager with at least one direct report.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 2, read `employees` once in `direct_teams`, grouping the 94 rows with a non-NULL `manager_id` by that `manager_id`, then join the CTE back to `employees` as `manager` to fetch `full_name`.
- **Expected result/shape:** For sql-25 Exercise 2, expected output: exactly 3 rows, employee 8 with 92 direct reports and 4077058.66 of payroll, then employees 1 and 2 with 1 report each (40633.52 and 40554.33). The final columns are `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`. The final order is `dt.direct_reports DESC, manager.employee_id`.
- **Independent verification:** For sql-25 Exercise 2, confirm the `direct_reports` values add to 94 and the payrolls to 4158246.51, matching `SELECT COUNT(*), ROUND(SUM(salary), 2) FROM employees WHERE manager_id IS NOT NULL`, and that `SELECT COUNT(DISTINCT manager_id) FROM employees` also returns 3; employees 1 and 2 tie at one report, so only the `manager.employee_id` tiebreaker keeps employee 1 ahead.
- **Intermediate relation check:** `direct_teams` groups the 94 employees who have a manager and returns 3 rows: manager 8 with 92 reports, and managers 1 and 2 with one each.
- **Clause check:** Joining `direct_teams` back to `employees` by `manager.employee_id = dt.manager_id` adds the manager's name without changing the row count. Employee 8's direct payroll of 4,077,058.66 is the same as the depth-2 payroll from the first answer, because those are the same 92 people.
- **Alternative/trade-off:** Grouping a self join directly, `employees AS manager JOIN employees AS report`, gives the same three rows. The CTE keeps the aggregate separate from the name lookup, which makes each step easy to check on its own.
- **Edge case:** Employees with no reports never appear, because the inner join drops them. Use a left join and `COALESCE(dt.direct_reports, 0)` if the report must list every employee.

## Exercise 3: Query writing

**Prompt:** Identify hierarchy roots and leaves in one report.

**Reasoning:** Create root and leaf CTEs at employee grain, then union compatible labeled rows.

```sql
WITH roots AS (
  SELECT
    e.employee_id,
    e.full_name
  FROM
    employees AS e
  WHERE
    e.manager_id IS NULL
),
leaves AS (
  SELECT
    e.employee_id,
    e.full_name
  FROM
    employees AS e
  WHERE
    NOT EXISTS (
      SELECT
        1
      FROM
        employees AS child
      WHERE
        child.manager_id = e.employee_id))
SELECT
  'root' AS node_type,
  employee_id,
  full_name
FROM
  roots
UNION ALL
SELECT
  'leaf' AS node_type,
  employee_id,
  full_name
FROM
  leaves
ORDER BY
  node_type,
  employee_id;
```

**Expected shape:** One labeled row per root or leaf employee.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 3, read `employees` in two CTEs: `roots` keeps the 6 rows with `manager_id IS NULL`, and `leaves` keeps rows for which `NOT EXISTS` finds no child pointing at them; the outer query labels each CTE and stacks them with `UNION ALL`.
- **Expected result/shape:** For sql-25 Exercise 3, expected output: 103 rows, 97 `leaf` rows followed by 6 `root` rows (employees 1 through 6); employees 3, 4, 5, and 6 appear twice because they have no manager and no reports. The final columns are `node_type`, `employee_id`, and `full_name`. The final order is `node_type, employee_id`.
- **Independent verification:** For sql-25 Exercise 3, count rows by `node_type` and confirm 97 and 6, and that `SELECT employee_id FROM employees e WHERE manager_id IS NULL AND NOT EXISTS (SELECT 1 FROM employees c WHERE c.manager_id = e.employee_id)` returns exactly 3, 4, 5, and 6; then rewrite the leaf test as `employee_id NOT IN (SELECT manager_id FROM employees)` and confirm it returns 0 leaves, because the 6 NULL `manager_id` values make every `NOT IN` test unknown.
- **Intermediate relation check:** `roots` has 6 rows and `leaves` has 97. Employees 3, 4, 5 and 6 are in both, because they have no manager and nobody reports to them.
- **Clause check:** `UNION ALL` keeps all 103 labeled rows, so those four employees appear once as `leaf` and once as `root`. Sorting by `node_type` puts the 97 `leaf` rows before the 6 `root` rows, because the labels sort alphabetically.
- **Alternative/trade-off:** `NOT EXISTS` is the safe way to find leaves. Writing `employee_id NOT IN (SELECT manager_id FROM employees)` returns no rows, because that list contains `NULL` for every root, and a comparison with `NULL` is never true.
- **Edge case:** The independent check asks for unique `employee_id`, which fails for those four employees. The pair (`node_type`, `employee_id`) is unique, and that is the real key of this result.

## Exercise 4: Prediction

**Prompt:** Count employees reachable from roots and compare with total employees.

**Reasoning:** A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.

```sql
WITH RECURSIVE organization AS (
  SELECT
    e.employee_id,
    ARRAY[e.employee_id] AS path
  FROM
    employees AS e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    child.employee_id,
    parent.path || child.employee_id
  FROM
    organization AS parent
    JOIN employees AS child ON child.manager_id = parent.employee_id
  WHERE
    NOT child.employee_id = ANY (parent.path))
SELECT
  (
    SELECT
      COUNT(*)
    FROM
      employees) AS all_employees,
  COUNT(DISTINCT employee_id) AS reachable_employees,
  (
    SELECT
      COUNT(*)
    FROM
      employees) - COUNT(DISTINCT employee_id) AS unreachable_employees
FROM
  organization;
```

**Expected shape:** One row with zero unreachable employees.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 4, read `employees` twice: the recursive `organization` CTE walks down from the 6 roots with a `path` guard, and two scalar subqueries count the full table; the outer query compares `COUNT(DISTINCT employee_id)` from the CTE with that total and has no `GROUP BY`.
- **Expected result/shape:** For sql-25 Exercise 4, expected output: exactly one row, 100 `all_employees`, 100 `reachable_employees`, and 0 `unreachable_employees`. The final columns are `all_employees`, `reachable_employees`, and `unreachable_employees`.
- **Independent verification:** For sql-25 Exercise 4, confirm the CTE returns 100 rows and 100 distinct `employee_id` values, so no employee is reached twice; then, inside `BEGIN ... ROLLBACK`, run `UPDATE employees SET manager_id = 9 WHERE employee_id = 1` and confirm the row changes to 100, 6, and 94, because employee 1, employee 8, and the 92 reports under 8 form a loop with no root.
- **Intermediate relation check:** `organization` returns exactly 100 rows with 100 distinct ids, which means the walk reached every employee and none twice.
- **Clause check:** The two scalar subqueries count `employees` again, independently of the walk, so the result is one row: 100, 100 and 0. Because there is no `GROUP BY`, `COUNT(DISTINCT employee_id)` runs over the whole CTE.
- **Alternative/trade-off:** An anti-join, `employees LEFT JOIN organization ... WHERE organization.employee_id IS NULL`, would list the unreachable people by id. That is more useful when the count is not 0.
- **Edge case:** An employee whose `manager_id` points at a missing id, or two employees who manage each other, would never be reached from a root. The count would then show 99 or 98 reachable and a nonzero gap.

## Exercise 5: Debugging

**Prompt:** Calculate full-subtree report counts per manager without counting the manager as their own report.

**Reasoning:** Seed direct edges and recurse descendants while carrying the original manager.

```sql
WITH RECURSIVE descendants AS (
  SELECT
    parent.employee_id AS manager_id,
    child.employee_id AS report_id,
    ARRAY[parent.employee_id,
    child.employee_id] AS path
  FROM
    employees AS parent
    JOIN employees AS child ON child.manager_id = parent.employee_id
UNION ALL
SELECT
  d.manager_id,
  child.employee_id,
  d.path || child.employee_id
FROM
  descendants AS d
  JOIN employees AS child ON child.manager_id = d.report_id
  WHERE
    NOT child.employee_id = ANY (d.path))
SELECT
  manager_id,
  COUNT(DISTINCT report_id) AS all_descendant_reports
FROM
  descendants
GROUP BY
  manager_id
ORDER BY
  all_descendant_reports DESC,
  manager_id;
```

**Expected shape:** One row per manager with descendant count.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 5, read `employees` twice in the anchor of the recursive `descendants` CTE (each manager joined to direct children, with `path` seeded as `ARRAY[parent, child]`), then keep joining children of `report_id`; the outer query groups by `manager_id`.
- **Expected result/shape:** For sql-25 Exercise 5, expected output: exactly 3 rows, manager 1 with 93 descendants, manager 8 with 92, and manager 2 with 1. The final columns are `manager_id`, and `all_descendant_reports`. The final order is `all_descendant_reports DESC, manager_id`.
- **Independent verification:** For sql-25 Exercise 5, confirm manager 8's 92 matches `SELECT COUNT(*) FROM employees WHERE manager_id = 8`, manager 1's 93 is that 92 plus employee 8 itself, `COUNT(*)` equals `COUNT(DISTINCT report_id)` for each manager, and no row has `report_id = manager_id`; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm managers 1, 8, and 9 each return 93 and still never count themselves.
- **Intermediate relation check:** `descendants` starts from the 94 manager-report edges and adds the 92 pairs that link manager 1 to the people under employee 8, giving 186 pairs.
- **Clause check:** Grouping by the carried `manager_id` gives three rows: manager 1 with 93 reports, manager 8 with 92 and manager 2 with 1. The anchor never pairs a manager with themselves, which is why nobody is counted as their own report.
- **Alternative/trade-off:** `COUNT(DISTINCT report_id)` equals `COUNT(*)` here, because each employee has one manager and can be reached by only one path. The `DISTINCT` is a safety net if the data ever allowed two paths to the same person.
- **Edge case:** Summing salaries over these pairs counts employees 9 to 100 twice, giving 8,235,305.17 across all subtrees. Report subtree payrolls per manager only, never added together.

## Exercise 6: Extension

**Prompt:** Report department headcount split between managers and nonmanagers.

**Reasoning:** First derive the manager ID set, then conditionally aggregate employees once.

```sql
WITH managers AS (
  SELECT DISTINCT
    e.manager_id AS employee_id
  FROM
    employees AS e
  WHERE
    e.manager_id IS NOT NULL
)
SELECT
  d.department_id,
  d.name,
  COUNT(e.employee_id) AS headcount,
  COUNT(e.employee_id) FILTER (WHERE m.employee_id IS NOT NULL) AS managers,
  COUNT(e.employee_id) FILTER (WHERE m.employee_id IS NULL) AS nonmanagers
FROM
  departments AS d
  LEFT JOIN employees AS e ON e.department_id = d.department_id
  LEFT JOIN managers AS m ON m.employee_id = e.employee_id
GROUP BY
  d.department_id,
  d.name
ORDER BY
  d.department_id;
```

**Expected shape:** One row per department.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 6, read all 6 `departments`, `LEFT JOIN` their 100 `employees`, and `LEFT JOIN` the `managers` CTE, which holds the 3 distinct non-NULL `manager_id` values; the `FILTER` clauses split each department's count on whether that join found a match.
- **Expected result/shape:** For sql-25 Exercise 6, expected output: exactly 6 rows; Sales has 17 people (1 manager), Engineering 17 (2 managers), HR and Finance 17 each, and Marketing and Operations 16 each, all with 0 managers. The final columns are `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`. The final order is `d.department_id`.
- **Independent verification:** For sql-25 Exercise 6, confirm `headcount` adds to 100, `managers` adds to 3, and `managers + nonmanagers = headcount` on every row; then, inside `BEGIN ... ROLLBACK`, run `INSERT INTO departments (department_id, name) VALUES (7, 'Legal')` and confirm a seventh row with 0, 0, and 0, while `COUNT(*)` would wrongly report 1 for that empty department.
- **Intermediate relation check:** The `managers` CTE has 3 rows (employees 1, 2 and 8). Without `DISTINCT` it would keep all 94 `manager_id` values.
- **Clause check:** The two left joins keep every department and every employee. `FILTER (WHERE m.employee_id IS NOT NULL)` counts managers: 1 in Sales, 2 in Engineering and 0 elsewhere. Headcounts are 17, 17, 17, 17, 16 and 16, and each row's two parts add up to its headcount.
- **Alternative/trade-off:** `COUNT(e.employee_id) FILTER (WHERE EXISTS (SELECT 1 FROM employees r WHERE r.manager_id = e.employee_id))` avoids the extra join. The CTE version makes the manager set visible, so you can check it alone.
- **Edge case:** If `managers` loses its `DISTINCT`, employee 8 joins 92 times and Engineering's headcount becomes 108. `COUNT(e.employee_id)` rather than `COUNT(*)` keeps a department with no employees at 0.

## Final self-check

- Which of your CTEs are one row per employee, and does each still total
  100 people?
- Why do subtree payrolls add up to almost twice the company payroll?
- Which employees are both roots and leaves, and how many rows does that add?
- What does `NOT IN` return when the subquery contains `NULL`?
