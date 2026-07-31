# Day 05 solutions — CROSS and SELF JOINs: Combinatorics and Relationships to Self


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day05_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day05_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Cartesian product, Self-join, Canonical pair. Its worked-model focus is:
For product pairs, compare p1.productid <> p2.productid with p1.productid < p2.productid. The first produces both (A,B) and (B,A); the second removes reversed duplicates and self-pairs in one predicate.

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

These answers align one-for-one with [day05_cross_self_joins.sql](../day05_cross_self_joins.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
- **Assumptions:** The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
- **Primary pitfall:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** List every employee with their direct manager when present.

**Reasoning:** Self join employees and use a left join so top-level employees remain visible.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.full_name AS employee_name,
       m.employee_id AS manager_id,
       m.full_name AS manager_name
FROM employees AS e
LEFT JOIN employees AS m
  ON m.employee_id = e.manager_id
ORDER BY e.employee_id;
```

**Expected shape:** One row per employee.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 1, read from `employees`. Build the answer toward `employee_id`, `employee_name`, `manager_id`, and `manager_name`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-05 Exercise 1, expected output: One row per employee. The final columns are `employee_id`, `employee_name`, `manager_id`, and `manager_name`. The final order is `e.employee_id`.
- **Independent verification:** For sql-05 Exercise 1, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `employee_name`, `manager_id`, and `manager_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
- **Intermediate relation check:** For sql-05 Exercise 1, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-05 Exercise 1, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `employee_name`, `manager_id`, and `manager_name` ordered by `e.employee_id`.
- **Alternative/trade-off:** For sql-05 Exercise 1, the chosen form is justified by this lesson-specific rationale: Self join employees and use a left join so top-level employees remain visible. Evaluate another form against the concrete expected result (One row per employee) and the verification above.
- **Edge case:** Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.

## Exercise 2 — Query writing

**Prompt:** Find employees who manage nobody.

**Reasoning:** Left join candidate managers to reports and retain managers with no right-side match.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.full_name
FROM employees AS e
LEFT JOIN employees AS report
  ON report.manager_id = e.employee_id
WHERE report.employee_id IS NULL
ORDER BY e.employee_id;
```

**Expected shape:** One row per leaf employee.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 2, read from `employees`. Build the answer toward `employee_id`, and `full_name`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-05 Exercise 2, expected output: One row per leaf employee. The final columns are `employee_id`, and `full_name`. The final order is `e.employee_id`.
- **Independent verification:** For sql-05 Exercise 2, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, and `full_name` values match those staged rows without unintended fanout or loss. Add one row for which `(report.employee_id IS NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.
- **Intermediate relation check:** For sql-05 Exercise 2, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-05 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, and `full_name` ordered by `e.employee_id`.
- **Alternative/trade-off:** For sql-05 Exercise 2, the chosen form is justified by this lesson-specific rationale: Left join candidate managers to reports and retain managers with no right-side match. Evaluate another form against the concrete expected result (One row per leaf employee) and the verification above.
- **Edge case:** Add one row for which `(report.employee_id IS NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.

## Exercise 3 — Query writing

**Prompt:** Build a complete grid of six recent months and all expense categories.

**Reasoning:** Cross join two small declared dimensions; do not cross join raw fact tables.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH months AS (
  SELECT generate_series(
           date_trunc('month', CURRENT_DATE) - INTERVAL '5 months',
           date_trunc('month', CURRENT_DATE),
           INTERVAL '1 month'
         )::date AS month_start
), categories AS (
  SELECT DISTINCT e.category
  FROM expenses AS e
)
SELECT c.category,
       m.month_start
FROM categories AS c
CROSS JOIN months AS m
ORDER BY c.category, m.month_start;
```

**Expected shape:** Six rows per distinct expense category.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 3, read from `expenses`. Build the answer toward `category`, and `month_start`; keep `category` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-05 Exercise 3, expected output: Six rows per distinct expense category. The final columns are `category`, and `month_start`. The final order is `c.category, m.month_start`.
- **Independent verification:** For sql-05 Exercise 3, project `category` plus the raw source columns from `expenses` at each join stage; record row count and distinct `category`, then assert the final `category`, and `month_start` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
- **Intermediate relation check:** For sql-05 Exercise 3, run `months`, and `categories` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
- **Clause check:** For sql-05 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `expenses`, preserve one row per `category`, and finish with `category`, and `month_start` ordered by `c.category, m.month_start`.
- **Alternative/trade-off:** For sql-05 Exercise 3, the chosen form is justified by this lesson-specific rationale: Cross join two small declared dimensions; do not cross join raw fact tables. Evaluate another form against the concrete expected result (Six rows per distinct expense category) and the verification above.
- **Edge case:** Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.

## Exercise 4 — Prediction

**Prompt:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.

**Reasoning:** Cross-join cardinality is the product of input row counts.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.

```sql
WITH months AS (
  SELECT generate_series(1, 12) AS month_number
)
SELECT COUNT(*) AS department_month_combinations
FROM departments AS d
CROSS JOIN months AS m;
```

**Expected shape:** One row containing 72.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 4, read from `departments`. Build the answer toward `department_month_combinations`; keep `department_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-05 Exercise 4, expected output: One row containing 72. The final columns are `department_month_combinations`.
- **Independent verification:** For sql-05 Exercise 4, project `department_id` plus the raw source columns from `departments` at each join stage; record row count and distinct `department_id`, then assert the final `department_month_combinations` values match those staged rows without unintended fanout or loss. Add one source row with a new `department_id`; verify the result gains exactly one row carrying that `department_id` value.
- **Intermediate relation check:** For sql-05 Exercise 4, run `months` one at a time. Record each CTE's row count and `department_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-05 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, and `SELECT`. Read only those operations: begin at `departments`, preserve one row per `department_id`, and finish with `department_month_combinations`.
- **Alternative/trade-off:** For sql-05 Exercise 4, the chosen form is justified by this lesson-specific rationale: Cross-join cardinality is the product of input row counts. Evaluate another form against the concrete expected result (One row containing 72) and the verification above.
- **Edge case:** Add one source row with a new `department_id`; verify the result gains exactly one row carrying that `department_id` value.

## Exercise 5 — Debugging

**Prompt:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.

**Reasoning:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT left_employee.department_id,
       left_employee.employee_id AS first_employee_id,
       right_employee.employee_id AS second_employee_id
FROM employees AS left_employee
JOIN employees AS right_employee
  ON right_employee.department_id = left_employee.department_id
 AND left_employee.employee_id < right_employee.employee_id
ORDER BY left_employee.department_id,
         left_employee.employee_id,
         right_employee.employee_id;
```

**Expected shape:** One row per unordered same-department pair.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 5, read from `employees` twice at employee grain. Build the answer toward `department_id`, `first_employee_id`, and `second_employee_id`; keep all three columns visible as the composite pair key.
- **Expected result/shape:** For sql-05 Exercise 5, expected output: One row per unordered same-department pair. The final columns are `department_id`, `first_employee_id`, and `second_employee_id`. The final order is `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
- **Independent verification:** For sql-05 Exercise 5, assert `first_employee_id < second_employee_id` for every row, require uniqueness of (`department_id`, `first_employee_id`, `second_employee_id`), and anti-check for both self-pairs and mirrored `(a, b)` / `(b, a)` pairs. For each department with `n` employees, independently require `n * (n - 1) / 2` result rows.
- **Intermediate relation check:** For sql-05 Exercise 5, start with the first relation in `employees`; after each join, record total rows and distinct `department_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-05 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `department_id`, and finish with `department_id`, `first_employee_id`, and `second_employee_id` ordered by `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
- **Alternative/trade-off:** For sql-05 Exercise 5, the chosen form is justified by this lesson-specific rationale: Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule. Evaluate another form against the concrete expected result (One row per unordered same-department pair) and the verification above.
- **Edge case:** Add duplicate source candidates for `department_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 6 — Extension

**Prompt:** Show each employee, their manager, and their manager's manager.

**Reasoning:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.employee_id,
       e.full_name AS employee_name,
       manager.full_name AS manager_name,
       grandmanager.full_name AS grandmanager_name
FROM employees AS e
LEFT JOIN employees AS manager
  ON manager.employee_id = e.manager_id
LEFT JOIN employees AS grandmanager
  ON grandmanager.employee_id = manager.manager_id
ORDER BY e.employee_id;
```

**Expected shape:** One row per employee with up to two ancestor columns.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-05 Exercise 6, read from `employees`. Build the answer toward `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`; keep `employee_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-05 Exercise 6, expected output: One row per employee with up to two ancestor columns. The final columns are `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`. The final order is `e.employee_id`.
- **Independent verification:** For sql-05 Exercise 6, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
- **Intermediate relation check:** For sql-05 Exercise 6, start with the first relation in `employees`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-05 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `employees`, preserve one row per `employee_id`, and finish with `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name` ordered by `e.employee_id`.
- **Alternative/trade-off:** For sql-05 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use two independently aliased left self joins; NULLs indicate the hierarchy ends. Evaluate another form against the concrete expected result (One row per employee with up to two ancestor columns) and the verification above.
- **Edge case:** Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
