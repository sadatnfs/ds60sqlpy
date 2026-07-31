# Day 24 — Recursive CTEs: Hierarchies, Trees, and Graph Walks (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 23 — common table expressions](day23_ctes_intro.md)
- **Artifacts:** [learner SQL](../day24_recursive_ctes.sql) ·
  [solution reasoning](../solutions/day24_solutions.md) ·
  [executable solution](../solutions/day24_solutions.sql)

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

2. Open **SQL-24 — Recursive CTEs** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-24/day24_recursive_ctes.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day24_recursive_ctes.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day24_recursive_ctes.sql
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
Anchor member, Recursive member, Cycle guard. Its worked SQL reads or creates `employees`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Seed each direct manager/report edge with a path array containing both keys. Each recursive step joins the current report to its direct reports, increments depth, and rejects a key already present in the path. Inspect the maximum depth and path before trusting the hierarchy.
The expected contract is that One row per ancestor-descendant pair. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day24_recursive_ctes.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH RECURSIVE org AS (
  SELECT e.employee_id,
         e.full_name,
         e.manager_id,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT e.employee_id,
         e.full_name,
         e.manager_id,
         o.depth + 1,
         o.path || e.employee_id
  FROM employees e
  JOIN org o ON e.manager_id = o.employee_id
  -- A path is evidence of traversal and a guard against malformed cycles.
  WHERE NOT e.employee_id = ANY(o.path)
)
SELECT employee_id, full_name, manager_id, depth, path
FROM org
ORDER BY depth, full_name, employee_id
LIMIT 100;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per ancestor-descendant pair.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH RECURSIVE months AS (
  SELECT date_trunc('month', CURRENT_DATE)::date AS m, 1 AS n
  UNION ALL
  SELECT (m - interval '1 month')::date, n+1 FROM months WHERE n < 12
)
SELECT m AS month_start, n AS step
FROM months
ORDER BY month_start;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per ancestor-descendant pair.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Build a recursive CTE from compatible anchor and recursive members.
- Track depth and path while preventing cycles.

## Vocabulary and concepts

- **Anchor member:** the non-recursive seed rows.
- **Recursive member:** the query that derives the next rows from prior output.
- **Cycle guard:** a path or visited-key check that prevents revisiting nodes.

## Worked example / walkthrough

Seed each direct manager/report edge with a path array containing both keys.
Each recursive step joins the current report to its direct reports, increments
depth, and rejects a key already present in the path. Inspect the maximum depth
and path before trusting the hierarchy.

## Practice assumptions and review method

- **Focus:** Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
- **Assumptions:** Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
- **Failure to watch for:** `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List every manager's direct and indirect reports with depth and path.
   **Progressive hint:** Seed every direct edge, carry the original manager, and reject IDs already in the path.
   **Expected shape:** One row per ancestor-descendant pair.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Generate integers 1 through 100 recursively and return their sum.
   **Progressive hint:** Anchor at 1 and stop producing rows after 100.
   **Expected shape:** Exactly one row with 5050.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Generate the first day of the current and prior 11 months recursively.
   **Progressive hint:** Carry a counter as an explicit termination condition.
   **Expected shape:** Exactly 12 chronological month rows.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Traverse a local graph containing a cycle and prove a path-array guard terminates.
   **Progressive hint:** Reject a destination already present in the path before adding it.
   **Expected shape:** Finite paths starting from node 1; no repeated node inside a path.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Walk upward from every employee to ancestors while preventing cycles.
   **Progressive hint:** The recursive step follows current manager ID to the manager row and appends it to path.
   **Expected shape:** One row per employee-ancestor relation.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Summarize employee count by hierarchy depth from all roots.
   **Progressive hint:** Build the guarded root traversal first, then aggregate only after depth is assigned.
   **Expected shape:** One row per observed depth.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Do anchor and recursive branches return the same column types?
- Can you prove recursion terminates for malformed cyclic data?

## Next step

Continue to [Day 25 — multiple CTEs and hierarchies](day25_multiple_ctes_hierarchies.md).

## Deep dive and reference

Learning objectives
- Use WITH RECURSIVE to traverse hierarchical/graph data (up/down)
- Understand anchor vs recursive member, UNION ALL, and termination
- Compute depth, paths, cycle detection, and ordering

Why this matters
Many data structures are hierarchical: org charts, category trees, dependency graphs. Recursive CTEs let you explore them without procedural code.

Core concepts and deep dive
- Anatomy
  - WITH RECURSIVE t AS ( anchor_query UNION ALL recursive_query ) SELECT ... FROM t;
  - Anchor emits starting rows (roots). Recursive member references t and produces next-level rows.
  - Termination occurs when recursive member returns no new rows.
- Columns
  - Ensure both SELECTs output the same column list/types (id, parent_id, depth, path, ...).
- Depth and path
  - depth := anchor depth 0 (or 1) plus 1 each recursion.
  - path := path || id to accumulate ancestry for cycle checks and sorting.
- Cycle detection
  - WHERE id <> ALL(path) prevents revisiting nodes (for graphs with cycles).
- Ordering
  - Use ORDER BY path for pre-order traversal; or track sort_keys.

Patterns
- Downward traversal: employees (`employee_id`, `manager_id`) from a manager to
  all reports.
- Level summaries: GROUP BY depth to count nodes per level.

Pitfalls
- Infinite recursion on cycles; always implement a cycle guard or LIMIT depth.
- UNION vs UNION ALL: use UNION ALL to avoid global de-dup unless necessary; dedup can be expensive.
- Large trees can be costly; index parent_id and id.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WITH RECURSIVE: https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-RECURSIVE
- Tree traversal recipes: https://wiki.postgresql.org/wiki/Hierarchical_queries

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-24 — Recursive CTEs.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day24_recursive_ctes.md
- Answer-free learner SQL: sql/postgres-60day/day24_recursive_ctes.sql

The lesson concepts include Anchor member, Recursive member, Cycle guard. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Seed each direct manager/report edge with a path array containing both keys. Each recursive step joins the current report to its direct reports, increments depth, and rejects a key already present in the path. Inspect the maximum depth and path before trusting the hierarchy.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-24/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
