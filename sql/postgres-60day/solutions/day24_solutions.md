# Day 24 solutions — Recursive CTEs: Hierarchies, Trees, and Graph Walks


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day24_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day24_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Anchor member, Recursive member, Cycle guard. Its worked-model focus is:
Seed each direct manager/report edge with a path array containing both keys. Each recursive step joins the current report to its direct reports, increments depth, and rejects a key already present in the path. Inspect the maximum depth and path before trusting the hierarchy.

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

These answers align one-for-one with [day24_recursive_ctes.sql](../day24_recursive_ctes.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
- **Assumptions:** Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
- **Primary pitfall:** `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List every manager's direct and indirect reports with depth and path.

**Reasoning:** Seed every direct edge, carry the original manager, and reject IDs already in the path.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH RECURSIVE reports AS (
  SELECT manager.employee_id AS manager_id,
         report.employee_id AS report_id,
         1 AS depth,
         ARRAY[manager.employee_id, report.employee_id] AS path
  FROM employees AS manager
  JOIN employees AS report
    ON report.manager_id = manager.employee_id
  UNION ALL
  SELECT r.manager_id,
         report.employee_id,
         r.depth + 1,
         r.path || report.employee_id
  FROM reports AS r
  JOIN employees AS report
    ON report.manager_id = r.report_id
  WHERE NOT report.employee_id = ANY(r.path)
)
SELECT manager_id,
       report_id,
       depth,
       path
FROM reports
ORDER BY manager_id, depth, report_id;
```

**Expected shape:** One row per ancestor-descendant pair.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 1, read from `employees`, and `reports`. Build the answer toward `manager_id`, `report_id`, `depth`, and `path`; keep `manager_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-24 Exercise 1, expected output: One row per ancestor-descendant pair. The final columns are `manager_id`, `report_id`, `depth`, and `path`. The final order is `manager_id, depth, report_id`.
- **Independent verification:** For sql-24 Exercise 1, project `manager_id` plus the raw source columns from `employees`, and `reports` at each join stage; record row count and distinct `manager_id`, then assert the final `manager_id`, `report_id`, `depth`, and `path` values match those staged rows without unintended fanout or loss. Add one source row with a new `manager_id`; verify the result gains exactly one row carrying that `manager_id` value.
- **Intermediate relation check:** For sql-24 Exercise 1, start with the first relation in `employees`, and `reports`; after each join, record total rows and distinct `manager_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-24 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, and `reports`, preserve one row per `manager_id`, and finish with `manager_id`, `report_id`, `depth`, and `path` ordered by `manager_id, depth, report_id`.
- **Alternative/trade-off:** For sql-24 Exercise 1, the chosen form is justified by this lesson-specific rationale: Seed every direct edge, carry the original manager, and reject IDs already in the path. Evaluate another form against the concrete expected result (One row per ancestor-descendant pair) and the verification above.
- **Edge case:** Add one source row with a new `manager_id`; verify the result gains exactly one row carrying that `manager_id` value.

## Exercise 2 — Query writing

**Prompt:** Generate integers 1 through 100 recursively and return their sum.

**Reasoning:** Anchor at 1 and stop producing rows after 100.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.

```sql
WITH RECURSIVE numbers(n) AS (
  VALUES (1)
  UNION ALL
  SELECT n + 1
  FROM numbers
  WHERE n < 100
)
SELECT SUM(n) AS sum_1_to_100
FROM numbers;
```

**Expected shape:** Exactly one row with 5050.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 2, read from `numbers`. Compute `sum_1_to_100` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-24 Exercise 2, expected output: Exactly one row with 5050. The final columns are `sum_1_to_100`.
- **Independent verification:** For sql-24 Exercise 2, evaluate each of `sum_1_to_100` in a separate control `SELECT` over `numbers`; require one final row and compare every value. Force the final predicate to match zero rows and record `sum_1_to_100`; distinguish `COUNT` zero from nullable `SUM` or `AVG` results.
- **Intermediate relation check:** For sql-24 Exercise 2, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-24 Exercise 2, the solution actually uses `WITH`, `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `numbers`, preserve exactly one summary row, and finish with `sum_1_to_100`.
- **Alternative/trade-off:** For sql-24 Exercise 2, the chosen form is justified by this lesson-specific rationale: Anchor at 1 and stop producing rows after 100. Evaluate another form against the concrete expected result (Exactly one row with 5050) and the verification above.
- **Edge case:** Force the final predicate to match zero rows and record `sum_1_to_100`; distinguish `COUNT` zero from nullable `SUM` or `AVG` results.

## Exercise 3 — Query writing

**Prompt:** Generate the first day of the current and prior 11 months recursively.

**Reasoning:** Carry a counter as an explicit termination condition.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH RECURSIVE months(month_start, step) AS (
  SELECT date_trunc('month', CURRENT_DATE)::date, 1
  UNION ALL
  SELECT (month_start - INTERVAL '1 month')::date, step + 1
  FROM months
  WHERE step < 12
)
SELECT month_start
FROM months
ORDER BY month_start;
```

**Expected shape:** Exactly 12 chronological month rows.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 3, read from `months`. Build the answer toward `month_start`; keep `month_start` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-24 Exercise 3, expected output: Exactly 12 chronological month rows. The final columns are `month_start`. The final order is `month_start`.
- **Independent verification:** For sql-24 Exercise 3, reselect the returned keys directly from the source; require unique `month_start` where the expected grain is one row per key and confirm the projected `month_start` against `months`. Tie two rows on `month_start` and give them different `month_start` values; verify `month_start` chooses a stable first/last row.
- **Intermediate relation check:** For sql-24 Exercise 3, inspect the source keys that survive `WHERE`; then check `month_start` before applying the row cap.
- **Clause check:** For sql-24 Exercise 3, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `months`, preserve one row per `month_start`, and finish with `month_start` ordered by `month_start`.
- **Alternative/trade-off:** For sql-24 Exercise 3, the chosen form is justified by this lesson-specific rationale: Carry a counter as an explicit termination condition. Evaluate another form against the concrete expected result (Exactly 12 chronological month rows) and the verification above.
- **Edge case:** Tie two rows on `month_start` and give them different `month_start` values; verify `month_start` chooses a stable first/last row.

## Exercise 4 — Prediction

**Prompt:** Traverse a local graph containing a cycle and prove a path-array guard terminates.

**Reasoning:** Reject a destination already present in the path before adding it.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH RECURSIVE edges(source, destination) AS (
  VALUES (1, 2), (2, 3), (3, 1), (2, 4)
), walk(node, path) AS (
  VALUES (1, ARRAY[1])
  UNION ALL
  SELECT e.destination,
         w.path || e.destination
  FROM walk AS w
  JOIN edges AS e
    ON e.source = w.node
  WHERE NOT e.destination = ANY(w.path)
)
SELECT node, path
FROM walk
ORDER BY array_length(path, 1), path;
```

**Expected shape:** Finite paths starting from node 1; no repeated node inside a path.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 4, read from `walk`, and `edges`. Build the answer toward `node`, and `path`; keep `node` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-24 Exercise 4, expected output: Finite paths starting from node 1; no repeated node inside a path. The final columns are `node`, and `path`. The final order is `array_length(path, 1), path`.
- **Independent verification:** For sql-24 Exercise 4, project `node` plus the raw source columns from `walk`, and `edges` at each join stage; record row count and distinct `node`, then assert the final `node`, and `path` values match those staged rows without unintended fanout or loss. Add one source row with a new `node`; verify the result gains exactly one row carrying that `node` value.
- **Intermediate relation check:** For sql-24 Exercise 4, start with the first relation in `walk`, and `edges`; after each join, record total rows and distinct `node` so the exact fanout or loss is visible.
- **Clause check:** For sql-24 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `walk`, and `edges`, preserve one row per `node`, and finish with `node`, and `path` ordered by `array_length(path, 1), path`.
- **Alternative/trade-off:** For sql-24 Exercise 4, the chosen form is justified by this lesson-specific rationale: Reject a destination already present in the path before adding it. Evaluate another form against the concrete expected result (Finite paths starting from node 1; no repeated node inside a path) and the verification above.
- **Edge case:** Add one source row with a new `node`; verify the result gains exactly one row carrying that `node` value.

## Exercise 5 — Debugging

**Prompt:** Walk upward from every employee to ancestors while preventing cycles.

**Reasoning:** The recursive step follows current manager ID to the manager row and appends it to path.

**Clause-by-clause reading:**

- `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH RECURSIVE ancestors AS (
  SELECT e.employee_id AS origin_employee_id,
         e.manager_id AS ancestor_id,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NOT NULL
  UNION ALL
  SELECT a.origin_employee_id,
         manager.manager_id,
         a.depth + 1,
         a.path || manager.employee_id
  FROM ancestors AS a
  JOIN employees AS manager
    ON manager.employee_id = a.ancestor_id
  WHERE manager.manager_id IS NOT NULL
    AND NOT manager.employee_id = ANY(a.path)
)
SELECT origin_employee_id,
       ancestor_id,
       depth
FROM ancestors
WHERE ancestor_id IS NOT NULL
ORDER BY origin_employee_id, depth;
```

**Expected shape:** One row per employee-ancestor relation.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 5, read from `employees`, and `ancestors`. Build the answer toward `origin_employee_id`, `ancestor_id`, and `depth`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-24 Exercise 5, expected output: One row per employee-ancestor relation. The final columns are `origin_employee_id`, `ancestor_id`, and `depth`. The final order is `origin_employee_id, depth`.
- **Independent verification:** For sql-24 Exercise 5, project `employee_id` plus the raw source columns from `employees`, and `ancestors` at each join stage; record row count and distinct `employee_id`, then assert the final `origin_employee_id`, `ancestor_id`, and `depth` values match those staged rows without unintended fanout or loss. Add one row for which `(ancestor_id IS NOT NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.
- **Intermediate relation check:** For sql-24 Exercise 5, start with the first relation in `employees`, and `ancestors`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-24 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, and `ancestors`, preserve one row per `employee_id`, and finish with `origin_employee_id`, `ancestor_id`, and `depth` ordered by `origin_employee_id, depth`.
- **Alternative/trade-off:** For sql-24 Exercise 5, the chosen form is justified by this lesson-specific rationale: The recursive step follows current manager ID to the manager row and appends it to path. Evaluate another form against the concrete expected result (One row per employee-ancestor relation) and the verification above.
- **Edge case:** Add one row for which `(ancestor_id IS NOT NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.

## Exercise 6 — Extension

**Prompt:** Summarize employee count by hierarchy depth from all roots.

**Reasoning:** Build the guarded root traversal first, then aggregate only after depth is assigned.

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
         0 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT child.employee_id,
         child.manager_id,
         parent.depth + 1,
         parent.path || child.employee_id
  FROM organization AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  WHERE NOT child.employee_id = ANY(parent.path)
)
SELECT depth,
       COUNT(*) AS employee_count
FROM organization
GROUP BY depth
ORDER BY depth;
```

**Expected shape:** One row per observed depth.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-24 Exercise 6, read from `employees`, and `organization`. Build the answer toward `depth`, and `employee_count`; keep `depth` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-24 Exercise 6, expected output: One row per observed depth. The final columns are `depth`, and `employee_count`. The final order is `depth`.
- **Independent verification:** For sql-24 Exercise 6, independently aggregate `employees`, and `organization` by `depth`; require one output row for every distinct `depth` tuple and compare `employee_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `employee_count` for the existing `depth` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-24 Exercise 6, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `depth` so the exact fanout or loss is visible.
- **Clause check:** For sql-24 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, and `organization`, preserve one row per `depth`, and finish with `depth`, and `employee_count` ordered by `depth`.
- **Alternative/trade-off:** For sql-24 Exercise 6, the chosen form is justified by this lesson-specific rationale: Build the guarded root traversal first, then aggregate only after depth is assigned. Evaluate another form against the concrete expected result (One row per observed depth) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `employee_count` for the existing `depth` tuple and verify the new tuple appears exactly once.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
