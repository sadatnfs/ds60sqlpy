# Day 27 — Pivoting/Unpivoting: Crosstabs and Conditional Aggregation (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 26 — CTEs with window functions](day26_ctes_with_windows.md)
- **Artifacts:** [learner SQL](../day27_pivot_unpivot.sql) ·
  [solution reasoning](../solutions/day27_solutions.md) ·
  [executable solution](../solutions/day27_solutions.sql)

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

2. Open **SQL-27 — Pivot Unpivot** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-27/day27_pivot_unpivot.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day27_pivot_unpivot.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day27_pivot_unpivot.sql
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
Pivot, Unpivot, Conditional aggregation. Its worked SQL reads or creates `order_items`, `orders`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: At one row per quarter, calculate SUM(amount) FILTER (WHERE method = 'card') and parallel columns for the other known methods. Reconcile the sum of pivot columns to the long-form payment total and decide whether absent combinations display as NULL or zero.
The expected contract is that Exactly one row. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day27_pivot_unpivot.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT p.category,
       SUM(oi.quantity) FILTER (
         WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 1
       ) AS jan_qty,
       SUM(oi.quantity) FILTER (
         WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 2
       ) AS feb_qty,
       SUM(oi.quantity) FILTER (
         WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 3
       ) AS mar_qty
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.order_date >= (
        date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        AT TIME ZONE 'UTC'
      )
  AND o.order_date < (
        date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        + INTERVAL '1 year'
      ) AT TIME ZONE 'UTC'
GROUP BY p.category
ORDER BY p.category;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Exactly one row.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH source AS (
  SELECT p.category,
         EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC')::integer
           AS month_number,
         oi.quantity
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.order_date >= (
          date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
          AT TIME ZONE 'UTC'
        )
    AND o.order_date < (
          date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
          + INTERVAL '1 year'
        ) AT TIME ZONE 'UTC'
), wide AS (
  SELECT category,
         SUM(quantity) FILTER (WHERE month_number = 1) AS jan_qty,
         SUM(quantity) FILTER (WHERE month_number = 2) AS feb_qty
  FROM source
  GROUP BY category
)
SELECT wide.category,
       month_value.month_name,
       month_value.quantity
FROM wide
CROSS JOIN LATERAL (
  VALUES ('jan', wide.jan_qty), ('feb', wide.feb_qty)
) AS month_value(month_name, quantity)
ORDER BY wide.category, month_value.month_name;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Exactly one row.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Pivot controlled categories with portable conditional aggregation.
- Normalize wide values to a typed long-form relation.

## Vocabulary and concepts

- **Pivot:** turn row values into separate output columns.
- **Unpivot:** turn several columns into key/value rows.
- **Conditional aggregation:** aggregates restricted by `FILTER` or `CASE`.

## Worked example / walkthrough

At one row per quarter, calculate
`SUM(amount) FILTER (WHERE method = 'card')` and parallel columns for the other
known methods. Reconcile the sum of pivot columns to the long-form payment total
and decide whether absent combinations display as `NULL` or zero.

## Practice assumptions and review method

- **Focus:** Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
- **Assumptions:** PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
- **Failure to watch for:** Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Pivot order counts by status into one summary row.
   **Progressive hint:** Use one filtered count per known status and keep an all-orders denominator.
   **Expected shape:** Exactly one row.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Pivot customer counts for US, CA, GB, and DE by segment.
   **Progressive hint:** Group at segment grain and use filtered counts for known country columns.
   **Expected shape:** One row per segment.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Unpivot a wide quarterly sample into quarter/amount rows.
   **Progressive hint:** Use a lateral `VALUES` relation with one output row per source column.
   **Expected shape:** Eight rows from two source rows and four quarters.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Compare a missing pivot combination with a real zero and preserve the distinction.
   **Progressive hint:** Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
   **Expected shape:** One row per expense category with nullable/zero-aware columns.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
   **Progressive hint:** Aggregate category/value pairs into data values so the result schema remains stable.
   **Expected shape:** One row per UTC month with a JSON object of category revenue.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
6. **Extension:** Round-trip a wide sample to long form and back, verifying values and NULLs.
   **Progressive hint:** Unpivot with lateral values, then use conditional aggregation keyed by company.
   **Expected shape:** Two reconstructed rows matching the source.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Is the category domain controlled enough for fixed output columns?
- Do the wide and long forms reconcile without silently changing types?

## Next step

Continue to [Day 28 — JSONB and XML](day28_json_xml.md).

## Deep dive and reference

Learning objectives
- Build pivot tables from row-form data using two approaches in Postgres
  - Conditional aggregation (portable SQL)
  - tablefunc.crosstab (extension) for tidy pivot syntax
- Unpivot wide tables back to long form for analysis

Why this matters
Reports often require metrics by columns (months across columns, categories as columns). Knowing when to pivot/unpivot keeps data pipelines flexible and analytics straightforward.

Core concepts and deep dive
- Conditional aggregation (portable)
  - SELECT key, SUM(CASE WHEN bucket='A' THEN val END) AS a, ... GROUP BY key
  - Pros: no extension; dynamic columns require generating SQL
  - Cons: verbose for many buckets
- crosstab (tablefunc)
  - CREATE EXTENSION IF NOT EXISTS tablefunc;
  - crosstab(text source_sql, text category_sql) → returns setof record with specified column layout
  - Requires declaring the output column types (key, val for each category)
  - Extension installation requires sufficient database privileges; the
    portable course answer does not depend on it
  - Pros: concise; Cons: requires predeclared categories (static schema) or dynamic SQL
- Unpivot
  - Use UNION ALL over columns or use jsonb_each/text arrays to normalize wide to long
  - Example pattern: SELECT id, 'jan' AS month, jan_val AS val FROM t UNION ALL SELECT id, 'feb', feb_val FROM t ...
  - For many columns, convert row to JSON and jsonb_each_text to key/value rows

Design decisions
- For dashboards with fixed categories/months, crosstab is ergonomic
- For ad-hoc analysis or dynamic categories, prefer conditional aggregates or generate SQL in the application

Pitfalls
- crosstab requires sorted input and category queries; mismatches yield misaligned columns
- NULLs vs zeroes: decide whether to COALESCE NULL to 0 for metrics
- Unpivoting monetary/numeric columns: ensure data types are preserved

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- tablefunc: https://www.postgresql.org/docs/current/tablefunc.html
- Crosstab examples: https://wiki.postgresql.org/wiki/Tablefunc

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-27 — Pivot Unpivot.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day27_pivot_unpivot.md
- Answer-free learner SQL: sql/postgres-60day/day27_pivot_unpivot.sql

The lesson concepts include Pivot, Unpivot, Conditional aggregation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At one row per quarter, calculate SUM(amount) FILTER (WHERE method = 'card') and parallel columns for the other known methods. Reconcile the sum of pivot columns to the long-form payment total and decide whether absent combinations display as NULL or zero.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-27/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
