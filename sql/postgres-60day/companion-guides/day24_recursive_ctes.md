# Day 24: Recursive CTEs: Hierarchies, Trees, and Graph Walks (Companion Guide)

## How to run this lesson

This lesson runs from `./classroom`: select **sql-24** among the PostgreSQL
lessons and use **Whole SQL lesson (psql)**. It executes your copy at
`.learning/sql/sql-24/lesson/workspace/sql/postgres-60day/day24_recursive_ctes.sql`
inside `advanced_sql_training`. Both statements are read-only recursive
queries, one over `employees` and one that generates dates from nothing, and
the file wraps them in `BEGIN`/`ROLLBACK`. A recursive query that never stops
would make `psql` hang rather than fail, so if the transcript stalls, cancel
it and look for a missing guard before anything else. More launcher detail is
in [Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

In a notebook you can run the anchor member alone, then add the recursive
member ([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-24
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 23; common table expressions](day23_ctes_intro.md)
- **Artifacts:** [learner SQL](../day24_recursive_ctes.sql) ·
  [solution reasoning](../solutions/day24_solutions.md) ·
  [executable solution](../solutions/day24_solutions.sql)

## A beginner's mental model for this lesson

`WITH RECURSIVE` builds a result in rounds. The **anchor member** (the query
before `UNION ALL`) runs once and produces the first rows. The **recursive
member** (the query after it) then runs again and again, each time reading
only the rows the previous round added, until a round adds nothing. The final
result is every round stacked together.

The course's org chart is small enough to trace by hand:

- Round 1 (the anchor, `manager_id IS NULL`) returns six roots, employees 1 to
  6, one per department.
- Round 2 finds the people whose manager is a root: employee 8 reports to 1
  and employee 7 reports to 2.
- Round 3 finds the 92 employees (9 to 100) who report to employee 8.
- Round 4 finds nobody who reports to anyone in round 3, so recursion stops.

That gives 100 rows at depths 1, 2 and 3. The `path` array records the chain
from the root, such as `{1,8,10}`, and doubles as a **cycle guard**: the
recursive member refuses any employee already in the path, so even corrupted
data where someone manages their own manager cannot loop forever.

Recursion also works without a table. Example 2 starts from the first day of
the current month and subtracts one month per round, while a counter `n`
stops it after 12 rounds. Either a data limit (no more children) or an
explicit counter must end every recursive query you write.

Both members must produce the same column types. Example 2 casts
`(m - interval '1 month')` back to `date`; without that cast PostgreSQL
rejects the query because the recursive member would yield `timestamp`.

## Two worked SQL examples

### Example 1

```sql
WITH RECURSIVE org AS (
  SELECT
    e.employee_id,
    e.full_name,
    e.manager_id,
    1 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    e.employee_id,
    e.full_name,
    e.manager_id,
    o.depth + 1,
    o.path || e.employee_id
  FROM
    employees e
    JOIN org o ON e.manager_id = o.employee_id
    -- A path is evidence of traversal and a guard against malformed cycles.
  WHERE
    NOT e.employee_id = ANY (o.path))
SELECT
  employee_id,
  full_name,
  manager_id,
  depth,
  path
FROM
  org
ORDER BY
  depth,
  full_name,
  employee_id
LIMIT 100;
```

**How to read it:** The anchor selects the six roots with `depth` 1 and
a one-element `path`. The recursive member joins `employees` to the previous
round on `e.manager_id = o.employee_id`, adds 1 to `depth`, appends the new id
with `||` and skips anyone already in `o.path`. The outer query sorts by
depth, then by the text value of `full_name`, then by `employee_id`.

**Expected result/shape:** Exactly 100 rows, one per employee, so the
`LIMIT 100` cuts nothing. Rows 1 to 6 are the roots with `manager_id` blank
and paths `{1}` to `{6}`; then Employee 7 with path `{2,7}` and Employee 8
with `{1,8}`; then 92 depth-3 rows whose paths all start `{1,8,...}`. Because
names sort as text, the depth-3 block begins Employee 10, Employee 100,
Employee 11 rather than in numeric order.

### Example 2

```sql
WITH RECURSIVE months AS (
  SELECT
    date_trunc('month', CURRENT_DATE)::date AS m,
    1 AS n
  UNION ALL
  SELECT
    (m - interval '1 month')::date,
    n + 1
  FROM
    months
  WHERE
    n < 12
)
SELECT
  m AS month_start,
  n AS step
FROM
  months
ORDER BY
  month_start;
```

**How to read it:** The anchor is a single row: the first of the
current month as a `date`, with step `n` = 1. Each round subtracts one month
and adds 1 to `n`, and `WHERE n < 12` stops the recursive member from
producing a thirteenth row. There is no source table, so the counter is the
only thing that ends the recursion.

**Expected result/shape:** 12 rows. Sorted by `month_start`, the
earliest month comes first with `step` 12 and the current month is last with
`step` 1. The dates depend on the day you run it, but they are always first
days of consecutive months.

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
- **Review loop:** run the anchor alone and count its rows (6 roots), then
  add the recursive member and check the row count per depth (6, 2 and 92)
  before adding ordering or aggregation.

## Exercises

Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.

Before running Exercises 1, 5 and 6, sketch the three-level org chart
from the mental model and count the rows each query should return. For
Exercise 4, draw the four edges and list the paths the guard should allow;
Exercises 2 and 3 should return 1 row and 12 rows.

1. **Query writing:** List every manager's direct and indirect reports with depth and path.
   **Progressive hint:** Seed every direct edge, carry the original manager, and reject IDs already in the path.
   **Inputs/evidence:** For sql-24 Exercise 1, read `employees` twice in the anchor, joining each report to its manager on `report.manager_id = manager.employee_id` (94 direct pairs), then join the recursive `reports` CTE back to `employees` on `report.manager_id = r.report_id`, appending to `path` and refusing any `employee_id` already in it.
   **Expected result/shape:** For sql-24 Exercise 1, expected output: 186 rows, 94 at depth 1 and 92 at depth 2, for only three managers: employee 1 with 93 reports, employee 8 with 92, and employee 2 with 1. The final columns are `manager_id`, `report_id`, `depth`, and `path`. The final order is `manager_id, depth, report_id`.
   **Verify:** For sql-24 Exercise 1, confirm the 94 depth-1 rows match `SELECT COUNT(*) FROM employees WHERE manager_id IS NOT NULL` and that all 92 depth-2 rows belong to manager 1 with a `path` starting `{1,8}`; then, inside `BEGIN ... ROLLBACK`, run `UPDATE employees SET manager_id = 9 WHERE employee_id = 1` to close the loop 1, 8, 9, 1 and confirm the query still finishes, now with 280 rows and a maximum depth of 3.
2. **Query writing:** Generate integers 1 through 100 recursively and return their sum.
   **Progressive hint:** Anchor at 1 and stop producing rows after 100.
   **Inputs/evidence:** For sql-24 Exercise 2, no table is read: the recursive `numbers` CTE starts from `VALUES (1)` and adds `n + 1` while `n < 100`, and the outer query applies one `SUM` with no `GROUP BY`.
   **Expected result/shape:** For sql-24 Exercise 2, expected output: exactly one row, `sum_1_to_100` = 5050. The final columns are `sum_1_to_100`.
   **Verify:** For sql-24 Exercise 2, compare with the non-recursive control `SELECT SUM(n) FROM generate_series(1, 100) AS n`, which also returns 5050, and add `COUNT(*)` to see exactly 100 generated rows; then change the stop test to `n <= 100` and confirm the CTE produces 101 rows and a sum of 5151, the classic off-by-one in a recursive stop condition.
3. **Query writing:** Generate the first day of the current and prior 11 months recursively.
   **Progressive hint:** Carry a counter as an explicit termination condition.
   **Inputs/evidence:** For sql-24 Exercise 3, no table is read: the recursive `months` CTE starts at `date_trunc('month', CURRENT_DATE)::date` with `step` 1 and subtracts `INTERVAL '1 month'` while `step < 12`, so the result moves with the run date.
   **Expected result/shape:** For sql-24 Exercise 3, expected output: exactly 12 rows, all on day 1 of a month, from 11 months before the current month up to the current month (2025-12-01 through 2026-11-01 when run in November 2026). The final columns are `month_start`. The final order is `month_start`.
   **Verify:** For sql-24 Exercise 3, confirm `COUNT(*)` is 12, `COUNT(DISTINCT month_start)` is 12, `MAX(month_start)` equals `date_trunc('month', CURRENT_DATE)::date`, and no row fails `EXTRACT(DAY FROM month_start) = 1`; then start the same recursion from `DATE '2026-03-31'` without `date_trunc` and see the values drift to 2026-02-28 and 2026-01-28, which is why the anchor truncates first.
4. **Prediction:** Traverse a local graph containing a cycle and prove a path-array guard terminates.
   **Progressive hint:** Reject a destination already present in the path before adding it.
   **Inputs/evidence:** For sql-24 Exercise 4, no table is read: the `edges` CTE holds four `VALUES` pairs, (1, 2), (2, 3), (3, 1), and (2, 4), with the cycle 1, 2, 3, 1; the recursive `walk` CTE starts at `VALUES (1, ARRAY[1])` and follows edges while `NOT e.destination = ANY (w.path)`.
   **Expected result/shape:** For sql-24 Exercise 4, expected output: exactly 4 rows, `{1}`, `{1,2}`, `{1,2,3}`, and `{1,2,4}`, with nodes 1, 2, 3, and 4; the edge from 3 back to 1 is never taken. The final columns are `node`, and `path`. The final order is `array_length(path, 1), path`.
   **Verify:** For sql-24 Exercise 4, confirm no `path` repeats a node, for example `SELECT COUNT(*) FROM walk WHERE array_length(path, 1) <> (SELECT COUNT(DISTINCT x) FROM unnest(path) AS x)` returns 0; then replace the path guard with a depth cap `array_length(w.path, 1) < 5` and confirm two extra rows, `{1,2,3,1}` and `{1,2,3,1,2}`, revisit node 1, so only the `ANY (path)` guard makes the walk end on its own.
5. **Debugging:** Walk upward from every employee to ancestors while preventing cycles.
   **Progressive hint:** The recursive step follows current manager ID to the manager row and appends it to path.
   **Inputs/evidence:** For sql-24 Exercise 5, read `employees`: the anchor takes the 94 rows with a non-NULL `manager_id`, and the recursive `ancestors` CTE joins `employees` as `manager` on `manager.employee_id = a.ancestor_id`, climbing while `manager.manager_id IS NOT NULL` and the manager is not already in `path`.
   **Expected result/shape:** For sql-24 Exercise 5, expected output: 186 rows for 94 origin employees, 94 at depth 1 and 92 at depth 2; employee 9 has ancestor 8 at depth 1 and ancestor 1 at depth 2, while employee 8 has only ancestor 1. The final columns are `origin_employee_id`, `ancestor_id`, and `depth`. The final order is `origin_employee_id, depth`.
   **Verify:** For sql-24 Exercise 5, confirm `COUNT(DISTINCT origin_employee_id)` is 94, matching `SELECT COUNT(*) FROM employees WHERE manager_id IS NOT NULL`, and that removing the outer `ancestor_id IS NOT NULL` filter leaves 186 rows; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm the query returns 374 rows with a maximum depth of 4, and that employee 1 now lists ancestors 9, 8, and itself at depths 1, 2, and 3.
6. **Extension:** Summarize employee count by hierarchy depth from all roots.
   **Progressive hint:** Build the guarded root traversal first, then aggregate only after depth is assigned.
   **Inputs/evidence:** For sql-24 Exercise 6, read `employees`: the anchor of the recursive `organization` CTE takes the 6 roots with `manager_id IS NULL` at depth 0, the recursive step joins children on `child.manager_id = parent.employee_id`, and the outer query counts rows per `depth`.
   **Expected result/shape:** For sql-24 Exercise 6, expected output: exactly 3 rows, depth 0 with 6 employees, depth 1 with 2, and depth 2 with 92. The final columns are `depth`, and `employee_count`. The final order is `depth`.
   **Verify:** For sql-24 Exercise 6, confirm the counts add to 100, matching `SELECT COUNT(*) FROM employees`, and that the depth-1 count of 2 matches `SELECT COUNT(*) FROM employees WHERE manager_id IN (SELECT employee_id FROM employees WHERE manager_id IS NULL)`; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm only 6 employees remain (5 at depth 0, 1 at depth 1), because the 94 people in the loop through employee 1 no longer hang from any root.

## Common mistakes and how to recover

- **Leaving out the cycle guard.** Exercise 4's graph has the loop 1, 2, 3, 1.
  Without `NOT e.destination = ANY (w.path)`, the walk keeps producing rows
  such as `{1,2,3,1,2,3}` forever; with an outer `LIMIT 8` you can watch it
  repeat, but without one `psql` never returns.
- **Expecting `UNION` to stop a loop.** `UNION` removes duplicate rows, but a
  row that carries a growing path is never a duplicate. It only stops
  recursion when the row is just the node, and then you lose the path.
- **Mismatched anchor and recursive types.** Dropping the `::date` cast in
  Example 2 raises `recursive query "months" column 1 has type date in
  non-recursive term but type timestamp without time zone overall`. Cast the
  anchor or the recursive member so both agree.
- **Starting from the wrong anchor.** An anchor of `manager_id IS NULL` walks
  down from roots; an anchor of `manager_id IS NOT NULL` walks up from each
  employee, as Exercise 5 does. Mixing the two directions in one query
  produces pairs that are neither ancestors nor reports.
- **Letting `NULL` managers into the result.** In Exercise 5, removing
  `manager.manager_id IS NOT NULL` from the recursive member adds 94 rows with
  a `NULL` ancestor (280 instead of 186) before the outer filter removes them.
- General recovery steps, such as cancelling a run and rerunning the full
  file, are in
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

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

Further reading
- WITH RECURSIVE: https://www.postgresql.org/docs/17/queries-with.html#QUERIES-WITH-RECURSIVE
- Tree traversal recipes: https://wiki.postgresql.org/wiki/Hierarchical_queries

## Ask an AI tutor about this lesson

A tutor works well for tracing recursion round by round: ask it to
stop after each round and let you predict the next rows. Keep it on the guide
and learner file using the prompt below
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-24: Recursive CTEs for Hierarchies and Graphs.

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
