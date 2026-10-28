# Day 25: Multiple CTEs and Hierarchies in One Query (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-25**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-25/lesson/workspace/sql/postgres-60day/day25_multiple_ctes_hierarchies.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-25
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 24; recursive CTEs](day24_recursive_ctes.md)
- **Artifacts:** [learner SQL](../day25_multiple_ctes_hierarchies.sql) ·
  [solution reasoning](../solutions/day25_solutions.md) ·
  [executable solution](../solutions/day25_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is CTE pipeline, Hierarchy enrichment, Stage invariant. Its worked SQL reads or creates `employees`, `departments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Build the employee hierarchy separately and validate (employeeid, depth). Build department aggregates separately at one row per department. Join them only after both grains are stable, so a department measure is not accidentally re-aggregated across hierarchy paths.
The expected contract is that One row per hierarchy depth. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day25_multiple_ctes_hierarchies.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
WITH RECURSIVE base_org AS (
  SELECT e.employee_id,
         e.manager_id,
         e.department_id,
         e.salary,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT e.employee_id,
         e.manager_id,
         e.department_id,
         e.salary,
         b.depth + 1,
         b.path || e.employee_id
  FROM employees e
  JOIN base_org b ON e.manager_id = b.employee_id
  WHERE NOT e.employee_id = ANY(b.path)
), dept_counts AS (
  -- Aggregate the traversed employee relation so the hierarchy CTE is an
  -- observable, testable stage rather than an unused declaration.
  SELECT department_id,
         COUNT(*) AS reachable_headcount,
         ROUND(AVG(salary), 2) AS avg_salary,
         MAX(depth) AS deepest_level
  FROM base_org
  GROUP BY department_id
)
SELECT d.department_id,
       d.name AS department,
       COALESCE(dc.reachable_headcount, 0) AS reachable_headcount,
       dc.avg_salary,
       dc.deepest_level
FROM departments d
LEFT JOIN dept_counts dc ON dc.department_id = d.department_id
ORDER BY reachable_headcount DESC, d.department_id;
```

**How to read it:** Example 1: Start with `employees`, `base_org`, and `departments` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys; append branches with `UNION ALL` (duplicates are retained). The final `SELECT` displays `department_id`, `department`, `reachable_headcount`, `avg_salary`, and `deepest_level`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `department_id` with columns `department_id`, `department`, `reachable_headcount`, `avg_salary`, and `deepest_level` from `employees`, `base_org`, and `departments`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH RECURSIVE base_org AS (
  SELECT e.employee_id,
         e.manager_id,
         e.department_id,
         e.salary,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT e.employee_id,
         e.manager_id,
         e.department_id,
         e.salary,
         b.depth + 1,
         b.path || e.employee_id
  FROM employees e
  JOIN base_org b ON e.manager_id = b.employee_id
  WHERE NOT e.employee_id = ANY(b.path)
), dept_counts AS (
  -- Aggregate the traversed employee relation so the hierarchy CTE is an
  -- observable, testable stage rather than an unused declaration.
  SELECT department_id,
         COUNT(*) AS reachable_headcount,
         ROUND(AVG(salary), 2) AS avg_salary,
         MAX(depth) AS deepest_level
  FROM base_org
  GROUP BY department_id
)
SELECT d.department_id,
       d.name AS department,
       COALESCE(dc.reachable_headcount, 0) AS reachable_headcount,
       dc.avg_salary,
       dc.deepest_level
FROM departments d
LEFT JOIN dept_counts dc ON dc.department_id = d.department_id
ORDER BY reachable_headcount DESC, d.department_id;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `department_id` key set and row count over `employees`, `base_org`, and `departments`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

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
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Build a root-based organization CTE and report headcount and payroll by depth.
   **Progressive hint:** Assign depth during recursion, then aggregate employee rows once.
   **Inputs/evidence:** For sql-25 Exercise 1, read from `employees`, and `organization`. Build the answer toward `depth`, `headcount`, and `payroll`; keep `depth` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-25 Exercise 1, expected output: One row per hierarchy depth. The final columns are `depth`, `headcount`, and `payroll`. The final order is `depth`.
   **Verify:** For sql-25 Exercise 1, independently aggregate `employees`, and `organization` by `depth`; require one output row for every distinct `depth` tuple and compare `headcount`, and `payroll` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `headcount`, and `payroll` for the existing `depth` tuple and verify the new tuple appears exactly once.
2. **Query writing:** Report each manager's direct-report count and payroll.
   **Progressive hint:** Direct-team grain needs one self join, not full recursive descendants.
   **Inputs/evidence:** For sql-25 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-25 Exercise 2, expected output: One row per manager with at least one direct report. The final columns are `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`. The final order is `dt.direct_reports DESC, manager.employee_id`.
   **Verify:** For sql-25 Exercise 2, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
3. **Query writing:** Identify hierarchy roots and leaves in one report.
   **Progressive hint:** Create root and leaf CTEs at employee grain, then union compatible labeled rows.
   **Inputs/evidence:** For sql-25 Exercise 3, read from `employees`. Build the answer toward `node_type`, `employee_id`, and `full_name`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-25 Exercise 3, expected output: One labeled row per root or leaf employee. The final columns are `node_type`, `employee_id`, and `full_name`. The final order is `node_type, employee_id`.
   **Verify:** For sql-25 Exercise 3, reselect the returned keys directly from the source; require unique `employee_id` where the expected grain is one row per key and confirm the projected `node_type`, `employee_id`, and `full_name` against `employees`. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
4. **Prediction:** Count employees reachable from roots and compare with total employees.
   **Progressive hint:** A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
   **Inputs/evidence:** For sql-25 Exercise 4, read from `employees`, and `organization`. Build the answer toward `all_employees`, `reachable_employees`, and `unreachable_employees`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-25 Exercise 4, expected output: One row with zero unreachable employees. The final columns are `all_employees`, `reachable_employees`, and `unreachable_employees`.
   **Verify:** For sql-25 Exercise 4, project `employee_id` plus the raw source columns from `employees`, and `organization` at each join stage; record row count and distinct `employee_id`, then assert the final `all_employees`, `reachable_employees`, and `unreachable_employees` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
5. **Debugging:** Calculate full-subtree report counts per manager without counting the manager as their own report.
   **Progressive hint:** Seed direct edges and recurse descendants while carrying the original manager.
   **Inputs/evidence:** For sql-25 Exercise 5, read from `employees`, and `descendants`. Build the answer toward `manager_id`, and `all_descendant_reports`; keep `manager_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-25 Exercise 5, expected output: One row per manager with descendant count. The final columns are `manager_id`, and `all_descendant_reports`. The final order is `all_descendant_reports DESC, manager_id`.
   **Verify:** For sql-25 Exercise 5, independently aggregate `employees`, and `descendants` by `manager_id`; require one output row for every distinct `manager_id` tuple and compare `all_descendant_reports` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `all_descendant_reports` for the existing `manager_id` tuple and verify the new tuple appears exactly once.
6. **Extension:** Report department headcount split between managers and nonmanagers.
   **Progressive hint:** First derive the manager ID set, then conditionally aggregate employees once.
   **Inputs/evidence:** For sql-25 Exercise 6, read from `employees`, and `departments`. Build the answer toward `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`; keep `department_id`, and `name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-25 Exercise 6, expected output: One row per department. The final columns are `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`. The final order is `d.department_id`.
   **Verify:** For sql-25 Exercise 6, independently aggregate `employees`, and `departments` by `department_id`, and `name`; require one output row for every distinct `department_id`, and `name` tuple and compare `headcount`, `managers`, and `nonmanagers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `headcount`, `managers`, and `nonmanagers` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

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
- Performance: since Postgres 12, non-recursive CTEs may be inlined. Force MATERIALIZED for expensive reused CTEs.

Patterns
- Stage raw lines -> enrich with dims -> filter -> aggregate -> final select.
- Build an employee hierarchy and join it to department headcount, payroll, or
  average-salary aggregates.

Pitfalls
- Circular references between CTEs are invalid.
- Excessive staging for trivial logic harms readability; strike a balance.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-25 — Multiple CTEs Hierarchies.

I have completed the direct catalog prerequisite: `sql-24`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day25_multiple_ctes_hierarchies.md
- Answer-free learner SQL: sql/postgres-60day/day25_multiple_ctes_hierarchies.sql

Key terms to teach in context: CTE pipeline, Hierarchy enrichment, Stage invariant. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build the employee hierarchy separately and validate (employeeid, depth). Build department aggregates separately at one row per department. Join them only after both grains are stable, so a department measure is not accidentally re-aggregated across hierarchy paths.

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
