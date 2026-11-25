# Day 22: Advanced Windows: Multiple Partitions, Named Windows, Exclusion (Companion Guide)

## How to run this lesson

In `./classroom`, pick **sql-22** under PostgreSQL and run it with **Whole SQL
lesson (psql)**. Your saved copy lives at
`.learning/sql/sql-22/lesson/workspace/sql/postgres-60day/day22_advanced_windows.sql`
and runs against the disposable `advanced_sql_training` database. Every
statement in it is a `SELECT` over `orders`, `order_items`, `products`,
`employees` or `events`, wrapped in `BEGIN`/`ROLLBACK`, so the `psql`
transcript should show only result tables. Several of them stay at order or
event grain, so expect long outputs and scroll back to the first one before
judging any later result. For launcher and saving details, see
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

Contributors can explore the sessionization steps cell by cell
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-22
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 21; distribution functions](day21_distribution_functions.md)
- **Artifacts:** [learner SQL](../day22_advanced_windows.sql) ·
  [solution reasoning](../solutions/day22_solutions.md) ·
  [executable solution](../solutions/day22_solutions.sql)

## A beginner's mental model for this lesson

One `SELECT` can carry several `OVER` clauses at once, and each one may group
the same rows differently. Example 2 keeps all 4,362 orders and attaches a
per-customer average, a grand total over every order and a per-customer rank to
each row. None of those windows removes a row; they only add columns. This
lesson adds three tools on top of that idea:

- A `WINDOW` clause names a definition once so several functions can share it.
  Exercise 1 reuses `customer_window` four times. The name fixes the
  partition, the ordering and the frame together, which matters because
  `LAST_VALUE` only returns the customer's latest order date when the frame
  runs to `UNBOUNDED FOLLOWING`.
- `EXCLUDE CURRENT ROW` removes the row being computed from its own frame,
  giving "everyone else in my partition". Employee 1 in department 1 earns
  40,079.19; the department average including them is 43,880.31, but the
  average of the other 16 colleagues is 44,117.88.
- A window function cannot take another window function as its argument.
  Sessionization therefore runs in layers: `LAG` in one CTE, a 0/1
  "new session" flag in the next, and a running `SUM` of the flags last.

Predict with the fixture in mind. Each customer's events sit roughly a day
apart (the smallest gap is 18 hours 57 minutes), so with a 30-minute threshold
all 20,000 events start their own session. Likewise, no customer orders on two
consecutive days, so every order-day island is one day long. The queries are
still correct; to see multi-row sessions or islands you add test rows inside a
transaction, as the solution notes show.

## Two worked SQL examples

### Example 1

```sql
WITH prod_rev AS (
  SELECT
    p.product_id,
    p.name,
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    order_items oi
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.product_id,
    p.name,
    p.category
)
SELECT
  *,
  RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category,
  RANK() OVER (ORDER BY revenue DESC) AS rank_overall
FROM
  prod_rev
ORDER BY
  category,
  rank_in_category,
  revenue DESC,
  product_id
LIMIT 100;
```

**How to read it:** `prod_rev` joins `order_items` to `products` and
sums net line revenue per product, so it holds only the 275 products that ever
sold (Books has 45 sold products, every other category 46). The outer query
keeps all four `prod_rev` columns through `*` (`product_id`, `name`,
`category`, `revenue`) and adds two ranks over the same revenue ordering: one
restarted per category, one across the whole catalog. Product 271 is first in
Apparel and first overall, while Product 247 is second in Apparel but tenth
overall.

**Expected result/shape:** 100 product rows sorted by category name,
so the transcript shows all 46 Apparel rows, all 46 Beauty rows and the top 8
Books rows. `rank_in_category` restarts at 1 for each category and reaches 46;
`rank_overall` runs up to 275. The 25 unsold products never appear, because
the query starts from `order_items` rather than from `products`.

### Example 2

```sql
SELECT
  o.customer_id,
  o.order_id,
  o.total_amount,
  AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS avg_per_customer,
  SUM(o.total_amount) OVER () AS total_revenue_all,
  RANK() OVER (PARTITION BY o.customer_id ORDER BY o.total_amount DESC) AS order_value_rank
FROM
  orders o
ORDER BY
  o.customer_id,
  order_value_rank,
  o.total_amount DESC,
  o.order_id
LIMIT 100;
```

**How to read it:** There is no `GROUP BY`, so each of the 4,362 orders
stays a row. `AVG(...) OVER (PARTITION BY o.customer_id)` repeats one
customer's average on every one of that customer's orders. `SUM(...) OVER ()`
has empty parentheses, so its window is the entire table and every row shows
the same 2,355,646.89. `RANK()` orders each customer's orders by amount, so
customer 1's largest order (order 4, 1,155.92) gets rank 1 next to an average
of 504.33.

**Expected result/shape:** 100 order rows, not a summary row. They
cover customers 1 to 7 and 9 to 11 in full and the first two orders of
customer 12; customer 8 has no orders. Within each customer the rank column
counts 1, 2, 3 and so on, and `avg_per_customer` stays constant across that
customer's rows.

## Learning objectives

- Combine local and global windows at a stable grain.
- Reuse named window specifications and exclude current rows or peers when
  required.

## Vocabulary and concepts

- **Named window:** a reusable `WINDOW name AS (...)` specification.
- **Peer exclusion:** removal of the current row, its peers, or ties from a
  frame.
- **Mixed grain:** an unsafe calculation that combines measures defined at
  different row meanings.

## Worked example / walkthrough

Aggregate revenue to `(country, category)` first. Rank categories within each
country from that relation, then calculate a separate category-total relation
for the overall rank. Joining those stable grains avoids incorrectly ranking
every country/category pair as though it were one global category.

## Practice assumptions and review method

- **Focus:** Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.
- **Assumptions:** Event sessions use a 30-minute inactivity threshold and UTC instants. Named windows share partition/order clauses but may still need different frames.
- **Failure to watch for:** Layered window calculations require CTEs because one window result cannot generally be nested directly inside another at the same query level.
- **Review loop:** after each CTE, compare its row count with the base table
  (4,362 orders, 100 employees, 20,000 events) and read one customer's or
  department's rows end to end before trusting the window columns.

## Exercises

Combine named windows, explicit frames, exclusions, and gap/session logic while keeping each intermediate grain inspectable.

Exercises 1 to 3 only add columns, so their answers should have exactly as
many rows as `orders` or `employees`. Exercises 4 to 6 add layers, and the
fixture note in the mental model tells you what session and island counts to
predict before running.

1. **Query writing:** Use a named window to show each order with customer count, average, first date, and last date.
   **Progressive hint:** Name a full-partition customer window once and reuse it.
   **Inputs/evidence:** For sql-22 Exercise 1, read `orders` once and define the named window `customer_window` as `PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id` with an explicit `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` frame; keep `order_id` because every order stays a row.
   **Expected result/shape:** For sql-22 Exercise 1, expected output: 4362 rows, one per `order_id`, where every row of a customer repeats the same count, average, first date, and last date (customer 1 shows 5 orders averaging 504.33). The final columns are `order_id`, `customer_id`, `customer_order_count`, `customer_average`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-22 Exercise 1, compare against `SELECT customer_id, COUNT(*), ROUND(AVG(total_amount), 2), MIN(order_date), MAX(order_date) FROM orders GROUP BY customer_id` (438 rows; counts run from 4 to 16) and require every order row to match its customer; then drop the explicit frame and count rows where `LAST_VALUE(order_date)` differs from the customer's `MAX(order_date)`: 3924 rows (4362 minus the 438 last orders) disagree, because the default frame stops at the current row.
2. **Query writing:** Compare each employee salary with the average of other employees in the department.
   **Progressive hint:** Use `EXCLUDE CURRENT ROW`; a one-person partition yields NULL.
   **Inputs/evidence:** For sql-22 Exercise 2, read the 100 rows of `employees`, partition by `department_id`, and average `salary` over the whole partition with `EXCLUDE CURRENT ROW` so each employee is compared only with colleagues; keep `employee_id` because the result is employee grain.
   **Expected result/shape:** For sql-22 Exercise 2, expected output: 100 rows, one per employee; no department has a single employee, so no average is NULL on the seed. The final columns are `employee_id`, `department_id`, `salary`, and `other_employee_average`. The final order is `e.department_id, e.employee_id`.
   **Verify:** For sql-22 Exercise 2, for department 1 (17 employees, salary total 745965.27) check (total - salary) / 16 by hand: employee 1 at 40079.19 returns 44117.88 and employee 7 at 40554.33 returns 44088.18; then run the window on `VALUES (9, 50000)` as a one-employee department and confirm `other_employee_average` is NULL, because excluding the only row leaves an empty frame.
3. **Query writing:** Show each order's distance from its customer's average and standard deviation.
   **Progressive hint:** Compute independent partition windows and guard interpretation when variation is zero.
   **Inputs/evidence:** For sql-22 Exercise 3, read `orders` with one named window `customer_orders AS (PARTITION BY o.customer_id)` and no `ORDER BY`, so the average and population standard deviation cover all of a customer's orders; `NULLIF(..., 0)` guards the z-score denominator.
   **Expected result/shape:** For sql-22 Exercise 3, expected output: 4362 rows, one per order, with z-scores between -2.3308 and 2.6257 on the seed and none NULL, because every customer has at least 4 orders that are not all equal. The final columns are `order_id`, `customer_id`, `total_amount`, `customer_average`, `customer_stddev`, and `customer_z_score`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-22 Exercise 3, for customer 1 confirm `SELECT ROUND(AVG(total_amount), 2), ROUND(STDDEV_POP(total_amount), 2) FROM orders WHERE customer_id = 1` returns 504.33 and 366.08, and that order 1 at 240.20 has z = -0.7215; then run the z-score expression on the one-row fixture `VALUES (1, 50.00)` and confirm it returns NULL with `NULLIF` and the error `division by zero` without it.
4. **Prediction:** Sessionize events using a 30-minute gap and predict why the first event starts a session.
   **Progressive hint:** Lag event time per customer, flag NULL/large gaps, then cumulative-sum flags in a second layer.
   **Inputs/evidence:** For sql-22 Exercise 4, read `events` (20000 rows, 40 per customer), use `LAG(event_time)` per customer to find the previous event, flag a session start when there is no previous event or the gap is more than 30 minutes, and keep a running `SUM` of the flags; keep `event_id` because each event stays a row.
   **Expected result/shape:** For sql-22 Exercise 4, expected output: 20000 rows, one per event; on the seed the shortest gap between a customer's consecutive events is about 19 hours, so every event starts a new session and `session_number` runs from 1 to 40 for each of the 500 customers. The final columns are `event_id`, `customer_id`, `event_time`, and `session_number`. The final order is `customer_id, event_time, event_id`.
   **Verify:** For sql-22 Exercise 4, confirm exactly 500 rows have no previous event (one per customer) and `MAX(session_number)` is 40; because the seed never shows two events in one session, run the same CTEs on `VALUES (1, 1, TIMESTAMPTZ '2025-01-01 10:00+00'), (2, 1, TIMESTAMPTZ '2025-01-01 10:20+00'), (3, 1, TIMESTAMPTZ '2025-01-01 11:00+00')` and expect session numbers 1, 1, 2; a gap of exactly 30 minutes stays in the same session, since the test is strictly greater than.
5. **Debugging:** Find consecutive calendar-day islands in customer order dates without nesting windows.
   **Progressive hint:** Deduplicate dates, use row number to derive a stable grouping key, then aggregate islands.
   **Inputs/evidence:** For sql-22 Exercise 5, read from `orders`, reduce them to distinct (`customer_id`, UTC order day) pairs, number each customer's days with `ROW_NUMBER()`, and group by `order_day - day_number` to find runs of consecutive days.
   **Expected result/shape:** For sql-22 Exercise 5, expected output: One row per customer/date island. The final columns are `customer_id`, `island_start`, `island_end`, and `days_in_island`. The final order is `customer_id, island_start`.
   **Verify:** For sql-22 Exercise 5, confirm that `SUM(days_in_island)` equals the number of distinct customer order days, `SELECT COUNT(*) FROM (SELECT DISTINCT customer_id, (order_date AT TIME ZONE 'UTC')::date FROM orders) d`; on the seed both are 4362 and every island is one day long, because a customer's orders are always more than two days apart, so also run the same CTEs on `VALUES (1, DATE '2025-01-01'), (1, DATE '2025-01-02'), (1, DATE '2025-01-04')` and expect two islands of 2 and 1 days.
6. **Extension:** Summarize sessions from the sessionized event stream with start, end, event count, and duration.
   **Progressive hint:** Aggregate only after session IDs exist at event grain.
   **Inputs/evidence:** For sql-22 Exercise 6, read `events`, reuse the Exercise 4 sessionizing CTEs (`sequenced`, `flagged`, `assigned`), then group by `customer_id` and `session_number`; keep both keys because they identify a session.
   **Expected result/shape:** For sql-22 Exercise 6, expected output: one row per customer session; on the seed that is 20000 rows, each with `event_count` 1 and `session_duration` `00:00:00`, because no two events of a customer fall within 30 minutes. The final columns are `customer_id`, `session_number`, `session_start`, `session_end`, `event_count`, and `session_duration`. The final order is `customer_id, session_number`.
   **Verify:** For sql-22 Exercise 6, confirm `SUM(event_count)` equals `SELECT COUNT(*) FROM events` (20000) and that (`customer_id`, `session_number`) is unique; then run the CTEs on the three-event fixture from Exercise 4 (10:00, 10:20, 11:00) and expect two sessions: session 1 with 2 events and duration `00:20:00`, and session 2 with 1 event and duration `00:00:00`.

## Common mistakes and how to recover

- **Nesting one window inside another.** `SUM(LAG(total_amount) OVER (...))
  OVER ()` fails with `window function calls cannot be nested`. Compute the
  inner window in a CTE and aggregate its column in the next layer, as
  Exercise 4 does with `sequenced`, `flagged` and the final `SUM`.
- **Trusting `LAST_VALUE` with the default frame.** Remove the `ROWS BETWEEN
  UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` clause from Exercise 1 and
  customer 1's rows show counts of 1, 2, 3, 4, 5 and a `last_order_date` equal
  to each row's own date, because the default frame stops at the current row.
- **Comparing a person with an average that includes them.** Without
  `EXCLUDE CURRENT ROW`, every employee's own salary pulls the comparison
  toward themselves; for employee 1 the gap shrinks from 44,117.88 to
  43,880.31.
- **Concluding the session logic is broken.** Every fixture event is its own
  session because events are about a day apart. Insert a burst of test events
  inside `BEGIN`/`ROLLBACK` before deciding the threshold does nothing.
- **Skipping `DISTINCT` before the islands trick.** Two orders on one day
  would get different row numbers, shift the `order_day - day_number` key and
  split one island in two.
- The general recovery routine (re-count after each stage, rerun the whole
  file after the first `psql` error) is in
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Can you state the grain before every window layer?
- Does an excluded-row calculation handle one-row partitions without dividing
  by zero?

## Next step

Continue to [Day 23; common table expressions](day23_ctes_intro.md).

## Deep dive and reference

Learning objectives
- Reuse window specs with WINDOW clause and combine multiple windows efficiently
- Use EXCLUDE to omit current row/peers from aggregates
- Optimize window queries with pre-aggregation and indexing

Why this matters
Complex analytics often require many windowed metrics at different grains. Clean specs and performance awareness keep queries readable and fast.

Core concepts and deep dive
- WINDOW w AS (PARTITION BY k ORDER BY t): define once, reuse across functions.
- EXCLUDE CURRENT ROW/EXCLUDE TIES to remove the current row or equal-ordered peers from an aggregate (e.g., average of others).
- Mixed grains: daily pre-aggregate then window across days, not raw events.
- Indexing: multi-column btree on (k, t) supports partitioned sorts; work_mem affects window performance.

Patterns
- Leave-one-out mean: (SUM(x) OVER w - x) / NULLIF(COUNT(*) OVER w - 1, 0) with EXCLUDE CURRENT ROW.
- Cross-window features: per-customer cumulative plus global cumulative in one SELECT using named windows w1 (partitioned) and w2 (global).

Pitfalls
- Window after GROUP BY changes row cardinality; ensure you window the intended grain.
- Excessive repeated specs without WINDOW harms readability.

Further reading
- WINDOW clause: https://www.postgresql.org/docs/17/sql-select.html#SQL-WINDOW
- Exclusion: https://www.postgresql.org/docs/17/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask an AI tutor about this lesson

If you use a tutor, ask it to quiz you on frames and exclusions using
customer 1's five orders; the prompt below keeps the solutions out of the
conversation ([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-22: Advanced Windows: Named Windows, Multiple Partitions, and Exclusions.

I have completed the direct catalog prerequisite: `sql-21`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day22_advanced_windows.md
- Answer-free learner SQL: sql/postgres-60day/day22_advanced_windows.sql

Key terms to teach in context: Named window, Peer exclusion, Mixed grain. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate revenue to `(country, category)` first. Rank categories within each country from that relation, then calculate a separate category-total relation for the overall rank. Joining those stable grains avoids incorrectly ranking every country/category pair as though it were one global category.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-22/ working copy. Never point setup, reset, DDL, or DML
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
