# Day 50: Finance/Operations Project, Part 2: Budget Variance

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-50**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-50/lesson/workspace/sql/postgres-60day/day50_project2_finance_part2.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-50
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 49; revenue forecasting](day49_project2_finance_part1.md)
- **Artifacts:** [learner SQL](../day50_project2_finance_part2.sql) ·
  [solution reasoning](../solutions/day50_solutions.md) ·
  [executable solution](../solutions/day50_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Variance, Budget-only row, Static pivot. Its worked SQL reads or creates `expenses`, `budgets`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Aggregate actuals and budgets independently at (month, category), full-join those stable relations, and retain both raw values. Derive absolute variance and guard percentage variance with NULLIF(budget, 0); only then pivot the five known categories.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `month`, and `category`, capped at 100 rows with columns `month`, `category`, `actual`, `budget`, `variance`, and `variance_pct` from `expenses`, and `budgets`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `category`, `month`, `budget`, `actual`, `variance`, and `variance_pct`. Independently group `expenses`, `budgets`, `monthly_budget`, and `monthly_exp` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day50_project2_finance_part2.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
WITH monthly_exp AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    1,
    2
),
monthly_budget AS (
  SELECT
    period AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  GROUP BY
    1,
    2
)
SELECT
  coalesce(b.category, e.category) AS category,
  coalesce(b.month, e.month) AS month,
  COALESCE(b.budget, 0) AS budget,
  COALESCE(e.actual, 0) AS actual,
  ROUND(COALESCE(e.actual, 0) - COALESCE(b.budget, 0), 2) AS variance,
  ROUND((COALESCE(e.actual, 0) - COALESCE(b.budget, 0)) / NULLIF (b.budget, 0), 4) AS variance_pct
FROM
  monthly_budget b
  FULL OUTER JOIN monthly_exp e ON e.month = b.month
  AND e.category = b.category
ORDER BY
  month DESC,
  category
LIMIT 100;
```

**How to read it:** Example 1: Start with `expenses`, and `budgets` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `category`, `month`, `budget`, `actual`, `variance`, and `variance_pct`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `month`, and `category`, capped at 100 rows with columns `month`, `category`, `actual`, `budget`, `variance`, and `variance_pct` from `expenses`, and `budgets`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', expense_date)::date AS month,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  GROUP BY
    1,
    2
),
bud AS (
  SELECT
    period AS month,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  GROUP BY
    1,
    2
),
joined AS (
  SELECT
    coalesce(b.category, m.category) AS category,
    coalesce(b.month, m.month) AS month,
    COALESCE(b.budget, 0) AS budget,
    COALESCE(m.actual, 0) AS actual
  FROM
    bud b
    FULL JOIN monthly m ON m.month = b.month
      AND m.category = b.category
)
  SELECT
    category,
    month,
    SUM(actual) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS actual_ma3,
    SUM(budget) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS budget_ma3
  FROM
    joined
  ORDER BY
    month DESC,
    category
  LIMIT 100;
```

**How to read it:** Example 2: Start with `expenses`, and `budgets` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `category`, `month`, `actual_ma3`, and `budget_ma3`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `month`, and `category`, capped at 100 rows with columns `month`, `category`, `actual`, `budget`, `actual_ma3`, and `budget_ma3` from `expenses`, and `budgets`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-50 Exercise 1, read from `expenses`, and `budgets`. Build the answer toward `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-50 Exercise 1, expected output: one row per month and category, including periods found on only one side of the actual/budget comparison. The final columns are `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct`. The final order is `month DESC, category`.
   **Verify:** For sql-50 Exercise 1, project `month` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `month`, then assert the final `month`, `category`, `actual`, `prior_year_actual`, `year_over_year_variance_pct`, `budget_variance_pct`, and `overspent_by_more_than_15_pct` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
2. Pivot monthly category variance.
   **Inputs/evidence:** For sql-50 Exercise 2, read from `expenses`, and `budgets`. Build the answer toward `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-50 Exercise 2, expected output: one row per budget month and one variance column per known category. The final columns are `month`, `cogs`, `marketing`, `payroll`, `infrastructure`, and `general_admin`. The final order is `month DESC`.
   **Verify:** For sql-50 Exercise 2, independently aggregate `expenses`, and `budgets` by `month`; require one output row for every distinct `month` tuple and compare `cogs`, `marketing`, and `payroll` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cogs`, `marketing`, and `payroll` for the existing `month` tuple and verify the new tuple appears exactly once.
3. Define absent-budget policy before using `COALESCE`.
   **Inputs/evidence:** For sql-50 Exercise 3, read from `expenses`, and `budgets`. Build the answer toward `month`, `category`, `actual`, `budget`, and `comparison_status`; keep `month`, and `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-50 Exercise 3, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `actual`, `budget`, and `comparison_status`. The final order is `month DESC, category`.
   **Verify:** For sql-50 Exercise 3, project `month`, and `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `month`, and `category`, then assert the final `month`, `category`, `actual`, `budget`, and `comparison_status` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`, and `category`; verify the result gains exactly one row carrying that `month`, and `category` value.
4. Add category YTD actual, budget, variance, and variance percentage.
   **Inputs/evidence:** For sql-50 Exercise 4, read from `expenses`, `budgets`, and `month`. Build the answer toward `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`; keep `month`, and `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-50 Exercise 4, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `actual_ytd`, `budget_ytd`, and `variance_ytd`. The final order is `month DESC, category`.
   **Verify:** For sql-50 Exercise 4, choose one complete partition from `expenses`, `budgets`, and `month`; hand-calculate its first, middle, and final window values for `variance_ytd`, then verify output keys remain `month`, and `category`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
5. Normalize joined keys before applying windows.
   **Inputs/evidence:** For sql-50 Exercise 5, complete the normalize joined keys before applying windows written analysis and support its claims with read-only evidence from `monthly.month`, and `monthly.category`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-50 Exercise 5, expected output: a completed the normalize joined keys before applying windows written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
   **Verify:** For sql-50 Exercise 5, check the normalize joined keys before applying windows written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
6. Label unbudgeted spend separately from ordinary overspend.
   **Inputs/evidence:** For sql-50 Exercise 6, aggregate `expenses` and `budgets` independently to (`month`, `category`) before joining.
   **Expected result/shape:** For sql-50 Exercise 6, expected output: one row per (`month`, `category`) found in either source, with `actual`, `budget`, and `status`.
   **Verify:** For sql-50 Exercise 6, reconcile joined actual and budget totals to independent source totals. Test actual-only, budget-only, and zero-budget keys; a budget must never be multiplied by expense-row fanout.

Test actual-only, budget-only, and zero-budget toy rows.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Preserve actual-only and budget-only rows before deciding how to display
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

- Are missing and zero values kept semantically distinct?
- Does every pivot row reconcile with the long-form variance rows?

## Next step

Continue to [Day 51; cash flow](day51_project2_finance_part3.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-50 — Project2 Finance Part2.

I have completed the direct catalog prerequisite: `sql-49`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day50_project2_finance_part2.md
- Answer-free learner SQL: sql/postgres-60day/day50_project2_finance_part2.sql

Key terms to teach in context: Variance, Budget-only row, Static pivot. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate actuals and budgets independently at (month, category), full-join those stable relations, and retain both raw values. Derive absolute variance and guard percentage variance with NULLIF(budget, 0); only then pivot the five known categories.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-50/ working copy. Never point setup, reset, DDL, or DML
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
