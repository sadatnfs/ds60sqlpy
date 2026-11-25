# Day 22 solutions: Advanced Windows: Multiple Partitions, Named Windows, Exclusion


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Nothing in `day22_solutions.sql` writes: it reads `orders`, `employees` and
`events` with `search_path` set to `training`, between `BEGIN` and
`ROLLBACK`, so you can rerun it as often as you like. The general comparison
method is in [Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day22_solutions.sql
```

## How these answers fit together

Exercises 1 to 3 add window columns to a base table and must keep its row
count (4,362 orders, 100 employees). Exercises 4 to 6 build in layers: event
gaps, then session flags, then session numbers, then one row per session,
while Exercise 5 applies the same layering idea to order dates. On the standard
fixture, sessions and islands are all single-row, so the edge-case notes below
show how to insert test rows that exercise the logic. The learner file is
[day22_advanced_windows.sql](../day22_advanced_windows.sql).

## Reading contract

- **Focus:** Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
- **Assumptions:** Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
- **Primary pitfall:** Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Use a named window to show each order with customer count, average, first date, and last date.

**Reasoning:** Name a full-partition customer window once and reuse it.

```sql
SELECT
  o.order_id,
  o.customer_id,
  COUNT(*) OVER customer_window AS customer_order_count,
  ROUND(AVG(o.total_amount) OVER customer_window, 2) AS customer_average,
  FIRST_VALUE(o.order_date) OVER customer_window AS first_order_date,
  LAST_VALUE(o.order_date) OVER customer_window AS last_order_date
FROM
  orders AS o
WINDOW customer_window AS (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 1, read `orders` once and define the named window `customer_window` as `PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id` with an explicit `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` frame; keep `order_id` because every order stays a row.
- **Expected result/shape:** For sql-22 Exercise 1, expected output: 4362 rows, one per `order_id`, where every row of a customer repeats the same count, average, first date, and last date (customer 1 shows 5 orders averaging 504.33). The final columns are `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-22 Exercise 1, compare against `SELECT customer_id, COUNT(*), ROUND(AVG(total_amount), 2), MIN(order_date), MAX(order_date) FROM orders GROUP BY customer_id` (438 rows; counts run from 4 to 16) and require every order row to match its customer; then drop the explicit frame and count rows where `LAST_VALUE(order_date)` differs from the customer's `MAX(order_date)`: 3924 rows (4362 minus the 438 last orders) disagree, because the default frame stops at the current row.
- **Intermediate relation check:** There is no CTE, so check the base: 4,362 orders from 438 customers with 4 to 16 orders each. The answer must return 4,362 rows, and every row for one customer must show the same four window values.
- **Clause check:** The `WINDOW customer_window AS (...)` clause sits after `FROM` and before `ORDER BY`, and four functions refer to it by name. Its frame from `UNBOUNDED PRECEDING` to `UNBOUNDED FOLLOWING` makes `COUNT` and `AVG` cover the whole customer despite the `ORDER BY`, and makes `LAST_VALUE` return the latest date. Customer 1 shows 5 orders and an average of 504.33 on every row.
- **Alternative/trade-off:** `MIN(o.order_date) OVER (PARTITION BY o.customer_id)` and the matching `MAX` give the same first and last dates without any frame to get wrong; on this fixture `MAX` matches `LAST_VALUE` on all 4,362 rows. A `GROUP BY` summary joined back to `orders` also works but adds a join.
- **Edge case:** Delete only the frame clause and customer 1's five rows show running counts 1 to 5, running averages from 240.20 to 504.33, and each row's own date as `last_order_date`.

## Exercise 2: Query writing

**Prompt:** Compare each employee salary with the average of other employees in the department.

**Reasoning:** Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.

```sql
SELECT
  e.employee_id,
  e.department_id,
  e.salary,
  ROUND(AVG(e.salary) OVER (PARTITION BY e.department_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING EXCLUDE CURRENT ROW), 2) AS other_employee_average
FROM
  employees AS e
ORDER BY
  e.department_id,
  e.employee_id;
```

**Expected shape:** One row per employee with nullable peer average.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 2, read the 100 rows of `employees`, partition by `department_id`, and average `salary` over the whole partition with `EXCLUDE CURRENT ROW` so each employee is compared only with colleagues; keep `employee_id` because the result is employee grain.
- **Expected result/shape:** For sql-22 Exercise 2, expected output: 100 rows, one per employee; no department has a single employee, so no average is NULL on the seed. The final columns are `employee_id`, `department_id`, `salary`, and `other_employee_average`. The final order is `e.department_id, e.employee_id`.
- **Independent verification:** For sql-22 Exercise 2, for department 1 (17 employees, salary total 745965.27) check (total - salary) / 16 by hand: employee 1 at 40079.19 returns 44117.88 and employee 7 at 40554.33 returns 44088.18; then run the window on `VALUES (9, 50000)` as a one-employee department and confirm `other_employee_average` is NULL, because excluding the only row leaves an empty frame.
- **Intermediate relation check:** Departments 1 to 4 have 17 employees and departments 5 and 6 have 16, so each "other employees" average covers 16 or 15 salaries. The result keeps all 100 employees.
- **Clause check:** The window has no `ORDER BY`, so its frame spans the whole department, and `EXCLUDE CURRENT ROW` drops only the row being computed. Employee 1 (40,079.19) therefore sees 44,117.88, the mean of the other 16, rather than the department mean of 43,880.31.
- **Alternative/trade-off:** `(SUM(salary) OVER w - salary) / NULLIF(COUNT(*) OVER w - 1, 0)` with `w AS (PARTITION BY department_id)` matches all 100 values and works in databases that lack frame exclusion. The `EXCLUDE` form states the intent more directly.
- **Edge case:** With no `ORDER BY` every row in the department is a peer, so `EXCLUDE GROUP` would remove the whole department and return `NULL`, and `EXCLUDE TIES` would leave only the current row and return the employee's own salary. A department with a single employee returns `NULL` under `EXCLUDE CURRENT ROW`, which the contract treats as correct.

## Exercise 3: Query writing

**Prompt:** Show each order's distance from its customer's average and standard deviation.

**Reasoning:** Compute independent partition windows and guard interpretation when variation is zero.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.total_amount,
  ROUND(AVG(o.total_amount) OVER customer_orders, 2) AS customer_average,
  ROUND(STDDEV_POP(o.total_amount) OVER customer_orders, 2) AS customer_stddev,
  ROUND((o.total_amount - AVG(o.total_amount) OVER customer_orders) / NULLIF (STDDEV_POP(o.total_amount) OVER customer_orders, 0), 4) AS customer_z_score
FROM
  orders AS o
WINDOW customer_orders AS (PARTITION BY o.customer_id)
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 3, read `orders` with one named window `customer_orders AS (PARTITION BY o.customer_id)` and no `ORDER BY`, so the average and population standard deviation cover all of a customer's orders; `NULLIF(..., 0)` guards the z-score denominator.
- **Expected result/shape:** For sql-22 Exercise 3, expected output: 4362 rows, one per order, with z-scores between -2.3308 and 2.6257 on the seed and none NULL, because every customer has at least 4 orders that are not all equal. The final columns are `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-22 Exercise 3, for customer 1 confirm `SELECT ROUND(AVG(total_amount), 2), ROUND(STDDEV_POP(total_amount), 2) FROM orders WHERE customer_id = 1` returns 504.33 and 366.08, and that order 1 at 240.20 has z = -0.7215; then run the z-score expression on the one-row fixture `VALUES (1, 50.00)` and confirm it returns NULL with `NULLIF` and the error `division by zero` without it.
- **Intermediate relation check:** Every customer has at least four orders and none has identical amounts across all of them, so no fixture partition has a standard deviation of 0. The z-scores run from about -2.33 to 2.63 across 4,362 rows.
- **Clause check:** `customer_orders` has a partition but no ordering, so `AVG` and `STDDEV_POP` each read all of a customer's orders. `NULLIF(..., 0)` turns a zero deviation into `NULL`, so the division returns `NULL` instead of raising a division-by-zero error.
- **Alternative/trade-off:** `STDDEV_SAMP` divides by n - 1, giving larger deviations and z-scores from about -2.18 to 2.54. Population deviation fits here because each partition is the complete set of that customer's orders, not a sample.
- **Edge case:** A customer with one order, or with identical amounts, would get a deviation of 0 and a `NULL` z-score. Adding `ORDER BY o.order_date` to the named window would silently switch both measures to running statistics.

## Exercise 4: Prediction

**Prompt:** Sessionize events using a 30-minute gap and predict why the first event starts a session.

**Reasoning:** Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.

```sql
WITH sequenced AS (
  SELECT
    e.*,
    LAG(e.event_time) OVER (PARTITION BY e.customer_id ORDER BY e.event_time,
      e.event_id) AS previous_event_time
  FROM
    events AS e
),
flagged AS (
  SELECT
    sequenced.*,
    CASE WHEN previous_event_time IS NULL
      OR event_time - previous_event_time > INTERVAL '30 minutes' THEN
      1
    ELSE
      0
    END AS starts_session
  FROM
    sequenced
)
SELECT
  event_id,
  customer_id,
  event_time,
  SUM(starts_session) OVER (PARTITION BY customer_id ORDER BY event_time, event_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS session_number
FROM
  flagged
ORDER BY
  customer_id,
  event_time,
  event_id;
```

**Expected shape:** One row per event with session number starting at one.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 4, read `events` (20000 rows, 40 per customer), use `LAG(event_time)` per customer to find the previous event, flag a session start when there is no previous event or the gap is more than 30 minutes, and keep a running `SUM` of the flags; keep `event_id` because each event stays a row.
- **Expected result/shape:** For sql-22 Exercise 4, expected output: 20000 rows, one per event; on the seed the shortest gap between a customer's consecutive events is about 19 hours, so every event starts a new session and `session_number` runs from 1 to 40 for each of the 500 customers. The final columns are `event_id`, `customer_id`, `event_time`, and `session_number`. The final order is `customer_id, event_time, event_id`.
- **Independent verification:** For sql-22 Exercise 4, confirm exactly 500 rows have no previous event (one per customer) and `MAX(session_number)` is 40; because the seed never shows two events in one session, run the same CTEs on `VALUES (1, 1, TIMESTAMPTZ '2025-01-01 10:00+00'), (2, 1, TIMESTAMPTZ '2025-01-01 10:20+00'), (3, 1, TIMESTAMPTZ '2025-01-01 11:00+00')` and expect session numbers 1, 1, 2; a gap of exactly 30 minutes stays in the same session, since the test is strictly greater than.
- **Intermediate relation check:** `sequenced` has 20,000 rows, and `previous_event_time` is `NULL` for exactly 500 of them, one per customer. In `flagged`, `starts_session` is 1 on all 20,000 rows, because the smallest gap between a customer's events is 18 hours 57 minutes.
- **Clause check:** `LAG` ordered by `event_time, event_id` fetches the previous event; the `CASE` marks a `NULL` previous time or a gap over 30 minutes as 1; the running `SUM` turns those marks into session numbers. The first event has no predecessor, so its flag is 1 and its session number is 1, which answers the prediction.
- **Alternative/trade-off:** The flag can be computed in the same level as `LAG` by repeating the `LAG(...) OVER (...)` expression inside the `CASE`, leaving two layers instead of three. That is legal because a window result may sit inside an ordinary expression such as `CASE`; only passing it as the argument of another window function needs a new layer.
- **Edge case:** Inside `BEGIN`/`ROLLBACK`, insert events for customer 1 at 10:00, 10:20, 10:50 and 11:21 on a future date. They become sessions 41, 41, 41 and 42: a gap of exactly 30 minutes stays in the session because the test is `>`, and 31 minutes starts a new one.

## Exercise 5: Debugging

**Prompt:** Find consecutive calendar-day islands in customer order dates without nesting windows.

**Reasoning:** Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.

```sql
WITH order_days AS (
  SELECT DISTINCT
    o.customer_id,
    (o.order_date AT TIME ZONE 'UTC')::date AS order_day
  FROM
    orders AS o
),
numbered AS (
  SELECT
    customer_id,
    order_day,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_day) AS day_number
FROM
  order_days
),
grouped AS (
  SELECT
    customer_id,
    order_day,
    order_day - day_number::integer AS island_key
  FROM
    numbered
)
SELECT
  customer_id,
  MIN(order_day) AS island_start,
  MAX(order_day) AS island_end,
  COUNT(*) AS days_in_island
FROM
  grouped
GROUP BY
  customer_id,
  island_key
ORDER BY
  customer_id,
  island_start;
```

**Expected shape:** One row per customer/date island.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 5, read from `orders`, reduce them to distinct (`customer_id`, UTC order day) pairs, number each customer's days with `ROW_NUMBER()`, and group by `order_day - day_number` to find runs of consecutive days.
- **Expected result/shape:** For sql-22 Exercise 5, expected output: One row per customer/date island. The final columns are `customer_id`, `island_start`, `island_end`, and `days_in_island`. The final order is `customer_id, island_start`.
- **Independent verification:** For sql-22 Exercise 5, confirm that `SUM(days_in_island)` equals the number of distinct customer order days, `SELECT COUNT(*) FROM (SELECT DISTINCT customer_id, (order_date AT TIME ZONE 'UTC')::date FROM orders) d`; on the seed both are 4362 and every island is one day long, because a customer's orders are always more than two days apart, so also run the same CTEs on `VALUES (1, DATE '2025-01-01'), (1, DATE '2025-01-02'), (1, DATE '2025-01-04')` and expect two islands of 2 and 1 days.
- **Intermediate relation check:** `order_days` has 4,362 rows, the same as `orders`, so no customer ordered twice on one UTC day. `numbered` and `grouped` keep that count.
- **Clause check:** Within a run of consecutive days, `order_day` and `day_number` both rise by 1 per row, so `order_day - day_number` stays constant and becomes the island key. Consecutive order days are at least 2 days apart for every customer, so each key covers one day and the answer has 4,362 islands with `days_in_island` = 1.
- **Alternative/trade-off:** The layering from Exercise 4 works too: `LAG(order_day)`, a flag when the gap exceeds 1 day, and a running sum as the island number. It needs two windows instead of one but does not depend on deduplicated input.
- **Edge case:** Without `DISTINCT`, two orders on one day would receive different row numbers, shift the key and split the island. `AT TIME ZONE 'UTC'` fixes which calendar day an order belongs to; casting with the session time zone could move a late-evening order to the next day.

## Exercise 6: Extension

**Prompt:** Summarize sessions from the sessionized event stream with start, end, event count, and duration.

**Reasoning:** Aggregate only after session IDs exist at event grain.

```sql
WITH sequenced AS (
  SELECT
    e.*,
    LAG(e.event_time) OVER (PARTITION BY e.customer_id ORDER BY e.event_time,
      e.event_id) AS previous_event_time
  FROM
    events AS e
),
flagged AS (
  SELECT
    sequenced.*,
    (previous_event_time IS NULL
      OR event_time - previous_event_time > INTERVAL '30 minutes')::integer AS starts_session
  FROM
    sequenced
),
assigned AS (
  SELECT
    flagged.*,
    SUM(starts_session) OVER (PARTITION BY customer_id ORDER BY event_time,
      event_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS session_number
FROM
  flagged
)
SELECT
  customer_id,
  session_number,
  MIN(event_time) AS session_start,
  MAX(event_time) AS session_end,
  COUNT(*) AS event_count,
  MAX(event_time) - MIN(event_time) AS session_duration
FROM
  assigned
GROUP BY
  customer_id,
  session_number
ORDER BY
  customer_id,
  session_number;
```

**Expected shape:** One row per customer session.

### Reasoning and verification

- **Inputs/evidence:** For sql-22 Exercise 6, read `events`, reuse the Exercise 4 sessionizing CTEs (`sequenced`, `flagged`, `assigned`), then group by `customer_id` and `session_number`; keep both keys because they identify a session.
- **Expected result/shape:** For sql-22 Exercise 6, expected output: one row per customer session; on the seed that is 20000 rows, each with `event_count` 1 and `session_duration` `00:00:00`, because no two events of a customer fall within 30 minutes. The final columns are `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`. The final order is `customer_id, session_number`.
- **Independent verification:** For sql-22 Exercise 6, confirm `SUM(event_count)` equals `SELECT COUNT(*) FROM events` (20000) and that (`customer_id`, `session_number`) is unique; then run the CTEs on the three-event fixture from Exercise 4 (10:00, 10:20, 11:00) and expect two sessions: session 1 with 2 events and duration `00:20:00`, and session 2 with 1 event and duration `00:00:00`.
- **Intermediate relation check:** `assigned` has 20,000 event rows with `session_number` from 1 to 40 per customer. That is the event-grain relation the final `GROUP BY` collapses.
- **Clause check:** `GROUP BY customer_id, session_number` produces one row per session; `MIN` and `MAX` of `event_time` give its boundaries, and their difference is the duration. On the fixture there are 20,000 sessions, each with one event and a duration of `00:00:00`.
- **Alternative/trade-off:** If you only need the number of sessions per customer, `SUM(starts_session)` grouped by customer over `flagged` skips the `assigned` layer. Keeping `assigned` is what lets you report start, end and duration per session.
- **Edge case:** With the four test events from Exercise 4 inserted, customer 1 gains session 41 with 3 events lasting `00:50:00` and session 42 with 1 event. A single-event session reports a zero interval, not `NULL`.

## Final self-check

- Which of your windows needed an explicit frame, and what would each return
  with the default frame?
- Can you state what `EXCLUDE CURRENT ROW`, `EXCLUDE GROUP` and `EXCLUDE TIES`
  each leave in a frame that has no `ORDER BY`?
- Why does the fixture produce one event per session, and which test rows
  prove the 30-minute rule works?
- Where did each of your answers change grain, and did the row count match?
