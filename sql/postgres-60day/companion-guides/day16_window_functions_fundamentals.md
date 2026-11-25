# Day 16: Window Functions Fundamentals: OVER, PARTITION BY, ORDER BY, Frames (Companion Guide)

## How to run this lesson

From the repository root, start `./classroom`, pick PostgreSQL and **sql-16**, and choose **Whole SQL lesson (psql)**. The script connects to `advanced_sql_training`, opens a transaction, points `search_path` at `training`, and prints three window results before it rolls back: six category rows that each carry the grand total, the first 100 orders with their customer's average and order count, and the 30 most recent UTC order dates with a seven-row rolling sum.

Your editable copy is
`.learning/sql/sql-16/lesson/workspace/sql/postgres-60day/day16_window_functions_fundamentals.sql`.
A quick experiment: in the second query, change `OVER (PARTITION BY o.customer_id)` to `OVER ()`. Every row's `avg_customer_order` becomes 540.04, the average of all 4,362 orders, and `orders_per_customer` becomes 4362.

If the classroom does not open or reports a database error, the study guide's [classroom start-up guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) lists the usual fixes. Contributors can also use the [notebook path, meant for contributors](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Intermediate
- **Direct prerequisite:** [SQL-FOUND-01; Relational design, DDL, and integrity
  constraints](../../professional/companion-guides/sql_found_01_relational_design.md).
  That module follows [Day 15; Phase 1 project](day15_phase1_project.md), so
  you should already be comfortable with grouped aggregates and declared
  result grain.
- **Artifacts:** [learner SQL](../day16_window_functions_fundamentals.sql) ·
  [solution reasoning](../solutions/day16_solutions.md) ·
  [executable solution](../solutions/day16_solutions.sql)

## A beginner's mental model for this lesson

An ordinary aggregate such as `AVG(total_amount)` with `GROUP BY customer_id` folds each customer's orders into one row, so 4,362 orders become 438 rows. A window function computes the same average but writes it onto every order instead. The `OVER (...)` clause is what turns `AVG`, `SUM`, `COUNT`, `MIN` or `MAX` into a window function.

The **window** is the set of rows a window function can see when it computes the value for one row. `OVER ()` with nothing inside makes the window the whole result, which is how Example 1 puts the 2,355,647.12 grand total on each of its six category rows. A **partition** splits the rows into independent groups: `OVER (PARTITION BY customer_id)` lets customer 1's five orders see only each other, so all five show 504.33 while customer 2's six orders show 602.72. A **frame** narrows the window further, to rows near the current one in some order. The learner file's third query uses `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` to add each day's revenue to that of the six dates before it.

Windows are computed after `WHERE`, `GROUP BY` and `HAVING`, and before the final `ORDER BY` and `LIMIT`. Two things follow. A `WHERE` clause cannot test a window value, which is the bug in Exercise 5. And `LIMIT` cannot shrink a window: in Example 2, customer 12's two visible rows still report 16 orders, because the count was taken before the cut at row 100.

## Two worked SQL examples

### Example 1

```sql
WITH category_totals AS (
  SELECT
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    order_items oi
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category
)
SELECT
  category,
  ROUND(revenue, 2) AS category_revenue,
  ROUND(SUM(revenue) OVER (), 2) AS total_revenue,
  ROUND(revenue / NULLIF (SUM(revenue) OVER (), 0), 4) AS category_share
FROM
  category_totals
ORDER BY
  category_revenue DESC,
  category;
```

**How to read it:** The CTE `category_totals` is an ordinary grouped query: it joins 13,085 order lines to `products` and adds net revenue (unit price times quantity, less the discount) into one row per category. The outer query then works on those six rows. `SUM(revenue) OVER ()` has an empty window specification, so each row sees all six and receives the same grand total, and dividing a row's revenue by that total gives its share. `NULLIF(..., 0)` only matters if every category sold nothing.

**Expected result/shape:** Six rows, Sports first at 397,427.70 (share 0.1687) and Books last at 386,192.77 (0.1639). `total_revenue` reads 2,355,647.12 on every row. That is 0.23 more than the sum of `orders.total_amount`, because the order totals were rounded per order while this sums exact line values. The six rounded shares add to 0.9999, a reminder that rounding each share does not keep the sum at exactly 1.

### Example 2

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  o.total_amount,
  ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2) AS avg_customer_order,
  COUNT(*) OVER (PARTITION BY o.customer_id) AS orders_per_customer
FROM
  orders o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id
LIMIT 100;
```

**How to read it:** Two window functions share the partition `PARTITION BY o.customer_id`. `AVG(o.total_amount)` gives each order its customer's lifetime average, and `COUNT(*)` gives the customer's number of orders, both without collapsing any rows. The query has no `GROUP BY`, so each output row is still one order. `ORDER BY o.customer_id, o.order_date, o.order_id` lists each customer's orders in date order, and `LIMIT 100` shows only the first 100.

**Expected result/shape:** 100 rows covering 11 customers, 1 to 12 without customer 8, who lives in BR and has no orders. Customer 1's five rows all show 504.33 and 5; customer 2's six rows show 602.72 and 6. The last two rows belong to customer 12 and show `orders_per_customer` 16 even though only two of those orders are on screen, because the window counted the whole partition before `LIMIT` cut the list.

## Learning objectives

- Add partition-level and running metrics without collapsing detail rows.
- Choose an explicit `ROWS` frame when peer-aware `RANGE` behavior is not
  intended.

## Vocabulary and concepts

- **Window:** the related rows visible to a window function for one result row.
- **Partition:** an independent window group created by `PARTITION BY`.
- **Frame:** the ordered subset of a partition used for the current row.

## Worked example / walkthrough

Take customer 1, whose five orders total 240.20, 417.94, 601.73, 1,155.92 and 105.84. With `GROUP BY customer_id` you get one row: 2,521.63 in revenue and an average of 504.33. With `SUM(total_amount) OVER (PARTITION BY customer_id)` you keep all five rows and each carries 2,521.63, so `total_amount / SUM(...) OVER (...)` gives each order's share: 0.0953, 0.1657, 0.2386, 0.4584 and 0.0420, adding to 1.0000. Add `ORDER BY order_date` inside the `OVER` and the average turns into a running average instead (240.20, 329.07, 419.96, 603.95, 504.33), because the default frame then stops at the current row.

## Practice assumptions and review method

- **Focus:** Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
- **Assumptions:** Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
- **Failure to watch for:** Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
- **Review loop:** after each run, take one partition you can hold in your head (customer 1's five orders, department 1's 17 salaries) and recompute its window values by hand before trusting the other rows.

## Exercises

Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.

Before writing each answer, name the partition column and say how many rows the result should have. Every exercise except Exercise 4 keeps one row per order or per employee, so the expected count is 4,362 or 100 before any filter.

1. **Query writing:** Show each order with the customer's average order total.
   **Sketch the answer:** what value should all five of customer 1's rows show?
   **Progressive hint:** Partition by customer ID and keep one output row per order.
   **Inputs/evidence:** For sql-16 Exercise 1, attach `ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2)` to each of the 4,362 `orders` rows; the 438 buyers have between 4 and 16 orders each.
   **Expected result/shape:** For sql-16 Exercise 1, return 4,362 rows, one per order, grouped by customer; customer 1's five orders (1 to 5) all show `customer_average` 504.33, and customer 500's ten orders show 613.75. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-16 Exercise 1, confirm 4,362 distinct `order_id` values and that customer 1's value equals 2521.63 / 5 = 504.33 from `SELECT SUM(total_amount), COUNT(*) FROM orders WHERE customer_id = 1`. Inside a rolled-back transaction, add one order of 100.00 for customer 8, who has none; that new one-row partition must show `customer_average` 100.00 while customer 1's rows stay at 504.33.
2. **Query writing:** Show each employee salary with department average, minimum, and maximum.
   **Sketch the answer:** for employee 1, which of the three department values will equal the employee's own salary?
   **Progressive hint:** Partition all three window aggregates by department.
   **Inputs/evidence:** For sql-16 Exercise 2, attach the department's `AVG`, `MIN`, and `MAX` salary to each of the 100 `employees` rows with three `OVER (PARTITION BY e.department_id)` windows.
   **Expected result/shape:** For sql-16 Exercise 2, return 100 rows, one per employee; department 1's 17 rows all carry average 43880.31, minimum 40079.19, and maximum 47681.43, and departments 5 and 6 have 16 rows each. The final columns are `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`. The final order is `e.department_id, e.employee_id`.
   **Verify:** For sql-16 Exercise 2, confirm 100 rows and that each department's three values match `SELECT department_id, ROUND(AVG(salary), 2), MIN(salary), MAX(salary) FROM employees GROUP BY department_id`. Inside a rolled-back transaction, set employee 1's salary to 50000; department 1 must change to 44463.89, 40554.33, and 50000.00 on all 17 rows, while department 2 stays at 43959.50, 40158.38, and 47760.62.
3. **Query writing:** Calculate every order's share of its customer's stored revenue.
   **Sketch the answer:** will every customer's rounded shares add up to exactly 1.0000?
   **Progressive hint:** Use a partition total denominator and guard it with `NULLIF`.
   **Inputs/evidence:** For sql-16 Exercise 3, divide each order's `total_amount` by `SUM(o.total_amount) OVER (PARTITION BY o.customer_id)`, guarded with `NULLIF(..., 0)`, and round the share to 4 places.
   **Expected result/shape:** For sql-16 Exercise 3, return 4,362 rows, one per order; customer 1's five shares are 0.0953, 0.1657, 0.2386, 0.4584, and 0.0420, which add to exactly 1.0000. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-16 Exercise 3, sum the shares per customer: all 438 totals must be within 0.0003 of 1, and 231 of them miss 1 exactly only because of rounding to 4 places. Inside a rolled-back transaction, add one order for customer 8, who has none; that one-row partition must show a share of 1.0000.
4. **Prediction:** Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.
   **Sketch the answer:** write both row counts down before running; 62 customers have no orders at all.
   **Progressive hint:** Grouping collapses to one row per customer; a window preserves every order row.
   **Inputs/evidence:** For sql-16 Exercise 4, compare a `grouped` CTE (`AVG(o.total_amount) ... GROUP BY o.customer_id`) with a `windowed` CTE (`AVG(o.total_amount) OVER (PARTITION BY o.customer_id)`) over `orders`, then count the rows of each.
   **Expected result/shape:** For sql-16 Exercise 4, expected output: two rows ordered by `method`, with columns `method` and `row_count`: `('grouped', 438)` and `('windowed', 4362)` on the course seed.
   **Verify:** For sql-16 Exercise 4, confirm that the `grouped` count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` and the `windowed` count equals `SELECT COUNT(*) FROM orders`; grouping keeps one row per ordering customer, while the window keeps every order row.
5. **Debugging:** Return orders above their customer average without placing a window function in `WHERE`.
   **Sketch the answer:** which error does PostgreSQL raise if the `AVG(...) OVER (...)` goes straight into `WHERE`?
   **Progressive hint:** Compute the window value in a CTE, then filter the named column outside.
   **Inputs/evidence:** For sql-16 Exercise 5, compute `AVG(o.total_amount) OVER (PARTITION BY o.customer_id)` as `customer_average` in a `scored` CTE over `orders`, then filter `total_amount > customer_average` in the outer query.
   **Expected result/shape:** For sql-16 Exercise 5, expected output: one row per `order_id` whose `total_amount` is strictly above its customer's mean (2,249 rows on the course seed), with columns `order_id`, `customer_id`, `total_amount`, and `customer_average` (rounded to 2 places), ordered by `customer_id, total_amount DESC, order_id`.
   **Verify:** For sql-16 Exercise 5, compare the row count with `SELECT COUNT(*) FROM orders o WHERE o.total_amount > (SELECT AVG(i.total_amount) FROM orders i WHERE i.customer_id = o.customer_id)` (2,249), require unique `order_id`, and confirm that moving the window expression into `WHERE` fails with `window functions are not allowed in WHERE`.
6. **Extension:** Show order count and revenue context at both customer and country levels in the same row.
   **Sketch the answer:** how many distinct `country_revenue` values will appear, given that BR customers placed no orders?
   **Progressive hint:** Use different partitions for independent analytical contexts.
   **Inputs/evidence:** For sql-16 Exercise 6, join `orders` to `customers` and attach three windows to each order: `COUNT(*)` and `SUM(total_amount)` partitioned by `o.customer_id`, and `SUM(total_amount)` partitioned by `c.country`.
   **Expected result/shape:** For sql-16 Exercise 6, return 4,362 rows, one per order, across 7 countries (`BR` has no orders); the first rows are customer 7's 11 orders in `AU`, each with `customer_revenue` 5274.48 and `country_revenue` 330947.62. The final columns are `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`. The final order is `c.country, o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-16 Exercise 6, confirm that the 7 distinct `country_revenue` values match `SELECT c.country, SUM(o.total_amount) FROM orders o JOIN customers c USING (customer_id) GROUP BY c.country` (from 329081.73 for `IN` to 343290.09 for `FR`) and add up to 2355646.89. Inside a rolled-back transaction, add one 100.00 order for customer 8; a `BR` row must appear with a count of 1 and both revenues at 100.00.

## Common mistakes and how to recover

- **Putting a window in `WHERE`:** `WHERE total_amount > AVG(total_amount) OVER (PARTITION BY customer_id)` fails with `window functions are not allowed in WHERE`, because `WHERE` runs before windows exist. Compute the window in a CTE or subquery and filter its alias outside, as Exercise 5 does.
- **Forgetting `PARTITION BY`:** `AVG(total_amount) OVER ()` is not an error. It quietly puts 540.04, the average over all orders, on every row, so customer 1's rows look plausible but are wrong.
- **Adding `ORDER BY` inside `OVER` by accident:** `AVG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date)` becomes a running average. Customer 1's first order shows 240.20, not 504.33, and only the last row reaches the full average.
- **Expecting `LIMIT` to shrink the window:** in Example 2 customer 12 shows 16 orders on two rows. If you want windows over the visible rows only, limit in a subquery first.
- **Reading seven rows as seven days:** the third query's `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` counts dates that had orders. In our check there were 1,081 such dates across a span of 1,380 days, and on 406 rows a seven-calendar-day `RANGE` frame gives a different total.

When a run stops at the first `ERROR`, the study guide's [troubleshooting notes](../../STUDY-GUIDE.md#recover-from-common-failures) explain how to reset and run the whole file again.

## Self-check

- Does the result retain the intended number of detail rows?
- Can you state the partition, ordering, and frame for every window expression?

## Next step

Continue to [Day 17; ranking functions](day17_rank_functions.md).

## Deep dive and reference

Learning objectives
- Understand what a window is and how window functions differ from aggregates
- Use OVER() with PARTITION BY and ORDER BY to compute per-row metrics without collapsing rows
- Control frames with ROWS/RANGE; grasp default frames and their impact
- Combine multiple window functions in the same SELECT

Why this matters
Window functions unlock powerful analytics: running totals, per-customer averages alongside each row, shares of totals, and rank-based features, all without subqueries that collapse results.

Core concepts and deep dive
- Window vs aggregate
  - Aggregates (SUM, AVG, COUNT) collapse groups into a single row.
  - Window functions compute values across a set of rows related to the current row, but keep one row per input row.
- OVER() clause
  - PARTITION BY defines independent windows (e.g., per customer or per category).
  - ORDER BY defines an order within each partition enabling running/lagged calculations.
  - You can define named windows via WINDOW w AS (PARTITION BY ... ORDER BY ...).
- Default frame
  - If you specify ORDER BY without an explicit frame, the default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.
  - RANGE groups peers with equal ORDER BY values; SUM(RANGE ...) may include more rows than expected when there are ties.
  - Prefer ROWS BETWEEN ... for precise row-count frames: ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW for cumulative sums, or ROWS BETWEEN 6 PRECEDING AND CURRENT ROW for 7-row rolling.
- Mixing GROUP BY and window functions
  - You may compute aggregates in a subquery/CTE then apply window functions to the aggregated rows, or vice versa. Know which level is appropriate for your metric.

Walkthrough of the day’s script
- Category share of total revenue: a CTE first produces one row per category,
  then `SUM(revenue) OVER ()` exposes the grand total without collapsing those
  category rows.
- Customer-level windows: AVG(total_amount) OVER (PARTITION BY customer_id) and COUNT(*) OVER (PARTITION BY customer_id) produce lifetime averages and counts joined to each order without GROUP BY.
- Rolling window: `SUM(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` totals the current and six previous observed dates; dates without orders are skipped. For seven calendar days use `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` or a date spine.

Patterns to master
- Running total: SUM(x) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
- Percent of partition: x / NULLIF(SUM(x) OVER (PARTITION BY k),0)
- Windowed average/stddev for anomaly detection

Pitfalls
- Mixing RANGE with non-unique ORDER BY can include ties; use ROWS for exact counts.
- Window functions run after WHERE but before ORDER BY LIMIT at the outermost level; to filter on a windowed value, wrap in a subquery.
- Performance: Heavy windows over millions of rows may spill; ensure indexes on partition/order keys.

Further reading
- Postgres windows: https://www.postgresql.org/docs/17/tutorial-window.html
- Frames: https://www.postgresql.org/docs/17/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask an AI tutor about this lesson

A tutor is optional here. One useful prompt: paste customer 1's five order totals and ask for the value each row gets from `AVG(...) OVER (PARTITION BY customer_id)` and from the same window with `ORDER BY order_date` added, then check both columns in `psql`. The study guide's [pointers on working with a tutor](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) help keep it explaining instead of writing your answers.

```text
Tutor me through sql-16: Window Function Fundamentals: OVER, PARTITION BY, and Frames.

I have completed the direct catalog prerequisite: `sql-found-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day16_window_functions_fundamentals.md
- Answer-free learner SQL: sql/postgres-60day/day16_window_functions_fundamentals.sql

Key terms to teach in context: Window, Partition, Frame. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Pre-aggregate net revenue to one row per category, then calculate `SUM(revenue) OVER ()` beside each category. The ordinary aggregate establishes the category grain; the window exposes the grand total without removing those category rows.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-16/ working copy. Never point setup, reset, DDL, or DML
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
