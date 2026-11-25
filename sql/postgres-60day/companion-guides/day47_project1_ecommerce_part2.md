# Day 47: E-commerce Project, Part 2: Cohort Retention

## How to run this lesson

Open **sql-47** from `./classroom` (PostgreSQL), pick **Whole SQL lesson
(psql)** and work in
`.learning/sql/sql-47/lesson/workspace/sql/postgres-60day/day47_project1_ecommerce_part2.sql`.
It reads `customers` and `orders` in `advanced_sql_training` inside a
`BEGIN` ... `ROLLBACK` block. A clean `psql` run prints the active-customer
counts by cohort and month offset, then an `EXPLAIN` plan for the same query,
then your exercise results. Signup months and order months are generated
relative to the day the fixture was loaded, so the newest cohort and its
counts move as time passes; the shape of the answer does not. The
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) has the
launcher and recovery steps, and the notebook path is in its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 46; LTV and cohorts](day46_project1_ecommerce_part1.md) Day 46 built signup cohorts and summed their revenue; today the same cohorts are measured in customers instead of money.
- **Artifacts:** [learner SQL](../day47_project1_ecommerce_part2.sql) ·
  [solution reasoning](../solutions/day47_solutions.md) ·
  [executable solution](../solutions/day47_solutions.sql)

## A beginner's mental model for this lesson

Retention asks what share of a cohort came back in a later month. That needs
two numbers from two different grains. The denominator is cohort size: every
customer who signed up in that month, from `customers` alone, whether or not
they ever ordered. The numerator is active customers: distinct people with at
least one order in the month being measured. The 4,362 orders collapse to
3,912 (customer, order month) pairs, because a customer with two orders in a
month is still one returning customer.

The month offset is the gap between the signup month and the order month,
built from `age()` as years times 12 plus months, so offset 0 is the signup
month and offset 12 is a year later. Offsets have three possible states: a
row with active customers, a row with zero active customers, and a missing
row. The learner query only produces the first. A month with no buyers simply
has no row, and a month that has not happened yet has no row either. The
exercises separate those cases. Read each CTE in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both excerpts run inside the learner transaction; the second prints a plan.

### Example 1

```sql
WITH orders_m AS (
  SELECT
    o.customer_id,
    date_trunc('month', o.order_date)::date AS order_month
  FROM
    orders o
  GROUP BY
    o.customer_id,
    date_trunc('month', o.order_date)
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at)::date AS cohort_month
  FROM
    customers c
),
retention AS (
  SELECT
    co.cohort_month,
    om.order_month,
    (EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12 + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month)))::int AS month_offset,
    COUNT(DISTINCT om.customer_id) AS active_customers
  FROM
    orders_m om
    JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY
    co.cohort_month,
    om.order_month
)
SELECT
  cohort_month,
  month_offset,
  active_customers
FROM
  retention
WHERE
  month_offset BETWEEN 0 AND 12
ORDER BY
  cohort_month DESC,
  month_offset;
```

**How to read it:** `orders_m` groups orders to one row per (customer, order month). `cohorts`
gives each customer a signup month. `retention` joins the two, computes the
offset and counts distinct customers per (cohort month, order month). The
outer query keeps offsets 0 to 12.

**Expected result/shape:** One row per (cohort month, offset) that had at least one buyer, about 487 on
a fresh load, newest cohort first. The newest cohort has only offsets 0 and 1
because later months have not arrived. There is no rate yet and no cohort
size, so the counts cannot be compared across cohorts of different sizes.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH orders_m AS (
  SELECT
    o.customer_id,
    date_trunc('month', o.order_date)::date AS order_month
  FROM
    orders o
  GROUP BY
    o.customer_id,
    date_trunc('month', o.order_date)),
  cohorts AS (
    SELECT
      c.customer_id,
      date_trunc('month', c.created_at)::date AS cohort_month
    FROM
      customers c),
    retention AS (
      SELECT
        co.cohort_month,
        om.order_month,
        (EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12 + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month)))::int AS month_offset,
        COUNT(DISTINCT om.customer_id) AS active_customers
      FROM
        orders_m om
        JOIN cohorts co ON co.customer_id = om.customer_id
      GROUP BY
        co.cohort_month,
        om.order_month
)
    SELECT
      cohort_month,
      month_offset,
      active_customers
    FROM
      retention
    WHERE
      month_offset BETWEEN 0 AND 12
    ORDER BY
      cohort_month DESC,
      month_offset;
```

**How to read it:** `EXPLAIN (COSTS OFF)` plans the same statement without running it, so no
counts appear.

**Expected result/shape:** A plan tree, read from the bottom up: a `HashAggregate` over `orders` builds
the customer-month rows, a `Hash Join` with `customers` applies the 0 to 12
offset test as a join filter (the planner pushed the outer `WHERE` down), then
a `GroupAggregate` counts customers and a final `Sort` orders the output. Run
the plain query to see the counts.

## Learning objectives

- Define cohort size independently from later activity.
- Produce a chart-ready retention table with explicit numerator, denominator,
  and lifecycle offset.

## Vocabulary and concepts

- **Cohort size:** all eligible signups in the cohort, including non-purchasers.
- **Active customer:** a distinct customer meeting the declared period rule.
- **Retention curve:** retention rate across lifecycle offsets for one cohort.

## Worked example / walkthrough

Deduplicate activity to `(customer_id, order_month)`, count active customers per
cohort/offset, and join to cohort size calculated from all customers. Cast
before division and build a cohort/offset spine when missing periods must appear
as explicit zeros.

## Exercises

Complete these in the [learner SQL](../day47_project1_ecommerce_part2.sql):

1. Convert active-customer counts to retention rates.
   **Inputs/evidence:** For sql-47 Exercise 1, start from the lesson's cohort query over `customers` and `orders`: keep the `cohort_sizes` CTE (one row per signup `cohort_month`) and divide `active_customers` by `cohort_size` as `numeric` to produce `retention_rate`, rounded to 4 places.
   **Expected result/shape:** For sql-47 Exercise 1, expected output: one row per `cohort_month` and `month_offset` for the latest six cohorts, with every `retention_rate` between 0 and 1. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`.
   **Verify:** For sql-47 Exercise 1, for one `cohort_month`, recount its customers with `SELECT COUNT(*) FROM customers WHERE date_trunc('month', created_at)::date = <that month>` and compare the result with `cohort_size`; then confirm that `retention_rate = ROUND(active_customers::numeric / cohort_size, 4)` and `active_customers <= cohort_size` on every row.
   **Data check:** Expect 27 rows for the six newest cohorts, because each cohort has only as many offsets as months have passed (2 for the newest, 7 for the sixth). Cohort sizes are 9 to 12 customers, so one returning customer moves a rate by about 0.1; the newest cohort shows 8 of 9, 0.8889, at offsets 0 and 1.
2. Return the latest six cohort curves in tidy form.
   **Inputs/evidence:** For sql-47 Exercise 2, reuse the Exercise 1 query and keep only cohorts listed in `latest_six`, the six newest `cohort_month` values from `cohort_sizes`; the charting itself happens outside SQL, with `cohort_month` as the series, `month_offset` on the x axis, and `retention_rate` on the y axis.
   **Expected result/shape:** For sql-47 Exercise 2, expected output: one row per (`cohort_month`, `month_offset`) pair for the six newest cohorts, ordered by `cohort_month DESC`, then `month_offset`, with columns `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; 27 rows on our load, because each cohort has only as many offsets as months have passed (2 for the newest, 7 for the sixth).
   **Verify:** For sql-47 Exercise 2, confirm 6 distinct `cohort_month` values, a unique (`cohort_month`, `month_offset`) pair on every row, one `cohort_size` per cohort, and `active_customers <= cohort_size` everywhere; then recount one point directly, such as the newest cohort at offset 1, with `COUNT(DISTINCT o.customer_id)` over orders in the next calendar month from customers created in that cohort month, and compare it with `active_customers` (8 of 9 on our load).
   **Data check:** Every row should satisfy `active_customers <= cohort_size`, and each cohort should carry the same `cohort_size` on all of its rows. Some offset 1 rates are higher than offset 0 rates; customers who sign up late in a month often place their first order the next month.
3. Compare signup-month and first-order-month cohort anchors.
   **Inputs/evidence:** For sql-47 Exercise 3, `LEFT JOIN orders` to `customers`, group by `c.customer_id` and the signup month, and report `date_trunc('month', c.created_at)` as `signup_cohort` beside `date_trunc('month', MIN(o.order_date))` as `first_order_cohort`.
   **Expected result/shape:** For sql-47 Exercise 3, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `signup_cohort`, and `first_order_cohort`, ordered by `customer_id`; `first_order_cohort` is `NULL` for the 62 customers without orders.
   **Verify:** For sql-47 Exercise 3, count the rows where the two anchors match (39), where the first order comes in a later month (399), and where `first_order_cohort` is `NULL` (62), and confirm they add up to 500; check customer 2, who signed up in 2026-09 but first ordered in 2026-10 on our load, and confirm the largest gap is 10 months, which is how far a curve shifts when it switches anchors.
   **Data check:** Expect 500 rows. On the course data 39 customers first order in their signup month, 399 first order later (up to 10 months later) and 62 have `first_order_cohort` `NULL` because they never ordered. The two anchors define different cohorts, so state which one a curve uses.
4. Build a complete cohort/offset spine.
   **Inputs/evidence:** For sql-47 Exercise 4, `CROSS JOIN` the 48 signup cohorts in `sizes` with `generate_series(0, 12)` in `offsets`, then `LEFT JOIN` the `activity` counts (distinct ordering customers by cohort and month offset) on both `cohort_month` and `month_offset`, using `COALESCE(..., 0)` for missing activity.
   **Expected result/shape:** For sql-47 Exercise 4, expected output: 624 rows, one per (`cohort_month`, `month_offset`) pair for 48 cohorts times 13 offsets, with columns `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`, ordered by `cohort_month DESC`, then `month_offset`.
   **Verify:** For sql-47 Exercise 4, confirm that every cohort has exactly 13 rows with offsets 0 to 12 and that `cohort_size` summed over one offset is 500; count the zero rows (137 on our load) and compare them with the latest order month: 66 are offsets after it, which cannot be observed yet, and 71 are observed months with no orders. Then remove the `LEFT JOIN` and use an inner join, and confirm that every zero row disappears.
   **Data check:** Expect 48 cohorts times 13 offsets, 624 rows. Recent cohorts show 0 at high offsets; most of those zeros are months that have not happened yet, not months when everyone left, which is the problem Exercise 6 addresses.
5. Prevent negative offsets from inconsistent chronology.
   **Inputs/evidence:** For sql-47 Exercise 5, join `customers` to `orders`, group by `customer_id` and `created_at`, and keep customers whose `MIN(o.order_date)` is earlier than `c.created_at`, which would produce a negative `month_offset`.
   **Expected result/shape:** For sql-47 Exercise 5, expected output: one row per `customer_id` whose first order precedes signup, with columns `customer_id`, `created_at`, and `first_order_at`, ordered by `customer_id`; on the course data this returns 0 rows, which is the passing answer.
   **Verify:** For sql-47 Exercise 5, confirm the empty result independently: the smallest gap between signup and first order over the 438 ordering customers is just over 2 days. Then, in a transaction, set customer 1's earliest order to `created_at - interval '1 day'`, rerun the query, confirm it returns exactly that customer with `first_order_at` one day before `created_at`, and `ROLLBACK`.
   **Data check:** On the course data the query returns 0 rows: every first order is at least two days after signup. An empty result here is the passing answer. To see the check fire, update one order date before its customer's `created_at` inside a transaction and roll back.
6. Distinguish observed zero retention from future, unobservable offsets.
   **Inputs/evidence:** For sql-47 Exercise 6, take the latest observed month as `date_trunc('month', MAX(order_date))` from `orders`, build a `sample` of (`cohort_month`, `month_offset`) pairs with `VALUES` for the current month at offsets 0 and 6, and flag each pair observable when `cohort_month + make_interval(months => month_offset)` is on or before that month.
   **Expected result/shape:** For sql-47 Exercise 6, expected output: 2 rows, one per sample pair, with columns `cohort_month`, `month_offset`, and `is_observable`; offset 0 is `true` and offset 6 is `false` when the latest order month is the current month, as it is on a fresh load. A rate for an unobservable offset should then be `NULL`, never 0.
   **Verify:** For sql-47 Exercise 6, confirm the latest observed month from `orders` (2026-11 on our load) and check both flags by hand; then apply the same test to the 624-row spine from Exercise 4 and confirm 66 rows are not observable, all currently shown as 0, while the 71 observed zeros stay real zeros. On an older load where `CURRENT_DATE` is past the last order month, offset 0 also becomes `false`.
   **Data check:** The solution returns two sample rows, not order rows: the current month at offset 0 is observable and at offset 6 is not, compared with the latest order month in `orders`. A rate for an unobservable offset should be `NULL`, never 0.

Retain numerator and denominator beside every rate.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A missing offset row and a present
  zero-rate row are different. Build a cohort-by-offset spine when a complete
  matrix is required. Exercise 4's 624-row grid shows the zeros the learner
  query leaves out.
- **Rates of exactly 0 or 1 everywhere:** integer division. Cast
  `active_customers::numeric` before dividing by `cohort_size`.
- **Rates above 1:** orders were counted instead of customers, or the
  denominator came from customers who ordered. Rebuild `cohort_size` from
  `customers` alone.
- **Offsets that reset to 0 after a year:** the month part of `age()` was used
  without the year part.
- Other recovery steps are in the
  [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Is each customer counted once per activity month regardless of order count?
- Are rates bounded by zero and one, with missing rows distinguished from zero?

## Next step

Continue to [Day 48; affinity and attribution](day48_project1_ecommerce_part3.md).

## Deep dive and reference

## Project focus

- Define signup cohort size.
- Count distinct active customers by lifecycle month.
- Produce six chart-ready retention curves.

## How the learner script uses the current schema

The starter deduplicates `orders` to one row per `(customer_id, order_month)`,
joins each customer to the signup month from `customers.created_at`, and counts
active customers at offsets 0-12.

This lesson is retention only. Funnel analysis belongs to the later
event/capstone work and is not a Day 47 deliverable.

## Practice map

Exercises 1 and 2 turn counts into rates and a six-cohort chart table, Exercise 3 compares two ways to define a cohort, Exercise 4 fills the grid
with explicit zeros, and Exercises 5 and 6 guard against impossible and not
yet observable offsets. The learner SQL carries the same numbered contract
word for word.

## Grain and denominator

- Cohort size includes every signup in the month, not only later purchasers.
- Multiple orders by the same customer in one month count as one active
  customer.
- Cast before division so PostgreSQL does not perform integer division.
- Combine year and month components when calculating lifecycle offset.

## Validation and limits

- A missing offset row and a present zero-rate row are different. Build a
  cohort-by-offset spine when a complete matrix is required.
- Do not count orders as retained customers.
- Restrict activity to order months on or after signup.
- The synthetic curves are technique demonstrations, not expected business
  retention shapes.

## Ask an AI tutor about this lesson

A tutor can help you explain why a rate rises from offset 0 to offset 1, but
the cohort sizes and counts must be your own. If you want one, paste this
prompt and see the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-47: E-Commerce Project, Part 2: Cohort Retention.

I have completed the direct catalog prerequisite: `sql-46`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day47_project1_ecommerce_part2.md
- Answer-free learner SQL: sql/postgres-60day/day47_project1_ecommerce_part2.sql

Key terms to teach in context: Cohort size, Active customer, Retention curve. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Deduplicate activity to `(customer_id, order_month)`, count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-47/ working copy. Never point setup, reset, DDL, or DML
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
