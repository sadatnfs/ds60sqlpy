# Day 46: E-commerce Project, Part 1: LTV and Cohorts

## How to run this lesson

Open **sql-46** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit your copy at
`.learning/sql/sql-46/lesson/workspace/sql/postgres-60day/day46_project1_ecommerce_part1.sql`.
The lesson reads `customers`, `orders` and `order_items` in
`advanced_sql_training`, and the script wraps its queries in `BEGIN` ...
`ROLLBACK`. A clean `psql` run prints the 100 highest-LTV customers with a
quartile, then one row per signup month counting new customers, then your
exercise results. Signup and order dates are generated relative to the day
you loaded the fixture, so cohort months and recency in days shift over time,
while lifetime totals do not. Launcher and recovery steps are in the
[SQL study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom), and the
notebook option is in its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 45; optimization project](day45_phase3_optimization_project.md) Day 45 practiced measuring a query before tuning it; today the same evidence-first habit is applied to a customer metric.
- **Artifacts:** [learner SQL](../day46_project1_ecommerce_part1.sql) ·
  [solution reasoning](../solutions/day46_solutions.md) ·
  [executable solution](../solutions/day46_solutions.sql)

## A beginner's mental model for this lesson

Lifetime value (LTV) is a customer-grain number: one row per customer, the sum
of everything that customer bought. The data arrives at a finer grain, so the
lesson climbs one level at a time. `order_items` lines become one value per
order, orders become one LTV per customer, and only then do you label or rank
customers. If you skip a level, for example by joining payments to order lines
before summing, some orders are counted twice and every segment boundary moves.

Two population questions come next. First, who counts? 438 of the 500
customers have orders; the 62 BR customers have none. An inner join quietly
drops them, while `customers LEFT JOIN orders` plus `COALESCE(..., 0)` keeps
them with an explicit zero. Second, what does a label mean? `NTILE(4)` is
relative: it cuts whoever is in the result into four equal groups, so a
customer's quartile can change when other customers arrive. A fixed threshold
such as "gold from 5,000" is a business policy that stays put. Note that the
stored `customers.segment` column (`standard`, `silver`, `gold`,
`platinum`) is an unrelated marketing tier, not an LTV label. Read each query
in [logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both excerpts come from the learner script and run inside its transaction.

### Example 1

```sql
WITH order_values AS (
  SELECT
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    o.order_id
),
ltv AS (
  SELECT
    customer_id,
    ROUND(SUM(order_value), 2) AS ltv
  FROM
    order_values
  GROUP BY
    customer_id
)
SELECT
  c.customer_id,
  c.country,
  c.segment,
  l.ltv,
  NTILE(4) OVER (ORDER BY l.ltv DESC) AS ltv_quartile
FROM
  customers c
  JOIN ltv l ON l.customer_id = c.customer_id
ORDER BY
  l.ltv DESC
LIMIT 100;
```

**How to read it:** `order_values` sums net line revenue per (customer, order); `ltv` sums those
order values per customer and rounds. The final `SELECT` joins customer
attributes onto `ltv` and computes `NTILE(4) OVER (ORDER BY l.ltv DESC)`
before `ORDER BY` and `LIMIT 100` cut the list.

**Expected result/shape:** 100 rows, led by customer 181 (FR) at 9,502.22. The quartiles are computed
over the 438 customers who have orders, about 110 per quartile, so every row
shown is in quartile 1; the inner join means no BR customer is ranked at all.
The `segment` column shows the stored tier, which does not follow LTV.

### Example 2

```sql
SELECT
  date_trunc('month', created_at)::date AS cohort_month,
  COUNT(*) AS new_customers
FROM
  customers
GROUP BY
  1
ORDER BY
  cohort_month DESC;
```

**How to read it:** One `GROUP BY` on the signup month, written as ordinal `1`, counts customers
per cohort. There is no join, so every customer counts once whether or not
they ever ordered.

**Expected result/shape:** About four years of monthly cohorts, newest first, with roughly 9 to 12 new
customers each. These counts are the denominators you need before any cohort
revenue in Exercise 2 means anything.

## Learning objectives

- Calculate customer lifetime value (LTV) at one row per customer.
- Assign policy-driven segments and measure cohort revenue over lifecycle
  months.

## Vocabulary and concepts

- **LTV:** lifetime value under a stated revenue, margin, and refund definition.
- **Signup cohort:** customers grouped by their creation month.
- **Lifecycle offset:** elapsed whole months from cohort start to activity.

## Worked example / walkthrough

Collapse line items to order value, then orders to one customer LTV row. Left
join from customers if zero-order customers belong in the population. Reconcile
summed LTV with the chosen source total before assigning thresholds; segmenting
at a duplicated order-line grain would bias both counts and value.

## Exercises

Complete these in the [learner SQL](../day46_project1_ecommerce_part1.sql):

1. Define fixed LTV segments and analyze them by country.
   **Inputs/evidence:** For sql-46 Exercise 1, build `lifetime` from `customers` `LEFT JOIN orders` grouped by `customer_id` and `country` with `COALESCE(SUM(total_amount), 0)` as `ltv`, label it in `segmented` with `ltv >= 20000` as gold and `ltv >= 10000` as silver, then count customers and sum LTV by `country` and `ltv_segment`.
   **Expected result/shape:** For sql-46 Exercise 1, expected output: one row per (`country`, `ltv_segment`) pair that has customers, with columns `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`, ordered by `country`, then `avg_ltv DESC`. On the course data every customer is bronze, so it returns 8 rows, one per country.
   **Verify:** For sql-46 Exercise 1, confirm that `customers` sums to 500 and `total_ltv` sums to 2355646.89, equal to `SELECT SUM(total_amount) FROM orders`; confirm BR shows 62 customers at 0.00 and the highest single LTV is 9502.21 (customer 181), below the silver cutoff; then evaluate the same `CASE` on `VALUES (20000.00), (19999.99), (10000.00), (9999.99)` and confirm gold, silver, silver, bronze, so each boundary value falls into the higher band.
   **Data check:** Exercise 1 sets gold at 20,000 and silver at 10,000, but the highest LTV in the course data is about 9,502. Expect eight rows, one bronze row per country, including BR with 62 customers at 0.00. That is a real finding: the thresholds are policy, and this policy puts everyone in one band. State it rather than tuning the cutoffs until the result looks interesting.
2. Calculate cohort revenue for offsets 0-12.
   **Inputs/evidence:** For sql-46 Exercise 2, take each customer's `cohort_month` from `date_trunc('month', created_at)`, sum `orders.total_amount` by `customer_id` and order month in `monthly_customer`, compute `month_offset` from `age()` as years times 12 plus months, and keep offsets 0 through 12.
   **Expected result/shape:** For sql-46 Exercise 2, expected output: one row per (`cohort_month`, `month_offset`) pair with any revenue, with columns `cohort_month`, `month_offset`, and `revenue`, ordered by `cohort_month DESC`, then `month_offset`; 487 rows over 48 cohorts on our load, with offsets from 0 to 12.
   **Verify:** For sql-46 Exercise 2, confirm that (`cohort_month`, `month_offset`) is unique and that `SUM(revenue)` equals an independent `SUM(o.total_amount)` over orders whose order month falls on or after the customer's cohort month and before that month plus `interval '13 months'` (1410578.53 on our load); then check that `age(date '2025-02-01', date '2024-01-01')` gives offset 13, not 1, so the year term is what keeps that month out of the result.
   **Data check:** Expect hundreds of rows, a few per cohort, with offsets only from 0 to 12; older cohorts reach offset 12, the newest only offset 0 or 1. Offset 0 is the signup month itself. Compute the offset from years and months together, or a 13-month gap will wrap back to 1.
3. Predict how `NTILE` labels change when unrelated customers arrive.
   **Inputs/evidence:** For sql-46 Exercise 3, from `lifetime` (one row per `customer_id` with `COALESCE(SUM(total_amount), 0)` as `ltv`), assign `NTILE(4) OVER (ORDER BY ltv DESC, customer_id)` and a fixed `CASE` that labels `ltv >= 5000` gold and `ltv >= 2000` silver.
   **Expected result/shape:** For sql-46 Exercise 3, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`, ordered by `ltv DESC`, then `customer_id`; each quartile has exactly 125 customers, while the fixed labels give 246 gold, 171 silver, and 83 bronze.
   **Verify:** For sql-46 Exercise 3, cross-tabulate `population_quartile` by `fixed_segment` and confirm that quartile 2 holds 121 gold and 4 silver customers and quartile 4 holds 83 bronze and 42 silver; check the boundary rows by `row_number()`: customer 203 at 6971.42 is the last row of quartile 1 and customer 139 at 6961.84 the first of quartile 2. Then, in a rolled-back transaction, insert 4 customers with orders above 9502.21 and confirm customer 203 moves to quartile 2 while its fixed label stays gold.
   **Data check:** Expect 500 rows. With fixed cutoffs at 5,000 and 2,000 there are 246 gold, 171 silver and 83 bronze customers, while each quartile has exactly 125. The labels disagree: a customer at 4,964 is in quartile 2 but only silver.
4. Produce LTV, orders, AOV, and recency at customer grain.
   **Inputs/evidence:** For sql-46 Exercise 4, aggregate `orders` to one row per `customer_id` in `behavior` (`COUNT(*)`, `SUM(total_amount)`, `AVG(total_amount)`, and `MAX(order_date)`), then `LEFT JOIN` it from `customers` so customers without orders stay in the result.
   **Expected result/shape:** For sql-46 Exercise 4, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`, ordered by `ltv DESC`, then `customer_id`; customer 181 leads with 16 orders and 9502.21.
   **Verify:** For sql-46 Exercise 4, confirm that `order_count` sums to 4362 and `ltv` sums to 2355646.89, matching `orders`, and that exactly 62 rows have `order_count` 0, `ltv` 0, and `NULL` in both `average_order_value` and `days_since_last_order`; recompute customer 181 directly from `orders` (16 orders, average 593.89) and confirm that `days_since_last_order` equals `CURRENT_DATE - MAX(order_date)::date`, which changes with the run date.
   **Data check:** Expect 500 rows led by customer 181 with 16 orders and 9,502.21. The 62 BR customers show `order_count` 0 and `ltv` 0 but `NULL` average order value and `NULL` recency, because neither exists without an order.
5. Repair payment/item fanout in LTV.
   **Inputs/evidence:** For sql-46 Exercise 5, sum `quantity * unit_price * (1 - discount)` from `order_items` joined to `orders` into `order_value` at one row per `order_id`, then sum those values by `customer_id`; compare against the raw form that also joins `payments` before summing lines.
   **Expected result/shape:** For sql-46 Exercise 5, expected output: 438 rows, one per `customer_id` with at least one order, with columns `customer_id` and `line_ltv`, ordered by `line_ltv DESC`, then `customer_id`; the order grain lives in the `order_value` CTE (4,362 rows), not in the final result.
   **Verify:** For sql-46 Exercise 5, confirm that `line_ltv` sums to 2355647.12 and that customer 181 shows 9502.22, a cent above its 9502.21 `total_amount` sum because each order total is rounded; then run the raw form with `LEFT JOIN payments` and confirm it reads 13,432 rows instead of 13,085 line rows and reports 9682.06 for customer 181, because 347 orders have two payments. With an inner join to `payments` instead, the 873 orders without a payment also drop out.
   **Data check:** Expect 438 rows, one per customer with orders; the order grain lives in the `order_value` CTE. Values can differ from `orders.total_amount` sums by a cent (9,502.22 versus 9,502.21 for customer 181) because `total_amount` is rounded per order.
6. Retain no-order customers with an explicit zero-LTV policy.
   **Inputs/evidence:** For sql-46 Exercise 6, `LEFT JOIN orders` to `customers`, group by `c.customer_id`, take `COALESCE(SUM(o.total_amount), 0)` as `ltv`, and label `activity_status` from `COUNT(o.order_id)`, keeping every order condition out of `WHERE`.
   **Expected result/shape:** For sql-46 Exercise 6, expected output: 500 rows, one per `customer_id`, with columns `customer_id`, `ltv`, and `activity_status`, ordered by `customer_id`; 438 rows are `has-order` and 62 are `no-order` with `ltv` 0.
   **Verify:** For sql-46 Exercise 6, confirm the 438 and 62 split and that `ltv` sums to 2355646.89; then add `WHERE o.order_date >= '2020-01-01'` and confirm the result drops to 438 rows, because the filter rejects the `NULL` order rows the `LEFT JOIN` kept; finally move a recent-order condition such as `o.order_date >= CURRENT_DATE - 90` into the `ON` clause and confirm all 500 customers remain.
   **Data check:** Expect 500 rows in `customer_id` order: 438 labeled `has-order` and 62 labeled `no-order` with `ltv` 0. If you see 438 rows, an order condition has turned the `LEFT JOIN` into an inner join.

Add a zero-order-customer test and state its segment.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Treat segment thresholds as business
  policy, not universal cutoffs. Exercise 1's 20,000 and 10,000 cutoffs put
  every customer in bronze; Exercise 3's 5,000 and 2,000 cutoffs split them.
  Neither is wrong, but each must be stated with the result.
- **Customers missing from the population:** an inner join to orders, or a
  `WHERE o.order_date ...` filter after a `LEFT JOIN`, drops the 62 BR
  customers. Count the result; customer-grain answers should have 500 rows.
- **LTV larger than the order totals:** payments or a second line-level join
  multiplied rows before `SUM`. Compare the grand total of your LTV with
  `SUM(orders.total_amount)`, about 2,355,647 on the course data.
- **Cohort offsets that wrap after 11 months:** `EXTRACT(month FROM age(...))`
  alone ignores the year part. Multiply years by 12 and add months.
- General recovery steps are in the
  [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does every customer contribute at most once to segmentation input?
- Are threshold ownership, refund/margin scope, and multi-year month offsets
  explicit?

## Next step

Continue to [Day 47; cohort retention](day47_project1_ecommerce_part2.md).

## Deep dive and reference

## Project focus

- Calculate lifetime value at one row per customer.
- Assign explicit gold, silver, and bronze value segments.
- Measure cohort revenue over lifecycle months 0-12.

## How the learner script uses the current schema

The starter first collapses `order_items` to order value, then sums orders to
customer LTV and assigns `NTILE(4)` for exploration. Signup cohort is
`date_trunc('month', customers.created_at)`.

`orders.total_amount` is already reconciled from line-item net revenue by setup,
so it is also valid for customer LTV when the metric definition is gross booked
order value. The schema does not model a separate refund fact.

## Practice map

Exercises 1 and 3 contrast two segmentation policies with the relative
`NTILE` view, Exercise 2 turns signup cohorts into revenue by month offset,
and Exercises 4 to 6 build a customer feature row, check the line-level
total for fanout and keep no-order customers visible. The numbered list above
is the contract, repeated unchanged in the learner SQL.

## Grain and date reasoning

- One customer must contribute once to the LTV segmentation input.
- Customers with no orders need a deliberate policy; a left join can retain
  them with zero LTV.
- A multi-year month offset must combine years and months from `age`; extracting
  only the month component wraps after 11.
- A missing cohort/offset row means no represented orders, not necessarily a
  stored zero.

## Validation and limits

- Treat segment thresholds as business policy, not universal cutoffs.
- Reconcile summed customer LTV to `SUM(orders.total_amount)`.
- Signup month defines cohort membership; order month defines lifecycle revenue.
- Synthetic data demonstrates the method, not a real customer-value benchmark.

## Ask an AI tutor about this lesson

A tutor is useful here for debating where segment cutoffs should sit, but
any customer count or LTV it quotes must come from your own query. If you use
one, paste this prompt and follow the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-46: E-Commerce Project, Part 1: Lifetime Value and Cohorts.

I have completed the direct catalog prerequisite: `sql-45`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day46_project1_ecommerce_part1.md
- Answer-free learner SQL: sql/postgres-60day/day46_project1_ecommerce_part1.sql

Key terms to teach in context: LTV, Signup cohort, Lifecycle offset. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Collapse line items to order value, then orders to one customer LTV row. Left join from customers if zero-order customers belong in the population. Reconcile summed LTV with the chosen source total before assigning thresholds; segmenting at a duplicated order-line grain would bias both counts and value.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-46/ working copy. Never point setup, reset, DDL, or DML
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
