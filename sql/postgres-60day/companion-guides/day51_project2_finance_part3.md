# Day 51: Finance/Operations Project, Part 3: Cash Flow

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-51**. The
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
   `.learning/sql/sql-51/lesson/workspace/sql/postgres-60day/day51_project2_finance_part3.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-51
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
- **Prerequisites:** [Day 50; budget variance](day50_project2_finance_part2.md)
- **Artifacts:** [learner SQL](../day51_project2_finance_part3.sql) ·
  [solution reasoning](../solutions/day51_solutions.md) ·
  [executable solution](../solutions/day51_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Cash-in, Cash-out, Seasonal average. Its worked SQL reads or creates `payments`, `expenses`, `budgets`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Aggregate payments and expenses independently by month, full-join the two series, and calculate net and cumulative cash. For a future target month, join historical net cash on calendar month, average the matches, and return the supporting observation count beside the projection.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `month`, capped at 36 rows with columns `month`, `cash_in`, `cash_out`, `net_cash_flow`, and `cumulative_cash` from `payments`, and `expenses`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `month`, `net_cash_flow`, and `cumulative_cash`. Independently group `payments`, `expenses`, `pay_m`, `exp_m`, and `joined` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day51_project2_finance_part3.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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

**How to read it:** Example 1: Start with `payments`, and `expenses` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `month`, `net_cash_flow`, and `cumulative_cash`. `ORDER BY` determines presentation order and the final `LIMIT 36` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `month`, capped at 36 rows with columns `month`, `cash_in`, `cash_out`, `net_cash_flow`, and `cumulative_cash` from `payments`, and `expenses`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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

**How to read it:** Example 2: Start with `expenses`, and `budgets` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `category`, `month`, `actual`, `budget`, `variance`, `actual_ma3`, and `budget_ma3`. `ORDER BY` determines presentation order and the final `LIMIT 120` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `month`, and `category`, capped at 120 rows with columns `month`, `category`, `actual`, `budget`, `variance`, and `actual_ma3` from `expenses`, and `budgets`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-51 Exercise 1, read from `payments`, and `expenses`. Build the answer toward `month`, `cash_in`, `operating_cost`, and `operating_margin`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-51 Exercise 1, expected output: one row per month appearing in either payments or operating expenses. The final columns are `month`, `cash_in`, `operating_cost`, and `operating_margin`. The final order is `month DESC`.
   **Verify:** For sql-51 Exercise 1, project `month` plus the raw source columns from `payments`, and `expenses` at each join stage; record row count and distinct `month`, then assert the final `month`, `cash_in`, `operating_cost`, and `operating_margin` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
2. Project three months of seasonal-naive net cash.
   **Inputs/evidence:** For sql-51 Exercise 2, read from `payments`, `expenses`, `h.month`, and `f.forecast_month`. Build the answer toward `forecast_month`, `projected_net_cash`, and `matching_historical_months`; keep `forecast_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-51 Exercise 2, expected output: exactly three future month rows. The count column shows how much history supports each estimate; a `NULL` projection means there was none. The final columns are `forecast_month`, `projected_net_cash`, and `matching_historical_months`. The final order is `f.forecast_month`.
   **Verify:** For sql-51 Exercise 2, independently aggregate `payments`, `expenses`, `h.month`, and `f.forecast_month` by `forecast_month`; require one output row for every distinct `forecast_month` tuple and compare `projected_net_cash`, and `matching_historical_months` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `projected_net_cash`, and `matching_historical_months` for the existing `forecast_month` tuple and verify the new tuple appears exactly once.
3. Explain cash-basis versus order-revenue timing.
   **Inputs/evidence:** For sql-51 Exercise 3, read from `orders`, and `payments`. Build the answer toward `month`, `booked_order_revenue`, and `cash_received`; keep `cash_received` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-51 Exercise 3, expected output: one row per `cash_received`. The final columns are `month`, `booked_order_revenue`, and `cash_received`. The final order is `month`.
   **Verify:** For sql-51 Exercise 3, independently aggregate `orders`, and `payments` by `cash_received`; require one output row for every distinct `cash_received` tuple and compare `booked_order_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `booked_order_revenue` for the existing `cash_received` tuple and verify the new tuple appears exactly once.
4. Produce beginning cash, flows, net cash, and ending cash.
   **Inputs/evidence:** For sql-51 Exercise 4, read from `payments`, and `expenses`. Build the answer toward `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-51 Exercise 4, expected output: one row per `month`. The final columns are `month`, `beginning_cash`, `cash_in`, `cash_out`, `net_cash`, and `ending_cash`. The final order is `month`.
   **Verify:** For sql-51 Exercise 4, choose one complete partition from `payments`, and `expenses`; hand-calculate its first, middle, and final window values for `beginning_cash`, `cash_in`, and `cash_out`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
5. Preserve expense-only/payment-only months with a calendar spine.
   **Inputs/evidence:** For sql-51 Exercise 5, read from `payments`, and `expenses`. Build the answer toward `month`, `cash_in`, and `cash_out`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-51 Exercise 5, expected output: one row per `month`. The final columns are `month`, `cash_in`, and `cash_out`. The final order is `m.month`.
   **Verify:** For sql-51 Exercise 5, project `month` plus the raw source columns from `payments`, and `expenses` at each join stage; record row count and distinct `month`, then assert the final `month`, `cash_in`, and `cash_out` values match those staged rows without unintended fanout or loss. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
6. Keep zero-cash-in margin NULL with an explanatory status.
   **Inputs/evidence:** For sql-51 Exercise 6, read from `toy`. Build the answer toward `month`, `operating_margin`, and `margin_status`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-51 Exercise 6, expected output: one row per `month`. The final columns are `month`, `operating_margin`, and `margin_status`.
   **Verify:** For sql-51 Exercise 6, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `operating_margin`, and `margin_status` against `toy`. Repeat with `NULL` in `month`, and `operating_margin` and state whether the row is kept, rejected, or classified.

Show all three forecast months even without matching history.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Use a full outer join so payment-only and expense-only months remain visible.
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

- Do monthly net totals reconcile to payments minus expenses over the same
  represented period?
- Is the forecast definition, and its behavior with one or zero historical
  matches, explicit?

## Next step

Continue to [Day 52; star-schema warehouse](day52_project3_dwh_part1.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-51 — Project2 Finance Part3.

I have completed the direct catalog prerequisite: `sql-50`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day51_project2_finance_part3.md
- Answer-free learner SQL: sql/postgres-60day/day51_project2_finance_part3.sql

Key terms to teach in context: Cash-in, Cash-out, Seasonal average. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate payments and expenses independently by month, full-join the two series, and calculate net and cumulative cash. For a future target month, join historical net cash on calendar month, average the matches, and return the supporting observation count beside the projection.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-51/ working copy. Never point setup, reset, DDL, or DML
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
