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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per employee.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per employee.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List every employee with their direct manager when present” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `employee_name`, `manager_id`, `manager_name`, `e`, `m`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Find employees who manage nobody.
   **Progressive hint:** Left join candidate managers to reports and retain managers with no right-side match.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Find employees who manage nobody” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `e`, `report`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Build a complete grid of six recent months and all expense categories.
   **Progressive hint:** Cross join two small declared dimensions; do not cross join raw fact tables.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Build a complete grid of six recent months and all expense categories” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `month_start`, `e`, `c`, `m`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `expenses`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
   **Progressive hint:** Cross-join cardinality is the product of input row counts.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `month_number`, `department_month_combinations`, `d`, `m`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `departments`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** List unique employee pairs in the same department without self-pairs or mirrored duplicates.
   **Progressive hint:** Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: List unique employee pairs in the same department without self-pairs or mirrored duplicates” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `both`, `evidence`, `first_employee_id`, `second_employee_id`, `left_employee`, `right_employee`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `employees`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Extension:** Show each employee, their manager, and their manager's manager.
   **Progressive hint:** Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
   **Expected result/shape:** Exercise 6 must make “Extension: Show each employee, their manager, and their manager's manager” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `employee_name`, `manager_name`, `grandmanager_name`, `e`, `manager`, `grandmanager`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `employee_name`, `manager_name`, `grandmanager_name`, `e`, `manager`, `grandmanager`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

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

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
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
