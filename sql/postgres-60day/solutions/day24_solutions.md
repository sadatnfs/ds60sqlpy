# Day 24 solutions: Recursive CTEs: Hierarchies, Trees, and Graph Walks


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The companion script reads `employees` and literal `VALUES` lists only, with
`search_path` set to `training` and a `BEGIN`/`ROLLBACK` pair around it.
Every recursive query in it carries a guard, so it should finish in well under
a second. The general method is in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day24_solutions.sql
```

## How these answers fit together

Three answers walk the same 100-employee hierarchy in different directions.
The first goes down from every manager, the fifth goes up from every
employee, and the sixth goes down from the roots and then counts by depth.
Exercises 2 and 3 recurse over a counter instead of a table, and Exercise 4
uses a four-edge graph with a loop to prove the path guard works. Check row
counts per depth before comparing columns: the hierarchy has 6 roots, 2
middle managers and 92 employees under employee 8. The learner file is
[day24_recursive_ctes.sql](../day24_recursive_ctes.sql).

## Reading contract

- **Focus:** Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
- **Assumptions:** Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
- **Primary pitfall:** `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** List every manager's direct and indirect reports with depth and path.

**Reasoning:** Seed every direct edge, carry the original manager, and reject IDs already in the path.

```sql
WITH RECURSIVE reports AS (
  SELECT
    manager.employee_id AS manager_id,
    report.employee_id AS report_id,
    1 AS depth,
    ARRAY[manager.employee_id,
    report.employee_id] AS path
  FROM
    employees AS manager
    JOIN employees AS report ON report.manager_id = manager.employee_id
UNION ALL
SELECT
  r.manager_id,
  report.employee_id,
  r.depth + 1,
  r.path || report.employee_id
FROM
  reports AS r
  JOIN employees AS report ON report.manager_id = r.report_id
  WHERE
    NOT report.employee_id = ANY (r.path))
SELECT
  manager_id,
  report_id,
  depth,
  path
FROM
  reports
ORDER BY
  manager_id,
  depth,
  report_id;
```

**Expected shape:** One row per ancestor-descendant pair.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 1, read `employees` twice in the anchor, joining each report to its manager on `report.manager_id = manager.employee_id` (94 direct pairs), then join the recursive `reports` CTE back to `employees` on `report.manager_id = r.report_id`, appending to `path` and refusing any `employee_id` already in it.
- **Expected result/shape:** For sql-24 Exercise 1, expected output: 186 rows, 94 at depth 1 and 92 at depth 2, for only three managers: employee 1 with 93 reports, employee 8 with 92, and employee 2 with 1. The final columns are `manager_id`, `report_id`, `depth`, and `path`. The final order is `manager_id, depth, report_id`.
- **Independent verification:** For sql-24 Exercise 1, confirm the 94 depth-1 rows match `SELECT COUNT(*) FROM employees WHERE manager_id IS NOT NULL` and that all 92 depth-2 rows belong to manager 1 with a `path` starting `{1,8}`; then, inside `BEGIN ... ROLLBACK`, run `UPDATE employees SET manager_id = 9 WHERE employee_id = 1` to close the loop 1, 8, 9, 1 and confirm the query still finishes, now with 280 rows and a maximum depth of 3.
- **Intermediate relation check:** The anchor joins each manager to each direct report, giving 94 edges: 1 to 8, 2 to 7 and 8 to each of employees 9 to 100. The recursive member adds 92 more rows, linking manager 1 to those 92 people at depth 2, for 186 rows in total.
- **Clause check:** The recursive member keeps `r.manager_id` from the anchor and advances only `report_id`, which is what makes the result an ancestor-descendant pair table rather than a list of edges. The path starts with both ids, such as `{1,8}`, and grows to `{1,8,9}`.
- **Alternative/trade-off:** Anchoring on employees instead of edges and carrying a root column gives only root-to-descendant pairs. Seeding every edge, as here, also lists employee 8 as a manager of the 92 below it, which is what "every manager" requires.
- **Edge case:** Manager 1 appears with one depth-1 report and 92 depth-2 reports; manager 2 has only employee 7. Employees with no reports, such as 9 to 100, never appear in `manager_id`.

## Exercise 2: Query writing

**Prompt:** Generate integers 1 through 100 recursively and return their sum.

**Reasoning:** Anchor at 1 and stop producing rows after 100.

```sql
WITH RECURSIVE numbers (
  n
) AS (
  VALUES (1)
  UNION ALL
  SELECT
    n + 1
  FROM
    numbers
  WHERE
    n < 100
)
SELECT
  SUM(n) AS sum_1_to_100
FROM
  numbers;
```

**Expected shape:** Exactly one row with 5050.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 2, no table is read: the recursive `numbers` CTE starts from `VALUES (1)` and adds `n + 1` while `n < 100`, and the outer query applies one `SUM` with no `GROUP BY`.
- **Expected result/shape:** For sql-24 Exercise 2, expected output: exactly one row, `sum_1_to_100` = 5050. The final columns are `sum_1_to_100`.
- **Independent verification:** For sql-24 Exercise 2, compare with the non-recursive control `SELECT SUM(n) FROM generate_series(1, 100) AS n`, which also returns 5050, and add `COUNT(*)` to see exactly 100 generated rows; then change the stop test to `n <= 100` and confirm the CTE produces 101 rows and a sum of 5151, the classic off-by-one in a recursive stop condition.
- **Intermediate relation check:** `numbers` has 100 rows, from 1 to 100. The anchor contributes the 1 and each round adds one more integer until `n < 100` fails on the row holding 100.
- **Clause check:** The column list `numbers (n)` names the output column once, so `VALUES (1)` needs no alias. The outer `SUM(n)` returns one row with 5050, which matches 100 times 101 divided by 2.
- **Alternative/trade-off:** `SELECT SUM(n) FROM generate_series(1, 100) AS n` gives the same 5050 without recursion and is the normal choice in PostgreSQL. The recursive form is here to show anchor, step and stop on the simplest possible data.
- **Edge case:** Changing the stop to `n <= 100` produces 101 rows and a sum of 5151, because the test runs on the previous row before the next one is added.

## Exercise 3: Query writing

**Prompt:** Generate the first day of the current and prior 11 months recursively.

**Reasoning:** Carry a counter as an explicit termination condition.

```sql
WITH RECURSIVE months (
  month_start,
  step
) AS (
  SELECT
    date_trunc('month', CURRENT_DATE)::date,
    1
  UNION ALL
  SELECT
    (month_start - INTERVAL '1 month')::date,
    step + 1
  FROM
    months
  WHERE
    step < 12
)
SELECT
  month_start
FROM
  months
ORDER BY
  month_start;
```

**Expected shape:** Exactly 12 chronological month rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 3, no table is read: the recursive `months` CTE starts at `date_trunc('month', CURRENT_DATE)::date` with `step` 1 and subtracts `INTERVAL '1 month'` while `step < 12`, so the result moves with the run date.
- **Expected result/shape:** For sql-24 Exercise 3, expected output: exactly 12 rows, all on day 1 of a month, from 11 months before the current month up to the current month (2025-12-01 through 2026-11-01 when run in November 2026). The final columns are `month_start`. The final order is `month_start`.
- **Independent verification:** For sql-24 Exercise 3, confirm `COUNT(*)` is 12, `COUNT(DISTINCT month_start)` is 12, `MAX(month_start)` equals `date_trunc('month', CURRENT_DATE)::date`, and no row fails `EXTRACT(DAY FROM month_start) = 1`; then start the same recursion from `DATE '2026-03-31'` without `date_trunc` and see the values drift to 2026-02-28 and 2026-01-28, which is why the anchor truncates first.
- **Intermediate relation check:** `months` has 12 rows, with `step` running from 1 for the current month to 12 for the month eleven months earlier.
- **Clause check:** `date_trunc('month', CURRENT_DATE)::date` gives the first day of this month as a `date`. Each round subtracts `INTERVAL '1 month'` and casts back to `date`, so the column keeps one type across both members. The outer query returns only `month_start`, sorted oldest first.
- **Alternative/trade-off:** `generate_series(date_trunc('month', CURRENT_DATE) - INTERVAL '11 months', date_trunc('month', CURRENT_DATE), INTERVAL '1 month')` returns the same 12 instants as `timestamptz` values in one call. Cast them to `date` if you need the same output type.
- **Edge case:** Without the `::date` cast in the recursive member, PostgreSQL stops with `recursive query "months" column 1 has type date in non-recursive term but type timestamp without time zone overall`. The result changes from day to day, so compare the count and spacing rather than the exact dates.

## Exercise 4: Prediction

**Prompt:** Traverse a local graph containing a cycle and prove a path-array guard terminates.

**Reasoning:** Reject a destination already present in the path before adding it.

```sql
WITH RECURSIVE edges (
  source,
  destination
) AS (
  VALUES (1, 2),
    (2, 3),
    (3, 1),
    (2, 4)
),
walk (
  node, path
) AS (
  VALUES (1, ARRAY[1])
  UNION ALL
  SELECT
    e.destination, w.path || e.destination
  FROM
    walk AS w
    JOIN edges AS e ON e.source = w.node
  WHERE
    NOT e.destination = ANY (w.path))
SELECT
  node,
  path
FROM
  walk
ORDER BY
  array_length(path, 1),
  path;
```

**Expected shape:** Finite paths starting from node 1; no repeated node inside a path.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 4, no table is read: the `edges` CTE holds four `VALUES` pairs, (1, 2), (2, 3), (3, 1), and (2, 4), with the cycle 1, 2, 3, 1; the recursive `walk` CTE starts at `VALUES (1, ARRAY[1])` and follows edges while `NOT e.destination = ANY (w.path)`.
- **Expected result/shape:** For sql-24 Exercise 4, expected output: exactly 4 rows, `{1}`, `{1,2}`, `{1,2,3}`, and `{1,2,4}`, with nodes 1, 2, 3, and 4; the edge from 3 back to 1 is never taken. The final columns are `node`, and `path`. The final order is `array_length(path, 1), path`.
- **Independent verification:** For sql-24 Exercise 4, confirm no `path` repeats a node, for example `SELECT COUNT(*) FROM walk WHERE array_length(path, 1) <> (SELECT COUNT(DISTINCT x) FROM unnest(path) AS x)` returns 0; then replace the path guard with a depth cap `array_length(w.path, 1) < 5` and confirm two extra rows, `{1,2,3,1}` and `{1,2,3,1,2}`, revisit node 1, so only the `ANY (path)` guard makes the walk end on its own.
- **Intermediate relation check:** `edges` has four rows: 1 to 2, 2 to 3, 3 to 1 and 2 to 4. `walk` has four rows: `{1}`, `{1,2}`, `{1,2,3}` and `{1,2,4}`.
- **Clause check:** From node 3 the only edge leads back to 1, which is already in `{1,2,3}`, so the guard rejects it and node 3 has no successor. Node 4 has no outgoing edge at all. The next round therefore adds nothing and the walk ends.
- **Alternative/trade-off:** PostgreSQL 14 added `CYCLE node SET is_cycle USING route`, which tracks the path for you. It keeps the row that closes the loop and marks it `is_cycle = true`, so that version returns five rows, ending with `{(1),(2),(3),(1)}`.
- **Edge case:** Delete the guard and the walk keeps going: with `LIMIT 8` on the outer query you see `{1,2,3,1}`, `{1,2,3,1,2}` and longer paths, and without a limit the statement never finishes.

## Exercise 5: Debugging

**Prompt:** Walk upward from every employee to ancestors while preventing cycles.

**Reasoning:** The recursive step follows current manager ID to the manager row and appends it to path.

```sql
WITH RECURSIVE ancestors AS (
  SELECT
    e.employee_id AS origin_employee_id,
    e.manager_id AS ancestor_id,
    1 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees AS e
  WHERE
    e.manager_id IS NOT NULL
  UNION ALL
  SELECT
    a.origin_employee_id,
    manager.manager_id,
    a.depth + 1,
    a.path || manager.employee_id
  FROM
    ancestors AS a
    JOIN employees AS manager ON manager.employee_id = a.ancestor_id
  WHERE
    manager.manager_id IS NOT NULL
    AND NOT manager.employee_id = ANY (a.path))
SELECT
  origin_employee_id,
  ancestor_id,
  depth
FROM
  ancestors
WHERE
  ancestor_id IS NOT NULL
ORDER BY
  origin_employee_id,
  depth;
```

**Expected shape:** One row per employee-ancestor relation.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 5, read `employees`: the anchor takes the 94 rows with a non-NULL `manager_id`, and the recursive `ancestors` CTE joins `employees` as `manager` on `manager.employee_id = a.ancestor_id`, climbing while `manager.manager_id IS NOT NULL` and the manager is not already in `path`.
- **Expected result/shape:** For sql-24 Exercise 5, expected output: 186 rows for 94 origin employees, 94 at depth 1 and 92 at depth 2; employee 9 has ancestor 8 at depth 1 and ancestor 1 at depth 2, while employee 8 has only ancestor 1. The final columns are `origin_employee_id`, `ancestor_id`, and `depth`. The final order is `origin_employee_id, depth`.
- **Independent verification:** For sql-24 Exercise 5, confirm `COUNT(DISTINCT origin_employee_id)` is 94, matching `SELECT COUNT(*) FROM employees WHERE manager_id IS NOT NULL`, and that removing the outer `ancestor_id IS NOT NULL` filter leaves 186 rows; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm the query returns 374 rows with a maximum depth of 4, and that employee 1 now lists ancestors 9, 8, and itself at depths 1, 2, and 3.
- **Intermediate relation check:** The anchor gives 94 rows, one per employee who has a manager, each at depth 1. The recursive member adds 92 depth-2 rows for employees 9 to 100, whose manager 8 reports to 1, giving 186 rows.
- **Clause check:** Each round looks up the current ancestor's own row and moves to that person's `manager_id`. Employee 9 therefore yields `(9, 8, 1)` and `(9, 1, 2)`, and stops because employee 1 has no manager.
- **Alternative/trade-off:** Reversing Exercise 1's result (`report_id` as origin, `manager_id` as ancestor) produces the same 186 pairs. Walking upward is cheaper when you only need the chain for a few employees, because the anchor can filter to them first.
- **Edge case:** Without `manager.manager_id IS NOT NULL` in the recursive member, the recursion also emits 94 rows whose ancestor is `NULL`, 280 in total, and only the outer `WHERE ancestor_id IS NOT NULL` brings it back to 186.

## Exercise 6: Extension

**Prompt:** Summarize employee count by hierarchy depth from all roots.

**Reasoning:** Build the guarded root traversal first, then aggregate only after depth is assigned.

```sql
WITH RECURSIVE organization AS (
  SELECT
    e.employee_id,
    e.manager_id,
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
    parent.depth + 1,
    parent.path || child.employee_id
  FROM
    organization AS parent
    JOIN employees AS child ON child.manager_id = parent.employee_id
  WHERE
    NOT child.employee_id = ANY (parent.path))
SELECT
  depth,
  COUNT(*) AS employee_count
FROM
  organization
GROUP BY
  depth
ORDER BY
  depth;
```

**Expected shape:** One row per observed depth.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 6, read `employees`: the anchor of the recursive `organization` CTE takes the 6 roots with `manager_id IS NULL` at depth 0, the recursive step joins children on `child.manager_id = parent.employee_id`, and the outer query counts rows per `depth`.
- **Expected result/shape:** For sql-24 Exercise 6, expected output: exactly 3 rows, depth 0 with 6 employees, depth 1 with 2, and depth 2 with 92. The final columns are `depth`, and `employee_count`. The final order is `depth`.
- **Independent verification:** For sql-24 Exercise 6, confirm the counts add to 100, matching `SELECT COUNT(*) FROM employees`, and that the depth-1 count of 2 matches `SELECT COUNT(*) FROM employees WHERE manager_id IN (SELECT employee_id FROM employees WHERE manager_id IS NULL)`; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm only 6 employees remain (5 at depth 0, 1 at depth 1), because the 94 people in the loop through employee 1 no longer hang from any root.
- **Intermediate relation check:** `organization` holds all 100 employees exactly once, because each has one manager and the hierarchy has no cycles.
- **Clause check:** This answer starts the roots at depth 0, unlike Example 1, so the result is three rows: depth 0 with 6 employees, depth 1 with 2 and depth 2 with 92. The `GROUP BY depth` runs only after recursion has finished.
- **Alternative/trade-off:** Counting `array_length(path, 1) - 1` instead of carrying `depth` gives the same three groups, since each path has one entry per level. Carrying `depth` explicitly is easier to read.
- **Edge case:** The three counts must add up to 100. An employee whose manager id points to nobody would be missing from every depth, and the total would drop below 100.

## Final self-check

- What does each round of your recursive member read, and what makes a round
  return nothing?
- Which guard stops Exercise 4, and what would `UNION` without a path do
  instead?
- How many rows does each depth of the org chart hold, and do your answers
  agree with 6, 2 and 92?
- Where did you need a cast so the anchor and recursive member agree on type?
