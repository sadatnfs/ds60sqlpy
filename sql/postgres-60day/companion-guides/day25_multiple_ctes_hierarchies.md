# Day 25: Multiple CTEs and Hierarchies in One Query (Companion Guide)

## How to run this lesson

Open `./classroom`, pick **sql-25** under PostgreSQL and choose
**Whole SQL lesson (psql)**. The launcher runs your workspace copy,
`.learning/sql/sql-25/lesson/workspace/sql/postgres-60day/day25_multiple_ctes_hierarchies.sql`,
against `advanced_sql_training`. The file only reads `employees` and
`departments` inside `BEGIN`/`ROLLBACK`, and its second statement is an
`EXPLAIN` of the first, so the transcript ends with a plan tree instead of a
result grid. Launcher and transcript details are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

The notebook is handy for running each CTE on its own before chaining them
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-25
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 24; recursive CTEs](day24_recursive_ctes.md)
- **Artifacts:** [learner SQL](../day25_multiple_ctes_hierarchies.sql) ·
  [solution reasoning](../solutions/day25_solutions.md) ·
  [executable solution](../solutions/day25_solutions.sql)

## A beginner's mental model for this lesson

One `WITH` clause can hold several CTEs separated by commas. Each one is a
named stage, and a later stage can read any earlier one. Writing
`WITH RECURSIVE` once at the top allows any of them to be recursive; the
others behave like ordinary CTEs.

Example 1 has two stages over the same org chart used in sql-24:

- `base_org` walks the hierarchy from the six roots and yields 100 employee
  rows, each with `department_id`, `salary` and `depth`.
- `dept_counts` groups those 100 rows by department: Sales, Engineering, HR
  and Finance have 17 employees each, and Marketing and Operations have 16.
  Every department reaches depth 3, because the 92 people under employee 8
  are spread across all six departments.
- The final `SELECT` starts from `departments` and left joins the counts, so
  a department with no reachable employees would still appear with 0.

The main risk in this lesson is fanout. A full-subtree relation, which pairs
each manager with every descendant, lists employees 9 to 100 twice: once
under employee 8 and once under employee 1. Summing salaries over those
pairs gives 8,235,305.17, while the whole company's payroll is only
4,399,909.50. Decide first whether a measure belongs to a depth, a direct
team or a full subtree, and aggregate at that grain.

Example 2 shows how PostgreSQL treats the two stages differently. The
recursive `base_org` always appears as its own `CTE base_org` node, built by
a `Recursive Union` over a `WorkTable Scan`, and is read once through
`CTE Scan on base_org`. The plain `dept_counts` is folded into the main query
and shows up only as `Subquery Scan on dc` above a `HashAggregate`.

## Two worked SQL examples

### Example 1

```sql
WITH RECURSIVE base_org AS (
  SELECT
    e.employee_id,
    e.manager_id,
    e.department_id,
    e.salary,
    1 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    e.employee_id,
    e.manager_id,
    e.department_id,
    e.salary,
    b.depth + 1,
    b.path || e.employee_id
  FROM
    employees e
    JOIN base_org b ON e.manager_id = b.employee_id
  WHERE
    NOT e.employee_id = ANY (b.path)
),
dept_counts AS (
  -- Aggregate the traversed employee relation so the hierarchy CTE is an
  -- observable, testable stage rather than an unused declaration.
  SELECT
    department_id,
    COUNT(*) AS reachable_headcount,
    ROUND(AVG(salary), 2) AS avg_salary,
    MAX(depth) AS deepest_level
  FROM
    base_org
  GROUP BY
    department_id
)
SELECT
  d.department_id,
  d.name AS department,
  COALESCE(dc.reachable_headcount, 0) AS reachable_headcount,
  dc.avg_salary,
  dc.deepest_level
FROM
  departments d
  LEFT JOIN dept_counts dc ON dc.department_id = d.department_id
ORDER BY
  reachable_headcount DESC,
  d.department_id;
```

**How to read it:** Read the stages top to bottom. `base_org` carries
`department_id` and `salary` through recursion so nothing needs to be looked
up later. `dept_counts` collapses its 100 rows to one per department with a
count, an average rounded to cents and the deepest level. The outer query
puts `departments` on the left side of the join, and `COALESCE` turns a
missing count into 0 before the sort uses it.

**Expected result/shape:** Six rows, one per department. Sales,
Engineering, HR and Finance have 17 employees and come first in id order;
Marketing and Operations follow with 16. `deepest_level` is 3 on every row,
and `avg_salary` ranges from 43,880.31 for Sales to 44,117.88 for Finance.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH RECURSIVE base_org AS (
  SELECT
    e.employee_id,
    e.manager_id,
    e.department_id,
    e.salary,
    1 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    e.employee_id,
    e.manager_id,
    e.department_id,
    e.salary,
    b.depth + 1,
    b.path || e.employee_id
  FROM
    employees e
    JOIN base_org b ON e.manager_id = b.employee_id
  WHERE
    NOT e.employee_id = ANY (b.path)),
  dept_counts AS (
    -- Aggregate the traversed employee relation so the hierarchy CTE is an
    -- observable, testable stage rather than an unused declaration.
    SELECT
      department_id,
      COUNT(*) AS reachable_headcount,
      ROUND(AVG(salary), 2) AS avg_salary,
      MAX(depth) AS deepest_level
    FROM
      base_org
    GROUP BY
      department_id
)
  SELECT
    d.department_id,
    d.name AS department,
    COALESCE(dc.reachable_headcount, 0) AS reachable_headcount,
  dc.avg_salary,
  dc.deepest_level
FROM
  departments d
  LEFT JOIN dept_counts dc ON dc.department_id = d.department_id
ORDER BY
  reachable_headcount DESC,
  d.department_id;
```

**How to read it:** Read the plan from the innermost nodes out. The
`CTE base_org` block runs the anchor as `Seq Scan on employees e` with
`Filter: (manager_id IS NULL)`, then repeats a `Hash Join` against the
`WorkTable Scan`, applying the path guard as a `Join Filter`. The main branch
hashes the aggregated counts and left joins them to `departments`.

**Expected result/shape:** A plan of about 20 lines with `Sort` at
the top, keyed on `COALESCE(dc.reachable_headcount, '0'::bigint) DESC` and
`d.department_id`. There is a `CTE base_org` node, a `CTE Scan on base_org`
and no separate node named `dept_counts`. `COSTS OFF` removes the estimates,
so the text is the same on every run.

## Learning objectives

- Compose recursive and non-recursive stages without obscuring grain.
- Validate a complex query stage by stage.

## Vocabulary and concepts

- **CTE pipeline:** ordered named relations in which later stages consume
  earlier output.
- **Hierarchy enrichment:** joining traversal output to descriptive or
  aggregate data.
- **Stage invariant:** a property such as key uniqueness or row count checked
  before the next transformation.

## Worked example / walkthrough

Build the employee hierarchy separately and validate `(employee_id, depth)`.
Build department aggregates separately at one row per department. Join them
only after both grains are stable, so a department measure is not accidentally
re-aggregated across hierarchy paths.

## Practice assumptions and review method

- **Focus:** Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.
- **Assumptions:** The employee graph can have multiple roots. Payroll uses exact salary numeric and each employee should contribute once per intended output grain.
- **Failure to watch for:** Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.
- **Review loop:** run each CTE alone with `SELECT * FROM stage` and note
  its row count; the total headcount should stay 100 and the total payroll
  4,399,909.50 at every stage that is meant to be one row per employee.

## Exercises

Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.

Before running anything, decide which of the six answers needs
recursion: depth and full-subtree questions do, while direct teams, roots,
leaves and the manager split need only a self join or `EXISTS`. Write the
row count you expect for each, then check it.

1. **Query writing:** Build a root-based organization CTE and report headcount and payroll by depth.
   **Progressive hint:** Assign depth during recursion, then aggregate employee rows once.
   **Inputs/evidence:** For sql-25 Exercise 1, read `employees`: the recursive `organization` CTE starts at the 6 roots with `manager_id IS NULL`, carries each child's `salary` and `depth`, and guards against cycles with `path`; the outer query groups that CTE by `depth`.
   **Expected result/shape:** For sql-25 Exercise 1, expected output: exactly 3 rows, depth 0 with 6 people and 241662.99 payroll, depth 1 with 2 and 81187.85, and depth 2 with 92 and 4077058.66. The final columns are `depth`, `headcount`, and `payroll`. The final order is `depth`.
   **Verify:** For sql-25 Exercise 1, confirm the headcounts add to 100 and the payrolls to 4399909.50, matching `SELECT COUNT(*), ROUND(SUM(salary), 2) FROM employees`, and that the depth-1 payroll equals the two single-report payrolls in Exercise 2 (40633.52 + 40554.33); then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm only 5 people remain at depth 0 and 1 at depth 1.
2. **Query writing:** Report each manager's direct-report count and payroll.
   **Progressive hint:** Direct-team grain needs one self join, not full recursive descendants.
   **Inputs/evidence:** For sql-25 Exercise 2, read `employees` once in `direct_teams`, grouping the 94 rows with a non-NULL `manager_id` by that `manager_id`, then join the CTE back to `employees` as `manager` to fetch `full_name`.
   **Expected result/shape:** For sql-25 Exercise 2, expected output: exactly 3 rows, employee 8 with 92 direct reports and 4077058.66 of payroll, then employees 1 and 2 with 1 report each (40633.52 and 40554.33). The final columns are `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`. The final order is `dt.direct_reports DESC, manager.employee_id`.
   **Verify:** For sql-25 Exercise 2, confirm the `direct_reports` values add to 94 and the payrolls to 4158246.51, matching `SELECT COUNT(*), ROUND(SUM(salary), 2) FROM employees WHERE manager_id IS NOT NULL`, and that `SELECT COUNT(DISTINCT manager_id) FROM employees` also returns 3; employees 1 and 2 tie at one report, so only the `manager.employee_id` tiebreaker keeps employee 1 ahead.
3. **Query writing:** Identify hierarchy roots and leaves in one report.
   **Progressive hint:** Create root and leaf CTEs at employee grain, then union compatible labeled rows.
   **Inputs/evidence:** For sql-25 Exercise 3, read `employees` in two CTEs: `roots` keeps the 6 rows with `manager_id IS NULL`, and `leaves` keeps rows for which `NOT EXISTS` finds no child pointing at them; the outer query labels each CTE and stacks them with `UNION ALL`.
   **Expected result/shape:** For sql-25 Exercise 3, expected output: 103 rows, 97 `leaf` rows followed by 6 `root` rows (employees 1 through 6); employees 3, 4, 5, and 6 appear twice because they have no manager and no reports. The final columns are `node_type`, `employee_id`, and `full_name`. The final order is `node_type, employee_id`.
   **Verify:** For sql-25 Exercise 3, count rows by `node_type` and confirm 97 and 6, and that `SELECT employee_id FROM employees e WHERE manager_id IS NULL AND NOT EXISTS (SELECT 1 FROM employees c WHERE c.manager_id = e.employee_id)` returns exactly 3, 4, 5, and 6; then rewrite the leaf test as `employee_id NOT IN (SELECT manager_id FROM employees)` and confirm it returns 0 leaves, because the 6 NULL `manager_id` values make every `NOT IN` test unknown.
4. **Prediction:** Count employees reachable from roots and compare with total employees.
   **Progressive hint:** A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
   **Inputs/evidence:** For sql-25 Exercise 4, read `employees` twice: the recursive `organization` CTE walks down from the 6 roots with a `path` guard, and two scalar subqueries count the full table; the outer query compares `COUNT(DISTINCT employee_id)` from the CTE with that total and has no `GROUP BY`.
   **Expected result/shape:** For sql-25 Exercise 4, expected output: exactly one row, 100 `all_employees`, 100 `reachable_employees`, and 0 `unreachable_employees`. The final columns are `all_employees`, `reachable_employees`, and `unreachable_employees`.
   **Verify:** For sql-25 Exercise 4, confirm the CTE returns 100 rows and 100 distinct `employee_id` values, so no employee is reached twice; then, inside `BEGIN ... ROLLBACK`, run `UPDATE employees SET manager_id = 9 WHERE employee_id = 1` and confirm the row changes to 100, 6, and 94, because employee 1, employee 8, and the 92 reports under 8 form a loop with no root.
5. **Debugging:** Calculate full-subtree report counts per manager without counting the manager as their own report.
   **Progressive hint:** Seed direct edges and recurse descendants while carrying the original manager.
   **Inputs/evidence:** For sql-25 Exercise 5, read `employees` twice in the anchor of the recursive `descendants` CTE (each manager joined to direct children, with `path` seeded as `ARRAY[parent, child]`), then keep joining children of `report_id`; the outer query groups by `manager_id`.
   **Expected result/shape:** For sql-25 Exercise 5, expected output: exactly 3 rows, manager 1 with 93 descendants, manager 8 with 92, and manager 2 with 1. The final columns are `manager_id`, and `all_descendant_reports`. The final order is `all_descendant_reports DESC, manager_id`.
   **Verify:** For sql-25 Exercise 5, confirm manager 8's 92 matches `SELECT COUNT(*) FROM employees WHERE manager_id = 8`, manager 1's 93 is that 92 plus employee 8 itself, `COUNT(*)` equals `COUNT(DISTINCT report_id)` for each manager, and no row has `report_id = manager_id`; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm managers 1, 8, and 9 each return 93 and still never count themselves.
6. **Extension:** Report department headcount split between managers and nonmanagers.
   **Progressive hint:** First derive the manager ID set, then conditionally aggregate employees once.
   **Inputs/evidence:** For sql-25 Exercise 6, read all 6 `departments`, `LEFT JOIN` their 100 `employees`, and `LEFT JOIN` the `managers` CTE, which holds the 3 distinct non-NULL `manager_id` values; the `FILTER` clauses split each department's count on whether that join found a match.
   **Expected result/shape:** For sql-25 Exercise 6, expected output: exactly 6 rows; Sales has 17 people (1 manager), Engineering 17 (2 managers), HR and Finance 17 each, and Marketing and Operations 16 each, all with 0 managers. The final columns are `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`. The final order is `d.department_id`.
   **Verify:** For sql-25 Exercise 6, confirm `headcount` adds to 100, `managers` adds to 3, and `managers + nonmanagers = headcount` on every row; then, inside `BEGIN ... ROLLBACK`, run `INSERT INTO departments (department_id, name) VALUES (7, 'Legal')` and confirm a seventh row with 0, 0, and 0, while `COUNT(*)` would wrongly report 1 for that empty department.

## Common mistakes and how to recover

- **Summing over ancestor-descendant pairs.** Joining Exercise 5's 186 pairs
  to salaries counts employees 9 to 100 under both employee 8 and employee 1.
  Subtree payrolls then total 8,235,305.17, almost twice the 4,158,246.51 paid
  to non-root employees.
- **Forgetting `DISTINCT` in a manager list.** If Exercise 6's `managers` CTE
  keeps all 94 `manager_id` values, employee 8 matches 92 rows and
  Engineering's headcount jumps from 17 to 108.
- **Using `NOT IN` to find leaves.** `employee_id NOT IN (SELECT manager_id
  FROM employees)` returns no rows at all, because the six root rows put
  `NULL` in that list. `NOT EXISTS` returns the 97 leaves.
- **Assuming roots and leaves are disjoint.** Employees 3, 4, 5 and 6 have no
  manager and no reports, so they are both. A report that lists both labels
  has 103 rows for 99 distinct employees.
- **Recursing when one join is enough.** A direct-team count needs a single
  `GROUP BY manager_id`. Walking the full tree there gives employee 1 a team of
  93 instead of 1.
- General recovery steps are in
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does each CTE have one clear purpose and a testable output contract?
- Are repeated measures protected from hierarchy fanout?

## Next step

Continue to [Day 26; CTEs with window functions](day26_ctes_with_windows.md).

## Deep dive and reference

Learning objectives
- Chain multiple CTEs to express stepwise logic clearly
- Mix recursive and non-recursive CTEs for hierarchical problems
- Reuse earlier CTE outputs to avoid recomputation

Why this matters
Complex reports often need staging, filtering, enrichment, and aggregation in stages. Multiple CTEs provide a declarative pipeline that remains readable and testable.

Core concepts and deep dive
- Ordering of CTEs: later CTEs can reference earlier ones. Think of each as a named subquery stage.
- Mixed recursion: WITH RECURSIVE tree AS (...), leaves AS (...) SELECT ... FROM tree JOIN leaves ...
- Performance: since PostgreSQL 12, a side-effect-free, non-recursive CTE referenced once may be inlined. A CTE referenced several times is already materialized by default; use MATERIALIZED only to force a single-use CTE to be computed separately.

Patterns
- Stage raw lines -> enrich with dims -> filter -> aggregate -> final select.
- Build an employee hierarchy and join it to department headcount, payroll, or
  average-salary aggregates.

Pitfalls
- Circular references between CTEs are invalid.
- Excessive staging for trivial logic harms readability; strike a balance.

Further reading
- WITH queries: https://www.postgresql.org/docs/17/queries-with.html

## Ask an AI tutor about this lesson

Ask a tutor to quiz you on which grain each CTE in your answer has
and how many rows it should return. The prompt below keeps it on this lesson
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-25: Multiple CTEs and Hierarchies.

I have completed the direct catalog prerequisite: `sql-24`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day25_multiple_ctes_hierarchies.md
- Answer-free learner SQL: sql/postgres-60day/day25_multiple_ctes_hierarchies.sql

Key terms to teach in context: CTE pipeline, Hierarchy enrichment, Stage invariant. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build the employee hierarchy separately and validate `(employee_id, depth)`. Build department aggregates separately at one row per department. Join them only after both grains are stable, so a department measure is not accidentally re-aggregated across hierarchy paths.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-25/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
