# Day 24 solutions — Recursive CTEs: Hierarchies, Trees, and Graph Walks

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

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
