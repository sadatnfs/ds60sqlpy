# Day 13: Date/Time Functions and Time Zones (Companion Guide)

## How to run this lesson

In `./classroom`, choose PostgreSQL, open **sql-13** and run **Whole SQL lesson (psql)**. Inside one `BEGIN`/`ROLLBACK` block on `advanced_sql_training`, `psql` prints two result blocks: the 50 longest-standing customers with their tenure and UTC sign-up month, then the 30 latest UTC order dates with daily revenue and a seven-row running sum. Both queries only read.

Edit your copy at
`.learning/sql/sql-13/lesson/workspace/sql/postgres-60day/day13_date_time_functions.sql`.
This lesson is unusual: the fixture's timestamps are generated relative to the day the course tables were loaded, and several queries compare them with `now()` or `CURRENT_DATE`. The numbers quoted below come from a check run on 2026-11-25 UTC, roughly a day after loading. Your dates will differ; the patterns (which rows lead, where gaps appear, which boundary is excluded) will not.

Loading, resetting and the classroom buttons are covered in the study guide's [classroom section](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom); the [notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is optional.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 12; string functions](day12_string_functions.md)
- **Artifacts:** [learner SQL](../day13_date_time_functions.sql) ·
  [solution reasoning](../solutions/day13_solutions.md) ·
  [executable solution](../solutions/day13_solutions.sql)

## A beginner's mental model for this lesson

`orders.order_date`, `customers.created_at` and `events.event_time` are all `timestamptz`. Despite the name, a `timestamptz` stores no zone: it stores one instant, and `psql` prints it in the session's `TimeZone`, which is UTC in the classroom. That is why every value ends in `+00`. A calendar date, on the other hand, only exists once you pick a **time zone**: the first event in the fixture happened on 9 December 2022 in UTC and on 8 December in Los Angeles.

`instant AT TIME ZONE 'UTC'` turns the instant into a plain wall-clock `timestamp` for that zone, and `::date` or `date_trunc` then makes a **calendar bucket** from it. Do the conversion first and the truncation second. If you skip the conversion, PostgreSQL truncates in whatever zone the session uses; in a Los Angeles session, 69 orders would land in a different month.

To select a period, compare the raw instant with two boundaries: `order_date >= start AND order_date < next_start`. This **half-open interval** includes the first instant and excludes the next period's first instant, so consecutive months never share a row and never miss one. `BETWEEN` includes both ends, which double-counts an order placed exactly at midnight on the first.

## Two worked SQL examples

### Example 1

```sql
SELECT
  customer_id,
  full_name,
  now() - created_at AS tenure,
  date_trunc('month', created_at AT TIME ZONE 'UTC')::date AS cohort_month_utc
FROM
  customers
ORDER BY
  tenure DESC,
  customer_id
LIMIT 50;
```

**How to read it:** `now() - created_at` subtracts two instants and returns an `interval`, displayed as days plus a clock time such as `1483 days 04:37:06`. It never shows months, because a month has no fixed length. `created_at AT TIME ZONE 'UTC'` turns each instant into a UTC wall-clock time, `date_trunc('month', ...)` rounds it down to the first of the month, and `::date` drops the zero time. Sorting by `tenure DESC` puts the earliest sign-ups first.

**Expected result/shape:** 50 rows. In our check, customer 429 (created 2022-11-03 03:00 UTC) leads with about 1,483 days, followed by customers 343 and 257, all in the 2022-11-01 cohort. The 50 rows cover six cohort months, November 2022 to April 2023. No two customers share a `created_at`, so the `customer_id` tie-breaker never decides anything here. Rerun tomorrow and every tenure grows by one day while the order stays the same.

### Example 2

```sql
WITH daily AS (
  SELECT
    (o.order_date AT TIME ZONE 'UTC')::date AS d_utc,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    d_utc
)
SELECT
  d_utc,
  revenue,
  SUM(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_7_observed_days
FROM
  daily
ORDER BY
  d_utc DESC
LIMIT 30;
```

**How to read it:** `daily` converts each order to its UTC calendar date and adds up `total_amount` per date, one row per date that has orders. The window `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` then sums the current row and the six rows before it in date order. Those are the seven most recent dates that had orders, not necessarily the last seven calendar days, which is what the alias `revenue_7_observed_days` admits.

**Expected result/shape:** 30 rows, newest first. In our check they run from 2026-11-23 (one order, 742.14, seven-row sum 14,555.16) back to 2026-10-25. Every one of those 30 dates had orders, so here the seven rows do equal seven calendar days. Earlier history is sparser: only 1,081 dates between 2023-02-13 and 2026-11-23 have orders, and 406 of the seven-row windows stretch over more than seven calendar days, one of them over 60.

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
- **Review loop:** for each query, write the boundary instants it uses (in UTC) and say which side is included; then look at the first and last row printed and check they sit inside those boundaries.

## Exercises

Treat timestamps as instants, dates as calendar values, and reporting zones/window boundaries as explicit parts of the query.

Exercises 1, 4 and 6 depend on the current time, so note the timestamp you run them at; Exercises 2, 3 and 5 group or label fixed data. For each one, write down the boundary instants or zone it uses before you run it.

1. **Query writing:** List orders from the last 30 days with their UTC calendar date.
   **Think first:** the fixture never gains new orders. Will the count from this query rise or fall if you run it again next week?
   **Progressive hint:** Filter the timestamp directly and convert for display only.
   **Inputs/evidence:** For sql-13 Exercise 1, read `orders.order_date` (`timestamptz`) and keep rows on or after `CURRENT_TIMESTAMP - INTERVAL '30 days'`, adding `(o.order_date AT TIME ZONE 'UTC')::date` as `utc_order_date`.
   **Expected result/shape:** For sql-13 Exercise 1, return 209 rows on a freshly loaded fixture, newest first from order 2258 (`2026-11-23` UTC when loaded on 2026-11-25) back to order 734, the oldest order still inside the window. The final columns are `order_id`, `order_date`, and `utc_order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-13 Exercise 1, confirm 209 distinct `order_id` values and 0 returned rows where `order_date < CURRENT_TIMESTAMP - INTERVAL '30 days'`. Inside a rolled-back transaction, insert one order dated `CURRENT_TIMESTAMP - INTERVAL '29 days'` and one dated 31 days back; the count must become 210, so only the first one enters the window.
2. **Query writing:** Summarize orders and stored revenue by UTC month.
   **Think first:** orders start in February 2023 and every month since has at least one. How many month rows should print?
   **Progressive hint:** Convert to UTC before truncating when the reporting calendar is UTC.
   **Inputs/evidence:** For sql-13 Exercise 2, bucket all 4,362 `orders` by `date_trunc('month', o.order_date AT TIME ZONE 'UTC')`, counting orders and summing `total_amount` per UTC month.
   **Expected result/shape:** For sql-13 Exercise 2, return 46 month rows on a freshly loaded fixture, from `2023-02-01` (2 orders, 1203.26) to the current month, which holds 151 orders and 85364.67 when loaded on 2026-11-25. The final columns are `utc_month`, `order_count`, and `stored_revenue`. The final order is `utc_month`.
   **Verify:** For sql-13 Exercise 2, confirm the 46 `order_count` values add up to 4,362 and the `stored_revenue` values add up to 2355646.89, matching `SELECT SUM(total_amount) FROM orders`. Run it again after `SET LOCAL timezone = 'America/Los_Angeles'` in a rolled-back transaction; the output must not change, because the month is computed from the UTC wall time rather than the session zone.
3. **Query writing:** Calculate each customer's age in whole days as of the current date.
   **Think first:** subtracting one `date` from another gives what type? An integer, or an interval?
   **Progressive hint:** Compare calendar dates after declaring the UTC reporting date.
   **Inputs/evidence:** For sql-13 Exercise 3, subtract each customer's UTC `created_at` date from today's UTC date for all 500 `customers` rows.
   **Expected result/shape:** For sql-13 Exercise 3, return 500 rows, one per customer, with `customer_age_days` between 33 (customer 86) and 1,483 (customer 429) on a freshly loaded fixture; customer 1 shows 48. The final columns are `customer_id`, `created_at`, and `customer_age_days`. The final order is `c.customer_id`.
   **Verify:** For sql-13 Exercise 3, confirm 500 distinct `customer_id` values and 0 rows with a negative `customer_age_days`. Inside a rolled-back transaction, set customer 1's `created_at` to `CURRENT_TIMESTAMP`; its age must become 0, not 1, because both sides are converted to UTC dates before subtracting.
4. **Prediction:** Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
   **Think first:** which exact instant does `< next_month_start` leave out, and would `BETWEEN` count an order placed at that instant in two months?
   **Progressive hint:** Include the month start and exclude the next month start.
   **Inputs/evidence:** For sql-13 Exercise 4, build the current UTC month's start and the next month's start in a one-row `bounds` CTE, then keep `orders` with `order_date >= month_start AT TIME ZONE 'UTC'` and `order_date < next_month_start AT TIME ZONE 'UTC'`.
   **Expected result/shape:** For sql-13 Exercise 4, return one row per order placed in the current UTC month, oldest first; on a fixture loaded on 2026-11-25 that is 151 orders, from order 3106 on 2026-11-01 to order 2258 on 2026-11-23. The final columns are `order_id`, and `order_date`. The final order is `o.order_date, o.order_id`.
   **Verify:** For sql-13 Exercise 4, confirm the row count equals the last `order_count` from Exercise 2 (151 on that load). Inside a rolled-back transaction, insert one order one microsecond before the month start, one exactly at the month start, and one exactly at the next month's start; the count must rise by 1 only, and the new earliest row must be the one at midnight on the first.
5. **Debugging:** Compare UTC and America/Los_Angeles display times without stripping the stored instant.
   **Think first:** the earliest events are in December and January. How many hours behind UTC is Los Angeles then, and can that change the date?
   **Progressive hint:** `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
   **Inputs/evidence:** For sql-13 Exercise 5, sort the 20,000 `events` rows by `event_time, event_id`, keep the first 20, and show each instant as `AT TIME ZONE 'UTC'` and `AT TIME ZONE 'America/Los_Angeles'` wall times.
   **Expected result/shape:** For sql-13 Exercise 5, return 20 rows from event 17121 (`2022-12-09 07:14:09.605663` UTC, `2022-12-08 23:14:09.605663` in Los Angeles) to event 3362 on 2023-01-22; every winter row shows Los Angeles 8 hours behind UTC. The final columns are `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`. The final order is `e.event_time, e.event_id`.
   **Verify:** For sql-13 Exercise 5, confirm 20 distinct `event_id` values and that the 21st row of the same ordering is event 17001, which the `LIMIT` cuts off. Rerun after `SET LOCAL timezone = 'America/Los_Angeles'` in a rolled-back transaction: `event_time` must display as `2022-12-08 23:14:09.605663-08` while `utc_wall_time` stays the same. Event 6402 (`2023-07-01 01:13` UTC) shows the summer gap of 7 hours.
6. **Extension:** Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
   **Think first:** if today and yesterday had no orders, how many rows should still print, and what should they show?
   **Progressive hint:** Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
   **Inputs/evidence:** For sql-13 Exercise 6, generate the last seven UTC dates with `generate_series`, count `orders` per UTC date from the first of those days onward, and `LEFT JOIN` the counts to the calendar.
   **Expected result/shape:** For sql-13 Exercise 6, return exactly 7 rows ending with today's UTC date; on a fixture loaded on 2026-11-25 the counts run 4, 4, 2, 2, 1, 0, 0 from 2026-11-19, and the two zero days come from `COALESCE` on dates with no orders. The final columns are `utc_date`, and `order_count`. The final order is `c.utc_date`.
   **Verify:** For sql-13 Exercise 6, confirm 7 distinct dates and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6) AT TIME ZONE 'UTC'` (13 on that load). Inside a rolled-back transaction, insert an order at `CURRENT_TIMESTAMP`; the last row must change from 0 to 1 and the row count must stay 7.

## Common mistakes and how to recover

- **`BETWEEN` for a month:** `order_date BETWEEN '2026-11-01' AND '2026-12-01'` includes an order stamped exactly at midnight on 1 December, so it counts in both November and December. Use `>= start AND < next_start`.
- **Truncating before converting:** `date_trunc('month', order_date)` uses the session zone. In a session set to America/Los_Angeles, 69 of the 4,362 orders move into the previous month. Convert with `AT TIME ZONE 'UTC'` first when the report calendar is UTC.
- **Wrapping the column in the filter:** `WHERE order_date::date >= CURRENT_DATE - 30` silently switches to whole calendar days (211 rows instead of 209 in our check) and cannot use a plain index on `order_date`. Compare the raw column with a computed boundary instead, as Exercise 1 does.
- **Expecting "last 30 days" to be stable:** the fixture is generated once at load time. Each day you wait, the newest orders slide out of the window and no new ones arrive, so the count keeps shrinking.
- **Treating `ROWS` frames as calendar windows:** Example 2's seven rows can span 60 calendar days in sparse periods. For a true seven-day window, use `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` or a calendar spine.

If the script stopped on an error, follow the study guide's [failure recovery notes](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Are all time windows explicit about inclusivity and time zone?
- Does month-offset logic include both year and month components when periods
  can span more than one year?

## Next step

Continue to [Day 14; numeric types and casting](day14_numeric_and_casting.md).

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

Further reading
- Date/time: https://www.postgresql.org/docs/17/functions-datetime.html
- generate_series: https://www.postgresql.org/docs/17/functions-srf.html

## Ask an AI tutor about this lesson

A tutor is optional. A good use for one here: ask it to pick an instant near midnight UTC on the first of a month and quiz you on its date in UTC, Los Angeles and Tokyo before revealing them. The prompt below keeps `solutions/` closed; setup is in the study guide's [tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-13: Date and Time Functions and Time Zones.

I have completed the direct catalog prerequisite: `sql-12`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day13_date_time_functions.md
- Answer-free learner SQL: sql/postgres-60day/day13_date_time_functions.sql

Key terms to teach in context: Half-open interval, Time zone, Calendar bucket. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Express one day as `timestamp >= day_start AND timestamp < next_day_start`. Test a row exactly at each boundary. This half-open form prevents double counting when adjacent daily queries are combined and is friendlier to a normal timestamp index than wrapping the column in a function.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
