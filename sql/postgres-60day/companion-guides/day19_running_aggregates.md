# Day 19: Running Aggregates and Moving Windows (Companion Guide)

## How to run this lesson

In `./classroom`, select PostgreSQL, then **sql-19**, then **Whole SQL lesson (psql)**. Inside `BEGIN`/`ROLLBACK` on `advanced_sql_training`, `psql` prints two read-only results: the first 200 orders in customer order with a per-customer running total, then the 40 most recent UTC order dates with daily revenue and a seven-row moving average.

The editable copy is
`.learning/sql/sql-19/lesson/workspace/sql/postgres-60day/day19_running_aggregates.sql`.
Two experiments are worth running there. Delete the `ROWS BETWEEN ...` clause from Example 1 and nothing changes, because no two orders share a timestamp; the solution's Exercise 4 and 5 notes show data where it would matter. Delete it from Example 2 and `ma7` turns into the average of every day so far, so the newest row moves from 2,079.31 to 2,179.14, the mean over all 1,081 dates with orders, and the next rows barely differ from it.

Classroom setup, resets and the other buttons are explained in the study guide's [classroom section](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom); the [contributor notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is optional.

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 18; LAG and LEAD](day18_lag_lead.md)
- **Artifacts:** [learner SQL](../day19_running_aggregates.sql) ·
  [solution reasoning](../solutions/day19_solutions.md) ·
  [executable solution](../solutions/day19_solutions.sql)

## A beginner's mental model for this lesson

A running total is an ordinary `SUM` evaluated once per row over a slice of rows called the frame. `SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` reads as: within this customer's orders, sorted by time, add up everything from the first order through this one. That is a **cumulative aggregate**. The row count never changes; each order simply gains one more column.

Three parts control the answer. `PARTITION BY` decides where the total starts again from zero (each customer, or each category and month). `ORDER BY` decides which rows count as earlier. The frame clause decides how far back to look: `UNBOUNDED PRECEDING` means the start of the partition, while `6 PRECEDING` gives a **moving window** of at most seven rows. Each of those rows is one **observation** at whatever grain you fed in: an order in Exercise 3, a calendar date with orders in Example 2.

The frame has a hidden default. With an `ORDER BY` and no frame clause, PostgreSQL uses `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, which treats rows with the same sort value as one block. On `orders` that never shows, because no two orders share a timestamp. On `expenses`, 13 or 14 rows share each category and date, so the default would give all of them the same total. Writing `ROWS` and a unique tie-breaker makes the result predictable either way.

## Two worked SQL examples

### Example 1

```sql
SELECT
  o.customer_id,
  o.order_id,
  o.order_date,
  o.total_amount,
  SUM(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM
  orders o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id
LIMIT 200;
```

**How to read it:** The window restarts at each `customer_id`, sorts that customer's orders by `order_date` with `order_id` as the tie-breaker, and sums from the first order through the current one. The outer `ORDER BY` uses the same keys, so each customer's rows print in the order the total was built, and `LIMIT 200` stops partway through the table.

**Expected result/shape:** 200 rows across customers 1 to 23. Customer 1 has five orders and climbs 240.20, 658.14, 1,259.87, 2,415.79, 2,521.63. Customers 8 and 16 never appear: they are in Brazil and the fixture gives Brazilian customers no orders. The limit cuts customer 23 after 8 of their 14 orders, so the last running value printed is not that customer's full spend.

### Example 2

```sql
WITH daily AS (
  SELECT
    (order_date AT TIME ZONE 'UTC')::date AS d_utc,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    d_utc
)
SELECT
  d_utc,
  revenue,
  ROUND(AVG(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS ma7
FROM
  daily
ORDER BY
  d_utc DESC
LIMIT 40;
```

**How to read it:** `daily` collapses orders to one row per UTC date with its revenue. `AVG(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` then averages each date with up to six earlier dates that had orders, and `ROUND(..., 2)` trims it. The final `ORDER BY d_utc DESC LIMIT 40` shows the newest dates, but the average was computed in ascending order before that.

**Expected result/shape:** 40 rows, 2026-11-23 back to 2026-10-15 in our check (these dates move with the day the tables were loaded). The newest row shows revenue 742.14 and `ma7` 2,079.31. All 40 dates had orders, so here seven rows are seven calendar days. `ma7` peaks at 6,096.50 on 2026-10-19 and then sinks, because the last three days each brought in under 1,200.

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
- **Review loop:** for the first partition shown, add the first three amounts by hand and compare with the running column; then check that the last value of each partition matches a plain `SUM` grouped by that partition key.

## Exercises

Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.

For each exercise, decide the partition, the sort order and the frame before writing any SQL, and write down the value you expect in the first two rows of the first partition.

1. **Query writing:** Calculate cumulative stored revenue across all orders.
   **Call it:** what will the last row's `cumulative_revenue` be, given the stored total of all orders?
   **Progressive hint:** Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.
   **Inputs/evidence:** For sql-19 Exercise 1, attach `SUM(o.total_amount) OVER (ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` to each of the 4,362 `orders` rows, with no partition, so the total runs across the whole table.
   **Expected result/shape:** For sql-19 Exercise 1, return 4,362 rows, one per order; the first is order 2230 at 216.84, the second, order 3739, brings the total to 1203.26, and the last, order 2258, ends at 2355646.89. The final columns are `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`. The final order is `o.order_date, o.order_id`.
   **Verify:** For sql-19 Exercise 1, confirm that the last `cumulative_revenue` equals `SELECT SUM(total_amount) FROM orders` (2355646.89) and that the values strictly increase, because the smallest `total_amount` is 20.74. Inside a rolled-back transaction, add a 100.00 order at order 2230's exact `order_date`; it sorts after order 2230 by `order_id` and must show 316.84, and order 3739 must move to 1303.26.
2. **Query writing:** Calculate each customer's cumulative stored spend.
   **Call it:** for customer 1, what is the running value on their first order, and on their last?
   **Progressive hint:** Partition by customer and reset the explicit row frame for every customer.
   **Inputs/evidence:** For sql-19 Exercise 2, attach `SUM(o.total_amount)` partitioned by `o.customer_id` with the frame `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` to each of the 4,362 `orders` rows.
   **Expected result/shape:** For sql-19 Exercise 2, return 4,362 rows, one per order; customer 1 runs 240.20, 658.14, 1259.87 and ends at 2521.63, then the total resets so customer 2's first order 6 shows 460.35 and its last order 11 shows 3616.32. The final columns are `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-19 Exercise 2, confirm that each of the 438 customers' last value equals `SUM(total_amount)` from `orders` grouped by `customer_id`, and that those 438 values add up to 2355646.89. Inside a rolled-back transaction, add one 100.00 order for customer 8, who has none; that one-row partition must show 100.00.
3. **Query writing:** Calculate a trailing seven-order average within each customer.
   **Call it:** customer 1 has only five orders. How many orders feed the average on their fifth row?
   **Progressive hint:** A seven-row frame is based on observations, not seven calendar days.
   **Inputs/evidence:** For sql-19 Exercise 3, attach `ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2)` to each of the 4,362 `orders` rows.
   **Expected result/shape:** For sql-19 Exercise 3, return 4,362 rows, one per order; customer 1 starts at 240.20, 329.07, and 419.96, and 1,836 rows average a full seven-order frame while the earlier rows of each customer average fewer orders. The final columns are `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-19 Exercise 3, count the frame rows with `COUNT(*)` over the same window: 438 rows each have frames of 1, 2, 3, and 4 rows, 404 have 5, 370 have 6, and 1,836 have 7. Hand-check customer 7's eighth order, order 53: its 420.91 must equal the average of orders 47 to 53 (2946.37 / 7), with order 46 out of the frame.
4. **Prediction:** Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
   **Call it:** rows 1 and 2 share `sort_value` 1. What will `range_sum` show on row 1?
   **Progressive hint:** `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
   **Inputs/evidence:** For sql-19 Exercise 4, use the three-row `VALUES` fixture `(1, 1, 10), (2, 1, 20), (3, 2, 5)` as (`row_id`, `sort_value`, `amount`), and compare a `ROWS` running sum ordered by `sort_value, row_id` with a `RANGE` running sum ordered by `sort_value` alone.
   **Expected result/shape:** For sql-19 Exercise 4, return three rows, one per `row_id`, where `rows_sum` reads 10, 30, 35 and `range_sum` reads 30, 30, 35, because rows 1 and 2 are peers at `sort_value` 1. The final columns are `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`. The final order is `row_id`.
   **Verify:** For sql-19 Exercise 4, hand-calculate all three peer rows from the inline fixture: `rows_sum` must be `(10, 30, 35)` while `range_sum` must be `(30, 30, 35)` in `row_id` order. Require three unique `row_id` values and explain why the two rows tied at `sort_value = 1` advance separately under `ROWS` but together under `RANGE`.
5. **Debugging:** Reset a running expense total at each category and month.
   **Call it:** on the first expense of a new month, should the running value equal that expense's amount, or something larger?
   **Progressive hint:** Partition by both reset keys and order by date plus expense ID.
   **Inputs/evidence:** For sql-19 Exercise 5, attach a running `SUM(e.amount)` partitioned by `e.category, date_trunc('month', e.expense_date)` and ordered by `e.expense_date, e.expense_id` to each of the 10,000 `expenses` rows, which form 125 category-month partitions of 13 to 96 rows.
   **Expected result/shape:** For sql-19 Exercise 5, return 10,000 rows, one per expense; on a fixture loaded on 2026-11-25, `COGS` starts with expense 461 at 7700.69 on 2024-11-26, its 14-row November 2024 partition ends at 72384.36, and the total resets on 2024-12-01 so expense 576 shows its own 9339.04. The final columns are `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`. The final order is `e.category, e.expense_date, e.expense_id`.
   **Verify:** For sql-19 Exercise 5, confirm that the last row of each of the 125 partitions matches `SELECT category, date_trunc('month', expense_date), SUM(amount) FROM expenses GROUP BY 1, 2` and that those values add up to 50483850.00, and that every partition's first row equals its own `amount`. Inside a rolled-back transaction, add a 500.00 `COGS` expense dated 2027-01-15; it forms a one-row partition and must show 500.00.
6. **Extension:** Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
   **Call it:** what exact `difference` proves the window is right, and what would a nonzero value suggest?
   **Progressive hint:** Select the last ordered cumulative value and compare it with an independent aggregate.
   **Inputs/evidence:** For sql-19 Exercise 6, read from `orders`; compute `SUM(total_amount) OVER (ORDER BY order_date, order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` in the CTE `running`, keep the cumulative value of the last order, and compare it with an ordinary `SUM(total_amount)`.
   **Expected result/shape:** For sql-19 Exercise 6, return one row: `final_cumulative` 2355646.89, `aggregate_total` 2355646.89, and `difference` 0.00. The final columns are `final_cumulative`, `aggregate_total`, and `difference`.
   **Verify:** For sql-19 Exercise 6, confirm one row where `final_cumulative` and `aggregate_total` are both 2355646.89 and `difference` is 0.00; `running` must keep all 4362 orders, and its last row by `order_date DESC, order_id DESC` must carry the full total.

## Common mistakes and how to recover

- **Leaving the frame to the default:** with `ORDER BY expense_date` and no frame, all 14 COGS expenses on 2024-11-26 show the same total, 72,384.36. Add `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` and a unique tie-breaker such as `expense_id`.
- **Missing a reset key:** partitioning `expenses` by `category` alone keeps adding across months. On 2024-12-01 the first COGS expense then shows 81,723.40 instead of its own 9,339.04.
- **Calling seven rows a week:** Exercise 3 averages a customer's last seven orders, which might be spread over months. If the question is about calendar time, build a date spine or use a `RANGE` frame with an interval.
- **Sorting the output differently from the window:** if the outer `ORDER BY` does not match the window's order, the running column looks random even though every value is correct.
- **Filtering before the window:** adding `WHERE d_utc >= '2026-10-15'` to Example 2's outer query removes the earlier days before the window runs, so the 2026-10-15 row averages only itself (6,840.58 instead of 5,322.48). Filter in an outer query wrapped around the window, or cut rows with `LIMIT` as the example does.

If `psql` stops on an error, the study guide's [failure recovery notes](../../STUDY-GUIDE.md#recover-from-common-failures) show how to reset and rerun.

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

Further reading
- Window frames: https://www.postgresql.org/docs/17/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask an AI tutor about this lesson

A tutor is optional for this lesson. If you use one, ask it to write out a five-row table with two tied sort values and have you fill in `ROWS` and `RANGE` running totals by hand before it shows the answers. The prompt below keeps the solutions closed; setup is in the study guide's [tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-19: Running Totals and Moving Windows.

I have completed the direct catalog prerequisite: `sql-18`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day19_running_aggregates.md
- Answer-free learner SQL: sql/postgres-60day/day19_running_aggregates.sql

Key terms to teach in context: Cumulative aggregate, Moving window, Observation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate orders to daily revenue, then apply `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`. This includes at most seven observed order dates, not automatically seven calendar days. Compare it with a date-spined input that includes zero-revenue days.

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
