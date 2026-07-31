# Day 06 — Set Operations: UNION, INTERSECT, EXCEPT (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 05 — cross and self joins](day05_cross_self_joins.md)
- **Artifacts:** [learner SQL](../day06_set_operations.sql) ·
  [solution reasoning](../solutions/day06_solutions.md) ·
  [executable solution](../solutions/day06_solutions.sql)

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

2. Open **SQL-06 — Set Operations** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-06/lesson/workspace/sql/postgres-60day/day06_set_operations.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day06_set_operations.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day06_set_operations.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Set operation, Union compatibility, Duplicate semantics. Its worked SQL reads or creates `orders`, `events`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Project only orderid from orders and payments before applying EXCEPT. Because set operations compare every projected column, adding an unrelated amount or timestamp would change the meaning from “missing order IDs” to “missing complete tuples.”
The expected contract is that One distinct customer ID per qualifying customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day06_set_operations.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH purchasers AS (
  SELECT DISTINCT o.customer_id FROM orders o
), supporters AS (
  SELECT DISTINCT e.customer_id FROM events e WHERE e.event_type = 'support'
)
SELECT * FROM purchasers
INTERSECT
SELECT * FROM supporters
ORDER BY customer_id;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One distinct customer ID per qualifying customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH browsers AS (
  SELECT DISTINCT e.customer_id FROM events e WHERE e.event_type = 'page_view'
), purchasers AS (
  SELECT DISTINCT o.customer_id FROM orders o
)
SELECT * FROM browsers
EXCEPT
SELECT * FROM purchasers
ORDER BY customer_id;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One distinct customer ID per qualifying customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Combine compatible result sets and choose deliberately between duplicate
  preservation and removal.
- Express set overlap and difference at the correct projected grain.

## Vocabulary and concepts

- **Set operation:** an operator that combines or compares complete result rows.
- **Union compatibility:** equal column counts with compatible data types.
- **Duplicate semantics:** `UNION ALL` preserves duplicates; `UNION`,
  `INTERSECT`, and `EXCEPT` use set-style duplicate handling.

## Worked example / walkthrough

Project only `order_id` from orders and payments before applying `EXCEPT`.
Because set operations compare every projected column, adding an unrelated
amount or timestamp would change the meaning from “missing order IDs” to
“missing complete tuples.”

## Practice assumptions and review method

- **Focus:** Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
- **Assumptions:** Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
- **Failure to watch for:** `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return customer IDs that have either an order or a support event.
   **Progressive hint:** `UNION` expresses set membership and removes duplicates across both sources.
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Return customer IDs that have either an order or a support event” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `e`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `events`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Return customer IDs that have both an order and a support event.
   **Progressive hint:** `INTERSECT` keeps keys present in both compatible sets.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Return customer IDs that have both an order and a support event” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `e`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `events`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Return customers who have no orders.
   **Progressive hint:** `EXCEPT` subtracts the order-customer set from all customers.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Return customers who have no orders” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `c`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
   **Progressive hint:** `UNION ALL` preserves every input row; `UNION` returns distinct rows.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Compare row counts produced by UNION and UNION ALL for two overlapping status lists”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `o`, `operation`, `row_count`, `union`, `all`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
   **Progressive hint:** Each branch below returns one text label and one numeric amount at the same report grain.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts” at one row at the same report grain. Named evidence columns/objects: `evidence`, `measure`, `amount`, `o`, `e`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one row at the same report grain; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `expenses`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Extension:** Return the symmetric difference between customers with orders and customers with support events.
   **Progressive hint:** Subtract each set from the other, then union the two differences.
   **Expected result/shape:** Exercise 6 must make “Extension: Return the symmetric difference between customers with orders and customers with support events” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `o`, `e`, `source`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `o`, `e`, `source`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** UNION removes duplicates and can hide data multiplicity; NOT IN is not a safe substitute for EXCEPT when NULL is possible.
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

- Do both branches return columns in the same semantic order, not merely
  compatible types?
- Can you state whether duplicates should survive for the business question?

## Next step

Continue to [Day 07 — Week 1 project](day07_week1_project.md).

## Deep dive and reference

Learning objectives
- Combine result sets with UNION/UNION ALL
- Compute set intersection and differences with INTERSECT/EXCEPT
- Understand duplicate handling and column alignment rules

Why this matters
Merging and comparing result sets is common in data reconciliation, feature flags, and A/B test cohorts.

Core concepts and deep dive
- UNION ALL concatenates rows and keeps duplicates; UNION removes duplicates (implies sort/unique).
- INTERSECT returns rows present in both queries; EXCEPT returns rows in left not in right.
- Column rules: Both queries must have same number of columns and compatible types; column names come from the first query.
- Performance: DISTINCT/UNION can be expensive; prefer UNION ALL followed by targeted dedup when appropriate.

Examples in your schema
- Customers from the `gold` and `platinum` segments can be combined by
  selecting `customer_id` from each set.
- Orders with no payment can be found with `SELECT order_id FROM orders EXCEPT
  SELECT order_id FROM payments`.
- Common high-value customers across two periods can be found by intersecting
  compatible `customer_id` result sets.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Set operations: https://www.postgresql.org/docs/current/queries-union.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-06 — Set Operations.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day06_set_operations.md
- Answer-free learner SQL: sql/postgres-60day/day06_set_operations.sql

Key terms to teach in context: Set operation, Union compatibility, Duplicate semantics. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Project only orderid from orders and payments before applying EXCEPT. Because set operations compare every projected column, adding an unrelated amount or timestamp would change the meaning from “missing order IDs” to “missing complete tuples.”

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-06/ working copy. Never point setup, reset, DDL, or DML
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
