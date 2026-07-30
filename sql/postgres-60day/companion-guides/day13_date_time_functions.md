# Day 13 — Date/Time Functions and Time Zones (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 12 — string functions](day12_string_functions.md)
- **Artifacts:** [learner SQL](../day13_date_time_functions.sql) ·
  [solution reasoning](../solutions/day13_solutions.md) ·
  [executable solution](../solutions/day13_solutions.sql)

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
   **Expected shape:** Recent order rows in deterministic order.
2. **Query writing:** Summarize orders and stored revenue by UTC month.
   **Progressive hint:** Convert to UTC before truncating when the reporting calendar is UTC.
   **Expected shape:** One row per observed UTC month.
3. **Query writing:** Calculate each customer's age in whole days as of the current date.
   **Progressive hint:** Compare calendar dates after declaring the UTC reporting date.
   **Expected shape:** One row per customer with nonnegative age days.
4. **Prediction:** Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.
   **Progressive hint:** Include the month start and exclude the next month start.
   **Expected shape:** Orders in exactly one UTC month.
5. **Debugging:** Compare UTC and America/Los_Angeles display times without stripping the stored instant.
   **Progressive hint:** `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.
   **Expected shape:** One row per sampled event with two displays of the same instant.
6. **Extension:** Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.
   **Progressive hint:** Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.
   **Expected shape:** Exactly seven chronological rows.

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
