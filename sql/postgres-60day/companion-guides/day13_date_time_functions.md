# Day 13 — Date/Time Functions and Time Zones (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 12 — string functions](day12_string_functions.md)
- **Artifacts:** [learner SQL](../day13_date_time_functions.sql) ·
  [solution reasoning](../solutions/day13_solutions.md) ·
  [executable solution](../solutions/day13_solutions.sql)

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

2. Open **SQL-13 — Date Time Functions** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-13/lesson/workspace/sql/postgres-60day/day13_date_time_functions.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day13_date_time_functions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day13_date_time_functions.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Half-open interval, Time zone, Calendar bucket. Its worked SQL reads or creates `customers`, `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Express one day as timestamp >= daystart AND timestamp < nextdaystart. Test a row exactly at each boundary. This half-open form prevents double counting when adjacent daily queries are combined and is friendlier to a normal timestamp index than wrapping the column in a function.
The expected contract is that Recent order rows in deterministic order. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day13_date_time_functions.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT customer_id, full_name,
       now() - created_at AS tenure,
       date_trunc('month', created_at AT TIME ZONE 'UTC')::date
         AS cohort_month_utc
FROM customers
ORDER BY tenure DESC, customer_id
LIMIT 50;
```

**How to read it:** Example 1: Start with `customers` in `FROM`/`JOIN`. The final `SELECT` displays `customer_id`, `full_name`, `tenure`, and `cohort_month_utc`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `customer_id`, capped at 50 rows with columns `customer_id`, `full_name`, `tenure`, and `cohort_month_utc` from `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
WITH daily AS (
  SELECT (o.order_date AT TIME ZONE 'UTC')::date AS d_utc,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY d_utc
)
SELECT d_utc,
       revenue,
       SUM(revenue) OVER (
         ORDER BY d_utc
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS revenue_7_observed_days
FROM daily
ORDER BY d_utc DESC
LIMIT 30;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `d_utc`, `revenue`, and `revenue_7_observed_days`. `ORDER BY` determines presentation order and the final `LIMIT 30` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `d_utc`, capped at 30 rows with columns `d_utc`, `revenue`, and `revenue_7_observed_days` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Bucket, shift, and compare temporal values with explicit boundaries.
- Explain how timestamp type and session time zone affect a result.

## Vocabulary and concepts

- **Half-open interval:** a range including its start but excluding its end.
- **Time zone:** rules mapping an instant to local civil time and offsets.
- **Calendar bucket:** a period such as day or month produced by
  `date_trunc`.

## Worked example / walkthrough

Express one day as `timestamp >= day_start AND timestamp < next_day_start`.
Test a row exactly at each boundary. This half-open form prevents double
counting when adjacent daily queries are combined and is friendlier to a normal
timestamp index than wrapping the column in a function.

## Practice assumptions and review method

- **Focus:** Treat timestamps as instants, dates as calendar values, and reporting zones/window boundaries as explicit parts of the query.
- **Assumptions:** Stored event/order timestamps are `timestamptz`. Relative examples use the database clock; reports label UTC explicitly where conversion matters.
- **Failure to watch for:** `BETWEEN` is inclusive at both ends and is often wrong for adjacent time windows; use half-open `[start, end)` predicates.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Treat timestamps as instants, dates as calendar values, and reporting zones/window boundaries as explicit parts of the query.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List orders from the last 30 days with their UTC calendar date.
   **Progressive hint:** Filter the timestamp directly and convert for display only.
   **Inputs/evidence:** For sql-13 Exercise 1, read from `orders`. Build the answer toward `order_id`, `order_date`, and `utc_order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-13 Exercise 1, expected output: Recent order rows in deterministic order. The final columns are `order_id`, `order_date`, and `utc_order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-13 Exercise 1, run an anti-check that counts rows where NOT ((o.order_date >= CURRENT_TIMESTAMP - INTERVAL '30 days')); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `order_date`, and `utc_order_date` against `orders`. Tie two rows on `o.order_date DESC` and give them different `o.order_id DESC` values; verify `o.order_date DESC, o.order_id DESC` chooses a stable first/last row.
2. **Query writing:** Summarize orders and stored revenue by UTC month.
   **Progressive hint:** Convert to UTC before truncating when the reporting calendar is UTC.
   **Inputs/evidence:** For sql-13 Exercise 2, read from `orders`. Build the answer toward `utc_month`, `order_count`, and `stored_revenue`; keep `utc_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-13 Exercise 2, expected output: One row per observed UTC month. The final columns are `utc_month`, `order_count`, and `stored_revenue`. The final order is `utc_month`.
   **Verify:** For sql-13 Exercise 2, independently aggregate `orders` by `utc_month`; require one output row for every distinct `utc_month` tuple and compare `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `utc_month` tuple and verify the new tuple appears exactly once.
3. **Query writing:** Calculate each customer's age in whole days as of the current date.
   **Progressive hint:** Compare calendar dates after declaring the UTC reporting date.
   **Inputs/evidence:** For sql-13 Exercise 3, read from `customers`. Build the answer toward `customer_id`, `created_at`, and `customer_age_days`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-13 Exercise 3, expected output: One row per customer with nonnegative age days. The final columns are `customer_id`, `created_at`, and `customer_age_days`. The final order is `c.customer_id`.
   **Verify:** For sql-13 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `created_at`, and `customer_age_days` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
4. **Prediction:** Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
   **Progressive hint:** Include the month start and exclude the next month start.
   **Inputs/evidence:** For sql-13 Exercise 4, read from `orders`. Build the answer toward `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-13 Exercise 4, expected output: Orders in exactly one UTC month. The final columns are `order_id`, and `order_date`. The final order is `o.order_date, o.order_id`.
   **Verify:** For sql-13 Exercise 4, project `order_id` plus the raw source columns from `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, and `order_date` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
5. **Debugging:** Compare UTC and America/Los_Angeles display times without stripping the stored instant.
   **Progressive hint:** `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
   **Inputs/evidence:** For sql-13 Exercise 5, read from `events`. Build the answer toward `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`; keep `event_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-13 Exercise 5, expected output: One row per sampled event with two displays of the same instant. The final columns are `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`. The final order is `e.event_time, e.event_id`.
   **Verify:** For sql-13 Exercise 5, assert no more than 20 rows, no duplicate `event_id`, and no adjacent pair that violates `e.event_time, e.event_id`. Rejoin the returned keys to `events` to confirm `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `e.event_time, e.event_id`.
6. **Extension:** Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
   **Progressive hint:** Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
   **Inputs/evidence:** For sql-13 Exercise 6, read from `orders`. Build the answer toward `utc_date`, and `order_count`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-13 Exercise 6, expected output: Exactly seven chronological rows. The final columns are `utc_date`, and `order_count`. The final order is `c.utc_date`.
   **Verify:** For sql-13 Exercise 6, project `order_id` plus the raw source columns from `orders` at each join stage; record row count and distinct `order_id`, then assert the final `utc_date`, and `order_count` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** BETWEEN is inclusive at both ends and is often wrong for adjacent time windows; use half-open [start, end) predicates.
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

- Are all time windows explicit about inclusivity and time zone?
- Does month-offset logic include both year and month components when periods
  can span more than one year?

## Next step

Continue to [Day 14 — numeric types and casting](day14_numeric_and_casting.md).

## Deep dive and reference

Learning objectives
- Work with DATE, TIME, TIMESTAMP, TIMESTAMPTZ
- Use date_trunc, interval arithmetic, generate_series for time bucketing
- Handle time zones correctly; convert and display safely

Core concepts and deep dive
- Types: TIMESTAMPTZ stores UTC with zone conversion on display; TIMESTAMP has no zone.
- Bucketing: date_trunc('month', ts) for monthly; generate_series(start, stop, interval '1 day') to fill calendars.
- Arithmetic: ts + interval '7 days'; AGE(ts1, ts2) for differences.
- Time zones: AT TIME ZONE to convert; keep data in UTC internally, convert on output.

Examples
- Monthly revenue with generate_series left join to avoid missing months.
- Localize order times to user’s locale for reporting.

Pitfalls
- Mixing TIMESTAMP and TIMESTAMPTZ in comparisons; cast explicitly.
- DST transitions: avoid local timestamps as primary keys.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Date/time: https://www.postgresql.org/docs/current/functions-datetime.html
- generate_series: https://www.postgresql.org/docs/current/functions-srf.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-13 — Date Time Functions.

I have completed the direct catalog prerequisite: `sql-12`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day13_date_time_functions.md
- Answer-free learner SQL: sql/postgres-60day/day13_date_time_functions.sql

Key terms to teach in context: Half-open interval, Time zone, Calendar bucket. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Express one day as timestamp >= daystart AND timestamp < nextdaystart. Test a row exactly at each boundary. This half-open form prevents double counting when adjacent daily queries are combined and is friendlier to a normal timestamp index than wrapping the column in a function.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-13/ working copy. Never point setup, reset, DDL, or DML
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
