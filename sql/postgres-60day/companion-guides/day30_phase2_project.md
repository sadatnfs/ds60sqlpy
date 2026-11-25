# Day 30: Phase 2 Project: Cohort Retention and CLV (Companion Guide)

## How to run this lesson

Pick **sql-30** in `./classroom` and run **Whole SQL lesson (psql)**. The
project file,
`.learning/sql/sql-30/lesson/workspace/sql/postgres-60day/day30_phase2_project.sql`,
reads `customers`, `orders` and `order_items` in `advanced_sql_training`
and rolls back at the end. Example 1 is capped at 200 of its roughly 1,060
rows, newest cohort first, so scroll back to the top of its output rather
than reading only the tail. The shared steps are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

A notebook lets you keep each CTE as its own cell and count its rows before
the next one runs
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-30
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 29; pattern matching](day29_pattern_matching.md) and
  the complete window/CTE sequence from Days 16-29
- **Artifacts:** [learner SQL](../day30_phase2_project.sql) ·
  [solution reasoning](../solutions/day30_solutions.md) ·
  [executable solution](../solutions/day30_solutions.sql)

## A beginner's mental model for this lesson

A cohort table answers one question: of the customers who signed up in a
given month, what share ordered again N months later? Every query in this
project is built from the same four pieces, and each has its own grain.

| Piece | Grain | Rows on one load | Comes from |
|---|---|---|---|
| cohort sizes | one cohort month | 48 | `customers` only |
| order values | one order | 4,362 | `orders` joined to `order_items` |
| activity | one cohort and order month | about 1,060 | order values joined to cohorts |
| spine | one cohort and offset 0 to 12 | 48 x 13 = 624 | cohort sizes x `generate_series` |

The denominator is the cohort size from `customers`, never the number of
customers who ordered. Every customer belongs to a cohort, including the 62
in Brazil who never place an order. Those customers lower retention, which
is the honest answer.

The offset is the number of whole calendar months between the cohort month
and the order month. Both are first-of-month dates, so
`EXTRACT(YEAR FROM age(...)) * 12 + EXTRACT(MONTH FROM age(...))` is exact
here: an order in March for a January cohort is offset 2.

Signups are generated relative to `CURRENT_DATE`, from 30 to 1,489 days
before the load, so the exact cohort months and per-cohort counts shift a
little with the day you load the data. On the load used for these notes
there are 48 cohorts of 7 to 12 customers each.

## Two worked SQL examples

### Example 1

```sql
WITH orders_enriched AS (
  SELECT
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month_utc,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month_utc
  FROM
    customers c
),
cohort_sizes AS (
  -- The denominator includes customers who never place an order.
  SELECT
    cohort_month_utc,
    COUNT(*) AS original_customers
  FROM
    cohorts
  GROUP BY
    cohort_month_utc
),
metrics AS (
  SELECT
    e.customer_id,
    c.cohort_month_utc,
    e.order_month_utc,
    SUM(e.order_value) AS revenue
  FROM
    orders_enriched e
    JOIN cohorts c ON c.customer_id = e.customer_id
  GROUP BY
    e.customer_id,
    c.cohort_month_utc,
    e.order_month_utc
),
cohort_agg AS (
  SELECT
    cohort_month_utc,
    order_month_utc,
    (EXTRACT(YEAR FROM age(order_month_utc, cohort_month_utc)) * 12 + EXTRACT(MONTH FROM age(order_month_utc, cohort_month_utc)))::int AS month_offset,
    SUM(revenue) AS cohort_revenue,
    COUNT(DISTINCT customer_id) AS active_customers
  FROM
    metrics
  GROUP BY
    cohort_month_utc,
    order_month_utc)
  -- This first pass contains observed activity months only. Exercise 4 creates
  -- a dense offset spine so a missing month becomes an explicit zero.
  SELECT
    agg.cohort_month_utc,
    agg.month_offset,
    sizes.original_customers,
    agg.active_customers,
    ROUND(agg.active_customers::numeric / NULLIF (sizes.original_customers, 0), 4) AS retention_rate,
    ROUND(agg.cohort_revenue, 2) AS revenue,
    ROUND(agg.cohort_revenue / NULLIF (agg.active_customers, 0), 2) AS revenue_per_active
  FROM
    cohort_agg AS agg
    JOIN cohort_sizes AS sizes ON sizes.cohort_month_utc = agg.cohort_month_utc
  ORDER BY
    agg.cohort_month_utc DESC,
    agg.month_offset
  LIMIT 200;
```

**How to read it:** Follow the CTEs in order. `orders_enriched`
collapses line items to one value per order. `cohorts` gives each customer a
signup month, and `cohort_sizes` counts them. `metrics` attaches orders to
cohorts per customer and month, and `cohort_agg` turns that into active
customers and revenue per cohort and offset. The final join divides by the
cohort size, with `NULLIF` guarding the division.

**Expected result/shape:** One row per cohort and observed offset,
newest cohort first. The newest cohort, about 9 customers, shows only
offsets 0 and 1 because the calendar has not reached offset 2 yet. Offsets
with no orders are absent, not zero; the fourth exercise fixes that.
`retention_rate` stays below 1 on every row.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH orders_enriched AS (
  SELECT
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month_utc,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date),
  cohorts AS (
    SELECT
      c.customer_id,
      date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month_utc
    FROM
      customers c),
    cohort_sizes AS (
      -- The denominator includes customers who never place an order.
      SELECT
        cohort_month_utc,
        COUNT(*) AS original_customers
      FROM
        cohorts
      GROUP BY
        cohort_month_utc),
      metrics AS (
        SELECT
          e.customer_id,
          c.cohort_month_utc,
          e.order_month_utc,
          SUM(e.order_value) AS revenue
        FROM
          orders_enriched e
          JOIN cohorts c ON c.customer_id = e.customer_id
        GROUP BY
          e.customer_id,
          c.cohort_month_utc,
          e.order_month_utc),
        cohort_agg AS (
          SELECT
            cohort_month_utc,
            order_month_utc,
            (EXTRACT(YEAR FROM age(order_month_utc, cohort_month_utc)) * 12 + EXTRACT(MONTH FROM age(order_month_utc, cohort_month_utc)))::int AS month_offset,
            SUM(revenue) AS cohort_revenue,
            COUNT(DISTINCT customer_id) AS active_customers
          FROM
            metrics
          GROUP BY
            cohort_month_utc,
            order_month_utc)
          -- This first pass contains observed activity months only. Exercise 4 creates
          -- a dense offset spine so a missing month becomes an explicit zero.
          SELECT
            agg.cohort_month_utc,
            agg.month_offset,
            sizes.original_customers,
            agg.active_customers,
            ROUND(agg.active_customers::numeric / NULLIF (sizes.original_customers, 0), 4) AS retention_rate,
        ROUND(agg.cohort_revenue, 2) AS revenue,
      ROUND(agg.cohort_revenue / NULLIF (agg.active_customers, 0), 2) AS revenue_per_active
  FROM
    cohort_agg AS agg
    JOIN cohort_sizes AS sizes ON sizes.cohort_month_utc = agg.cohort_month_utc
  ORDER BY
    agg.cohort_month_utc DESC,
    agg.month_offset
  LIMIT 200;
```

**How to read it:** This is the same query under
`EXPLAIN (COSTS OFF)`. Look for the `CTE cohorts` node near the top:
because `cohorts` is used twice, PostgreSQL computes it once and scans it
from both `metrics` and `cohort_sizes`. The single-use CTEs are folded into
the main plan.

**Expected result/shape:** About 30 plan lines and no data. Reading
from the bottom: sequential scans of `order_items` and `orders`, a
`HashAggregate` to order grain, a hash join to the cohort CTE, a
`GroupAggregate` for the distinct count, a hash join to the cohort sizes,
then `Sort` and `Limit`.

## Learning objectives

- Build cohort-size, activity, retention, and revenue measures at compatible
  grains.
- Present an illustrative projection with explicit model limitations.

## Vocabulary and concepts

- **Cohort:** entities grouped by a shared starting period or event.
- **Retention denominator:** the original eligible population for a cohort.
- **Calendar spine:** explicit cohort/period combinations, including periods
  with no observed activity.

## Worked example / walkthrough

Calculate cohort size directly from customers at one row per signup cohort.
Separately deduplicate activity to one row per customer/order month, derive
month offset, and count active customers. Join numerator to denominator only
after both relations are stable, then guard and range-check the retention rate.

## Practice assumptions and review method

- **Focus:** Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
- **Assumptions:** Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
- **Failure to watch for:** Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
- **Review loop:** after each CTE, count its rows and compare with the
  table above. A wrong grain shows up as a row count that is too high,
  long before it shows up as a wrong rate.

## Exercises

Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.

Write the six answers as one growing script: the cohort sizes
from the first prompt and the order values from the second are reused by
every later answer. Before each run, predict the row count from the table
in the mental model, for example 48 rows for the first answer and 624 for
the fourth.

1. **Query writing:** Calculate original customer count for each UTC signup cohort month.
   **Progressive hint:** Build the denominator from customers, including customers who never order.
   **Inputs/evidence:** For sql-30 Exercise 1, read the 500 rows of `customers`, assign each one a `cohort_month` with `date_trunc('month', created_at AT TIME ZONE 'UTC')::date` in the `cohorts` CTE, and count customers per month.
   **Expected result/shape:** For sql-30 Exercise 1, expected output: one row per UTC signup month, 48 on this load (from 2022-11-01 through 2026-10-01), with `cohort_size` between 7 and 12 and a total of 500. The final columns are `cohort_month`, and `cohort_size`. The final order is `cohort_month`.
   **Verify:** For sql-30 Exercise 1, confirm `SUM(cohort_size)` is 500, the `customers` row count, so no customer is dropped by the UTC conversion; then, inside `BEGIN ... ROLLBACK`, insert one customer with the default `created_at` (now) and confirm a new cohort for the current month appears with size 1 while every older cohort keeps its count.
2. **Query writing:** Calculate active customers and net line revenue for each cohort/order month.
   **Progressive hint:** Aggregate line items to order grain before cohort joins, then count distinct active customers.
   **Inputs/evidence:** For sql-30 Exercise 2, read `orders` and `order_items` to build one net value per order and UTC `order_month` in `order_values`, read `customers` for each signup `cohort_month` in `cohorts`, then join the two on `customer_id` and group by cohort and order month.
   **Expected result/shape:** For sql-30 Exercise 2, expected output: one row per cohort and order month with activity, 1060 rows on this load across all 48 cohorts; the first is cohort 2022-11-01 in order month 2023-02-01 with 2 active customers and 1203.26 of revenue. The final columns are `cohort_month`, `order_month`, `active_customers`, and `net_revenue`. The final order is `c.cohort_month, ov.order_month`.
   **Verify:** For sql-30 Exercise 2, confirm `SUM(active_customers)` is 3912, equal to `COUNT(DISTINCT (customer_id, order_month))` over `order_values`, and that `SUM(net_revenue)` is 2355647.39, a few cents above the unrounded 2355647.12 because each cell is rounded; also confirm 0 rows have `order_month < cohort_month`, so no order predates its customer's signup.
3. **Query writing:** Calculate cohort month offset and retention using original cohort size.
   **Progressive hint:** Use year-plus-month age components and guard the denominator.
   **Inputs/evidence:** For sql-30 Exercise 3, read `customers` for each signup `cohort_month` and its `cohort_size`, read `orders` for distinct active customers per cohort and UTC order month in `activity`, then compute `month_offset` with `age()` and divide active customers by the original cohort size.
   **Expected result/shape:** For sql-30 Exercise 3, expected output: 1060 observed cohort and offset rows on this load, with `month_offset` from 0 to 45 and `retention_rate` between 0.0833 and 0.9091; only 12 cohorts have an offset 0 row, and the first cohort, 2022-11-01, starts at offset 3. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `a.cohort_month, month_offset`.
   **Verify:** For sql-30 Exercise 3, confirm no row has `active_customers > cohort_size` and that the 2022-11-01 cohort shows sizes of 10 with 2, 1, and 2 active customers at offsets 3, 4, and 5; then, inside `BEGIN ... ROLLBACK`, insert a customer with no orders and confirm the row count stays 1060, because the inner join to `activity` hides cohorts with no orders.
4. **Prediction:** Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
   **Progressive hint:** Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
   **Inputs/evidence:** For sql-30 Exercise 4, read `customers` for cohort sizes and `orders` for active customers per cohort and `month_offset`, build a `spine` by crossing every cohort with `generate_series(0, 12)`, and `LEFT JOIN` the activity onto it with `COALESCE(..., 0)`.
   **Expected result/shape:** For sql-30 Exercise 4, expected output: exactly 13 rows per cohort, 624 rows for the 48 cohorts on this load, of which 137 carry a zero-filled `active_customers`; cohort 2022-11-01 shows 0, 0, 0 at offsets 0 to 2 and then 2 at offset 3. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month, s.month_offset`.
   **Verify:** For sql-30 Exercise 4, confirm `COUNT(*) = 13 * COUNT(DISTINCT cohort_month)` and that the 487 nonzero rows match the offset 0 to 12 rows of Exercise 3; then, inside `BEGIN ... ROLLBACK`, insert a customer with no orders and confirm 637 rows, 150 of them zero, and 49 cohorts, because the spine keeps the new cohort that the inner join in Exercise 3 dropped.
5. **Debugging:** Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
   **Progressive hint:** Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
   **Inputs/evidence:** For sql-30 Exercise 5, read `orders` and `order_items` for net order values, read `customers` for cohorts, then aggregate active customers and revenue per cohort and order month in `metrics`, divide them in `per_active` with `NULLIF`, and average the last three `revenue_per_active` values per cohort with a `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` frame.
   **Expected result/shape:** For sql-30 Exercise 5, expected output: 487 rows on this load, all with `month_offset` from 0 to 12 and no NULL `revenue_per_active`; the first cohort's rows show `revenue_per_active` 601.63, 656.19, 660.47, and 76.67, with `illustrative_annualized_clv` 7219.56, 7546.92, 7673.15, and 5573.32. The final columns are `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`. The final order is `cohort_month, month_offset`.
   **Verify:** For sql-30 Exercise 5, confirm the first cohort by hand: 601.63 times 12 is 7219.56 for its first row, the second row averages two values, and the fourth row, 5573.32, drops the first value because the frame holds only three rows; also confirm that the first row of the next cohort equals its own `revenue_per_active` times 12, which shows the frame resets at each `cohort_month`.
6. **Extension:** Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0-12.
   **Progressive hint:** Calculate violations and compare totals at the same scoped population.
   **Inputs/evidence:** For sql-30 Exercise 6, read `orders`, `order_items`, and `customers` to rebuild `order_values`, `cohorts`, `cohort_sizes`, and `metrics`, keep offsets 0 to 12 in `scoped`, then count rows where active customers exceed the cohort size and compare their revenue with a subquery that sums `order_values` directly for the same offsets.
   **Expected result/shape:** For sql-30 Exercise 6, expected output: exactly one row: 0 violations, `cohort_revenue` 1410578.66, `independent_revenue` 1410578.66, and `revenue_difference` 0.00 on this load. The final columns are `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
   **Verify:** For sql-30 Exercise 6, confirm that the 1410578.66 is less than the full net revenue of 2355647.12 because orders after offset 12 are left out on purpose; then change `COUNT(DISTINCT ov.customer_id)` to `COUNT(*)` in `metrics` and confirm the audit reports 37 violations, because counting orders instead of customers lets activity exceed cohort size.

## Common mistakes and how to recover

- **Summing line items after the cohort join.** Joining `order_items`
  straight to customers works for revenue but makes it easy to count lines
  instead of customers. Collapse to one row per order first, as
  `order_values` does, then join.
- **Using active customers as the denominator.** Dividing by the customers
  who ordered at least once drops the 62 who never order and inflates every
  rate. Count the cohort from `customers`.
- **Reading a missing offset as "no data".** In the observed results about
  137 of the 624 cohort and offset slots between 0 and 12 have no orders and
  simply do not appear. The spine in the fourth answer shows them as 0.
- **Trusting a rows-based window across gaps.** `ROWS BETWEEN 2 PRECEDING`
  counts observed rows, so in six cohorts the three-row window covers more
  than three months. The fifth answer labels its projection as illustrative
  for that reason.
- **Comparing a partial month with full months.** The newest cohort and the
  current order month are still filling up, so their rates will rise.
- See [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures)
  for general recovery steps.

## Self-check

- Is `active_customers <= cohort_size` for every row and is retention in
  `[0, 1]`?
- Does the projection exclude current-period leakage and disclose sparse-month,
  margin, churn, and uncertainty limits?

## Next step

Continue to [Day 31; EXPLAIN and EXPLAIN ANALYZE](day31_explain_analyze.md).

## Deep dive and reference

Goal
- Extend the starter customer-cohort analysis with retention rates and an
  illustrative customer-lifetime-value projection.

Deliverable checklist
- The six prompts above are the complete deliverable: denominator, activity
  and revenue, retention, a dense offset spine, a limited teaching projection,
  and a reconciliation/constraint audit.

Guidance
1) Aggregate net order-line value to one row per order before cohort joins.
2) Calculate month offsets with year and month components from `age`; extracting
   only the month component wraps after 12 months.
3) Use the original cohort size as the retention denominator, including
   customers who never order.
4) Apply the moving window after revenue per active customer is computed.
5) Reconcile order-value totals to the underlying line-item formula.

Explicit limitations
- The maintained projection annualizes a trailing three-observation average of
  revenue per active customer. It is a teaching heuristic, not a production CLV
  model.
- Observed order months are not a dense calendar. A three-row frame may span
  missing month offsets unless you add a cohort calendar.
- The model does not incorporate margin, churn probability, discount rate,
  acquisition cost, or uncertainty.

Quality checklist
- `active_customers <= cohort_size` and retention remains between 0 and 1.
- Revenue is not multiplied by line or cohort joins.
- Cohort definition, active-customer rule, missing-month treatment, and
  projection horizon are stated beside the query.

## Ask an AI tutor about this lesson

A tutor can help you explain a retention curve in words for a
non-technical reader, once your counts reconcile
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-30: Phase 2 Project: Cohort Retention and Customer Lifetime Value.

I have completed the direct catalog prerequisite: `sql-29`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day30_phase2_project.md
- Answer-free learner SQL: sql/postgres-60day/day30_phase2_project.sql

Key terms to teach in context: Cohort, Retention denominator, Calendar spine. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Calculate cohort size directly from customers at one row per signup cohort. Separately deduplicate activity to one row per customer/order month, derive month offset, and count active customers. Join numerator to denominator only after both relations are stable, then guard and range-check the retention rate.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-30/ working copy. Never point setup, reset, DDL, or DML
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
