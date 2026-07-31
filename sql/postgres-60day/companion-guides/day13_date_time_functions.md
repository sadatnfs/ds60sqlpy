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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Recent order rows in deterministic order.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Recent order rows in deterministic order.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List orders from the last 30 days with their UTC calendar date” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `utc_order_date`, `o`, `utc`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Summarize orders and stored revenue by UTC month.
   **Progressive hint:** Convert to UTC before truncating when the reporting calendar is UTC.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Summarize orders and stored revenue by UTC month” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `utc_month`, `order_count`, `stored_revenue`, `o`, `utc`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Calculate each customer's age in whole days as of the current date.
   **Progressive hint:** Compare calendar dates after declaring the UTC reporting date.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Calculate each customer's age in whole days as of the current date” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `of`, `evidence`, `customer_age_days`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
   **Progressive hint:** Include the month start and exclude the next month start.
   **Expected result/shape:** Exercise 4 needs the plan evidence for “Prediction: Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `month_start`, `next_month_start`, `o`, `b`, `utc`.
   **Verify:** For Exercise 4, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
5. **Debugging:** Compare UTC and America/Los_Angeles display times without stripping the stored instant.
   **Progressive hint:** `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
   **Expected result/shape:** Exercise 5 requires a written prediction and the observed result for “Debugging: Compare UTC and America/LosAngeles display times without stripping the stored instant”. Show both compared result shapes at one row at TIME ZONE on timestamptz produces a local wall-clock display value grain, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `utc_wall_time`, `los_angeles_wall_time`, `e`, `utc`.
   **Verify:** For Exercise 5, run the two forms over the identical rows in `events`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
6. **Extension:** Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
   **Progressive hint:** Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
   **Expected result/shape:** Exercise 6 must make “Extension: Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero” observable through the exact DDL/DML command tag plus one row per requested calendar/cohort bucket and grouping key; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `utc_date`, `order_count`, `o`, `c`, `d`, `utc`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `utc_date`, `order_count`, `o`, `c`, `d`, `utc`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

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

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
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
