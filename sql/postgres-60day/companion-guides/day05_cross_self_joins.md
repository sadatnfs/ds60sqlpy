# Day 05 — CROSS and SELF JOINs: Combinatorics and Relationships to Self (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 04 — outer joins](day04_outer_joins.md)
- **Artifacts:** [learner SQL](../day05_cross_self_joins.sql) ·
  [solution reasoning](../solutions/day05_solutions.md) ·
  [executable solution](../solutions/day05_solutions.sql)

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

2. Open **SQL-05 — Cross Self Joins** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-05/lesson/workspace/sql/postgres-60day/day05_cross_self_joins.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day05_cross_self_joins.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day05_cross_self_joins.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Cartesian product, Self-join, Canonical pair. Its worked SQL reads or creates `products`, `customers`, `employees`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: For product pairs, compare p1.productid <> p2.productid with p1.productid < p2.productid. The first produces both (A,B) and (B,A); the second removes reversed duplicates and self-pairs in one predicate.
The expected contract is that One row per employee. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day05_cross_self_joins.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH cats AS (
  SELECT DISTINCT category FROM products
), ctries AS (
  SELECT DISTINCT country FROM customers
)
SELECT cats.category, ctries.country
FROM cats CROSS JOIN ctries
ORDER BY 1,2;
```

**How to read it:** Example 1: Start with `products`, and `customers` in `FROM`/`JOIN`. The final `SELECT` displays `category`, and `country`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `category`, and `country` with columns `category`, and `country` from `products`, and `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT e.employee_id, e.full_name AS employee, m.full_name AS manager
FROM employees e
LEFT JOIN employees m ON m.employee_id = e.manager_id
ORDER BY manager NULLS FIRST,
         m.employee_id NULLS FIRST,
         employee,
         e.employee_id
LIMIT 50;
```

**How to read it:** Example 2: Start with `employees` in `FROM`/`JOIN`. The final `SELECT` displays `employee_id`, `employee`, and `manager`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `employee_id`, capped at 50 rows with columns `employee_id`, `employee`, and `manager` from `employees`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Generate intentional combinations with `CROSS JOIN`.
- Traverse same-table relationships with distinct aliases and generate each
  unordered pair exactly once.

## Vocabulary and concepts

- **Cartesian product:** every possible left/right row combination.
- **Self-join:** joining a relation to another alias of itself.
- **Canonical pair:** one stable representation, such as `a.id < b.id`, for an
  unordered pair.

## Worked example / walkthrough

For product pairs, compare `p1.product_id <> p2.product_id` with
`p1.product_id < p2.product_id`. The first produces both `(A,B)` and `(B,A)`;
the second removes reversed duplicates and self-pairs in one predicate.

## Practice assumptions and review method

- **Focus:** Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
- **Assumptions:** The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
- **Failure to watch for:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List every employee with their direct manager when present.
   **Progressive hint:** Self join employees and use a left join so top-level employees remain visible.
   **Inputs/evidence:** For sql-05 Exercise 1, read from `employees`. Build the answer toward `employee_id`, `employee_name`, `manager_id`, and `manager_name`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-05 Exercise 1, expected output: One row per employee. The final columns are `employee_id`, `employee_name`, `manager_id`, and `manager_name`. The final order is `e.employee_id`.
   **Verify:** For sql-05 Exercise 1, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `employee_name`, `manager_id`, and `manager_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
2. **Query writing:** Find employees who manage nobody.
   **Progressive hint:** Left join candidate managers to reports and retain managers with no right-side match.
   **Inputs/evidence:** For sql-05 Exercise 2, read from `employees`. Build the answer toward `employee_id`, and `full_name`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-05 Exercise 2, expected output: One row per leaf employee. The final columns are `employee_id`, and `full_name`. The final order is `e.employee_id`.
   **Verify:** For sql-05 Exercise 2, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, and `full_name` values match those staged rows without unintended fanout or loss. Add one row for which `(report.employee_id IS NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.
3. **Query writing:** Build a complete grid of six recent months and all expense categories.
   **Progressive hint:** Cross join two small declared dimensions; do not cross join raw fact tables.
   **Inputs/evidence:** For sql-05 Exercise 3, read from `expenses`. Build the answer toward `category`, and `month_start`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-05 Exercise 3, expected output: Six rows per distinct expense category. The final columns are `category`, and `month_start`. The final order is `c.category, m.month_start`.
   **Verify:** For sql-05 Exercise 3, project `category` plus the raw source columns from `expenses` at each join stage; record row count and distinct `category`, then assert the final `category`, and `month_start` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
4. **Prediction:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
   **Progressive hint:** Cross-join cardinality is the product of input row counts.
   **Inputs/evidence:** For sql-05 Exercise 4, read from `departments`. Build the answer toward `department_month_combinations`; keep `department_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-05 Exercise 4, expected output: One row containing 72. The final columns are `department_month_combinations`.
   **Verify:** For sql-05 Exercise 4, project `department_id` plus the raw source columns from `departments` at each join stage; record row count and distinct `department_id`, then assert the final `department_month_combinations` values match those staged rows without unintended fanout or loss. Add one source row with a new `department_id`; verify the result gains exactly one row carrying that `department_id` value.
5. **Debugging:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.
   **Progressive hint:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
   **Inputs/evidence:** For sql-05 Exercise 5, read from `employees` twice at employee grain. Build the answer toward `department_id`, `first_employee_id`, and `second_employee_id`; keep all three columns visible as the composite pair key.
   **Expected result/shape:** For sql-05 Exercise 5, expected output: One row per unordered same-department pair. The final columns are `department_id`, `first_employee_id`, and `second_employee_id`. The final order is `left_employee.department_id, left_employee.employee_id, right_employee.employee_id`.
   **Verify:** For sql-05 Exercise 5, assert `first_employee_id < second_employee_id` for every row, require uniqueness of (`department_id`, `first_employee_id`, `second_employee_id`), and anti-check for both self-pairs and mirrored `(a, b)` / `(b, a)` pairs. For each department with `n` employees, independently require `n * (n - 1) / 2` result rows.
6. **Extension:** Show each employee, their manager, and their manager's manager.
   **Progressive hint:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
   **Inputs/evidence:** For sql-05 Exercise 6, read from `employees`. Build the answer toward `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-05 Exercise 6, expected output: One row per employee with up to two ancestor columns. The final columns are `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name`. The final order is `e.employee_id`.
   **Verify:** For sql-05 Exercise 6, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `employee_name`, `manager_name`, and `grandmanager_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.
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

- Does every table instance have a clear alias and role?
- Can you prove the pair query contains neither self-pairs nor reversed
  duplicates?

## Next step

Continue to [Day 06 — set operations](day06_set_operations.md).

## Deep dive and reference

Learning objectives
- Use CROSS JOIN to form Cartesian products intentionally
- Write self-joins to compare rows within the same table
- Generate pairs and ensure de-duplication (i<j pattern)

Why this matters
Some analyses require pairing rows (A/B comparisons, before/after, customer-customer similarity). Self-joins and controlled Cartesian products enable these.

Core concepts and deep dive
- CROSS JOIN: every row on left with every row on right; use only with small sets or with subsequent filters.
- SELF JOIN: join a table to itself (aliasing required) to compare peers (e.g., orders on consecutive days per customer).
- Pair generation patterns:
  - Symmetric pairs once: JOIN with key ordering (a.id < b.id) to avoid duplicates and self-pairs.
  - Time adjacency: join on the same key and use
    `date_a BETWEEN date_b - interval '1 day' AND date_b + interval '1 day'`.

Walkthrough mapping
- Product substitution pairs within a category (p1.category=p2.category AND p1.product_id<p2.product_id) for bundling analysis.
- Employee hierarchy: `employees e LEFT JOIN employees m ON
  e.manager_id=m.employee_id` gets manager names with a self-join.

Performance notes
- CROSS JOIN blows up quickly; reduce with filters immediately after.
- Consider generating sequences with generate_series for small domains rather than CROSS of large tables.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Self-joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOINS

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-05 — Cross Self Joins.

I have completed the direct catalog prerequisite: `sql-04`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day05_cross_self_joins.md
- Answer-free learner SQL: sql/postgres-60day/day05_cross_self_joins.sql

Key terms to teach in context: Cartesian product, Self-join, Canonical pair. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For product pairs, compare p1.productid <> p2.productid with p1.productid < p2.productid. The first produces both (A,B) and (B,A); the second removes reversed duplicates and self-pairs in one predicate.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-05/ working copy. Never point setup, reset, DDL, or DML
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
