# Day 25 — Multiple CTEs and Hierarchies in One Query (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 24 — recursive CTEs](day24_recursive_ctes.md)
- **Artifacts:** [learner SQL](../day25_multiple_ctes_hierarchies.sql) ·
  [solution reasoning](../solutions/day25_solutions.md) ·
  [executable solution](../solutions/day25_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-25 — Multiple CTEs Hierarchies** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-25/day25_multiple_ctes_hierarchies.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day25_multiple_ctes_hierarchies.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day25_multiple_ctes_hierarchies.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
CTE pipeline, Hierarchy enrichment, Stage invariant. Its worked SQL reads or creates `employees`, `departments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Build the employee hierarchy separately and validate (employeeid, depth). Build department aggregates separately at one row per department. Join them only after both grains are stable, so a department measure is not accidentally re-aggregated across hierarchy paths.
The expected contract is that One row per hierarchy depth. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day25_multiple_ctes_hierarchies.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per hierarchy depth.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per hierarchy depth.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. **Query writing:** Report each manager's direct-report count and payroll.
   **Progressive hint:** Direct-team grain needs one self join, not full recursive descendants.
   **Expected shape:** One row per manager with at least one direct report.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Identify hierarchy roots and leaves in one report.
   **Progressive hint:** Create root and leaf CTEs at employee grain, then union compatible labeled rows.
   **Expected shape:** One labeled row per root or leaf employee.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Count employees reachable from roots and compare with total employees.
   **Progressive hint:** A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
   **Expected shape:** One row with zero unreachable employees.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Calculate full-subtree report counts per manager without counting the manager as their own report.
   **Progressive hint:** Seed direct edges and recurse descendants while carrying the original manager.
   **Expected shape:** One row per manager with descendant count.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Report department headcount split between managers and nonmanagers.
   **Progressive hint:** First derive the manager ID set, then conditionally aggregate employees once.
   **Expected shape:** One row per department.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Does each CTE have one clear purpose and a testable output contract?
- Are repeated measures protected from hierarchy fanout?

## Next step

Continue to [Day 26 — CTEs with window functions](day26_ctes_with_windows.md).

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-25 — Multiple CTEs Hierarchies.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day25_multiple_ctes_hierarchies.md
- Answer-free learner SQL: sql/postgres-60day/day25_multiple_ctes_hierarchies.sql

The lesson concepts include CTE pipeline, Hierarchy enrichment, Stage invariant. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build the employee hierarchy separately and validate (employeeid, depth). Build department aggregates separately at one row per department. Join them only after both grains are stable, so a department measure is not accidentally re-aggregated across hierarchy paths.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-25/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
