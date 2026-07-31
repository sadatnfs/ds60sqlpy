# Day 51 — Finance/Operations Project, Part 3: Cash Flow

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 50 — budget variance](day50_project2_finance_part2.md)
- **Artifacts:** [learner SQL](../day51_project2_finance_part3.sql) ·
  [solution reasoning](../solutions/day51_solutions.md) ·
  [executable solution](../solutions/day51_solutions.sql)

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

2. Open **SQL-51 — Project2 Finance Part3** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-51/day51_project2_finance_part3.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day51_project2_finance_part3.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day51_project2_finance_part3.sql
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
Cash-in, Cash-out, Seasonal average. Its worked SQL reads or creates `payments`, `expenses`, `budgets`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Aggregate payments and expenses independently by month, full-join the two series, and calculate net and cumulative cash. For a future target month, join historical net cash on calendar month, average the matches, and return the supporting observation count beside the projection.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day51_project2_finance_part3.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH pay_m AS (
  SELECT date_trunc('month', payment_date)::date AS month,
         SUM(amount) AS cash_in
  FROM payments
  GROUP BY 1
), exp_m AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         SUM(amount) AS cash_out
  FROM expenses
  GROUP BY 1
), joined AS (
  SELECT COALESCE(p.month, e.month) AS month,
         COALESCE(p.cash_in, 0)     AS cash_in,
         COALESCE(e.cash_out, 0)    AS cash_out
  FROM pay_m p FULL OUTER JOIN exp_m e ON e.month = p.month
)
SELECT month,
       ROUND(cash_in - cash_out, 2) AS net_cash_flow,
       SUM(ROUND(cash_in - cash_out, 2)) OVER (ORDER BY month) AS cumulative_cash
FROM joined
ORDER BY month DESC
LIMIT 36;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH exp AS (
  SELECT date_trunc('month', expense_date)::date AS month,
         category,
         SUM(amount) AS actual
  FROM expenses
  GROUP BY 1,2
), bud AS (
  SELECT period AS month, category, SUM(amount) AS budget
  FROM budgets
  GROUP BY 1,2
), j AS (
  SELECT COALESCE(b.category, e.category) AS category,
         COALESCE(b.month, e.month) AS month,
         COALESCE(b.budget,0) AS budget,
         COALESCE(e.actual,0) AS actual
  FROM bud b FULL JOIN exp e ON e.month = b.month AND e.category = b.category
)
SELECT category,
       month,
       actual,
       budget,
       ROUND(actual - budget, 2) AS variance,
       SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
       SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
FROM j
ORDER BY month DESC, category
LIMIT 120;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Separate cash movement from booked order revenue.
- Project three future months under a precisely stated seasonal-average rule.

## Vocabulary and concepts

- **Cash-in:** received payment amount by payment date.
- **Cash-out:** expense amount by expense date.
- **Seasonal average:** an average of prior observations matching the target
  calendar period, distinct from a single seasonal-naive lag.

## Worked example / walkthrough

Aggregate payments and expenses independently by month, full-join the two
series, and calculate net and cumulative cash. For a future target month, join
historical net cash on calendar month, average the matches, and return the
supporting observation count beside the projection.

## Exercises

Complete these in the [learner SQL](../day51_project2_finance_part3.sql):

1. Calculate policy-defined monthly operating margin.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. Project three months of seasonal-naive net cash.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Explain cash-basis versus order-revenue timing.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Produce beginning cash, flows, net cash, and ending cash.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Preserve expense-only/payment-only months with a calendar spine.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Keep zero-cash-in margin NULL with an explanatory status.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Show all three forecast months even without matching history.

## Self-check

- Do monthly net totals reconcile to payments minus expenses over the same
  represented period?
- Is the forecast definition—and its behavior with one or zero historical
  matches—explicit?

## Next step

Continue to [Day 52 — star-schema warehouse](day52_project3_dwh_part1.md).

## Deep dive and reference

## Project focus

- Calculate monthly cash-in, cash-out, net cash flow, and cumulative cash.
- Define an operating-margin metric from selected expense categories.
- Project net cash for the next three months.

## How the learner script uses the current schema

Cash-in comes from `payments.payment_date` and `payments.amount`; cash-out comes
from `expenses.expense_date` and `expenses.amount`. This is cash movement, not
booked `orders.total_amount`. The starter also aligns monthly budgets and
actuals at category grain.

## Practice — match the learner prompts exactly

1. Calculate monthly operating margin as:
   `(cash_in - COGS - Payroll - Infrastructure - G&A) / cash_in`.
   Marketing is deliberately excluded by the prompt.
2. Return the next three calendar months with projected net cash from historical
   matching months.

## Ambiguous forecast wording

The learner says “average of last 12 matching months (seasonal naive).”
Seasonal naive usually means the single value from 12 months earlier, while
“average” implies several observations. The reference answer interprets
matching months as the same calendar month across prior years and averages the
available values. State this assumption and return the supporting history count.

## Validation and limits

- Use a full outer join so payment-only and expense-only months remain visible.
- Guard margin when cash-in is zero.
- Treat expense-category classification as course policy, not accounting advice.
- A one-observation seasonal average is only a naive estimate.
- Reconcile monthly net cash to total payments minus total expenses over the
  same represented period.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-51 — Project2 Finance Part3.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day51_project2_finance_part3.md
- Answer-free learner SQL: sql/postgres-60day/day51_project2_finance_part3.sql

The lesson concepts include Cash-in, Cash-out, Seasonal average. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate payments and expenses independently by month, full-join the two series, and calculate net and cumulative cash. For a future target month, join historical net cash on calendar month, average the matches, and return the supporting observation count beside the projection.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-51/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
