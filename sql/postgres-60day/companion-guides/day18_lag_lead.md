# Day 18: LAG/LEAD and Intra-Row Comparisons (Companion Guide)

## How to run this lesson

In the repository root, launch `./classroom`, pick PostgreSQL, choose **sql-18** and then **Whole SQL lesson (psql)**. The file uses `advanced_sql_training`, sets `search_path` to `training` inside a transaction that ends in `ROLLBACK`, and prints two results: the first 100 orders in customer order with the previous and next order amount beside each, and 36 months of revenue set against the same month a year earlier.

Edit your own copy at
`.learning/sql/sql-18/lesson/workspace/sql/postgres-60day/day18_lag_lead.sql`.
A useful first change: delete `PARTITION BY customer_id` from the first query and rerun. Customer 2's first order no longer shows a blank previous amount; it picks up customer 1's last order instead.

If `./classroom` cannot find the lesson or the database, follow the study guide's [classroom run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom). Contributors who prefer notebooks have a [separate route](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 17; ranking functions](day17_rank_functions.md)
- **Artifacts:** [learner SQL](../day18_lag_lead.sql) ·
  [solution reasoning](../solutions/day18_solutions.md) ·
  [executable solution](../solutions/day18_solutions.sql)

## A beginner's mental model for this lesson

`LAG` and `LEAD` let one row read a value from a neighbouring row without a self-join. `LAG(total_amount)` looks one row back, `LEAD(total_amount)` one row forward. "Back" and "forward" mean nothing until the `OVER` clause sets the order, and they stop at the edge of each **partition**: with `PARTITION BY customer_id`, customer 2's first order (order 6) has no previous row, even though customer 1's last order sits right above it in the sorted output.

The number of rows to move is the **offset**. It defaults to 1; Example 2 passes 12 so that each month looks a year back. An offset counts rows, not time. Twelve rows back equals twelve months back only if every month has a row, and here all 46 months from February 2023 to November 2026 do (in our check). With a missing month you would first build a **calendar spine**, one row per month, and join revenue onto it.

When the offset runs past the edge of the partition, the result is `NULL` unless you supply a third argument as a **default value**. That `NULL` is information: it marks a first (or last) row. `LAG(total_amount, 1, 0)` would replace it with zero and make customer 1's first order look like a jump of 240.20 from nothing. Exercise 4 uses the `NULL` deliberately to find first orders.

Both functions run after `WHERE` and `GROUP BY` and before the final `ORDER BY` and `LIMIT`. That order explains two results in this lesson: Exercise 5 must group by month before calling `LAG`, and Example 1's `LIMIT 100` cuts the output without changing which row counts as "next".

## Two worked SQL examples

### Example 1

```sql
WITH cust_orders AS (
  SELECT
    o.customer_id,
    o.order_id,
    o.order_date,
    o.total_amount
  FROM
    orders o
)
SELECT
  customer_id,
  order_id,
  order_date,
  total_amount,
  LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS prev_order_amount,
  total_amount - LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS delta_from_prev,
  LEAD(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS next_order_amount
FROM
  cust_orders
ORDER BY
  customer_id,
  order_date,
  order_id
LIMIT 100;
```

**How to read it:** The CTE `cust_orders` only narrows `orders` to four columns. The outer query asks for three window values over the same window, partitioned by customer and ordered by date with `order_id` as the tie-breaker: the previous amount, the current amount minus the previous one, and the next amount. All window values are computed over all 4,362 orders before `LIMIT 100` keeps the first hundred rows.

**Expected result/shape:** 100 rows covering customers 1 to 12 (customer 8 is Brazilian and has no orders). Customer 1's rows show `prev_order_amount` blank on order 1 and `delta_from_prev` falling to -1,050.08 on order 5, where `next_order_amount` is blank. The last two rows are customer 12's first two orders out of 16; their `next_order_amount` is filled because the cut happens after the window was computed.

### Example 2

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', order_date AT TIME ZONE 'UTC')::date AS month_utc,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    month_utc
),
compared AS (
  SELECT
    month_utc,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY month_utc) AS revenue_prev_year
  FROM
    monthly
)
SELECT
  month_utc,
  revenue,
  revenue_prev_year,
  ROUND((revenue - revenue_prev_year) / NULLIF (revenue_prev_year, 0), 4) AS yoy_growth
FROM
  compared
ORDER BY
  month_utc DESC
LIMIT 36;
```

**How to read it:** The first CTE, `monthly`, turns 4,362 orders into one revenue row per UTC month. The second, `compared`, orders those months and uses `LAG(revenue, 12)` to fetch the value twelve rows back. The final `SELECT` divides the change by last year's revenue, with `NULLIF` guarding against a zero, and shows the newest 36 months.

**Expected result/shape:** 36 rows, newest first. In our check October 2026 shows 170,179.13 against 65,987.62 a year earlier, growth of 1.5790. The top row is the current, unfinished month, so its growth (0.0455 in our check) compares a partial month with a full one. The bottom two rows have no month twelve rows back and show `NULL` growth.

## Learning objectives

- Compare each row with an earlier or later row in the same ordered partition.
- Distinguish an offset in result rows from a duration in calendar time.

## Vocabulary and concepts

- **Offset:** the number of ordered rows traversed by `LAG` or `LEAD`.
- **Default value:** the value returned when the requested offset does not
  exist.
- **Calendar spine:** an explicit row for every required date or period.

## Worked example / walkthrough

Customer 1 placed orders 1 to 5 about eight days apart for 240.20, 417.94, 601.73, 1,155.92 and 105.84. Ordered by `order_date, order_id`, `LAG(total_amount)` gives a blank, then 240.20, 417.94, 601.73 and 1,155.92; subtracting gives deltas of 177.74, 183.79, 554.19 and -1,050.08. `LEAD` runs the other way and is blank on order 5. At month grain the same idea needs one extra step: sum revenue per month first, then lag the monthly rows.

## Practice assumptions and review method

- **Focus:** Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
- **Assumptions:** Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
- **Failure to watch for:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
- **Review loop:** pick one customer, write out their orders in date order on paper, fill in the previous and next values by hand, then compare with the query for that `customer_id` only.

## Exercises

Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.

For every exercise, write the `OVER (...)` clause first and say out loud which rows will get `NULL`: the first row of each partition for `LAG`, the last for `LEAD`.

1. **Query writing:** Show each order with the previous order timestamp for that customer.
   **Hunch:** 4,362 rows come back. How many of them show a blank previous date, and why that number?
   **Progressive hint:** Partition by customer and order by timestamp plus ID.
   **Inputs/evidence:** For sql-18 Exercise 1, attach `LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id)` to each of the 4,362 `orders` rows; every buyer has at least 4 orders.
   **Expected result/shape:** For sql-18 Exercise 1, return 4,362 rows, one per order, with `previous_order_date` `NULL` on exactly 438 rows, one per buyer's first order; customer 1's orders 1 to 5 show `NULL` and then the dates of orders 1, 2, 3, and 4. The final columns are `order_id`, `customer_id`, `order_date`, and `previous_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-18 Exercise 1, confirm 4,362 distinct `order_id` values, 438 `NULL` previous dates, and that every non-null `previous_order_date` is earlier than its row's `order_date`. Inside a rolled-back transaction, add one order for customer 8, who has none; that new one-row partition must show `NULL`, and customer 1's first row must stay order 1 with `NULL`.
2. **Query writing:** Calculate days since each customer's previous order.
   **Hunch:** customer 1 orders about every eight days. Will the gap print as exactly 8?
   **Progressive hint:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
   **Inputs/evidence:** For sql-18 Exercise 2, compute `previous_order_date` with `LAG` in the `sequenced` CTE, then convert the gap to days with `EXTRACT(EPOCH FROM (order_date - previous_order_date)) / 86400.0`.
   **Expected result/shape:** For sql-18 Exercise 2, return 4,362 rows, one per order, with 438 `NULL` gaps; customer 1's four gaps are each 7.9005282256944444 days, and the 3,924 non-null gaps run from 2.2882 to 296.6473 days and average 65.4524. The final columns are `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`. The final order is `customer_id, order_date, order_id`.
   **Verify:** For sql-18 Exercise 2, confirm 3,924 non-null `days_since_previous` values and none at zero or below, since no customer has two orders at the same instant. Inside a rolled-back transaction, add an order for customer 1 with order 5's exact `order_date`; it sorts after order 5 by `order_id` and must show a gap of exactly 0.
3. **Query writing:** Show each promotion with the next promotion start date for the same product.
   **Hunch:** count the promotions per product before writing the window. What will `next_promotion_start` hold?
   **Progressive hint:** Partition by product and define a stable chronological order.
   **Inputs/evidence:** For sql-18 Exercise 3, attach `LEAD(pr.start_date) OVER (PARTITION BY pr.product_id ORDER BY pr.start_date, pr.promotion_id)` to each of the 200 `promotions` rows, which cover 200 different products.
   **Expected result/shape:** For sql-18 Exercise 3, return 200 rows, one per promotion, and every `next_promotion_start` is `NULL`, because no product has a second promotion; the first row is promotion 7 for product 1. The final columns are `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`. The final order is `pr.product_id, pr.start_date, pr.promotion_id`.
   **Verify:** For sql-18 Exercise 3, confirm that `SELECT product_id FROM promotions GROUP BY product_id HAVING COUNT(*) > 1` returns no rows, which explains the 200 `NULL` values. Inside a rolled-back transaction, copy promotion 7 for product 1 with both dates moved 30 days later; promotion 7 must then show the copy's `start_date` as its next start, while the copy shows `NULL`, leaving 201 rows with 200 `NULL` values.
4. **Prediction:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
   **Hunch:** will this return 500 rows, 438 rows or some other number?
   **Progressive hint:** NULL means there is no prior observation; preserve that semantic state.
   **Inputs/evidence:** For sql-18 Exercise 4, attach `LAG(o.order_id)` per customer, ordered by `o.order_date, o.order_id`, in the `sequenced` CTE, then keep the rows where `previous_order_id IS NULL`.
   **Expected result/shape:** For sql-18 Exercise 4, return 438 rows, one first order per buyer, with no rows for the 62 customers who never ordered; customer 1 returns order 1 and customer 500 returns order 4353. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `customer_id`.
   **Verify:** For sql-18 Exercise 4, confirm 438 distinct `customer_id` values and that all 438 rows match `SELECT customer_id, MIN(order_date) FROM orders GROUP BY customer_id`; their `total_amount` values add up to 236703.47. `order_id`, `customer_id`, and `order_date` are all `NOT NULL`, so test with inserts instead: inside a rolled-back transaction, add an order for customer 1 dated one day before order 1 and an order for customer 8; the result must grow to 439 rows, and customer 1 must return the new order instead of order 1.
5. **Debugging:** Compute month-over-month stored-revenue change after aggregating to month grain.
   **Hunch:** how many months does the data cover, and which month alone has no change?
   **Progressive hint:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
   **Inputs/evidence:** For sql-18 Exercise 5, read from `orders`, aggregate `SUM(total_amount)` to one row per UTC month in the CTE `monthly`, then apply `LAG(revenue) OVER (ORDER BY month_start)` to those monthly rows and compute `revenue_change = revenue - previous_revenue`.
   **Expected result/shape:** For sql-18 Exercise 5, return 46 rows, one per UTC month with orders; on a fixture loaded on 2026-11-25 the first row is `2023-02-01` with revenue 1203.26 and `NULL` comparisons, and the last is the partial month `2026-11-01` with 85364.67, a change of -84814.46 from 170179.13. The final columns are `month_start`, `revenue`, `previous_revenue`, and `revenue_change`. The final order is `month_start`.
   **Verify:** For sql-18 Exercise 5, confirm that `month_start` is unique and that the row count equals `SELECT COUNT(DISTINCT date_trunc('month', order_date AT TIME ZONE 'UTC')) FROM orders`; exactly one row, the earliest month, has NULL `previous_revenue` and `revenue_change`, and the `revenue` values add up to 2355646.89, the total of `orders.total_amount`.
6. **Extension:** Compare each product price with the next higher price in its category.
   **Hunch:** list Apparel's three cheapest prices. What gap do you expect between neighbours?
   **Progressive hint:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
   **Inputs/evidence:** For sql-18 Exercise 6, attach `LEAD(p.price) OVER (PARTITION BY p.category ORDER BY p.price, p.product_id)` to each of the 300 `products` rows across 6 categories.
   **Expected result/shape:** For sql-18 Exercise 6, return 300 rows, one per product, with `next_price` `NULL` only on the 6 most expensive products, one per category; `Apparel` starts with product 1 at 10.37 followed by 12.59, and `Sports` ends with product 299 at 120.63. The final columns are `product_id`, `category`, `price`, and `next_price`. The final order is `p.category, p.price, p.product_id`.
   **Verify:** For sql-18 Exercise 6, confirm 294 non-null `next_price` values and that `next_price - price` is exactly 2.22 on all of them, because each category's prices rise in even steps. Inside a rolled-back transaction, set product 7's price to 10.37; product 1 must then show a `next_price` of 10.37 (the tie is broken by `p.product_id`) and product 7 must show 14.81.

## Common mistakes and how to recover

- **No partition:** without `PARTITION BY customer_id`, the previous row is whichever order came just before in the whole table, so a customer's first order borrows another customer's amount or date and is no longer blank.
- **Ordering by date alone:** when two orders of one customer share a timestamp, their order is undefined and `LAG` can flip between runs. This fixture has no such ties, but the lessons add `order_id` anyway so the result can never change.
- **Lagging raw rows when you meant months:** `LAG(total_amount) OVER (ORDER BY order_date)` on `orders` compares each order with the one before it, 4,362 comparisons, not month with month. Group first, as Exercise 5 does.
- **Reading an offset as time:** `LAG(revenue, 12)` is "twelve rows back". If a month were missing, it would reach thirteen months back without any warning.
- **Filling the first row with a default:** `COALESCE` or a third `LAG` argument turns "no previous order" into a fake value, which then shows up as a big jump or a strange gap.
- **Filtering inside the window input:** a `WHERE` on dates runs before `LAG`, so the earliest order inside the filter starts to look like a customer's first order.

When `psql` aborts with an `ERROR`, the study guide's [recovery checklist](../../STUDY-GUIDE.md#recover-from-common-failures) explains how to get back to a clean run.

## Self-check

- Is each window ordered uniquely enough to define “previous” or “next”?
- Are missing first/last offsets and zero denominators handled explicitly?

## Next step

Continue to [Day 19; running aggregates](day19_running_aggregates.md).

## Deep dive and reference

Learning objectives
- Use LAG/LEAD to access prior/next row values within partitions
- Compute deltas, growth rates, and interval gaps
- Handle nulls and defaults with the third LAG/LEAD argument

Why this matters
Many metrics are changes over time: day-over-day growth, time since last purchase, step detection. LAG/LEAD express these cleanly and efficiently.

Core concepts and deep dive
- LAG(expr, offset, default) OVER (PARTITION BY k ORDER BY t): returns value offset rows before current; default substitutes for missing (e.g., first row).
- LEAD symmetric; often used for next timestamp to compute session gaps.
- Differences: expr - LAG(expr) for numeric deltas; AGE(ts, LAG(ts)) for time deltas.

Patterns
- DoD/YoY growth: (x - LAG(x)) / NULLIF(LAG(x),0).
- Sessionization: gap = ts - LAG(ts); new session if gap > interval '30 min'.
- Churn signal: last_order_date per customer and days_since_last.

Pitfalls
- Sorting by a non-unique timestamp yields unpredictable row pairing; add tiebreakers.
- Large partitions without indexes increase sort cost; index on (k, t) helps.

Further reading
- LAG/LEAD: https://www.postgresql.org/docs/17/functions-window.html#FUNCTIONS-WINDOW

## Ask an AI tutor about this lesson

A tutor is optional here. A good exercise is to paste customer 1's five orders and ask it for `LAG` and `LEAD` values under different `PARTITION BY` and `ORDER BY` choices, writing your own answers before reading its. The study guide's [advice on using a tutor](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) covers how to keep it from simply writing the queries.

```text
Tutor me through sql-18: LAG and LEAD: Comparing Neighboring Rows.

I have completed the direct catalog prerequisite: `sql-17`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day18_lag_lead.md
- Answer-free learner SQL: sql/postgres-60day/day18_lag_lead.sql

Key terms to teach in context: Offset, Default value, Calendar spine. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At monthly grain, place `revenue` beside `LAG(revenue) OVER (ORDER BY month)`. The first row has no predecessor and returns `NULL`. If a month is absent, the previous row is not necessarily the previous calendar month, so build a month spine before interpreting the difference as month-over-month.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-18/ working copy. Never point setup, reset, DDL, or DML
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
