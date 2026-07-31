# Day 25 solutions — Multiple CTEs and Hierarchies in One Query


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day25_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day25_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are CTE pipeline, Hierarchy enrichment, Stage invariant. Its worked-model focus is:
Build the employee hierarchy separately and validate (employeeid, depth). Build department aggregates separately at one row per department. Join them only after both grains are stable, so a department measure is not accidentally re-aggregated across hierarchy paths.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

These answers align one-for-one with [day25_multiple_ctes_hierarchies.sql](../day25_multiple_ctes_hierarchies.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.
- **Assumptions:** The employee graph can have multiple roots. Payroll uses exact salary numeric and each employee should contribute once per intended output grain.
- **Primary pitfall:** Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Build a root-based organization CTE and report headcount and payroll by depth.

**Reasoning:** Assign depth during recursion, then aggregate employee rows once.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH RECURSIVE organization AS (
  SELECT e.employee_id,
         e.manager_id,
         e.salary,
         0 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT child.employee_id,
         child.manager_id,
         child.salary,
         parent.depth + 1,
         parent.path || child.employee_id
  FROM organization AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  WHERE NOT child.employee_id = ANY(parent.path)
)
SELECT depth,
       COUNT(*) AS headcount,
       ROUND(SUM(salary), 2) AS payroll
FROM organization
GROUP BY depth
ORDER BY depth;
```

**Expected shape:** One row per hierarchy depth.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 1, read from `employees`, and `organization`. Build the answer toward `depth`, `headcount`, and `payroll`; keep `depth` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-25 Exercise 1, expected output: One row per hierarchy depth. The final columns are `depth`, `headcount`, and `payroll`. The final order is `depth`.
- **Independent verification:** For sql-25 Exercise 1, independently aggregate `employees`, and `organization` by `depth`; require one output row for every distinct `depth` tuple and compare `headcount`, and `payroll` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `headcount`, and `payroll` for the existing `depth` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-25 Exercise 1, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `depth` so the exact fanout or loss is visible.
- **Clause check:** For sql-25 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, and `organization`, preserve one row per `depth`, and finish with `depth`, `headcount`, and `payroll` ordered by `depth`.
- **Alternative/trade-off:** For sql-25 Exercise 1, the chosen form is justified by this lesson-specific rationale: Assign depth during recursion, then aggregate employee rows once. Evaluate another form against the concrete expected result (One row per hierarchy depth) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `headcount`, and `payroll` for the existing `depth` tuple and verify the new tuple appears exactly once.

## Exercise 2 — Query writing

**Prompt:** Report each manager's direct-report count and payroll.

**Reasoning:** Direct-team grain needs one self join, not full recursive descendants.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH direct_teams AS (
  SELECT e.manager_id,
         COUNT(*) AS direct_reports,
         SUM(e.salary) AS direct_report_payroll
  FROM employees AS e
  WHERE e.manager_id IS NOT NULL
  GROUP BY e.manager_id
)
SELECT manager.employee_id,
       manager.full_name,
       dt.direct_reports,
       ROUND(dt.direct_report_payroll, 2) AS direct_report_payroll
FROM direct_teams AS dt
JOIN employees AS manager
  ON manager.employee_id = dt.manager_id
ORDER BY dt.direct_reports DESC, manager.employee_id;
```

**Expected shape:** One row per manager with at least one direct report.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-25 Exercise 2, expected output: One row per manager with at least one direct report. The final columns are `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`. The final order is `dt.direct_reports DESC, manager.employee_id`.
- **Independent verification:** For sql-25 Exercise 2, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
- **Intermediate relation check:** For sql-25 Exercise 2, run `direct_teams` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-25 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll` ordered by `dt.direct_reports DESC, manager.employee_id`.
- **Alternative/trade-off:** For sql-25 Exercise 2, the chosen form is justified by this lesson-specific rationale: Direct-team grain needs one self join, not full recursive descendants. Evaluate another form against the concrete expected result (One row per manager with at least one direct report) and the verification above.
- **Edge case:** Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.

## Exercise 3 — Query writing

**Prompt:** Identify hierarchy roots and leaves in one report.

**Reasoning:** Create root and leaf CTEs at employee grain, then union compatible labeled rows.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH roots AS (
  SELECT e.employee_id, e.full_name
  FROM employees AS e
  WHERE e.manager_id IS NULL
), leaves AS (
  SELECT e.employee_id, e.full_name
  FROM employees AS e
  WHERE NOT EXISTS (
    SELECT 1 FROM employees AS child
    WHERE child.manager_id = e.employee_id
  )
)
SELECT 'root' AS node_type, employee_id, full_name FROM roots
UNION ALL
SELECT 'leaf' AS node_type, employee_id, full_name FROM leaves
ORDER BY node_type, employee_id;
```

**Expected shape:** One labeled row per root or leaf employee.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 3, read from `employees`. Build the answer toward `node_type`, `employee_id`, and `full_name`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-25 Exercise 3, expected output: One labeled row per root or leaf employee. The final columns are `node_type`, `employee_id`, and `full_name`. The final order is `node_type, employee_id`.
- **Independent verification:** For sql-25 Exercise 3, reselect the returned keys directly from the source; require unique `employee_id` where the expected grain is one row per key and confirm the projected `node_type`, `employee_id`, and `full_name` against `employees`. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
- **Intermediate relation check:** For sql-25 Exercise 3, run `roots`, and `leaves` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-25 Exercise 3, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `node_type`, `employee_id`, and `full_name` ordered by `node_type, employee_id`.
- **Alternative/trade-off:** For sql-25 Exercise 3, the chosen form is justified by this lesson-specific rationale: Create root and leaf CTEs at employee grain, then union compatible labeled rows. Evaluate another form against the concrete expected result (One labeled row per root or leaf employee) and the verification above.
- **Edge case:** Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.

## Exercise 4 — Prediction

**Prompt:** Count employees reachable from roots and compare with total employees.

**Reasoning:** A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.

```sql
WITH RECURSIVE organization AS (
  SELECT e.employee_id, ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT child.employee_id, parent.path || child.employee_id
  FROM organization AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  WHERE NOT child.employee_id = ANY(parent.path)
)
SELECT (SELECT COUNT(*) FROM employees) AS all_employees,
       COUNT(DISTINCT employee_id) AS reachable_employees,
       (SELECT COUNT(*) FROM employees) - COUNT(DISTINCT employee_id) AS unreachable_employees
FROM organization;
```

**Expected shape:** One row with zero unreachable employees.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 4, read from `employees`, and `organization`. Build the answer toward `all_employees`, `reachable_employees`, and `unreachable_employees`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-25 Exercise 4, expected output: One row with zero unreachable employees. The final columns are `all_employees`, `reachable_employees`, and `unreachable_employees`.
- **Independent verification:** For sql-25 Exercise 4, project `employee_id` plus the raw source columns from `employees`, and `organization` at each join stage; record row count and distinct `employee_id`, then assert the final `all_employees`, `reachable_employees`, and `unreachable_employees` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
- **Intermediate relation check:** For sql-25 Exercise 4, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-25 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, and `SELECT`. Read only those operations: begin at `employees`, and `organization`, preserve one row per `employee_id`, and finish with `all_employees`, `reachable_employees`, and `unreachable_employees`.
- **Alternative/trade-off:** For sql-25 Exercise 4, the chosen form is justified by this lesson-specific rationale: A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema. Evaluate another form against the concrete expected result (One row with zero unreachable employees) and the verification above.
- **Edge case:** Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.

## Exercise 5 — Debugging

**Prompt:** Calculate full-subtree report counts per manager without counting the manager as their own report.

**Reasoning:** Seed direct edges and recurse descendants while carrying the original manager.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH RECURSIVE descendants AS (
  SELECT parent.employee_id AS manager_id,
         child.employee_id AS report_id,
         ARRAY[parent.employee_id, child.employee_id] AS path
  FROM employees AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  UNION ALL
  SELECT d.manager_id,
         child.employee_id,
         d.path || child.employee_id
  FROM descendants AS d
  JOIN employees AS child
    ON child.manager_id = d.report_id
  WHERE NOT child.employee_id = ANY(d.path)
)
SELECT manager_id,
       COUNT(DISTINCT report_id) AS all_descendant_reports
FROM descendants
GROUP BY manager_id
ORDER BY all_descendant_reports DESC, manager_id;
```

**Expected shape:** One row per manager with descendant count.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 5, read from `employees`, and `descendants`. Build the answer toward `manager_id`, and `all_descendant_reports`; keep `manager_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-25 Exercise 5, expected output: One row per manager with descendant count. The final columns are `manager_id`, and `all_descendant_reports`. The final order is `all_descendant_reports DESC, manager_id`.
- **Independent verification:** For sql-25 Exercise 5, independently aggregate `employees`, and `descendants` by `manager_id`; require one output row for every distinct `manager_id` tuple and compare `all_descendant_reports` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `all_descendant_reports` for the existing `manager_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-25 Exercise 5, start with the first relation in `employees`, and `descendants`; after each join, record total rows and distinct `manager_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-25 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, and `descendants`, preserve one row per `manager_id`, and finish with `manager_id`, and `all_descendant_reports` ordered by `all_descendant_reports DESC, manager_id`.
- **Alternative/trade-off:** For sql-25 Exercise 5, the chosen form is justified by this lesson-specific rationale: Seed direct edges and recurse descendants while carrying the original manager. Evaluate another form against the concrete expected result (One row per manager with descendant count) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `all_descendant_reports` for the existing `manager_id` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Extension

**Prompt:** Report department headcount split between managers and nonmanagers.

**Reasoning:** First derive the manager ID set, then conditionally aggregate employees once.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH managers AS (
  SELECT DISTINCT e.manager_id AS employee_id
  FROM employees AS e
  WHERE e.manager_id IS NOT NULL
)
SELECT d.department_id,
       d.name,
       COUNT(e.employee_id) AS headcount,
       COUNT(e.employee_id) FILTER (
         WHERE m.employee_id IS NOT NULL
       ) AS managers,
       COUNT(e.employee_id) FILTER (
         WHERE m.employee_id IS NULL
       ) AS nonmanagers
FROM departments AS d
LEFT JOIN employees AS e
  ON e.department_id = d.department_id
LEFT JOIN managers AS m
  ON m.employee_id = e.employee_id
GROUP BY d.department_id, d.name
ORDER BY d.department_id;
```

**Expected shape:** One row per department.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-25 Exercise 6, read from `employees`, and `departments`. Build the answer toward `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`; keep `department_id`, and `name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-25 Exercise 6, expected output: One row per department. The final columns are `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`. The final order is `d.department_id`.
- **Independent verification:** For sql-25 Exercise 6, independently aggregate `employees`, and `departments` by `department_id`, and `name`; require one output row for every distinct `department_id`, and `name` tuple and compare `headcount`, `managers`, and `nonmanagers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `headcount`, `managers`, and `nonmanagers` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-25 Exercise 6, run `managers` one at a time. Record each CTE's row count and `department_id`, and `name` uniqueness before the next stage uses it.
- **Clause check:** For sql-25 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, and `departments`, preserve one row per `department_id`, and `name`, and finish with `department_id`, `name`, `headcount`, `managers`, and `nonmanagers` ordered by `d.department_id`.
- **Alternative/trade-off:** For sql-25 Exercise 6, the chosen form is justified by this lesson-specific rationale: First derive the manager ID set, then conditionally aggregate employees once. Evaluate another form against the concrete expected result (One row per department) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `headcount`, `managers`, and `nonmanagers` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
