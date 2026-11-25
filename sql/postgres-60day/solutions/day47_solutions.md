# Day 47 Solutions: E-commerce Analytics, Part 2


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day47_solutions.sql
```

The solution file only reads data. Check the 27-row and 624-row results
first, then compare individual rates; the general
[solution routine](../../STUDY-GUIDE.md#read-a-solution) has the rest.

## Clause-by-clause reading map

Follow each statement in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Retention answers hinge on two CTEs that never touch each other until late:
`cohort_sizes` comes from `customers` alone, and the activity CTE comes from
`orders` grouped to one row per customer and month. Find the join that brings
them together and check that it is one-to-one on `cohort_month` before any
division happens.

The deliverables are a true retention rate, a tidy six-cohort result suitable
for a line chart, a choice of cohort anchor, a complete grid, a chronology
check and an observability flag. See [`day47_solutions.sql`](day47_solutions.sql).

## Exercises 1 and 2: Retention rate and chart-ready curves

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT
    customer_id,
    date_trunc('month', created_at)::date AS cohort_month
  FROM
    customers
),
cohort_sizes AS (
  SELECT
    cohort_month,
    COUNT(*) AS cohort_size
  FROM
    cohorts
  GROUP BY
    cohort_month
),
active_months AS (
  SELECT
    customer_id,
    date_trunc('month', order_date)::date AS order_month
  FROM
    orders
  GROUP BY
    customer_id,
    date_trunc('month', order_date)
),
retained AS (
  SELECT
    c.cohort_month,
    a.order_month,
    (EXTRACT(year FROM age(a.order_month, c.cohort_month)) * 12 + EXTRACT(month FROM age(a.order_month, c.cohort_month)))::int AS month_offset,
    COUNT(DISTINCT a.customer_id) AS active_customers
  FROM
    cohorts c
    JOIN active_months a USING (customer_id)
  GROUP BY
    c.cohort_month, a.order_month
),
curves AS (
  SELECT
    r.cohort_month,
    r.month_offset,
    s.cohort_size,
    r.active_customers,
    r.active_customers::numeric / NULLIF (s.cohort_size, 0) AS retention_rate
  FROM
    retained r
    JOIN cohort_sizes s USING (cohort_month)
  WHERE
    r.month_offset BETWEEN 0 AND 12
),
latest_six AS (
  SELECT
    cohort_month
  FROM
    cohort_sizes
  ORDER BY
    cohort_month DESC
  LIMIT 6
)
SELECT
  cohort_month,
  month_offset,
  cohort_size,
  active_customers,
  ROUND(retention_rate, 4) AS retention_rate
FROM
  curves
WHERE
  cohort_month IN (
    SELECT
      cohort_month
    FROM
      latest_six)
ORDER BY
  cohort_month DESC,
  month_offset;
```

Expected grain: one row per `(cohort_month, month_offset)` for the six newest
signup cohorts, with numerator, denominator, and rate. Chart with
`month_offset` on X, `retention_rate` on Y, and `cohort_month` as the series.
The chart itself is explicitly outside SQL; this answer produces the tidy data
to export or pass to a notebook/BI tool.

## Reasoning, safety, and pitfalls

- `active_months` deliberately deduplicates multiple orders by one customer in
  one month.
- Cohort size is all signups in the cohort, not only customers who eventually
  ordered.
- Cast before division to avoid integer truncation.
- A missing row at an offset is different from a zero-rate row. To force a
  complete retention matrix, cross join cohorts to `generate_series(0, 12)` and
  left join activity.
- The seed is synthetic, so chart shape demonstrates technique rather than a
  business retention benchmark.

## Exercise 1: Calculate retention rates

`cohort_sizes` supplies the denominator and active distinct customers supply the
numerator. Numeric casting prevents integer truncation.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 1, start from the lesson's cohort query over `customers` and `orders`: keep the `cohort_sizes` CTE (one row per signup `cohort_month`) and divide `active_customers` by `cohort_size` as `numeric` to produce `retention_rate`, rounded to 4 places.
- **Expected result/shape:** For sql-47 Exercise 1, expected output: one row per `cohort_month` and `month_offset` for the latest six cohorts, with every `retention_rate` between 0 and 1. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`.
- **Independent verification:** For sql-47 Exercise 1, for one `cohort_month`, recount its customers with `SELECT COUNT(*) FROM customers WHERE date_trunc('month', created_at)::date = <that month>` and compare the result with `cohort_size`; then confirm that `retention_rate = ROUND(active_customers::numeric / cohort_size, 4)` and `active_customers <= cohort_size` on every row.
- **Intermediate relation check:** `cohort_sizes` should return 48 rows, one per signup month, adding up to 500. `active_months` should return 3,912 rows, fewer than the 4,362 orders, because repeat orders in one month collapse. `retained` and `curves` are one row per (cohort, offset) with buyers.
- **Clause check:** The division is `active_customers::numeric / NULLIF(cohort_size, 0)`. The cast avoids integer truncation, and `NULLIF` turns a zero-size cohort into a `NULL` rate instead of an error, although no cohort here is empty. `ROUND(..., 4)` runs only in the final `SELECT` so the CTE keeps full precision.
- **Alternative/trade-off:** A window `COUNT(*) OVER (PARTITION BY cohort_month)` on the customer rows could supply the size without a separate CTE, but a named `cohort_sizes` relation is easier to verify on its own and to reuse in Exercise 4.
- **Edge case:** Dividing two integers truncates, so `active_customers / cohort_size` without a `numeric` cast prints 0 for every rate below 1. With 8 of 9 customers active, integer division gives 0 while the correct answer is 0.8889.

## Exercise 2: Return six tidy curves

The final rows retain cohort month, offset, size, active count, and rate. “Chart
it” is downstream presentation; SQL should preserve the auditable components.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 2, reuse the Exercise 1 query and keep only cohorts listed in `latest_six`, the six newest `cohort_month` values from `cohort_sizes`; the charting itself happens outside SQL, with `cohort_month` as the series, `month_offset` on the x axis, and `retention_rate` on the y axis.
- **Expected result/shape:** For sql-47 Exercise 2, expected output: one row per (`cohort_month`, `month_offset`) pair for the six newest cohorts, ordered by `cohort_month DESC`, then `month_offset`, with columns `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; 27 rows on our load, because each cohort has only as many offsets as months have passed (2 for the newest, 7 for the sixth).
- **Independent verification:** For sql-47 Exercise 2, confirm 6 distinct `cohort_month` values, a unique (`cohort_month`, `month_offset`) pair on every row, one `cohort_size` per cohort, and `active_customers <= cohort_size` everywhere; then recount one point directly, such as the newest cohort at offset 1, with `COUNT(DISTINCT o.customer_id)` over orders in the next calendar month from customers created in that cohort month, and compare it with `active_customers` (8 of 9 on our load).
- **Intermediate relation check:** `latest_six` is six rows, the newest cohort months from `cohort_sizes`. The final `WHERE cohort_month IN (...)` keeps 27 of the `curves` rows. Count rows per cohort: 2, 3, 4, 5, 6 and 7 from newest to oldest.
- **Clause check:** `latest_six` orders `cohort_sizes` by month and takes `LIMIT 6`; because months are unique there, no tie-breaker is needed. The outer `ORDER BY cohort_month DESC, month_offset` lays the data out so each cohort is one series and the offset is the x axis of a line chart.
- **Alternative/trade-off:** `DENSE_RANK() OVER (ORDER BY cohort_month DESC) <= 6` on `curves` would pick the same cohorts. The `IN` subquery reads more directly and ties the choice to cohort size rather than to rows that happen to have buyers.
- **Edge case:** A new cohort with signups but no orders yet would still enter `latest_six` because it comes from `cohort_sizes`, yet it would contribute no curve rows. That cohort then silently pushes the sixth cohort out of the chart.

## Exercise 3: Choose a cohort anchor

Signup month measures post-registration behavior; first-order month measures
repeat purchasing. The answer displays both per customer so the semantic choice
is visible.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 3, `LEFT JOIN orders` to `customers`, group by `c.customer_id` and the signup month, and report `date_trunc('month', c.created_at)` as `signup_cohort` beside `date_trunc('month', MIN(o.order_date))` as `first_order_cohort`.
- **Expected result/shape:** For sql-47 Exercise 3, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `signup_cohort`, and `first_order_cohort`, ordered by `customer_id`; `first_order_cohort` is `NULL` for the 62 customers without orders.
- **Independent verification:** For sql-47 Exercise 3, count the rows where the two anchors match (39), where the first order comes in a later month (399), and where `first_order_cohort` is `NULL` (62), and confirm they add up to 500; check customer 2, who signed up in 2026-09 but first ordered in 2026-10 on our load, and confirm the largest gap is 10 months, which is how far a curve shifts when it switches anchors.
- **Intermediate relation check:** There is no CTE. `customers LEFT JOIN orders` produces one row per order plus one row for each of the 62 customers without orders; `GROUP BY` brings that back to 500 rows.
- **Clause check:** `MIN(o.order_date)` per customer gives the first order, truncated to a month. The signup month is part of the `GROUP BY` so it can be selected without an aggregate. The `LEFT JOIN` keeps no-order customers with a `NULL` `first_order_cohort`.
- **Alternative/trade-off:** A first-order cohort could instead be built with `DISTINCT ON (customer_id) ... ORDER BY customer_id, order_date`. `MIN` is shorter when only the date is needed; `DISTINCT ON` helps when the first order's other columns matter too.
- **Edge case:** A customer who signs up in March and first orders in June sits in different cohorts under the two anchors; 399 customers here move. A customer with no orders has no first-order cohort at all.

## Exercise 4: Complete the cohort grid

Cross joining cohorts with offsets creates every expected cell. A left join
then turns missing observed activity into zero without losing cohort size.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 4, `CROSS JOIN` the 48 signup cohorts in `sizes` with `generate_series(0, 12)` in `offsets`, then `LEFT JOIN` the `activity` counts (distinct ordering customers by cohort and month offset) on both `cohort_month` and `month_offset`, using `COALESCE(..., 0)` for missing activity.
- **Expected result/shape:** For sql-47 Exercise 4, expected output: 624 rows, one per (`cohort_month`, `month_offset`) pair for 48 cohorts times 13 offsets, with columns `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`, ordered by `cohort_month DESC`, then `month_offset`.
- **Independent verification:** For sql-47 Exercise 4, confirm that every cohort has exactly 13 rows with offsets 0 to 12 and that `cohort_size` summed over one offset is 500; count the zero rows (137 on our load) and compare them with the latest order month: 66 are offsets after it, which cannot be observed yet, and 71 are observed months with no orders. Then remove the `LEFT JOIN` and use an inner join, and confirm that every zero row disappears.
- **Intermediate relation check:** `sizes` is 48 rows and `offsets` is 13. Their `CROSS JOIN` is the 624-row spine. `activity` holds only the (cohort, offset) pairs with buyers. Count the spine before the `LEFT JOIN` and again after it; both should be 624.
- **Clause check:** The `LEFT JOIN` matches on both `cohort_month` and `month_offset`, so a pair with no activity keeps its spine row and `COALESCE` turns the missing count into 0. The `WHERE o.order_date::date >= c.cohort_month` filter keeps negative offsets out of `activity`.
- **Alternative/trade-off:** `generate_series` over months per cohort, joined on order month, would build the same spine from dates rather than offsets; the integer `offsets` table is simpler when every cohort needs exactly 13 points.
- **Edge case:** For the newest cohort the spine shows 0 at offsets 2 to 12, months that do not exist yet. The grid is complete but not all of its zeros are observations, which is why the observability flag in Exercise 6 exists.

## Exercise 5: Reject negative chronology

The diagnostic returns customers whose first order precedes recorded signup.
Such rows should be corrected or explicitly excluded before retention math.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 5, join `customers` to `orders`, group by `customer_id` and `created_at`, and keep customers whose `MIN(o.order_date)` is earlier than `c.created_at`, which would produce a negative `month_offset`.
- **Expected result/shape:** For sql-47 Exercise 5, expected output: one row per `customer_id` whose first order precedes signup, with columns `customer_id`, `created_at`, and `first_order_at`, ordered by `customer_id`; on the course data this returns 0 rows, which is the passing answer.
- **Independent verification:** For sql-47 Exercise 5, confirm the empty result independently: the smallest gap between signup and first order over the 438 ordering customers is just over 2 days. Then, in a transaction, set customer 1's earliest order to `created_at - interval '1 day'`, rerun the query, confirm it returns exactly that customer with `first_order_at` one day before `created_at`, and `ROLLBACK`.
- **Intermediate relation check:** The inner join from `customers` to `orders` gives 4,362 rows. `GROUP BY` makes one row per customer with orders, 438 rows, and `HAVING` keeps only those whose first order precedes signup. Run the query without `HAVING` once and look at the smallest gap between `created_at` and `first_order_at` to see how close the data comes to failing.
- **Clause check:** The test sits in `HAVING` because it compares an aggregate, `MIN(o.order_date)`, with a grouped column. On the course data it returns 0 rows; the earliest gap between signup and an order is about two days.
- **Alternative/trade-off:** A `WHERE o.order_date < c.created_at` filter with `DISTINCT customer_id` finds the same customers by checking every order instead of only the first one; the `HAVING` version returns one row per customer with the earliest offending date.
- **Edge case:** Move one order before its customer's signup in a rolled-back transaction and the query returns that customer once, with the bad date as `first_order_at`. Exercise 4's `WHERE` would quietly drop that order instead. Run this check before publishing any curve: a silent drop shrinks a cohort's active count, while a negative offset would add a point to the left of month 0.

## Exercise 6: Preserve future unknowns

An offset beyond the latest observed month is not a measured zero. The
`is_observable` flag keeps not-yet-available periods distinct.

### Reasoning and verification

- **Inputs/evidence:** For sql-47 Exercise 6, take the latest observed month as `date_trunc('month', MAX(order_date))` from `orders`, build a `sample` of (`cohort_month`, `month_offset`) pairs with `VALUES` for the current month at offsets 0 and 6, and flag each pair observable when `cohort_month + make_interval(months => month_offset)` is on or before that month.
- **Expected result/shape:** For sql-47 Exercise 6, expected output: 2 rows, one per sample pair, with columns `cohort_month`, `month_offset`, and `is_observable`; offset 0 is `true` and offset 6 is `false` when the latest order month is the current month, as it is on a fresh load. A rate for an unobservable offset should then be `NULL`, never 0.
- **Independent verification:** For sql-47 Exercise 6, confirm the latest observed month from `orders` (2026-11 on our load) and check both flags by hand; then apply the same test to the 624-row spine from Exercise 4 and confirm 66 rows are not observable, all currently shown as 0, while the 71 observed zeros stay real zeros. On an older load where `CURRENT_DATE` is past the last order month, offset 0 also becomes `false`.
- **Intermediate relation check:** `latest` is one row, the month of the newest order. `sample` is two hand-written rows for the current month at offsets 0 and 6. The `CROSS JOIN` attaches the latest month to each sample row.
- **Clause check:** `cohort_month + make_interval(months => month_offset)` turns the offset back into a calendar month, and the comparison with `latest_observed_month` returns true for offset 0 and false for offset 6. Applied to Exercise 4's grid, false rows should carry a `NULL` rate.
- **Alternative/trade-off:** Comparing with `date_trunc('month', CURRENT_DATE)` instead of the latest order month treats the calendar as the limit of observation; using the data's own latest month is safer when loads lag behind the calendar.
- **Edge case:** Partially observed months are a further trap: the current month is observable here but incomplete, so its rate is still rising. Flag it or stop one month earlier when comparing cohorts.