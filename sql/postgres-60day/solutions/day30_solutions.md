# Day 30 solutions: Phase 2 Project: Cohort Retention and CLV


<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers read `customers`, `orders` and `order_items` and change
nothing. The shared approach is in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day30_solutions.sql
```

## How these answers fit together

Each answer repeats the CTEs it needs so it can run alone, but together they
build one analysis. The first answer fixes the denominator, the second adds
revenue at order grain, and the third turns months into offsets and rates.
The fourth fills the calendar, the fifth adds a clearly limited projection,
and the sixth proves the pieces agree. The counts below come from one load;
cohort months shift slightly with the load date. The learner file is
[day30_phase2_project.sql](../day30_phase2_project.sql).

## Reading contract

- **Focus:** Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
- **Assumptions:** Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
- **Primary pitfall:** Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Calculate original customer count for each UTC signup cohort month.

**Reasoning:** Build the denominator from customers, including customers who never order.

```sql
WITH cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM
    customers AS c
)
SELECT
  cohort_month,
  COUNT(*) AS cohort_size
FROM
  cohorts
GROUP BY
  cohort_month
ORDER BY
  cohort_month;
```

**Expected shape:** One row per cohort month.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 1, read the 500 rows of `customers`, assign each one a `cohort_month` with `date_trunc('month', created_at AT TIME ZONE 'UTC')::date` in the `cohorts` CTE, and count customers per month.
- **Expected result/shape:** For sql-30 Exercise 1, expected output: one row per UTC signup month, 48 on this load (from 2022-11-01 through 2026-10-01), with `cohort_size` between 7 and 12 and a total of 500. The final columns are `cohort_month`, and `cohort_size`. The final order is `cohort_month`.
- **Independent verification:** For sql-30 Exercise 1, confirm `SUM(cohort_size)` is 500, the `customers` row count, so no customer is dropped by the UTC conversion; then, inside `BEGIN ... ROLLBACK`, insert one customer with the default `created_at` (now) and confirm a new cohort for the current month appears with size 1 while every older cohort keeps its count.
- **Intermediate relation check:** `cohorts` has 500 rows, one per customer, because it reads only `customers`. No customer is lost for lacking orders.
- **Clause check:** `date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date` gives each customer a first-of-month date, and `COUNT(*)` per month gives 48 cohorts of 7 to 12 customers. The sizes sum to 500.
- **Alternative/trade-off:** Counting from `orders` instead would return cohort sizes of customers who ordered, 438 in total, and every later rate would be too high. Starting from `customers` is the whole point.
- **Edge case:** Without `AT TIME ZONE 'UTC'`, the session time zone decides the month, and a signup late on the last day of a month can move cohorts. The fixture times are on the hour, so the shift is real if your session is not UTC.

## Exercise 2: Query writing

**Prompt:** Calculate active customers and net line revenue for each cohort/order month.

**Reasoning:** Aggregate line items to order grain before cohort joins, then count distinct active customers.

```sql
WITH order_values AS (
  SELECT
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM
    customers AS c
)
SELECT
  c.cohort_month,
  ov.order_month,
  COUNT(DISTINCT ov.customer_id) AS active_customers,
  ROUND(SUM(ov.order_value), 2) AS net_revenue
FROM
  cohorts AS c
  JOIN order_values AS ov ON ov.customer_id = c.customer_id
GROUP BY
  c.cohort_month,
  ov.order_month
ORDER BY
  c.cohort_month,
  ov.order_month;
```

**Expected shape:** One row per observed cohort/order month.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 2, read `orders` and `order_items` to build one net value per order and UTC `order_month` in `order_values`, read `customers` for each signup `cohort_month` in `cohorts`, then join the two on `customer_id` and group by cohort and order month.
- **Expected result/shape:** For sql-30 Exercise 2, expected output: one row per cohort and order month with activity, 1060 rows on this load across all 48 cohorts; the first is cohort 2022-11-01 in order month 2023-02-01 with 2 active customers and 1203.26 of revenue. The final columns are `cohort_month`, `order_month`, `active_customers`, and `net_revenue`. The final order is `c.cohort_month, ov.order_month`.
- **Independent verification:** For sql-30 Exercise 2, confirm `SUM(active_customers)` is 3912, equal to `COUNT(DISTINCT (customer_id, order_month))` over `order_values`, and that `SUM(net_revenue)` is 2355647.39, a few cents above the unrounded 2355647.12 because each cell is rounded; also confirm 0 rows have `order_month < cohort_month`, so no order predates its customer's signup.
- **Intermediate relation check:** `order_values` has 4,362 rows, one per order, totalling 2,355,647.12 from the line-item formula. That is 0.23 more than `SUM(orders.total_amount)`, which comes from rounding in the stored header totals.
- **Clause check:** Grouping by cohort and order month gives about 1,060 rows. `COUNT(DISTINCT ov.customer_id)` is needed because 286 customer and month pairs hold more than one order; the largest count is 10.
- **Alternative/trade-off:** Joining `order_items` directly to `cohorts` and summing lines gives the same revenue but makes `COUNT(*)` count lines. The order-grain CTE removes that temptation.
- **Edge case:** The revenue across all rows is again 2,355,647.12, so nothing was duplicated by the join. If it were higher, the join key would be wrong.

## Exercise 3: Query writing

**Prompt:** Calculate cohort month offset and retention using original cohort size.

**Reasoning:** Use year-plus-month age components and guard the denominator.

```sql
WITH cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM
    customers AS c
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
activity AS (
  SELECT
    c.cohort_month,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
    COUNT(DISTINCT o.customer_id) AS active_customers
  FROM
    cohorts AS c
    JOIN orders AS o ON o.customer_id = c.customer_id
  GROUP BY
    c.cohort_month,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC'))
SELECT
  a.cohort_month,
  (EXTRACT(YEAR FROM age(a.order_month, a.cohort_month)) * 12 + EXTRACT(MONTH FROM age(a.order_month, a.cohort_month)))::integer AS month_offset,
  cs.cohort_size,
  a.active_customers,
  ROUND(a.active_customers::numeric / NULLIF (cs.cohort_size, 0), 4) AS retention_rate
FROM
  activity AS a
  JOIN cohort_sizes AS cs USING (cohort_month)
ORDER BY
  a.cohort_month,
  month_offset;
```

**Expected shape:** Observed cohort/offset rows with retention from 0 to 1.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 3, read `customers` for each signup `cohort_month` and its `cohort_size`, read `orders` for distinct active customers per cohort and UTC order month in `activity`, then compute `month_offset` with `age()` and divide active customers by the original cohort size.
- **Expected result/shape:** For sql-30 Exercise 3, expected output: 1060 observed cohort and offset rows on this load, with `month_offset` from 0 to 45 and `retention_rate` between 0.0833 and 0.9091; only 12 cohorts have an offset 0 row, and the first cohort, 2022-11-01, starts at offset 3. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `a.cohort_month, month_offset`.
- **Independent verification:** For sql-30 Exercise 3, confirm no row has `active_customers > cohort_size` and that the 2022-11-01 cohort shows sizes of 10 with 2, 1, and 2 active customers at offsets 3, 4, and 5; then, inside `BEGIN ... ROLLBACK`, insert a customer with no orders and confirm the row count stays 1060, because the inner join to `activity` hides cohorts with no orders.
- **Intermediate relation check:** `activity` has the same 1,060 cohort and month rows as the second answer, but reads `orders` alone because it needs only customers, not revenue.
- **Clause check:** The `age` arithmetic turns two first-of-month dates into whole months, from 0 up to 45. The highest retention is 0.9091, 10 of 11 customers, and no row reaches 1.
- **Alternative/trade-off:** `(order_month - cohort_month) / 30` looks simpler but drifts: 31-day and 28-day months put some orders in the wrong offset. The year and month parts of `age` are exact.
- **Edge case:** No order happens before its customer's signup in this data, so there are no negative offsets. In real data a backfilled signup date can create them; filter or flag them instead of averaging them in.

## Exercise 4: Prediction

**Prompt:** Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.

**Reasoning:** Cross join cohort months with generate_series, then left join observed activity at the same offset grain.

```sql
WITH cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM
    customers AS c
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
activity AS (
  SELECT
    c.cohort_month,
    (EXTRACT(YEAR FROM age(date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date, c.cohort_month)) * 12 + EXTRACT(MONTH FROM age(date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date, c.cohort_month)))::integer AS month_offset,
    COUNT(DISTINCT o.customer_id) AS active_customers
  FROM
    cohorts AS c
    JOIN orders AS o ON o.customer_id = c.customer_id
  GROUP BY
    c.cohort_month,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
spine AS (
  SELECT
    cs.cohort_month,
    cs.cohort_size,
    offset_value AS month_offset
  FROM
    cohort_sizes AS cs
    CROSS JOIN generate_series(0, 12) AS offsets (offset_value))
SELECT
  s.cohort_month,
  s.month_offset,
  s.cohort_size,
  COALESCE(a.active_customers, 0) AS active_customers
FROM
  spine AS s
  LEFT JOIN activity AS a ON a.cohort_month = s.cohort_month
    AND a.month_offset = s.month_offset
  ORDER BY
    s.cohort_month,
    s.month_offset;
```

**Expected shape:** Thirteen rows per cohort.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 4, read `customers` for cohort sizes and `orders` for active customers per cohort and `month_offset`, build a `spine` by crossing every cohort with `generate_series(0, 12)`, and `LEFT JOIN` the activity onto it with `COALESCE(..., 0)`.
- **Expected result/shape:** For sql-30 Exercise 4, expected output: exactly 13 rows per cohort, 624 rows for the 48 cohorts on this load, of which 137 carry a zero-filled `active_customers`; cohort 2022-11-01 shows 0, 0, 0 at offsets 0 to 2 and then 2 at offset 3. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month, s.month_offset`.
- **Independent verification:** For sql-30 Exercise 4, confirm `COUNT(*) = 13 * COUNT(DISTINCT cohort_month)` and that the 487 nonzero rows match the offset 0 to 12 rows of Exercise 3; then, inside `BEGIN ... ROLLBACK`, insert a customer with no orders and confirm 637 rows, 150 of them zero, and 49 cohorts, because the spine keeps the new cohort that the inner join in Exercise 3 dropped.
- **Intermediate relation check:** `spine` has 48 cohorts times 13 offsets, 624 rows, before any orders are joined.
- **Clause check:** The `LEFT JOIN` on both cohort and offset keeps every spine row. 487 slots find activity and 137 do not; `COALESCE` shows those as 0 active customers.
- **Alternative/trade-off:** Building the spine from observed offsets would miss a month where no cohort member ordered. `generate_series(0, 12)` makes the 13 slots a fixed promise.
- **Edge case:** For the newest cohorts, offsets beyond today are also 0, though they have not happened yet. A report should mark those as future months rather than as zero retention.

## Exercise 5: Debugging

**Prompt:** Calculate revenue per active customer and a trailing three-observation annualized teaching projection.

**Reasoning:** Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.

```sql
WITH order_values AS (
  SELECT
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM
    customers AS c
),
metrics AS (
  SELECT
    c.cohort_month,
    ov.order_month,
    (EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12 + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month)))::integer AS month_offset,
    COUNT(DISTINCT ov.customer_id) AS active_customers,
    SUM(ov.order_value) AS revenue
  FROM
    cohorts AS c
    JOIN order_values AS ov ON ov.customer_id = c.customer_id
  GROUP BY
    c.cohort_month,
    ov.order_month
),
per_active AS (
  SELECT
    metrics.*,
    revenue / NULLIF (active_customers, 0) AS revenue_per_active
  FROM
    metrics
)
SELECT
  cohort_month,
  order_month,
  month_offset,
  active_customers,
  ROUND(revenue, 2) AS revenue,
  ROUND(revenue_per_active, 2) AS revenue_per_active,
  ROUND(AVG(revenue_per_active) OVER (PARTITION BY cohort_month ORDER BY month_offset ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) * 12, 2) AS illustrative_annualized_clv
FROM
  per_active
WHERE
  month_offset BETWEEN 0 AND 12
ORDER BY
  cohort_month,
  month_offset;
```

**Expected shape:** One row per observed cohort/month with nullable guarded measures.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 5, read `orders` and `order_items` for net order values, read `customers` for cohorts, then aggregate active customers and revenue per cohort and order month in `metrics`, divide them in `per_active` with `NULLIF`, and average the last three `revenue_per_active` values per cohort with a `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` frame.
- **Expected result/shape:** For sql-30 Exercise 5, expected output: 487 rows on this load, all with `month_offset` from 0 to 12 and no NULL `revenue_per_active`; the first cohort's rows show `revenue_per_active` 601.63, 656.19, 660.47, and 76.67, with `illustrative_annualized_clv` 7219.56, 7546.92, 7673.15, and 5573.32. The final columns are `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`. The final order is `cohort_month, month_offset`.
- **Independent verification:** For sql-30 Exercise 5, confirm the first cohort by hand: 601.63 times 12 is 7219.56 for its first row, the second row averages two values, and the fourth row, 5573.32, drops the first value because the frame holds only three rows; also confirm that the first row of the next cohort equals its own `revenue_per_active` times 12, which shows the frame resets at each `cohort_month`.
- **Intermediate relation check:** `metrics` is filtered to offsets 0 to 12, leaving 487 rows, the same observed slots the fourth answer found.
- **Clause check:** `revenue_per_active` is computed before the window, so the window averages per-customer values. For the newest cohort, offset 0 is 17,152.37 over 8 customers, or 2,144.05 each.
- **Alternative/trade-off:** Running the window over the dense spine from the fourth answer would make each frame exactly three months. Here, 7 rows in 6 cohorts follow a gap, so their frame stretches further back.
- **Edge case:** Multiplying a three-row average by 12 assumes every month looks like the recent ones. That ignores churn, margin and seasonality, which is why the column is named `illustrative_annualized_clv`.

## Exercise 6: Extension

**Prompt:** Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0-12.

**Reasoning:** Calculate violations and compare totals at the same scoped population.

```sql
WITH order_values AS (
  SELECT
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM
    customers AS c
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
metrics AS (
  SELECT
    c.cohort_month,
    ov.order_month,
    (EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12 + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month)))::integer AS month_offset,
    COUNT(DISTINCT ov.customer_id) AS active_customers,
    SUM(ov.order_value) AS revenue
  FROM
    cohorts AS c
    JOIN order_values AS ov ON ov.customer_id = c.customer_id
  GROUP BY
    c.cohort_month,
    ov.order_month
),
scoped AS (
  SELECT
    m.*,
    cs.cohort_size
  FROM
    metrics AS m
    JOIN cohort_sizes AS cs USING (cohort_month)
  WHERE
    m.month_offset BETWEEN 0 AND 12
)
SELECT
  COUNT(*) FILTER (WHERE active_customers > cohort_size) AS active_exceeds_cohort_violations,
  ROUND(SUM(revenue), 2) AS cohort_revenue,
  ROUND((
    SELECT
      SUM(ov.order_value)
    FROM order_values AS ov
    JOIN cohorts AS c ON c.customer_id = ov.customer_id
    WHERE (EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12 + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month)))::integer BETWEEN 0 AND 12), 2) AS independent_revenue,
  ROUND(SUM(revenue) - (
      SELECT
        SUM(ov.order_value)
      FROM order_values AS ov
      JOIN cohorts AS c ON c.customer_id = ov.customer_id
      WHERE (EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12 + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month)))::integer BETWEEN 0 AND 12), 2) AS revenue_difference
FROM
  scoped;
```

**Expected shape:** One row with zero retention violations and zero revenue difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-30 Exercise 6, read `orders`, `order_items`, and `customers` to rebuild `order_values`, `cohorts`, `cohort_sizes`, and `metrics`, keep offsets 0 to 12 in `scoped`, then count rows where active customers exceed the cohort size and compare their revenue with a subquery that sums `order_values` directly for the same offsets.
- **Expected result/shape:** For sql-30 Exercise 6, expected output: exactly one row: 0 violations, `cohort_revenue` 1410578.66, `independent_revenue` 1410578.66, and `revenue_difference` 0.00 on this load. The final columns are `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
- **Independent verification:** For sql-30 Exercise 6, confirm that the 1410578.66 is less than the full net revenue of 2355647.12 because orders after offset 12 are left out on purpose; then change `COUNT(DISTINCT ov.customer_id)` to `COUNT(*)` in `metrics` and confirm the audit reports 37 violations, because counting orders instead of customers lets activity exceed cohort size.
- **Intermediate relation check:** `scoped` keeps the 487 observed rows with offsets 0 to 12, each carrying its cohort size.
- **Clause check:** The answer is one row: 0 violations, 1,410,578.66 in cohort revenue on this load, the same total from the independent subquery, and a difference of 0.00.
- **Alternative/trade-off:** Comparing against all 2,355,647.12 would fail, because orders after offset 12 are outside the scope. Both sides must use the same offset filter.
- **Edge case:** A violation count above 0 would mean `active_customers` counted lines or orders instead of distinct customers. A revenue difference other than 0 would point to a duplicated or dropped order in a join.

## Final self-check

- Why is the cohort size counted from `customers` and not from `orders`?
- How many rows should the dense spine have, and why?
- What does a difference of 0.00 in the sixth answer prove?
- Why is the projection in the fifth answer labelled illustrative?
