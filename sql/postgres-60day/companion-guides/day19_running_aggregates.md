# Day 19: Running Aggregates and Moving Windows (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-19**. The
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
   `.learning/sql/sql-19/lesson/workspace/sql/postgres-60day/day19_running_aggregates.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-19
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 18; LAG and LEAD](day18_lag_lead.md)
- **Artifacts:** [learner SQL](../day19_running_aggregates.sql) ·
  [solution reasoning](../solutions/day19_solutions.md) ·
  [executable solution](../solutions/day19_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Cumulative aggregate, Moving window, Observation. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Aggregate orders to daily revenue, then apply ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. This includes at most seven observed order dates, not automatically seven calendar days. Compare it with a date-spined input that includes zero-revenue days.
The expected contract is that One row per order with nondecreasing cumulative revenue. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day19_running_aggregates.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 200;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `order_id`, `order_date`, `total_amount`, and `running_total`. `ORDER BY` determines presentation order and the final `LIMIT 200` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns exactly one summary row, capped at 200 rows with columns `customer_id`, `order_id`, `order_date`, `total_amount`, and `running_total` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
WITH daily AS (
  SELECT (order_date AT TIME ZONE 'UTC')::date AS d_utc,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY d_utc
)
SELECT d_utc,
       revenue,
       ROUND(AVG(revenue) OVER (
         ORDER BY d_utc
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ),2) AS ma7
FROM daily
ORDER BY d_utc DESC
LIMIT 40;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `d_utc`, `revenue`, and `ma7`. `ORDER BY` determines presentation order and the final `LIMIT 40` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `d_utc`, capped at 40 rows with columns `d_utc`, `revenue`, and `ma7` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Calculate cumulative and moving aggregates with explicit frames.
- Explain whether a frame counts observations, peer groups, or elapsed time.

## Vocabulary and concepts

- **Cumulative aggregate:** a summary from the partition start through the
  current row.
- **Moving window:** a bounded frame around or before the current row.
- **Observation:** one row at the grain supplied to the window calculation.

## Worked example / walkthrough

Aggregate orders to daily revenue, then apply
`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`. This includes at most seven observed
order dates, not automatically seven calendar days. Compare it with a
date-spined input that includes zero-revenue days.

## Practice assumptions and review method

- **Focus:** Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
- **Assumptions:** Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
- **Failure to watch for:** Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate cumulative stored revenue across all orders.
   **Progressive hint:** Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.
   **Inputs/evidence:** For sql-19 Exercise 1, read from `orders`. Build the answer toward `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-19 Exercise 1, expected output: One row per order with nondecreasing cumulative revenue. The final columns are `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`. The final order is `o.order_date, o.order_id`.
   **Verify:** For sql-19 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, `total_amount`, and `cumulative_revenue`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
2. **Query writing:** Calculate each customer's cumulative stored spend.
   **Progressive hint:** Partition by customer and reset the explicit row frame for every customer.
   **Inputs/evidence:** For sql-19 Exercise 2, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-19 Exercise 2, expected output: One row per order. The final columns are `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-19 Exercise 2, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, `total_amount`, and `customer_cumulative_spend`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
3. **Query writing:** Calculate a trailing seven-order average within each customer.
   **Progressive hint:** A seven-row frame is based on observations, not seven calendar days.
   **Inputs/evidence:** For sql-19 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-19 Exercise 3, expected output: One row per order with up to seven observations in its frame. The final columns are `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-19 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, and `trailing_7_order_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. **Prediction:** Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
   **Progressive hint:** `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
   **Inputs/evidence:** For sql-19 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`; keep `row_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-19 Exercise 4, expected output: Three rows making the peer difference visible. The final columns are `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`. The final order is `row_id`.
   **Verify:** For sql-19 Exercise 4, hand-calculate all three peer rows from the inline fixture: `rows_sum` must be `(10, 30, 35)` while `range_sum` must be `(30, 30, 35)` in `row_id` order. Require three unique `row_id` values and explain why the two rows tied at `sort_value = 1` advance separately under `ROWS` but together under `RANGE`.
5. **Debugging:** Reset a running expense total at each category and month.
   **Progressive hint:** Partition by both reset keys and order by date plus expense ID.
   **Inputs/evidence:** For sql-19 Exercise 5, read from `expenses`. Build the answer toward `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`; keep `expense_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-19 Exercise 5, expected output: One row per expense. The final columns are `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`. The final order is `e.category, e.expense_date, e.expense_id`.
   **Verify:** For sql-19 Exercise 5, choose one complete partition from `expenses`; hand-calculate its first, middle, and final window values for `amount`, then verify output keys remain `expense_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
6. **Extension:** Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
   **Progressive hint:** Select the last ordered cumulative value and compare it with an independent aggregate.
   **Inputs/evidence:** For sql-19 Exercise 6, read from `orders`. Build the answer toward `final_cumulative`, `aggregate_total`, and `difference`; keep `cumulative_revenue` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-19 Exercise 6, expected output: One row with zero difference. The final columns are `final_cumulative`, `aggregate_total`, and `difference`.
   **Verify:** For sql-19 Exercise 6, independently aggregate `orders` by `cumulative_revenue`; require one output row for every distinct `cumulative_revenue` tuple and compare `aggregate_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `aggregate_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
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

- Does the input grain match the period named in the metric?
- Are ties and missing dates treated deliberately rather than by a default
  frame?

## Next step

Continue to [Day 20; first, last, and Nth values](day20_first_last_value.md).

## Deep dive and reference

Learning objectives
- Compute cumulative sums/averages and moving windows
- Choose ROWS vs RANGE frames and understand their semantics
- Build KPI baselines and rolling signals

Why this matters
Rolling and cumulative metrics stabilize noisy data and reveal trends and seasonality.

Core concepts and deep dive
- Cumulative: SUM(x) OVER (ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW).
- Moving average: AVG(x) OVER (ORDER BY t ROWS BETWEEN n PRECEDING AND CURRENT ROW).
- RANGE vs ROWS: RANGE groups peers by value; ROWS counts physical rows; prefer ROWS for exact ‘last N rows/days after aggregation’.
- Partitioned cumulatives: add PARTITION BY to reset per key (e.g., customer_id, category).

Patterns
- Rolling 7/28-day revenue; cumulative MTD/QTD/ YTD by combining date_trunc and partitions.
- Baseline with stddev bands using STDDEV_SAMP over the same frame for anomaly z-scores.

Pitfalls
- Applying window over raw transactional rows when you intended daily aggregates; pre-aggregate first.
- Filtering on a windowed column in the same SELECT; wrap in subquery to allow WHERE on computed value.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Window frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-19 — Running Aggregates.

I have completed the direct catalog prerequisite: `sql-18`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day19_running_aggregates.md
- Answer-free learner SQL: sql/postgres-60day/day19_running_aggregates.sql

Key terms to teach in context: Cumulative aggregate, Moving window, Observation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate orders to daily revenue, then apply ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. This includes at most seven observed order dates, not automatically seven calendar days. Compare it with a date-spined input that includes zero-revenue days.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-19/ working copy. Never point setup, reset, DDL, or DML
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
