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

## Exercises

Complete the prompts in the [learner SQL](../day13_date_time_functions.sql).
Add explicit boundary rows and report the session `TimeZone` beside your
results.

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

Exercises from the learner script
1) Compute the fiscal quarter for every order.
2) Calculate days since each customer's last order.

The repository does not define a fiscal-year start. To match the maintained
answer, explicitly assume fiscal quarters equal UTC calendar quarters and use
`EXTRACT(quarter FROM order_date AT TIME ZONE 'UTC')`. A business with another
fiscal start month needs a shifted-quarter calculation.

For customers without orders, “days since last order” is undefined and should
remain `NULL` unless the report defines a substitute. Choose whether a “day” is
an elapsed 24-hour interval or a difference between calendar dates; the
maintained answer uses UTC calendar dates.

Further reading
- Date/time: https://www.postgresql.org/docs/current/functions-datetime.html
- generate_series: https://www.postgresql.org/docs/current/functions-srf.html
