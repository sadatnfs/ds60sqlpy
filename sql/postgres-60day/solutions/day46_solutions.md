# Day 46 Solutions: E-commerce Analytics, Part 1


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day46_solutions.sql
```

The solution only reads course tables. Check row counts first (8, 500, 438
and 500 for the customer-level answers) and the LTV grand total before
comparing segment figures; the
[solution routine](../../STUDY-GUIDE.md#read-a-solution) covers the rest.

## Clause-by-clause reading map

Read each query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
In this lesson the deciding clauses are the join and the first `GROUP BY`.
`customers LEFT JOIN orders` decides whether no-order customers exist in the
answer, and the `GROUP BY` that produces one row per customer must run before
any `CASE` threshold, `NTILE` or country summary. When a query starts from
`order_items`, look for the order-grain CTE that collapses lines first.

This project begins with explicit lifetime-value segments and signup-cohort
revenue, then compares relative and fixed labels, builds a customer feature
row, checks line-level LTV for fanout and keeps no-order customers. The
canonical executable answer is [`day46_solutions.sql`](day46_solutions.sql).

## Exercise 1: Gold, silver, and bronze LTV by country

The thresholds below are example business policy. Confirm or tune them for a
real organization rather than presenting them as statistically derived.

```sql
SET search_path TO training, public;

WITH lifetime AS (
  SELECT
    c.customer_id,
    c.country,
    COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM
    customers c
    LEFT JOIN orders o USING (customer_id)
  GROUP BY
    c.customer_id, c.country
),
segmented AS (
  SELECT
    *,
    CASE WHEN ltv >= 20000 THEN
      'gold'
    WHEN ltv >= 10000 THEN
      'silver'
    ELSE
      'bronze'
    END AS ltv_segment
  FROM
    lifetime
)
SELECT
  country,
  ltv_segment,
  COUNT(*) AS customers,
  ROUND(AVG(ltv), 2) AS avg_ltv,
  ROUND(SUM(ltv), 2) AS total_ltv
FROM
  segmented
GROUP BY
  country,
  ltv_segment
ORDER BY
  country,
  avg_ltv DESC;
```

Expected grain: one row per `(country, ltv_segment)`. The `LEFT JOIN` retains
customers with no orders and assigns them zero LTV.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 1, build `lifetime` from `customers` `LEFT JOIN orders` grouped by `customer_id` and `country` with `COALESCE(SUM(total_amount), 0)` as `ltv`, label it in `segmented` with `ltv >= 20000` as gold and `ltv >= 10000` as silver, then count customers and sum LTV by `country` and `ltv_segment`.
- **Expected result/shape:** For sql-46 Exercise 1, expected output: one row per (`country`, `ltv_segment`) pair that has customers, with columns `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`, ordered by `country`, then `avg_ltv DESC`. On the course data every customer is bronze, so it returns 8 rows, one per country.
- **Independent verification:** For sql-46 Exercise 1, confirm that `customers` sums to 500 and `total_ltv` sums to 2355646.89, equal to `SELECT SUM(total_amount) FROM orders`; confirm BR shows 62 customers at 0.00 and the highest single LTV is 9502.21 (customer 181), below the silver cutoff; then evaluate the same `CASE` on `VALUES (20000.00), (19999.99), (10000.00), (9999.99)` and confirm gold, silver, silver, bronze, so each boundary value falls into the higher band.
- **Intermediate relation check:** `lifetime` must have 500 rows, one per customer, with BR customers at 0 through `COALESCE`. `segmented` keeps those 500 rows and adds `ltv_segment`. Only the final `GROUP BY country, ltv_segment` collapses them, to eight rows on this data because no customer reaches 10,000.
- **Clause check:** The `CASE` tests the highest band first; reversing the order would label a 25,000 customer silver. `AVG(ltv)` and `SUM(ltv)` run over customers, not orders, because `lifetime` already collapsed the orders. BR's average is 0.00 rather than missing because the zeros are real values.
- **Alternative/trade-off:** Storing the cutoffs in a small `VALUES` table and joining on a range would let analysts change the policy without editing the `CASE`; for three bands the inline expression is easier to review.
- **Edge case:** Give one AU customer an extra order that lifts LTV past 10,000 and the result gains an AU silver row with one customer, while AU bronze drops to 61. A new customer with no orders lands in bronze at 0.

## Exercise 2: Cohort revenue at month offsets 0 through 12

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT
    customer_id,
    date_trunc('month', created_at)::date AS cohort_month
  FROM
    customers
),
monthly_customer AS (
  SELECT
    customer_id,
    date_trunc('month', order_date)::date AS order_month,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    customer_id,
    date_trunc('month', order_date)
),
cohort_revenue AS (
  SELECT
    c.cohort_month,
    mc.order_month,
    (EXTRACT(year FROM age(mc.order_month, c.cohort_month)) * 12 + EXTRACT(month FROM age(mc.order_month, c.cohort_month)))::int AS month_offset,
    SUM(mc.revenue) AS revenue
  FROM
    cohorts c
    JOIN monthly_customer mc USING (customer_id)
  GROUP BY
    c.cohort_month, mc.order_month
)
SELECT
  cohort_month,
  month_offset,
  ROUND(revenue, 2) AS revenue
FROM
  cohort_revenue
WHERE
  month_offset BETWEEN 0 AND 12
ORDER BY
  cohort_month DESC,
  month_offset;
```

Expected grain: one row per cohort and lifecycle month. A missing offset means
that cohort generated no orders in that lifecycle month; it is not automatically
equivalent to a stored zero.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 2, take each customer's `cohort_month` from `date_trunc('month', created_at)`, sum `orders.total_amount` by `customer_id` and order month in `monthly_customer`, compute `month_offset` from `age()` as years times 12 plus months, and keep offsets 0 through 12.
- **Expected result/shape:** For sql-46 Exercise 2, expected output: one row per (`cohort_month`, `month_offset`) pair with any revenue, with columns `cohort_month`, `month_offset`, and `revenue`, ordered by `cohort_month DESC`, then `month_offset`; 487 rows over 48 cohorts on our load, with offsets from 0 to 12.
- **Independent verification:** For sql-46 Exercise 2, confirm that (`cohort_month`, `month_offset`) is unique and that `SUM(revenue)` equals an independent `SUM(o.total_amount)` over orders whose order month falls on or after the customer's cohort month and before that month plus `interval '13 months'` (1410578.53 on our load); then check that `age(date '2025-02-01', date '2024-01-01')` gives offset 13, not 1, so the year term is what keeps that month out of the result.
- **Intermediate relation check:** `cohorts` has 500 rows; `monthly_customer` has one row per (customer, order month); `cohort_revenue` collapses to one row per (cohort, order month). Run each and confirm the last one has no duplicate (cohort_month, order_month) pairs before trusting the offset.
- **Clause check:** `age(order_month, cohort_month)` returns years and months separately, so the offset is `years * 12 + months`. The `WHERE month_offset BETWEEN 0 AND 12` filter runs on the outer query because the offset does not exist until the CTE computes it.
- **Alternative/trade-off:** `(EXTRACT(year FROM o) - EXTRACT(year FROM c)) * 12 + EXTRACT(month FROM o) - EXTRACT(month FROM c)` gives the same offsets from the two month starts and avoids `age`; both are correct because both inputs are first-of-month dates.
- **Edge case:** A cohort month with no orders at some offset has no row, not a zero row. To show zeros, generate offsets 0 to 12 per cohort and left join the revenue to them.

## Reasoning, safety, and pitfalls

- Use one customer row in the LTV CTE; joining items without first controlling
  grain can inflate totals.
- `age()` exposes both years and months. Using only `EXTRACT(month ...)` wraps
  after 11 and breaks multi-year offsets.
- Signup month defines the cohort here, while LTV includes all available order
  history.
- These answers are read-only and repeatable.

## Exercise 3: Compare relative and fixed segments

`NTILE(4)` is recalculated over the current population, so another customer's
arrival can move a boundary. Fixed monetary thresholds are stable but require a
reviewed business policy. The executable answer displays both.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 3, from `lifetime` (one row per `customer_id` with `COALESCE(SUM(total_amount), 0)` as `ltv`), assign `NTILE(4) OVER (ORDER BY ltv DESC, customer_id)` and a fixed `CASE` that labels `ltv >= 5000` gold and `ltv >= 2000` silver.
- **Expected result/shape:** For sql-46 Exercise 3, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`, ordered by `ltv DESC`, then `customer_id`; each quartile has exactly 125 customers, while the fixed labels give 246 gold, 171 silver, and 83 bronze.
- **Independent verification:** For sql-46 Exercise 3, cross-tabulate `population_quartile` by `fixed_segment` and confirm that quartile 2 holds 121 gold and 4 silver customers and quartile 4 holds 83 bronze and 42 silver; check the boundary rows by `row_number()`: customer 203 at 6971.42 is the last row of quartile 1 and customer 139 at 6961.84 the first of quartile 2. Then, in a rolled-back transaction, insert 4 customers with orders above 9502.21 and confirm customer 203 moves to quartile 2 while its fixed label stays gold.
- **Intermediate relation check:** `lifetime` has 500 rows, BR included at 0. The final query adds two labels side by side without grouping, so the output also has 500 rows, sorted by LTV with `customer_id` breaking ties among the 62 zeros.
- **Clause check:** `NTILE(4) OVER (ORDER BY ltv DESC, customer_id)` deals 500 rows into four groups of 125. The quartile 1 floor is about 6,971 and quartile 4 tops out near 2,860, while the fixed `CASE` uses 5,000 and 2,000, which is why 246 customers are gold but only 125 are in quartile 1.
- **Alternative/trade-off:** `PERCENT_RANK()` gives a continuous relative position instead of four buckets; it changes just as much when the population changes, so it does not replace the fixed policy either.
- **Edge case:** Add four new customers with no orders and every quartile grows to 126; some customers near a boundary move to the next quartile although their own LTV did not change. Their fixed segments stay the same, which is the point of the comparison.

## Exercise 4: Build a customer-grain feature row

The `behavior` CTE aggregates orders once per customer. Its outer join preserves
no-order customers and supports LTV, frequency, average order value, and recency
without mixing grains.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 4, aggregate `orders` to one row per `customer_id` in `behavior` (`COUNT(*)`, `SUM(total_amount)`, `AVG(total_amount)`, and `MAX(order_date)`), then `LEFT JOIN` it from `customers` so customers without orders stay in the result.
- **Expected result/shape:** For sql-46 Exercise 4, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`, ordered by `ltv DESC`, then `customer_id`; customer 181 leads with 16 orders and 9502.21.
- **Independent verification:** For sql-46 Exercise 4, confirm that `order_count` sums to 4362 and `ltv` sums to 2355646.89, matching `orders`, and that exactly 62 rows have `order_count` 0, `ltv` 0, and `NULL` in both `average_order_value` and `days_since_last_order`; recompute customer 181 directly from `orders` (16 orders, average 593.89) and confirm that `days_since_last_order` equals `CURRENT_DATE - MAX(order_date)::date`, which changes with the run date.
- **Intermediate relation check:** `behavior` is one row per customer with orders, 438 rows. After the `LEFT JOIN` from `customers`, the result is 500 rows. Run `behavior` alone first and confirm `order_count` adds up to 4,362, the total number of orders.
- **Clause check:** Aggregating in `behavior` before joining keeps the join one-to-one. `COALESCE` turns missing counts and LTV into 0, while `average_order_value` and `days_since_last_order` stay `NULL` for BR customers because there is no honest value to show. `CURRENT_DATE - last_order_at::date` makes recency a whole number of days.
- **Alternative/trade-off:** Joining `customers` to `orders` and grouping once would also give 500 rows, but `COUNT(*)` would then return 1 for no-order customers; you would need `COUNT(o.order_id)` to get 0. The CTE form also keeps the order statistics testable on their own, which matters once more features are added.
- **Edge case:** Recency changes every day you rerun the query because it subtracts from `CURRENT_DATE`; compare it with a fixed reference date when you need reproducible features. Two customers with 16 orders each can have very different recency (11 days for customer 181, 71 for customer 155), so the feature row carries information LTV alone does not.

## Exercise 5: Prevent LTV fanout

Line revenue is reduced to one row per order before it becomes customer LTV.
Payments would need their own order-grain aggregation; joining both raw sources
would multiply values.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 5, sum `quantity * unit_price * (1 - discount)` from `order_items` joined to `orders` into `order_value` at one row per `order_id`, then sum those values by `customer_id`; compare against the raw form that also joins `payments` before summing lines.
- **Expected result/shape:** For sql-46 Exercise 5, expected output: 438 rows, one per `customer_id` with at least one order, with columns `customer_id` and `line_ltv`, ordered by `line_ltv DESC`, then `customer_id`; the order grain lives in the `order_value` CTE (4,362 rows), not in the final result.
- **Independent verification:** For sql-46 Exercise 5, confirm that `line_ltv` sums to 2355647.12 and that customer 181 shows 9502.22, a cent above its 9502.21 `total_amount` sum because each order total is rounded; then run the raw form with `LEFT JOIN payments` and confirm it reads 13,432 rows instead of 13,085 line rows and reports 9682.06 for customer 181, because 347 orders have two payments. With an inner join to `payments` instead, the 873 orders without a payment also drop out.
- **Intermediate relation check:** `order_value` is one row per order, 4,362 rows, each summing its lines. The final `GROUP BY customer_id` gives 438 rows, one per customer with orders. The grand total of `line_ltv` is about 2,355,647.12, a few tenths more than the sum of `orders.total_amount` because that column is rounded per order.
- **Clause check:** The fix is the order of operations: collapse lines to orders, then orders to customers. Nothing joins `payments`; adding it after `order_items` would copy every line once per payment and inflate the 347 orders paid with two methods.
- **Alternative/trade-off:** Summing lines straight to customer grain without the order CTE gives the same totals because no other table is joined; the order CTE earns its place once an order-level fact such as payment method is needed.
- **Edge case:** To prove the fanout, join `payments` into the CTE and compare one two-payment customer; their `line_ltv` jumps. Because the 62 BR customers have no orders, they are absent here by design; Exercise 6 shows how to keep them.

## Exercise 6: Retain no-order customers

The answer keeps the LEFT JOIN outer and applies `COALESCE` only after grouping.
A WHERE predicate on order columns would accidentally remove the intended
zero-LTV population.

### Reasoning and verification

- **Inputs/evidence:** For sql-46 Exercise 6, `LEFT JOIN orders` to `customers`, group by `c.customer_id`, take `COALESCE(SUM(o.total_amount), 0)` as `ltv`, and label `activity_status` from `COUNT(o.order_id)`, keeping every order condition out of `WHERE`.
- **Expected result/shape:** For sql-46 Exercise 6, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `ltv`, and `activity_status`, ordered by `customer_id`; 438 rows are `has-order` and 62 are `no-order` with `ltv` 0.
- **Independent verification:** For sql-46 Exercise 6, confirm the 438 and 62 split and that `ltv` sums to 2355646.89; then add `WHERE o.order_date >= '2020-01-01'` and confirm the result drops to 438 rows, because the filter rejects the `NULL` order rows the `LEFT JOIN` kept; finally move a recent-order condition such as `o.order_date >= CURRENT_DATE - 90` into the `ON` clause and confirm all 500 customers remain.
- **Intermediate relation check:** There is no CTE. `customers LEFT JOIN orders` gives one row per order plus one row per no-order customer, 4,424 rows, and `GROUP BY c.customer_id` collapses that to 500.
- **Clause check:** `COUNT(o.order_id)` counts only matched orders, so it is 0 for the 62 BR customers and the `CASE` labels them `no-order`. `COALESCE(SUM(...), 0)` replaces the `NULL` sum with the zero-LTV policy, after the join rather than inside it.
- **Alternative/trade-off:** A `NOT EXISTS` query for no-order customers combined with `UNION ALL` to a grouped query for the rest also returns 500 rows, but it repeats the policy in two places.
- **Edge case:** Adding `WHERE o.status <> 'returned'` would remove the 62 BR customers, because their `o.status` is `NULL`; put such a condition in the `ON` clause instead. The same applies to a date window such as "orders in the last year": filter in `ON` and the zero-LTV customers survive, filter in `WHERE` and they vanish from the count of 500.