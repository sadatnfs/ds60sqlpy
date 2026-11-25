# Day 26: CTEs with Window Functions: Layered Analytics (Companion Guide)

## How to run this lesson

In `./classroom`, choose **sql-26** from the PostgreSQL list and run
**Whole SQL lesson (psql)**. That executes
`.learning/sql/sql-26/lesson/workspace/sql/postgres-60day/day26_ctes_with_windows.sql`
against `advanced_sql_training` inside `BEGIN`/`ROLLBACK`; nothing is written.
The first statement prints 1,314 ranked order rows, so scroll back to its
header before reading the plan that follows. The general run steps are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

A notebook lets you query `line` and `ranked` one at a time
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-26
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 25; multiple CTEs and hierarchies](day25_multiple_ctes_hierarchies.md)
- **Artifacts:** [learner SQL](../day26_ctes_with_windows.sql) ·
  [solution reasoning](../solutions/day26_solutions.md) ·
  [executable solution](../solutions/day26_solutions.sql)

## A beginner's mental model for this lesson

Window functions run after `WHERE`, `GROUP BY` and `HAVING`. That order
causes two problems a CTE solves neatly:

1. **You often want to rank or lag a total, not a detail row.** A first CTE
   aggregates to the grain you care about, such as one row per order or one
   row per month, and a second step applies the window to those totals.
2. **You cannot filter on a window result at the same level.** Writing
   `WHERE RANK() OVER (...) <= 3` fails with
   `window functions are not allowed in WHERE`. Computing the rank in a CTE
   and filtering it in the outer query is the standard fix.

Example 1 follows both rules. `line` sums `order_items` to one total per
order (4,362 rows); `ranked` numbers each customer's orders from largest to
smallest; the outer `WHERE rnk <= 3` keeps the top three. The 438 customers
who ordered all have at least four orders and no tied totals, so the result
is exactly 1,314 rows, three per customer.

The exercises move the same pattern to months. Order dates are spread from
each customer's signup up to the moment the fixture was loaded, so the
months you see depend on when your database was built, and the newest month
is only partly filled. What does not change is the money: however you group
by month, the monthly totals must add back to the 2,355,646.89 stored in
`orders.total_amount`.

## Two worked SQL examples

### Example 1

```sql
WITH line AS (
  SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    o.order_date
),
ranked AS (
  SELECT
    line.*,
    RANK() OVER (PARTITION BY customer_id ORDER BY order_total DESC) AS rnk
  FROM
    line
)
SELECT
  customer_id,
  order_id,
  order_date,
  order_total,
  rnk
FROM
  ranked
WHERE
  rnk <= 3
ORDER BY
  customer_id,
  rnk,
  order_total DESC,
  order_id;
```

**How to read it:** `line` joins orders to items and groups by order,
so `order_total` is the unrounded item formula with four decimal places.
`ranked` adds `RANK()` partitioned by customer and ordered by that total
descending. Only the outer query can see `rnk` as an ordinary column, which
is why the filter sits there.

**Expected result/shape:** 1,314 rows ordered by customer and rank.
Customer 1 comes first with orders 4, 3 and 2 at 1155.9185, 601.7295 and
417.9405; customer 2 follows with orders 8, 7 and 9. Every customer has
exactly ranks 1, 2 and 3. The 62 customers without orders do not appear.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH line AS (
  SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    o.order_date),
  ranked AS (
    SELECT
      line.*,
      RANK() OVER (PARTITION BY customer_id ORDER BY order_total DESC) AS rnk
    FROM
      line
)
  SELECT
    customer_id,
    order_id,
    order_date,
    order_total,
    rnk
  FROM
    ranked
  WHERE
    rnk <= 3
  ORDER BY
    customer_id,
    rnk,
    order_total DESC,
    order_id;
```

**How to read it:** Both CTEs vanish into the main plan as
`Subquery Scan on line` and `Subquery Scan on ranked`, since each is used
once. Look at the `WindowAgg` node: its `Run Condition: (rank() OVER (?) <= 3)`
means PostgreSQL stops ranking a customer's orders once the rank passes 3.
`HashAggregate` groups by `o.order_id` alone, because the other grouping
columns depend on the primary key.

**Expected result/shape:** A 16-line plan topped by
`Incremental Sort` with `Presorted Key: ranked.customer_id`. Beneath it are
the `WindowAgg`, a `Sort` on `line.customer_id, line.order_total DESC` and a
`Hash Join` of `order_items` to `orders`. There is no `CTE Scan` node.

## Learning objectives

- Pre-aggregate to the correct grain before calculating ranks, shares, or
  changes.
- Filter a window result through an outer query in PostgreSQL.

## Vocabulary and concepts

- **Layered analytics:** successive relational stages with progressively richer
  measures.
- **Window input grain:** the meaning of one row before `OVER (...)` is applied.
- **QUALIFY alternative:** an outer `SELECT` that filters a computed window
  column.

## Worked example / walkthrough

Create monthly totals in one CTE, add `LAG(total)` in the next, and calculate
growth in the outer query with a guarded denominator. Keeping the ratio outside
the `LAG` layer makes the prior value visible and lets you inspect both values
before interpreting the percentage.

## Practice assumptions and review method

- **Focus:** Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
- **Assumptions:** Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
- **Failure to watch for:** Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
- **Review loop:** after each monthly CTE, count the months and sum the
  revenue; the sum must equal 2,355,646.89 from `orders` (or 2,355,647.12
  when built from `order_items`) before you add any window.

## Exercises

Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.

For each answer, write the grain of the first CTE (one row per
month, or per month and category) and the window that comes after it. Count
the months in your copy of the data first; the category answers should
return six rows for every month.

1. **Query writing:** Calculate monthly stored revenue and its prior-month value/change.
   **Progressive hint:** Aggregate to month in a CTE, then lag the monthly measure.
   **Inputs/evidence:** For sql-26 Exercise 1, read from `orders`, aggregate `SUM(total_amount)` to one row per UTC month in the CTE `monthly`, then use `LAG(revenue) OVER (ORDER BY month_start)` in `compared` and return `change = revenue - previous_revenue`.
   **Expected result/shape:** For sql-26 Exercise 1, expected output: one row per UTC month with orders, 46 rows from 2023-02-01 to 2026-11-01 on a November 2026 load (seed dates move with the load date); the first row is 1203.26 with NULL `previous_revenue` and `change`, and the second is 1803.43 with a change of 600.17. The final columns are `month_start`, `revenue`, `previous_revenue`, and `change`. The final order is `month_start`.
   **Verify:** For sql-26 Exercise 1, confirm that `month_start` is unique and that the row count equals `SELECT COUNT(DISTINCT date_trunc('month', order_date AT TIME ZONE 'UTC')) FROM orders`; exactly one row, the earliest month, has NULL `previous_revenue` and `change`, and the `revenue` values add up to 2355646.89.
2. **Query writing:** Rank product categories by net revenue within each UTC order month.
   **Progressive hint:** Aggregate month/category first, then rank the stable aggregate.
   **Inputs/evidence:** For sql-26 Exercise 2, read `orders` joined to `order_items` and `products`, sum net item revenue `unit_price * quantity * (1 - discount)` per UTC month and `category` in `category_month`, then apply `DENSE_RANK()` partitioned by `month_start` and ordered by `revenue DESC`.
   **Expected result/shape:** For sql-26 Exercise 2, expected output: 6 rows per month, one per category, ranked 1 through 6 (276 rows for 46 months on this load); the first month, 2023-02-01, runs from Apparel at 407.05 down to Home at 30.20. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
   **Verify:** For sql-26 Exercise 2, confirm `COUNT(*)` is 6 times `COUNT(DISTINCT month_start)`, every month has ranks 1 through 6 exactly once, and the 2023-02-01 revenues add to 1203.26, the stored total for that month in Exercise 1; then rank the fixture `VALUES ('A', 10), ('B', 10), ('C', 5), ('D', 3)` and confirm `DENSE_RANK` gives 1, 1, 2, 3 where `RANK` gives 1, 1, 3, 4.
3. **Query writing:** Return the top three category revenue levels per month.
   **Progressive hint:** Rank in one CTE and filter the window result outside.
   **Inputs/evidence:** For sql-26 Exercise 3, read `orders`, `order_items`, and `products` into the same `category_month` CTE as Exercise 2, rank it in a second CTE `ranked`, and filter `revenue_rank <= 3` only in the outer query, after the window has run.
   **Expected result/shape:** For sql-26 Exercise 3, expected output: 3 rows per month (138 rows for 46 months on this load, because no month has a revenue tie); 2023-02-01 keeps Apparel, Books, and Electronics, and 2026-11-01 keeps Sports, Books, and Apparel. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
   **Verify:** For sql-26 Exercise 3, confirm `COUNT(*)` is 3 times `COUNT(DISTINCT month_start)` and each month shows ranks 1, 2, and 3 once; then apply the same rank and filter to `VALUES ('A', 10), ('B', 10), ('C', 5), ('D', 3), ('E', 1)` and confirm four rows survive (ranks 1, 1, 2, 3), showing that ties in `DENSE_RANK` can return more than three categories in a month.
4. **Prediction:** Calculate each category's cumulative share of monthly revenue in descending contribution order.
   **Progressive hint:** Divide running category revenue by the full monthly total; use explicit frames.
   **Inputs/evidence:** For sql-26 Exercise 4, read `orders`, `order_items`, and `products` into `category_month`, then divide a running `SUM(revenue)` ordered by `revenue DESC, category` with a `ROWS` frame by the month total `SUM(revenue) OVER (PARTITION BY month_start)`, guarded by `NULLIF`.
   **Expected result/shape:** For sql-26 Exercise 4, expected output: 276 rows on this load, 6 per month; in 2023-02-01 the shares climb 0.3383, 0.5708, 0.7510, 0.8968, 0.9749, and 1.0000. The final columns are `month_start`, `category`, `revenue`, and `cumulative_revenue_share`. The final order is `month_start, revenue DESC, category`.
   **Verify:** For sql-26 Exercise 4, confirm the last row of every month is exactly 1.0000 (46 such rows, one per month, and no month whose maximum differs) and that the first 2023-02-01 share equals 407.05 / 1203.26; then run both frames over `VALUES ('A', 10.0), ('B', 10.0), ('C', 5.0)` and confirm `ROWS` gives 0.4000, 0.8000, 1.0000 while the default `RANGE` frame gives 0.8000 to both tied rows.
5. **Debugging:** Calculate a three-month moving average after building a dense month calendar.
   **Progressive hint:** Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
   **Inputs/evidence:** For sql-26 Exercise 5, read `orders` three ways: `bounds` takes the first and last UTC month, `calendar` fills every month between them with `generate_series`, and `monthly` sums `total_amount`; `dense` `LEFT JOIN`s the calendar to `monthly` and turns a missing month into 0.
   **Expected result/shape:** For sql-26 Exercise 5, expected output: one row per calendar month with no gaps, 46 rows on this load; the moving average starts 1203.26, 1503.35, 2197.18 because the first two rows average only one and two months. The final columns are `month_start`, `revenue`, and `moving_3_month_average`. The final order is `month_start`.
   **Verify:** For sql-26 Exercise 5, confirm the row count equals the months between `MIN` and `MAX` month inclusive and that the third row averages 1203.26, 1803.43, and 3584.85; then, inside `BEGIN ... ROLLBACK`, move every 2023-04 order back one month and confirm `monthly` drops to 45 rows while the output keeps 46, with 2023-04-01 at 0.00 and its moving average 2197.18 still covering three calendar months.
6. **Extension:** Reconcile the final cumulative monthly revenue with the independent order total.
   **Progressive hint:** Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
   **Inputs/evidence:** For sql-26 Exercise 6, read from `orders`; aggregate to UTC months in `monthly`, accumulate the monthly revenue with `SUM(revenue) OVER (ORDER BY month_start)` in `running`, keep the last month's cumulative value in `final`, and compare it with an independent `SUM(total_amount)`.
   **Expected result/shape:** For sql-26 Exercise 6, expected output: exactly one row, `final_cumulative` 2355646.89, `independent_total` 2355646.89, and `difference` 0.00. The final columns are `final_cumulative`, `independent_total`, and `difference`.
   **Verify:** For sql-26 Exercise 6, confirm one row where `final_cumulative` and `independent_total` are both 2355646.89 and `difference` is 0.00; the `monthly` revenues must already add up to that total before the window is applied.

## Common mistakes and how to recover

- **Filtering a window in the same `SELECT`.** `WHERE RANK() OVER (...) <= 3`
  raises `window functions are not allowed in WHERE`. Rank in a CTE, then
  filter the outer query, as Exercise 3 does.
- **Filtering months before the lag.** If a `WHERE` keeps only the last six
  months inside the CTE, the earliest of them gets a `NULL` previous value
  even though the data exists. Compute `LAG` over all months, then filter.
- **Mixing the two revenue sources.** Monthly totals from
  `orders.total_amount` add to 2,355,646.89, while totals from the item
  formula add to 2,355,647.12 because each order was rounded when stored.
  Pick one source per report and reconcile against the same one.
- **Relying on the default frame for running totals.** With an `ORDER BY`
  and no frame, `SUM() OVER` uses `RANGE`, which treats tied values as one
  peer group. Exercise 4 adds `category` to the order and states
  `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` so ties cannot merge.
- **Reading the newest month as a trend.** The latest month stops when the
  fixture was loaded, so its change from the previous month is usually a
  large drop that says nothing about sales.
- General recovery steps are in
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does every window operate over the intended pre-aggregated relation?
- Is window filtering performed in an outer query rather than an invalid
  same-level `WHERE`?

## Next step

Continue to [Day 27; pivoting and unpivoting](day27_pivot_unpivot.md).

## Deep dive and reference

Learning objectives
- Combine CTE staging with window calculations for clarity and speed
- Decide which grain to aggregate at before applying windows
- Build multi-stage pipelines for advanced KPIs (shares, ranks, rolling metrics)

Why this matters
Complex analytics often need a staging step (pre-aggregations) before windowing. Getting the grain right avoids wrong answers and large sorts, and it yields maintainable queries.

Core concepts and deep dive
- Pre-aggregate, then window: compute daily/category totals in a CTE, then run windows over that smaller set.
- Windows across aggregates: once at daily grain, you can apply running totals, moving averages, and shares cheaply.
- Multiple windows: define named window specs to compute per-partition and global metrics in the same SELECT.

Patterns
- WITH daily AS (... GROUP BY day, key) SELECT day, key, SUM(x) OVER (PARTITION BY key ORDER BY day) ... FROM daily.
- Shares of total: x / NULLIF(SUM(x) OVER (PARTITION BY key),0) and x / NULLIF(SUM(x) OVER(),0).

Pitfalls
- Windowing raw rows creates noisy and heavy computations; pre-aggregate first.
- Filtering on windowed values in the same SELECT; wrap in another SELECT to filter.

Further reading
- CTEs: https://www.postgresql.org/docs/17/queries-with.html
- Windows: https://www.postgresql.org/docs/17/tutorial-window.html

## Ask an AI tutor about this lesson

A tutor can check whether each window in your answer sees totals or
detail rows. Give it the prompt below so it stays on this lesson's files
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-26: CTEs with Window Functions.

I have completed the direct catalog prerequisite: `sql-25`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day26_ctes_with_windows.md
- Answer-free learner SQL: sql/postgres-60day/day26_ctes_with_windows.sql

Key terms to teach in context: Layered analytics, Window input grain, QUALIFY alternative. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Create monthly totals in one CTE, add `LAG(total)` in the next, and calculate growth in the outer query with a guarded denominator. Keeping the ratio outside the `LAG` layer makes the prior value visible and lets you inspect both values before interpreting the percentage.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-26/ working copy. Never point setup, reset, DDL, or DML
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
