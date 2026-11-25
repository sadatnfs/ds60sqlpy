# Day 19 solutions: Running Aggregates and Moving Windows

<!-- beginner-solution-enrichment -->
## How to study and run this solution

These six answers are all window sums or averages, and each comes with a number you can check by hand or against a plain aggregate. Attempt them first, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day19_solutions.sql
```

The file runs read-only queries inside `BEGIN`/`ROLLBACK` and prints, in order, 4,362 order rows, 4,362 order rows again, 4,362 rows of averages, a three-row demonstration, 10,000 expense rows and a single check row. The first five are long; pipe the output through `less` or add a `LIMIT` to your own copy while studying. Prompts match [the learner file](../day19_running_aggregates.sql), and the study guide's [solution reading notes](../../STUDY-GUIDE.md#read-a-solution) explain how to compare your version.

## Reading contract

- **Focus:** Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
- **Assumptions:** Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
- **Primary pitfall:** Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
- **Safety:** read-only window queries wrapped in `BEGIN`/`ROLLBACK`; Exercise 4 builds its rows with `VALUES` and touches no table.

## Exercise 1: Query writing

**Prompt:** Calculate cumulative stored revenue across all orders.

**Reasoning:** Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.

**Clause-by-clause reading:**

- `FROM orders AS o`: all 4,362 orders, no partition, so one running total across the whole table.
- `SUM(o.total_amount) OVER (ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`: every order up to and including this one.
- `ORDER BY o.order_date, o.order_id`: prints rows in the same order the total accumulates.

```sql
SELECT
  o.order_id,
  o.order_date,
  o.total_amount,
  SUM(o.total_amount) OVER (ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
FROM
  orders AS o
ORDER BY
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order with nondecreasing cumulative revenue.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 1, attach `SUM(o.total_amount) OVER (ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` to each of the 4,362 `orders` rows, with no partition, so the total runs across the whole table.
- **Expected result/shape:** For sql-19 Exercise 1, return 4,362 rows, one per order; the first is order 2230 at 216.84, the second, order 3739, brings the total to 1203.26, and the last, order 2258, ends at 2355646.89. The final columns are `order_id`, `order_date`, `total_amount`, and `cumulative_revenue`. The final order is `o.order_date, o.order_id`.
- **Independent verification:** For sql-19 Exercise 1, confirm that the last `cumulative_revenue` equals `SELECT SUM(total_amount) FROM orders` (2355646.89) and that the values strictly increase, because the smallest `total_amount` is 20.74. Inside a rolled-back transaction, add a 100.00 order at order 2230's exact `order_date`; it sorts after order 2230 by `order_id` and must show 316.84, and order 3739 must move to 1303.26.
- **What prints:** 4,362 rows. The first is order 2230 (2023-02-13, 216.84); after order 3739 the total is 1,203.26, which is February 2023's revenue. The last row shows 2,355,646.89.
- **Never decreasing:** every `total_amount` is positive, so each value is at least as large as the one above. A dip would mean the output order and the window order disagree.
- **Tie-breaker:** no two orders share an `order_date`, so `order_id` never decides here. It still belongs in the window, because one duplicate timestamp in a later load would make the order of those rows arbitrary.
- **Spot check:** compare the row for any order with `SELECT SUM(total_amount) FROM orders WHERE (order_date, order_id) <= (that date, that id)`.

## Exercise 2: Query writing

**Prompt:** Calculate each customer's cumulative stored spend.

**Reasoning:** Partition by customer and reset the explicit row frame for every customer.

**Clause-by-clause reading:**

- `PARTITION BY o.customer_id`: the total restarts at zero for each of the 438 customers with orders.
- `ORDER BY o.order_date, o.order_id` inside the window: oldest order first within each customer.
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: from the customer's first order to this one.
- Outer `ORDER BY o.customer_id, o.order_date, o.order_id`: customers in turn, each in time order.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  o.total_amount,
  SUM(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS customer_cumulative_spend
FROM
  orders AS o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 2, attach `SUM(o.total_amount)` partitioned by `o.customer_id` with the frame `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` to each of the 4,362 `orders` rows.
- **Expected result/shape:** For sql-19 Exercise 2, return 4,362 rows, one per order; customer 1 runs 240.20, 658.14, 1259.87 and ends at 2521.63, then the total resets so customer 2's first order 6 shows 460.35 and its last order 11 shows 3616.32. The final columns are `order_id`, `customer_id`, `order_date`, `total_amount`, and `customer_cumulative_spend`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-19 Exercise 2, confirm that each of the 438 customers' last value equals `SUM(total_amount)` from `orders` grouped by `customer_id`, and that those 438 values add up to 2355646.89. Inside a rolled-back transaction, add one 100.00 order for customer 8, who has none; that one-row partition must show 100.00.
- **What prints:** 4,362 rows. Customer 1's five rows run 240.20, 658.14, 1,259.87, 2,415.79 and 2,521.63, and customer 2's first row starts again at its own first order.
- **Reset check:** the first row of every customer should equal that order's `total_amount`. Counting the rows where it does not should give 0.
- **Count to compare:** the last value per customer should equal `SUM(total_amount)` grouped by `customer_id`. Customer 12, one of those with 16 orders, ends at 9,244.27.
- **Missing customers:** the 62 Brazilian customers have no orders, so no rows appear for them. A `LEFT JOIN` from `customers` would be needed to list them with no spend.

## Exercise 3: Query writing

**Prompt:** Calculate a trailing seven-order average within each customer.

**Reasoning:** A seven-row frame is based on observations, not seven calendar days.

**Clause-by-clause reading:**

- `AVG(o.total_amount) OVER (... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`: the current order and up to six before it, within one customer.
- `PARTITION BY o.customer_id`: the window never reaches into another customer's orders.
- `ROUND(..., 2)`: two decimals for display only.

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS trailing_7_order_average
FROM
  orders AS o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id;
```

**Expected shape:** One row per order with up to seven observations in its frame.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 3, attach `ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2)` to each of the 4,362 `orders` rows.
- **Expected result/shape:** For sql-19 Exercise 3, return 4,362 rows, one per order; customer 1 starts at 240.20, 329.07, and 419.96, and 1,836 rows average a full seven-order frame while the earlier rows of each customer average fewer orders. The final columns are `order_id`, `customer_id`, `order_date`, and `trailing_7_order_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
- **Independent verification:** For sql-19 Exercise 3, count the frame rows with `COUNT(*)` over the same window: 438 rows each have frames of 1, 2, 3, and 4 rows, 404 have 5, 370 have 6, and 1,836 have 7. Hand-check customer 7's eighth order, order 53: its 420.91 must equal the average of orders 47 to 53 (2946.37 / 7), with order 46 out of the frame.
- **What prints:** 4,362 rows. Customer 1's averages are 240.20, 329.07, 419.96, 603.95 and 504.33; the fifth row averages all five orders because there are no more.
- **Short frames:** only the seventh and later orders of a customer average a full seven. That is 1,836 rows from the 336 customers with at least seven orders; the other 2,526 rows average fewer.
- **Finding the frame size:** add `COUNT(*) OVER` with the same window to show how many orders each average used. Without it, a two-order average looks just as trustworthy as a seven-order one.
- **Orders, not days:** a customer's seven orders can span months. The frame counts orders regardless of the gaps between them.

## Exercise 4: Prediction

**Prompt:** Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.

**Reasoning:** `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.

**Clause-by-clause reading:**

- `VALUES (1, 1, 10), (2, 1, 20), (3, 2, 5)`: three rows; the first two tie on `sort_value`.
- `rows_sum`: `ROWS` frame ordered by `sort_value, row_id`, so one physical row at a time.
- `range_sum`: `RANGE` frame ordered by `sort_value` only, so tied rows enter together.

```sql
SELECT
  row_id,
  sort_value,
  amount,
  SUM(amount) OVER (ORDER BY sort_value, row_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rows_sum,
  SUM(amount) OVER (ORDER BY sort_value RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS range_sum
FROM (
  VALUES (1, 1, 10),
    (2, 1, 20),
    (3, 2, 5)) AS sample (row_id, sort_value, amount)
ORDER BY
  row_id;
```

**Expected shape:** Three rows making the peer difference visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 4, use the three-row `VALUES` fixture `(1, 1, 10), (2, 1, 20), (3, 2, 5)` as (`row_id`, `sort_value`, `amount`), and compare a `ROWS` running sum ordered by `sort_value, row_id` with a `RANGE` running sum ordered by `sort_value` alone.
- **Expected result/shape:** For sql-19 Exercise 4, return three rows, one per `row_id`, where `rows_sum` reads 10, 30, 35 and `range_sum` reads 30, 30, 35, because rows 1 and 2 are peers at `sort_value` 1. The final columns are `row_id`, `sort_value`, `amount`, `rows_sum`, and `range_sum`. The final order is `row_id`.
- **Independent verification:** For sql-19 Exercise 4, hand-calculate all three peer rows from the inline fixture: `rows_sum` must be `(10, 30, 35)` while `range_sum` must be `(30, 30, 35)` in `row_id` order. Require three unique `row_id` values and explain why the two rows tied at `sort_value = 1` advance separately under `ROWS` but together under `RANGE`.
- **What prints:** `rows_sum` is 10, 30, 35 and `range_sum` is 30, 30, 35. Row 1's `RANGE` total already includes row 2's 20 because both have `sort_value` 1.
- **Where they agree:** row 3 has no peer, so both frames reach 35 there.
- **The default frame:** `SUM(amount) OVER (ORDER BY sort_value)` with no frame clause returns the `range_sum` column, because `RANGE` is the default.
- **Real data:** on `expenses`, 13 or 14 rows share each category and date, so this difference would appear on almost every row of Exercise 5.

## Exercise 5: Debugging

**Prompt:** Reset a running expense total at each category and month.

**Reasoning:** Partition by both reset keys and order by date plus expense ID.

**Clause-by-clause reading:**

- `PARTITION BY e.category, date_trunc('month', e.expense_date)`: a new total for each category in each month, 125 partitions in all.
- `ORDER BY e.expense_date, e.expense_id`: date first, then ID to separate same-day expenses.
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: one row at a time, so same-day expenses do not share a value.

```sql
SELECT
  e.expense_id,
  e.category,
  e.expense_date,
  e.amount,
  SUM(e.amount) OVER (PARTITION BY e.category, date_trunc('month', e.expense_date) ORDER BY e.expense_date,
    e.expense_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS category_month_running_expense
FROM
  expenses AS e
ORDER BY
  e.category,
  e.expense_date,
  e.expense_id;
```

**Expected shape:** One row per expense.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 5, attach a running `SUM(e.amount)` partitioned by `e.category, date_trunc('month', e.expense_date)` and ordered by `e.expense_date, e.expense_id` to each of the 10,000 `expenses` rows, which form 125 category-month partitions of 13 to 96 rows.
- **Expected result/shape:** For sql-19 Exercise 5, return 10,000 rows, one per expense; on a fixture loaded on 2026-11-25, `COGS` starts with expense 461 at 7700.69 on 2024-11-26, its 14-row November 2024 partition ends at 72384.36, and the total resets on 2024-12-01 so expense 576 shows its own 9339.04. The final columns are `expense_id`, `category`, `expense_date`, `amount`, and `category_month_running_expense`. The final order is `e.category, e.expense_date, e.expense_id`.
- **Independent verification:** For sql-19 Exercise 5, confirm that the last row of each of the 125 partitions matches `SELECT category, date_trunc('month', expense_date), SUM(amount) FROM expenses GROUP BY 1, 2` and that those values add up to 50483850.00, and that every partition's first row equals its own `amount`. Inside a rolled-back transaction, add a 500.00 `COGS` expense dated 2027-01-15; it forms a one-row partition and must show 500.00.
- **What prints:** 10,000 rows, five categories of 2,000 expenses each. COGS opens with 14 expenses on 2024-11-26 that end at 72,384.36; the next row, expense 576 on 2024-12-01, restarts at 9,339.04.
- **Seeing the bug:** partition by `category` only and expense 576 shows 81,723.40, November's total plus its own amount.
- **Second bug:** drop `expense_id` and the `ROWS` clause, and all 14 rows on 2024-11-26 show 72,384.36 at once.
- **Count to compare:** the last row of each category and month should equal `SUM(amount)` grouped by category and month. December 2024 COGS ends at 473,494.55.
- **Short first month:** there are 125 partitions, 5 categories times 25 months. The data starts on 2024-11-26, so COGS November 2024 holds only 14 expenses while December 2024 holds 95. A partition that small is a quick one to add up by hand.

## Exercise 6: Extension

**Prompt:** Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.

**Reasoning:** Select the last ordered cumulative value and compare it with an independent aggregate.

**Clause-by-clause reading:**

- `running`: the Exercise 1 cumulative column for every order.
- `final_running`: the last order in time order, `LIMIT 1`, which holds the total of everything.
- `CROSS JOIN orders` with `GROUP BY fr.cumulative_revenue`: pairs that one value with an independent `SUM` over all orders.
- `difference`: the two totals subtracted.

```sql
WITH running AS (
  SELECT
    o.order_id,
    o.order_date,
    SUM(o.total_amount) OVER (ORDER BY o.order_date,
      o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
  FROM
    orders AS o
),
final_running AS (
  SELECT
    r.cumulative_revenue
  FROM
    running AS r
  ORDER BY
    r.order_date DESC,
    r.order_id DESC
  LIMIT 1
)
SELECT
  ROUND(fr.cumulative_revenue, 2) AS final_cumulative,
  ROUND(SUM(o.total_amount), 2) AS aggregate_total,
  ROUND(fr.cumulative_revenue - SUM(o.total_amount), 2) AS difference
FROM
  final_running AS fr
  CROSS JOIN orders AS o
GROUP BY
  fr.cumulative_revenue;
```

**Expected shape:** One row with zero difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-19 Exercise 6, read from `orders`; compute `SUM(total_amount) OVER (ORDER BY order_date, order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` in the CTE `running`, keep the cumulative value of the last order, and compare it with an ordinary `SUM(total_amount)`.
- **Expected result/shape:** For sql-19 Exercise 6, return one row: `final_cumulative` 2355646.89, `aggregate_total` 2355646.89, and `difference` 0.00. The final columns are `final_cumulative`, `aggregate_total`, and `difference`.
- **Independent verification:** For sql-19 Exercise 6, confirm one row where `final_cumulative` and `aggregate_total` are both 2355646.89 and `difference` is 0.00; `running` must keep all 4362 orders, and its last row by `order_date DESC, order_id DESC` must carry the full total.
- **What prints:** one row: 2,355,646.89, 2,355,646.89 and a difference of 0.00.
- **What zero proves:** the window saw every order exactly once. A frame that skipped rows, or a partition that reset by mistake, would leave a gap.
- **Picking the last row:** `ORDER BY r.order_date DESC, r.order_id DESC LIMIT 1` must use the same keys as the window. Picking the row with the largest `order_id` instead would return a value from the middle of the series.
- **Exact arithmetic:** `total_amount` is `numeric`, so no rounding error can creep in and the difference is exactly zero, not merely small.

## Final self-check

- Why does Example 1 never show customers 8 and 16?
- How many orders feed customer 1's moving average on their third order?
- In Exercise 4, why does `range_sum` read 30 on row 1?
- Which value would expense 576 show if the partition ignored the month?
- What would a nonzero `difference` in Exercise 6 tell you?
