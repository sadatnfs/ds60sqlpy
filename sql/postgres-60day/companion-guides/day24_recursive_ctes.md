# Day 24: Recursive CTEs: Hierarchies, Trees, and Graph Walks (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-24**. The
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
   `.learning/sql/sql-24/lesson/workspace/sql/postgres-60day/day24_recursive_ctes.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-24
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
- **Prerequisites:** [Day 23; common table expressions](day23_ctes_intro.md)
- **Artifacts:** [learner SQL](../day24_recursive_ctes.sql) ·
  [solution reasoning](../solutions/day24_solutions.md) ·
  [executable solution](../solutions/day24_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Anchor member, Recursive member, Cycle guard. Its worked SQL reads or creates `employees`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Seed each direct manager/report edge with a path array containing both keys. Each recursive step joins the current report to its direct reports, increments depth, and rejects a key already present in the path. Inspect the maximum depth and path before trusting the hierarchy.
The expected contract is that One row per ancestor-descendant pair. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day24_recursive_ctes.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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

**How to read it:** Example 1: Start with `employees`, and `org` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; append branches with `UNION ALL` (duplicates are retained). The final `SELECT` displays `employee_id`, `full_name`, `manager_id`, `depth`, and `path`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `employee_id`, and `manager_id`, capped at 100 rows with columns `employee_id`, `full_name`, `manager_id`, `depth`, and `path` from `employees`, and `org`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

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

**How to read it:** Example 2: Start with `months` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; append branches with `UNION ALL` (duplicates are retained). The final `SELECT` displays `month_start`, and `step`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `month_start` with columns `month_start`, and `step` from `months`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

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
   **Inputs/evidence:** For sql-24 Exercise 1, read from `employees`, and `reports`. Build the answer toward `manager_id`, `report_id`, `depth`, and `path`; keep `manager_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-24 Exercise 1, expected output: One row per ancestor-descendant pair. The final columns are `manager_id`, `report_id`, `depth`, and `path`. The final order is `manager_id, depth, report_id`.
   **Verify:** For sql-24 Exercise 1, project `manager_id` plus the raw source columns from `employees`, and `reports` at each join stage; record row count and distinct `manager_id`, then assert the final `manager_id`, `report_id`, `depth`, and `path` values match those staged rows without unintended fanout or loss. Add one source row with a new `manager_id`; verify the result gains exactly one row carrying that `manager_id` value.
2. **Query writing:** Generate integers 1 through 100 recursively and return their sum.
   **Progressive hint:** Anchor at 1 and stop producing rows after 100.
   **Inputs/evidence:** For sql-24 Exercise 2, read from `numbers`. Compute `sum_1_to_100` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-24 Exercise 2, expected output: Exactly one row with 5050. The final columns are `sum_1_to_100`.
   **Verify:** For sql-24 Exercise 2, evaluate each of `sum_1_to_100` in a separate control `SELECT` over `numbers`; require one final row and compare every value. Force the final predicate to match zero rows and record `sum_1_to_100`; distinguish `COUNT` zero from nullable `SUM` or `AVG` results.
3. **Query writing:** Generate the first day of the current and prior 11 months recursively.
   **Progressive hint:** Carry a counter as an explicit termination condition.
   **Inputs/evidence:** For sql-24 Exercise 3, read from `months`. Build the answer toward `month_start`; keep `month_start` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-24 Exercise 3, expected output: Exactly 12 chronological month rows. The final columns are `month_start`. The final order is `month_start`.
   **Verify:** For sql-24 Exercise 3, reselect the returned keys directly from the source; require unique `month_start` where the expected grain is one row per key and confirm the projected `month_start` against `months`. Tie two rows on `month_start` and give them different `month_start` values; verify `month_start` chooses a stable first/last row.
4. **Prediction:** Traverse a local graph containing a cycle and prove a path-array guard terminates.
   **Progressive hint:** Reject a destination already present in the path before adding it.
   **Inputs/evidence:** For sql-24 Exercise 4, read from `walk`, and `edges`. Build the answer toward `node`, and `path`; keep `node` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-24 Exercise 4, expected output: Finite paths starting from node 1; no repeated node inside a path. The final columns are `node`, and `path`. The final order is `array_length(path, 1), path`.
   **Verify:** For sql-24 Exercise 4, project `node` plus the raw source columns from `walk`, and `edges` at each join stage; record row count and distinct `node`, then assert the final `node`, and `path` values match those staged rows without unintended fanout or loss. Add one source row with a new `node`; verify the result gains exactly one row carrying that `node` value.
5. **Debugging:** Walk upward from every employee to ancestors while preventing cycles.
   **Progressive hint:** The recursive step follows current manager ID to the manager row and appends it to path.
   **Inputs/evidence:** For sql-24 Exercise 5, read from `employees`, and `ancestors`. Build the answer toward `origin_employee_id`, `ancestor_id`, and `depth`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-24 Exercise 5, expected output: One row per employee-ancestor relation. The final columns are `origin_employee_id`, `ancestor_id`, and `depth`. The final order is `origin_employee_id, depth`.
   **Verify:** For sql-24 Exercise 5, project `employee_id` plus the raw source columns from `employees`, and `ancestors` at each join stage; record row count and distinct `employee_id`, then assert the final `origin_employee_id`, `ancestor_id`, and `depth` values match those staged rows without unintended fanout or loss. Add one row for which `(ancestor_id IS NOT NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.
6. **Extension:** Summarize employee count by hierarchy depth from all roots.
   **Progressive hint:** Build the guarded root traversal first, then aggregate only after depth is assigned.
   **Inputs/evidence:** For sql-24 Exercise 6, read from `employees`, and `organization`. Build the answer toward `depth`, and `employee_count`; keep `depth` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-24 Exercise 6, expected output: One row per observed depth. The final columns are `depth`, and `employee_count`. The final order is `depth`.
   **Verify:** For sql-24 Exercise 6, independently aggregate `employees`, and `organization` by `depth`; require one output row for every distinct `depth` tuple and compare `employee_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `employee_count` for the existing `depth` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** UNION ALL without a cycle/termination guard can recurse indefinitely; UNION duplicate removal is not a substitute for a path rule.
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

- Do anchor and recursive branches return the same column types?
- Can you prove recursion terminates for malformed cyclic data?

## Next step

Continue to [Day 25; multiple CTEs and hierarchies](day25_multiple_ctes_hierarchies.md).

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-24 — Recursive CTEs.

I have completed the direct catalog prerequisite: `sql-23`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day24_recursive_ctes.md
- Answer-free learner SQL: sql/postgres-60day/day24_recursive_ctes.sql

Key terms to teach in context: Anchor member, Recursive member, Cycle guard. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Seed each direct manager/report edge with a path array containing both keys. Each recursive step joins the current report to its direct reports, increments depth, and rejects a key already present in the path. Inspect the maximum depth and path before trusting the hierarchy.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-24/ working copy. Never point setup, reset, DDL, or DML
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
