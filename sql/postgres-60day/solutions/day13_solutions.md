# Day 13 solutions: Date/Time Functions and Time Zones

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Three of these answers depend on the clock (Exercises 1, 4 and 6), one labels fixed events in two zones, and two group or age the fixture. After your attempt, run the companion file:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day13_solutions.sql
```

It sets `search_path` to `training, public` and ends with `ROLLBACK`. Exercise 2 always returns 46 months, Exercise 3 always 500 customers, Exercise 5 always 20 events and Exercise 6 always 7 dates. The counts for Exercises 1 and 4 depend on when you run relative to loading the tables; the figures below come from 2026-11-25 UTC. The prompts follow [the learner file](../day13_date_time_functions.sql) in order, and the study guide's [solution reading notes](../../STUDY-GUIDE.md#read-a-solution) explain how to compare your query with these.

## Reading contract

- **Focus:** Treat timestamps as instants, dates as calendar values, and reporting zones/window boundaries as explicit parts of the query.
- **Assumptions:** Stored event/order timestamps are `timestamptz`. Relative examples use the database clock; reports label UTC explicitly where conversion matters.
- **Primary pitfall:** `BETWEEN` is inclusive at both ends and is often wrong for adjacent time windows; use half-open `[start, end)` predicates.
- **Safety:** only `SELECT` statements, still inside `BEGIN`/`ROLLBACK`; `SET TimeZone` experiments you add inside the transaction also end with it.

## Exercise 1: Query writing

**Prompt:** List orders from the last 30 days with their UTC calendar date.

**Reasoning:** Filter the timestamp directly and convert for display only.

**Clause-by-clause reading:**

- `FROM orders AS o`: every order, stored as an instant.
- `WHERE o.order_date >= CURRENT_TIMESTAMP - INTERVAL '30 days'`: compares the raw column with one computed instant, exactly 30 times 24 hours ago.
- `(o.order_date AT TIME ZONE 'UTC')::date AS utc_order_date`: a display-only UTC date beside the original value.
- `ORDER BY o.order_date DESC, o.order_id DESC`: newest first.

```sql
SELECT
  o.order_id,
  o.order_date,
  (o.order_date AT TIME ZONE 'UTC')::date AS utc_order_date
FROM
  orders AS o
WHERE
  o.order_date >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY
  o.order_date DESC,
  o.order_id DESC;
```

**Expected shape:** Recent order rows in deterministic order.

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 1, read `orders.order_date` (`timestamptz`) and keep rows on or after `CURRENT_TIMESTAMP - INTERVAL '30 days'`, adding `(o.order_date AT TIME ZONE 'UTC')::date` as `utc_order_date`.
- **Expected result/shape:** For sql-13 Exercise 1, return 209 rows on a freshly loaded fixture, newest first from order 2258 (`2026-11-23` UTC when loaded on 2026-11-25) back to order 734, the oldest order still inside the window. The final columns are `order_id`, `order_date`, and `utc_order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-13 Exercise 1, confirm 209 distinct `order_id` values and 0 returned rows where `order_date < CURRENT_TIMESTAMP - INTERVAL '30 days'`. Inside a rolled-back transaction, insert one order dated `CURRENT_TIMESTAMP - INTERVAL '29 days'` and one dated 31 days back; the count must become 210, so only the first one enters the window.
- **What prints:** at 2026-11-25 07:36 UTC, 209 orders, the newest dated 2026-11-23. The cutoff was 2026-10-26 07:36 UTC, so orders 1613 (00:21) and 3912 (01:08) that morning are excluded even though their date is 26 October.
- **Why the count moves:** `CURRENT_TIMESTAMP` advances but the fixture does not, so this number falls a little each day after loading.
- **Index-friendly form:** the column stands alone on one side of `>=`. Writing `(o.order_date AT TIME ZONE 'UTC')::date >= CURRENT_DATE - 30` selects calendar days instead of a rolling 30 times 24 hours, and cannot use a plain index on `order_date`.
- **Two different answers:** that calendar-day version starts at midnight on 26 October, picks up orders 1613 and 3912, and returns 211 rows instead of 209. Decide which one the question means before writing it.

## Exercise 2: Query writing

**Prompt:** Summarize orders and stored revenue by UTC month.

**Reasoning:** Convert to UTC before truncating when the reporting calendar is UTC.

**Clause-by-clause reading:**

- `o.order_date AT TIME ZONE 'UTC'`: the UTC wall-clock time of each order.
- `date_trunc('month', ...)::date AS utc_month`: the first day of that UTC month.
- `COUNT(*)` and `ROUND(SUM(o.total_amount), 2)`: orders and stored revenue per month.
- `GROUP BY` the same truncation expression, then `ORDER BY utc_month`.

```sql
SELECT
  date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS utc_month,
  COUNT(*) AS order_count,
  ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM
  orders AS o
GROUP BY
  date_trunc('month', o.order_date AT TIME ZONE 'UTC')
ORDER BY
  utc_month;
```

**Expected shape:** One row per observed UTC month.

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 2, bucket all 4,362 `orders` by `date_trunc('month', o.order_date AT TIME ZONE 'UTC')`, counting orders and summing `total_amount` per UTC month.
- **Expected result/shape:** For sql-13 Exercise 2, return 46 month rows on a freshly loaded fixture, from `2023-02-01` (2 orders, 1203.26) to the current month, which holds 151 orders and 85364.67 when loaded on 2026-11-25. The final columns are `utc_month`, `order_count`, and `stored_revenue`. The final order is `utc_month`.
- **Independent verification:** For sql-13 Exercise 2, confirm the 46 `order_count` values add up to 4,362 and the `stored_revenue` values add up to 2355646.89, matching `SELECT SUM(total_amount) FROM orders`. Run it again after `SET LOCAL timezone = 'America/Los_Angeles'` in a rolled-back transaction; the output must not change, because the month is computed from the UTC wall time rather than the session zone.
- **What prints:** 46 rows, from 2023-02-01 (2 orders, 1,203.26) to the current month. In our check the last two rows were 2026-10-01 (313 orders, 170,179.13) and 2026-11-01 (151 orders, 85,364.67, a partial month).
- **Totals to reconcile:** the counts add up to 4,362 and the revenue to 2,355,646.89, the same as one `SUM(total_amount)` over all orders. A missing or extra month would break that.
- **Where the zone matters:** run `SET TimeZone = 'America/Los_Angeles'` first and drop the `AT TIME ZONE 'UTC'`: 69 orders change month, and the monthly counts shift even though the total does not.
- **Edge case:** an order at 2026-12-01 00:00:00 UTC belongs to December here, because truncation in UTC rounds it to its own month start.

## Exercise 3: Query writing

**Prompt:** Calculate each customer's age in whole days as of the current date.

**Reasoning:** Compare calendar dates after declaring the UTC reporting date.

**Clause-by-clause reading:**

- `(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date`: today's UTC date.
- `(c.created_at AT TIME ZONE 'UTC')::date`: the customer's UTC sign-up date.
- The difference of two `date` values is an integer number of days, named `customer_age_days`.
- `ORDER BY c.customer_id`: all 500 customers.

```sql
SELECT
  c.customer_id,
  c.created_at,
  (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - (c.created_at AT TIME ZONE 'UTC')::date AS customer_age_days
FROM
  customers AS c
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer with nonnegative age days.

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 3, subtract each customer's UTC `created_at` date from today's UTC date for all 500 `customers` rows.
- **Expected result/shape:** For sql-13 Exercise 3, return 500 rows, one per customer, with `customer_age_days` between 33 (customer 86) and 1,483 (customer 429) on a freshly loaded fixture; customer 1 shows 48. The final columns are `customer_id`, `created_at`, and `customer_age_days`. The final order is `c.customer_id`.
- **Independent verification:** For sql-13 Exercise 3, confirm 500 distinct `customer_id` values and 0 rows with a negative `customer_age_days`. Inside a rolled-back transaction, set customer 1's `created_at` to `CURRENT_TIMESTAMP`; its age must become 0, not 1, because both sides are converted to UTC dates before subtracting.
- **What prints:** 500 rows. In our check customer 1 (created 2026-10-08) was 48 days old, and ages ranged from 33 to 1,483 days.
- **Whole days by design:** subtracting dates ignores the time of day, so a customer created at 23:00 is one day old an hour later. Use `now() - created_at` (as Example 1 does) when the hours matter.
- **Compared with `age()`:** `age(CURRENT_DATE, created_at::date)` returns an interval in years, months and days, which is not a single number you can sort or average.
- **Edge case:** without the UTC conversion, `created_at::date` follows the session zone. In a Los Angeles session, customer 429 (created 2022-11-03 03:00 UTC) gets a sign-up date of 2 November.

## Exercise 4: Prediction

**Prompt:** Use a half-open interval to select one UTC calendar month and explain which boundary instant is excluded.

**Reasoning:** Include the month start and exclude the next month start.

**Clause-by-clause reading:**

- `bounds`: `date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')` is midnight on the first of this UTC month as a plain timestamp; adding one month gives the next month's start.
- `CROSS JOIN bounds`: attaches the two boundaries to every order.
- `o.order_date >= b.month_start AT TIME ZONE 'UTC'`: turns the boundary back into an instant before comparing.
- `AND o.order_date < b.next_month_start AT TIME ZONE 'UTC'`: the excluded end.

```sql
WITH bounds AS (
  SELECT
    date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AS month_start,
    date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '1 month' AS next_month_start
)
SELECT
  o.order_id,
  o.order_date
FROM
  orders AS o
  CROSS JOIN bounds AS b
WHERE
  o.order_date >= b.month_start AT TIME ZONE 'UTC'
  AND o.order_date < b.next_month_start AT TIME ZONE 'UTC'
ORDER BY
  o.order_date,
  o.order_id;
```

**Expected shape:** Orders in exactly one UTC month.

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 4, build the current UTC month's start and the next month's start in a one-row `bounds` CTE, then keep `orders` with `order_date >= month_start AT TIME ZONE 'UTC'` and `order_date < next_month_start AT TIME ZONE 'UTC'`.
- **Expected result/shape:** For sql-13 Exercise 4, return one row per order placed in the current UTC month, oldest first; on a fixture loaded on 2026-11-25 that is 151 orders, from order 3106 on 2026-11-01 to order 2258 on 2026-11-23. The final columns are `order_id`, and `order_date`. The final order is `o.order_date, o.order_id`.
- **Independent verification:** For sql-13 Exercise 4, confirm the row count equals the last `order_count` from Exercise 2 (151 on that load). Inside a rolled-back transaction, insert one order one microsecond before the month start, one exactly at the month start, and one exactly at the next month's start; the count must rise by 1 only, and the new earliest row must be the one at midnight on the first.
- **What prints:** the orders of the current UTC month. In our check that was November 2026: 151 rows, the first at 2026-11-01 00:50:08 UTC. The count matches Exercise 2's November row.
- **The excluded instant:** 2026-12-01 00:00:00 UTC. An order at that instant belongs to December only, which is the answer to the prediction prompt.
- **Why two `AT TIME ZONE` calls:** the first makes a wall-clock timestamp so `date_trunc` works in UTC; the second turns the result back into a `timestamptz` instant so it compares with `order_date` correctly.
- **The tempting shortcut:** `BETWEEN` with the same two boundaries also returns 151 rows today, because no order sits exactly on 1 December. It is still wrong, and would double-count such an order in both months.

## Exercise 5: Debugging

**Prompt:** Compare UTC and America/Los_Angeles display times without stripping the stored instant.

**Reasoning:** `AT TIME ZONE` on `timestamptz` produces a local wall-clock display value.

**Clause-by-clause reading:**

- `FROM events AS e`: 20,000 events, sorted by time; the first 20 are shown.
- `e.event_time AT TIME ZONE 'UTC' AS utc_wall_time`: the UTC clock reading.
- `e.event_time AT TIME ZONE 'America/Los_Angeles' AS los_angeles_wall_time`: the Los Angeles clock reading for the same instant.
- `e.event_time` itself is left unchanged in the output.

```sql
SELECT
  e.event_id,
  e.event_time,
  e.event_time AT TIME ZONE 'UTC' AS utc_wall_time,
  e.event_time AT TIME ZONE 'America/Los_Angeles' AS los_angeles_wall_time
FROM
  events AS e
ORDER BY
  e.event_time,
  e.event_id
LIMIT 20;
```

**Expected shape:** One row per sampled event with two displays of the same instant.

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 5, sort the 20,000 `events` rows by `event_time, event_id`, keep the first 20, and show each instant as `AT TIME ZONE 'UTC'` and `AT TIME ZONE 'America/Los_Angeles'` wall times.
- **Expected result/shape:** For sql-13 Exercise 5, return 20 rows from event 17121 (`2022-12-09 07:14:09.605663` UTC, `2022-12-08 23:14:09.605663` in Los Angeles) to event 3362 on 2023-01-22; every winter row shows Los Angeles 8 hours behind UTC. The final columns are `event_id`, `event_time`, `utc_wall_time`, and `los_angeles_wall_time`. The final order is `e.event_time, e.event_id`.
- **Independent verification:** For sql-13 Exercise 5, confirm 20 distinct `event_id` values and that the 21st row of the same ordering is event 17001, which the `LIMIT` cuts off. Rerun after `SET LOCAL timezone = 'America/Los_Angeles'` in a rolled-back transaction: `event_time` must display as `2022-12-08 23:14:09.605663-08` while `utc_wall_time` stays the same. Event 6402 (`2023-07-01 01:13` UTC) shows the summer gap of 7 hours.
- **What prints:** 20 rows, from 2022-12-09 to 2023-01-22. Event 17121 happened at 2022-12-09 07:11:55 UTC, which was 2022-12-08 23:11:55 in Los Angeles, the previous day.
- **A year boundary:** event 6761 at 2023-01-01 00:33 UTC shows 2022-12-31 16:33 in Los Angeles, so a yearly report by local date puts it in a different year.
- **The offset:** all 20 rows are eight hours apart, because Los Angeles is on standard time in winter. A July event would show seven hours.
- **What stays fixed:** the `event_time` column still prints with `+00` and identifies the same instant; only the two derived columns are local readings, and they carry no zone.
- **Counting date changes:** wrap the query and count rows where the UTC date and the Los Angeles date differ. Four of the 20 do, all of them events logged before 08:00 UTC, when it is still the previous evening on the US west coast.

## Exercise 6: Extension

**Prompt:** Create a seven-day UTC calendar and left join daily order counts so missing days appear as zero.

**Reasoning:** Generate the date spine first, aggregate orders by the same UTC date, then `COALESCE` absent counts.

**Clause-by-clause reading:**

- `calendar`: `generate_series` from six days before today's UTC date up to today, one row per date.
- `daily_orders`: orders grouped by UTC date, limited to instants on or after the first calendar date at midnight UTC.
- `calendar LEFT JOIN daily_orders`: keeps every calendar date, matched or not.
- `COALESCE(d.order_count, 0)`: turns a missing match into zero.

```sql
WITH calendar AS (
  SELECT
    generate_series((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6, (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date, INTERVAL '1 day')::date AS utc_date
),
daily_orders AS (
  SELECT
    (o.order_date AT TIME ZONE 'UTC')::date AS utc_date,
    COUNT(*) AS order_count
  FROM
    orders AS o
  WHERE
    o.order_date >= ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6) AT TIME ZONE 'UTC'
  GROUP BY
    (o.order_date AT TIME ZONE 'UTC')::date
)
SELECT
  c.utc_date,
  COALESCE(d.order_count, 0) AS order_count
FROM
  calendar AS c
  LEFT JOIN daily_orders AS d ON d.utc_date = c.utc_date
ORDER BY
  c.utc_date;
```

**Expected shape:** Exactly seven chronological rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-13 Exercise 6, generate the last seven UTC dates with `generate_series`, count `orders` per UTC date from the first of those days onward, and `LEFT JOIN` the counts to the calendar.
- **Expected result/shape:** For sql-13 Exercise 6, return exactly 7 rows ending with today's UTC date; on a fixture loaded on 2026-11-25 the counts run 4, 4, 2, 2, 1, 0, 0 from 2026-11-19, and the two zero days come from `COALESCE` on dates with no orders. The final columns are `utc_date`, and `order_count`. The final order is `c.utc_date`.
- **Independent verification:** For sql-13 Exercise 6, confirm 7 distinct dates and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 6) AT TIME ZONE 'UTC'` (13 on that load). Inside a rolled-back transaction, insert an order at `CURRENT_TIMESTAMP`; the last row must change from 0 to 1 and the row count must stay 7.
- **What prints:** 7 rows. In our check: 19 November 4, 20 November 4, 21 November 2, 22 November 2, 23 November 1, then 24 and 25 November with 0. The fixture's last order is on 23 November, so the two most recent days appear only because of the spine.
- **Without the spine:** grouping `orders` alone returns 5 rows and silently skips the empty days.
- **Same key on both sides:** the spine and the aggregate both use the UTC date. Mixing a UTC spine with dates truncated in another zone makes some counts land on the wrong row.
- **Spotting the empty days:** `SELECT COUNT(*) FILTER (WHERE order_count = 0)` over this result gives 2 in our check; the number grows by one for every day you wait after loading.

## Final self-check

- What does `+00` at the end of a `timestamptz` tell you, and what does it not tell you?
- In Example 2, why can the seven-row sum cover 60 calendar days?
- Which instant does Exercise 4 exclude, and why is that the right choice?
- Why did event 17121 fall on a different date in Los Angeles?
- What would Exercise 6 print if you dropped the `LEFT JOIN` to the calendar?
