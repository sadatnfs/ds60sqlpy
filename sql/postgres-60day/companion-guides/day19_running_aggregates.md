# Day 19 — Running Aggregates and Moving Windows (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 18 — LAG and LEAD](day18_lag_lead.md)
- **Artifacts:** [learner SQL](../day19_running_aggregates.sql) ·
  [solution reasoning](../solutions/day19_solutions.md) ·
  [executable solution](../solutions/day19_solutions.sql)

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

2. Open **SQL-19 — Running Aggregates** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-19/day19_running_aggregates.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day19_running_aggregates.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day19_running_aggregates.sql
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
Cumulative aggregate, Moving window, Observation. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Aggregate orders to daily revenue, then apply ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. This includes at most seven observed order dates, not automatically seven calendar days. Compare it with a date-spined input that includes zero-revenue days.
The expected contract is that One row per order with nondecreasing cumulative revenue. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day19_running_aggregates.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order with nondecreasing cumulative revenue.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order with nondecreasing cumulative revenue.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per order with nondecreasing cumulative revenue.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Calculate each customer's cumulative stored spend.
   **Progressive hint:** Partition by customer and reset the explicit row frame for every customer.
   **Expected shape:** One row per order.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Calculate a trailing seven-order average within each customer.
   **Progressive hint:** A seven-row frame is based on observations, not seven calendar days.
   **Expected shape:** One row per order with up to seven observations in its frame.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
   **Progressive hint:** `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
   **Expected shape:** Three rows making the peer difference visible.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Reset a running expense total at each category and month.
   **Progressive hint:** Partition by both reset keys and order by date plus expense ID.
   **Expected shape:** One row per expense.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
   **Progressive hint:** Select the last ordered cumulative value and compare it with an independent aggregate.
   **Expected shape:** One row with zero difference.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Does the input grain match the period named in the metric?
- Are ties and missing dates treated deliberately rather than by a default
  frame?

## Next step

Continue to [Day 20 — first, last, and Nth values](day20_first_last_value.md).

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
- RANGE vs ROWS: RANGE groups peers by value; ROWS counts physical rows — prefer ROWS for exact ‘last N rows/days after aggregation’.
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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-19 — Running Aggregates.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day19_running_aggregates.md
- Answer-free learner SQL: sql/postgres-60day/day19_running_aggregates.sql

The lesson concepts include Cumulative aggregate, Moving window, Observation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate orders to daily revenue, then apply ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. This includes at most seven observed order dates, not automatically seven calendar days. Compare it with a date-spined input that includes zero-revenue days.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-19/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
