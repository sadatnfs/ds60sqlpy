# Day 50 — Finance/Operations Project, Part 2: Budget Variance

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 49 — revenue forecasting](day49_project2_finance_part1.md)
- **Artifacts:** [learner SQL](../day50_project2_finance_part2.sql) ·
  [solution reasoning](../solutions/day50_solutions.md) ·
  [executable solution](../solutions/day50_solutions.sql)

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

2. Open **SQL-50 — Project2 Finance Part2** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-50/day50_project2_finance_part2.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day50_project2_finance_part2.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day50_project2_finance_part2.sql
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
Variance, Budget-only row, Static pivot. Its worked SQL reads or creates `expenses`, `budgets`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Aggregate actuals and budgets independently at (month, category), full-join those stable relations, and retain both raw values. Derive absolute variance and guard percentage variance with NULLIF(budget, 0); only then pivot the five known categories.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day50_project2_finance_part2.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH monthly_exp AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), monthly_budget AS (
  SELECT period AS month,
         category,
         SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
)
SELECT coalesce(b.category, e.category) AS category,
       coalesce(b.month, e.month) AS month,
       COALESCE(b.budget, 0) AS budget,
       COALESCE(e.actual, 0) AS actual,
       ROUND(COALESCE(e.actual,0) - COALESCE(b.budget,0), 2) AS variance,
       ROUND((COALESCE(e.actual,0) - COALESCE(b.budget,0)) / NULLIF(b.budget,0), 4) AS variance_pct
FROM monthly_budget b
FULL OUTER JOIN monthly_exp e
  ON e.month = b.month AND e.category = b.category
ORDER BY month DESC, category
LIMIT 100;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH monthly AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), joined AS (
  SELECT coalesce(b.category, m.category) AS category,
         coalesce(b.month, m.month) AS month,
         COALESCE(b.budget, 0) AS budget,
         COALESCE(m.actual, 0) AS actual
  FROM bud b FULL JOIN monthly m ON m.month = b.month AND m.category = b.category
)
SELECT category,
       month,
       SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
       SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
FROM joined
ORDER BY month DESC, category
LIMIT 100;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Align actual and budget values without discarding one-sided periods.
- Calculate absolute and percentage variance and pivot controlled categories.

## Vocabulary and concepts

- **Variance:** actual minus budget under this course's declared convention.
- **Budget-only row:** a period/category with budget but no represented actual.
- **Static pivot:** fixed output columns for a controlled category domain.

## Worked example / walkthrough

Aggregate actuals and budgets independently at `(month, category)`, full-join
those stable relations, and retain both raw values. Derive absolute variance and
guard percentage variance with `NULLIF(budget, 0)`; only then pivot the five
known categories.

## Exercises

Complete these in the [learner SQL](../day50_project2_finance_part2.sql):

1. Calculate YoY variance and flag >15% overspend.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Pivot monthly category variance.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Define absent-budget policy before using `COALESCE`.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
4. Add category YTD actual, budget, variance, and variance percentage.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Normalize joined keys before applying windows.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Label unbudgeted spend separately from ordinary overspend.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Test actual-only, budget-only, and zero-budget toy rows.

## Self-check

- Are missing and zero values kept semantically distinct?
- Does every pivot row reconcile with the long-form variance rows?

## Next step

Continue to [Day 51 — cash flow](day51_project2_finance_part3.md).

## Deep dive and reference

## Project focus

- Align monthly actual expenses with monthly budgets.
- Add year-over-year and greater-than-15% overspend indicators.
- Pivot known expense categories into report columns.

## How the learner script uses the current schema

Actuals come from `expenses(expense_date, category, amount)`. Budgets come from
`budgets(period, category, amount)`, where `period` is the first day of a month.
The starter uses a full outer join so months/categories present on only one side
remain visible, then demonstrates rolling three-row totals.

The setup categories are `COGS`, `Marketing`, `Payroll`, `Infrastructure`, and
`G&A`.

## Practice — match the learner prompts exactly

1. Add prior-year actual and year-over-year percentage by category, plus
   `actual > budget * 1.15` as the requested overspend flag.
2. Return one row per month with actual-minus-budget variance columns for the
   five known categories.

## Metric semantics

- Variance is `actual - budget`; positive means overspend.
- Percentage variance uses budget as denominator and must guard zero budgets.
- A 12-row `LAG` assumes every category has a complete monthly series. Build a
  month/category spine when gaps are possible.
- A static pivot is appropriate only while the category set is controlled.

## Validation and limits

- Preserve actual-only and budget-only rows before deciding how to display
  missing values.
- Reconcile each pivot row to the long-form monthly variance.
- Do not silently label a missing budget as zero-percent variance.
- Report both absolute currency variance and percentage; either alone can
  mislead.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-50 — Project2 Finance Part2.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day50_project2_finance_part2.md
- Answer-free learner SQL: sql/postgres-60day/day50_project2_finance_part2.sql

The lesson concepts include Variance, Budget-only row, Static pivot. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate actuals and budgets independently at (month, category), full-join those stable relations, and retain both raw values. Derive absolute variance and guard percentage variance with NULLIF(budget, 0); only then pivot the five known categories.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-50/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
