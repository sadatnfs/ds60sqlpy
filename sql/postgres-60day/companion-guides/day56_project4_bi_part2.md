# Day 56: Complex BI Project, Part 2: Percentiles and CUBE

## How to run this lesson

Open **sql-56** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit
`.learning/sql/sql-56/lesson/workspace/sql/postgres-60day/day56_project4_bi_part2.sql`.
It reads the course tables in `advanced_sql_training` inside `BEGIN` and
`ROLLBACK`, so nothing is written. A clean `psql` run prints three result sets:
200 country and month percentile rows (cut by `LIMIT 200` from 303), 210
ranked product rows and a 56-row `CUBE` whose blank-country, blank-category
row holds the grand total 2,355,647.12. The
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) has the
launcher steps, and its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
covers the optional notebook.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 55; BI drill-downs](day55_project4_bi_part1.md) Day 55's drill-down queries over the same orders, lines and products are the background; nothing from Day 55 has to be loaded first.
- **Artifacts:** [learner SQL](../day56_project4_bi_part2.sql) ·
  [solution reasoning](../solutions/day56_solutions.md) ·
  [executable solution](../solutions/day56_solutions.sql)

## A beginner's mental model for this lesson

This lesson asks two questions about the same 13,085 order lines. The first is
how big a revenue cube gets when payment method becomes a third dimension. By
country and category, `CUBE` returns 56 rows: 7 ordering countries plus a
total, times 6 categories plus a total. Adding a method with 5 values (`bank`,
`card`, `credit`, `paypal`, `unpaid`) multiplies that by 6, to 336 rows. That
jump is **dimensional explosion**, and it happens before any join problem.

The join problem comes from `payments`. 347 orders were paid with two methods,
so joining raw payments to lines repeats those lines. Each order therefore gets
one **primary payment method**, chosen by a stated reporting rule (largest paid
amount, then method name) and joined only after payments are reduced to one row
per order. Unpaid orders get the label `unpaid`.

The second question is about distributions. A **continuous percentile**
(`PERCENTILE_CONT`) can interpolate between two values; `PERCENTILE_DISC`
always returns an observed one. Both need the right population: here, one
value per order and category, not one per line or one whole order total
copied into every category. Read every query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both excerpts come from the learner script and run as written inside its
transaction.

### Example 1

```sql
WITH orders_m AS (
  SELECT
    c.country,
    date_trunc('month', o.order_date)::date AS month,
    o.total_amount AS amt
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
)
SELECT
  country,
  month,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM
  orders_m
GROUP BY
  country,
  month
ORDER BY
  month DESC,
  country
LIMIT 200;
```

**How to read it:** `orders_m` keeps one row per order with its country, month and
`total_amount`. The outer query groups those orders by country and month and
asks for the median, 90th and 99th percentile of order value in each group.
The values come back as `double precision`, which is why some print with long
decimal tails such as `647.3399999999999`.

**Expected result/shape:** The 7 countries that have orders and the 46 order months produce 303
country-month groups; `ORDER BY month DESC, country` plus `LIMIT 200` keeps
the newest 200, starting with AU in November 2026. Groups with a single order
print the same number for all three percentiles.

### Example 2

```sql
WITH prod_rev AS (
  SELECT
    c.country,
    p.category,
    p.product_id,
    p.name,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    c.country,
    p.category,
    p.product_id,
    p.name
),
ranked AS (
  SELECT
    *,
    RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk_country,
    RANK() OVER (PARTITION BY country,
      category ORDER BY revenue DESC) AS rnk_in_cat
  FROM
    prod_rev
)
SELECT
  *
FROM
  ranked
WHERE
  rnk_in_cat <= 5
ORDER BY
  country,
  category,
  rnk_in_cat;
```

**How to read it:** `prod_rev` sums line revenue per country and product, and `ranked` gives
each product two ranks: one within its country and one within its country and
category. Filtering `rnk_in_cat <= 5` keeps the top five products of every
category in every country, while `rnk_country` stays visible for comparison.

**Expected result/shape:** 7 countries times 6 categories times 5 products gives 210 rows, so no ties
reach fifth place on this data. The first row is AU, Apparel, Product 271 with
2,646.48 in revenue; it ranks first in its category but only eighth in all of
AU.

## Learning objectives

- Control order, payment, and line grain before multidimensional aggregation.
- Calculate percentiles over category-attributable order values.

## Vocabulary and concepts

- **Dimensional explosion:** rapid subtotal-row growth as a cube gains
  dimensions.
- **Primary payment method:** a reporting policy selecting one method per order.
- **Continuous percentile:** an interpolated ordered-set statistic from
  `PERCENTILE_CONT`.

## Worked example / walkthrough

Aggregate payments at `(order_id, method)`, select one method by greatest total
with a stable tie-breaker, and only then join line revenue. Separately aggregate
line value at `(month, category, order_id)` before computing p50/p90; whole
order totals would repeat across categories.

## Exercises

Complete these in the [learner SQL](../day56_project4_bi_part2.sql):

1. Add payment method to the cube and compare row counts.
   **Inputs/evidence:** For sql-56 Exercise 1, build `line` with one row per order item (13,085 rows) carrying `country`, `category`, and `payment_method`, where `payment_method` is the method with the largest paid amount for the order (ties broken by method name, `unpaid` when the order has no payment), then count the rows of `CUBE (country, category)` and of `CUBE (country, category, payment_method)`.
   **Expected result/shape:** For sql-56 Exercise 1, expected output: one row with `two_dimension_rows` 56 and `three_dimension_rows` 336. The 7 ordering countries plus a subtotal times the 6 categories plus a subtotal gives 56, and the 5 payment values (`bank`, `card`, `credit`, `paypal`, `unpaid`) plus a subtotal multiply that by 6. The final columns are `two_dimension_rows` and `three_dimension_rows`.
   **Verify:** For sql-56 Exercise 1, confirm that `line` has 13085 rows and 210 distinct `(country, category, payment_method)` tuples (7 x 6 x 5, so every combination occurs and the cube is complete), and that `primary_payment` has one row per paid order (3489). In a rolled-back transaction, run `UPDATE payments SET method = 'bank' WHERE method = 'card'`: `two_dimension_rows` stays 56 while `three_dimension_rows` falls to 280 (56 x 5).
   **Data check:** On a fresh load `two_dimension_rows` is 56 and `three_dimension_rows` is 336. Rerun `cube_three` with `GROUP BY ROLLUP` instead and the count falls to 260, because a rollup keeps one subtotal path rather than every combination of the three dimensions.
2. Calculate category-month order-value P50/P90.
   **Inputs/evidence:** For sql-56 Exercise 2, sum line revenue per `(month, category, order_id)` in `category_orders`, so an order contributes one value to each category it bought from, then take `percentile_cont` at 0.50 and 0.90 of those values per `(month, category)`, rounded to 2 decimals.
   **Expected result/shape:** For sql-56 Exercise 2, expected output: 276 rows, one per `(month, category)` for 46 months (2023-02 to 2026-11) and 6 categories, starting with 2026-11 Apparel at `p50_order_value` 122.86 and `p90_order_value` 361.16. The final columns are `month`, `category`, `p50_order_value`, and `p90_order_value`. The final order is `month DESC, category`.
   **Verify:** For sql-56 Exercise 2, confirm 276 rows with no repeated `(month, category)` and that all six February 2023 rows show the same value for both percentiles, because each holds a single order. In a rolled-back transaction, add a January 2023 order with one 10.00 Books line: the result grows to 277 rows and the new 2023-01 Books row shows 10.00 for both percentiles.
   **Data check:** Expect 276 rows, every category in each of the 46 months. The oldest month, February 2023, has a single order in each category, so its p50 and p90 are the same value; in 64 of the 66 groups from 2026 the p90 is more than double the p50, the exceptions being January Electronics and June Sports.
3. Predict raw payment/item join fanout.
   **Inputs/evidence:** For sql-56 Exercise 3, join `orders` to `order_items` and to `payments` on `order_id` without pre-aggregation and count the joined rows, the distinct `order_item_id` values, and the distinct `payment_id` values.
   **Expected result/shape:** For sql-56 Exercise 3, expected output: one row with `raw_join_rows` 10816, `distinct_items` 10469, and `distinct_payments` 3836; an order with two payments repeats each of its items, so the joined rows exceed the distinct items. The final columns are `raw_join_rows`, `distinct_items`, and `distinct_payments`.
   **Verify:** For sql-56 Exercise 3, confirm that `raw_join_rows` equals `SELECT SUM(i.n * p.n) FROM (SELECT order_id, COUNT(*) n FROM order_items GROUP BY order_id) i JOIN (SELECT order_id, COUNT(*) n FROM payments GROUP BY order_id) p USING (order_id)` (10816); summing item revenue over this join would count every line once per payment of its order.
   **Data check:** The gap of 347 between joined rows and distinct items comes entirely from the 347 orders with two payments, each of which has a single line. The 2,616 lines of the 873 unpaid orders never reach the join at all.
4. Pre-aggregate payment methods and reconcile line revenue.
   **Inputs/evidence:** For sql-56 Exercise 4, reduce `payments` to one `reporting_method` per order with `MIN(method)`, an alphabetical rule that differs from the largest-amount rule of Exercise 1, reduce `order_items` to one revenue total per order, left-join them at order grain with `unpaid` for orders without payments, and sum revenue per reporting method.
   **Expected result/shape:** For sql-56 Exercise 4, expected output: 5 rows, one per `reporting_method` (`bank`, `card`, `credit`, `paypal`, and `unpaid`), whose `revenue` values add up to `reconciled_total` (2355647.1235), the exact line revenue repeated on every row. The final columns are `reporting_method`, `revenue`, and `reconciled_total`. The final order is `reporting_method`.
   **Verify:** For sql-56 Exercise 4, confirm that the five `revenue` values add up to `SELECT SUM(quantity * unit_price * (1 - discount)) FROM order_items` (2355647.1235) and that `method` has one row per paid order (3489), so no order's revenue is counted twice.
   **Data check:** On a fresh load `bank` has the most revenue, 479,821.35, and `unpaid` carries 469,843.08. Swapping `MIN(method)` for the largest-amount rule of Exercise 1 changes nothing here, since every split order either ties on amount or already favors the alphabetically first method.
5. Repair line-grain percentiles when the metric is order value.
   **Inputs/evidence:** For sql-56 Exercise 5, sum line revenue per `(category, order_id)` in `category_order` first, then take `percentile_cont(0.5)` of those order values per category with `COUNT(*)` as `observations`; the faulty version takes the percentile over raw `order_items` rows instead.
   **Expected result/shape:** For sql-56 Exercise 5, expected output: 6 rows whose `observations` add up to 13085 (Apparel 2192, Beauty 2189, Books 2145, Electronics 2187, Home 2186, Sports 2186), with `p50` between 146.54 (Home) and 150.24 (Electronics). The final columns are `category`, `observations`, and `p50`. The final order is `category`.
   **Verify:** For sql-56 Exercise 5, confirm that the line-grain query over `order_items` joined to `products` returns the same counts and medians here, because no order has two lines in one category. In a rolled-back transaction, add a second Apparel line (product 1, quantity 1, `unit_price` 10.00) to order 1: the line-grain count for Apparel rises to 2193, while `observations` stays 2192 because order 1 still contributes one Apparel value, now 166.92.
   **Data check:** Expect 6 rows whose `observations` add up to 13,085, between 2,145 for Books and 2,192 for Apparel, with medians near 150. No order here has two lines in the same category, so the line-grain answer matches; the fix matters once one does.
6. Compare continuous and discrete percentiles for an even population.
   **Inputs/evidence:** For sql-56 Exercise 6, reuse `category_order` (one value per category and order) and compute `percentile_cont(0.5)` and `percentile_disc(0.5)` side by side per category with `COUNT(*)` as `observations`; Apparel (2192), Home (2186), and Sports (2186) are the even-sized groups.
   **Expected result/shape:** For sql-56 Exercise 6, expected output: 6 rows in which `continuous_p50` equals `discrete_p50` in every category (Apparel 149.5, Beauty 147.66, Books 149.88, Electronics 150.24, Home 146.54, Sports 148.05), because the two middle values of each even group are tied. The final columns are `category`, `observations`, `continuous_p50`, and `discrete_p50`. The final order is `category`.
   **Verify:** For sql-56 Exercise 6, add `date_trunc('month', o.order_date)` to `category_order` and to the grouping, then compare the two columns: on the checked load 122 of the 133 even-sized category-months show different medians. For 2026-11 Electronics (82 orders) the two middle orders are 134.64 and 141.36, so `continuous_p50` returns their midpoint 138 while `discrete_p50` returns the observed 134.64.
   **Data check:** On this data `continuous_p50` and `discrete_p50` agree in every category. Line values repeat often (825 distinct values over 13,085 rows), so the two middle values of an even group such as Apparel's 2,192 are equal.

Retain cube and percentile observation counts.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Three-dimensional cube row count should
  exceed the two-dimensional count on this seed. If both counts match, the
  payment method never reached the `CUBE` list.
- **Revenue above 2,355,647.12:** lines were joined to raw `payments`, so the
  347 split orders count twice. Reduce payments to one row per order first.
- **Blank labels read as missing data:** in `CUBE` output a `NULL` country or
  category is a subtotal row. Use `GROUPING()` to label it, as the learner
  cube's `g_country` and `g_cat` columns do.
- **`ROUND` fails on a percentile:** `round(double precision, integer)` does
  not exist. Cast with `::numeric` before rounding, as Exercise 2 does.
- **Percentiles of copied totals:** joining `orders.total_amount` to each
  category repeats one value per category in the order. Sum the category's own
  lines instead.
- More recovery steps are in the
  [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does the cube grand total reconcile to source line revenue?
- Is the payment-method choice labeled as policy rather than an intrinsic order
  attribute?

## Next step

Continue to [Day 57; trends and anomalies](day57_project4_bi_part3.md).

## Deep dive and reference

## Project focus

- Measure the dimensional growth caused by adding payment method to a cube.
- Calculate category-month p50 and p90 order-value distributions.
- Control join grain before multidimensional aggregation.

## How the learner script uses the current schema

The starter calculates order-value percentiles by `(country, month)`, ranks
products within country/category, and cubes line revenue across country and
category.

Orders can have multiple payment rows. For the exercise, the reference policy
defines one primary method per order as the method with the greatest total paid
amount, breaking ties by method name. Unpaid orders receive an `unpaid` label.

## Practice map

Exercises 1 and 3 measure how row counts grow when payments join the data, Exercise 4 attributes revenue without double counting, and Exercises 2, 5 and 6
compute medians and 90th percentiles over order values per category. Each
prompt above also appears, word for word, in the learner file.

## BI and percentile reasoning

- Aggregate payments by `(order_id, method)` before choosing the greatest
  method; otherwise split rows can produce an arbitrary label.
- Reduce to one payment-method row before joining order items to prevent revenue
  multiplication.
- `PERCENTILE_CONT` interpolates and should be accompanied by observation count
  in a production report.
- Cast its result to numeric before two-argument `ROUND`.

## Validation and limits

- Three-dimensional cube row count should exceed the two-dimensional count on
  this seed.
- Reconcile cube grand-total revenue to source line revenue.
- Primary payment method is a declared reporting policy, not an intrinsic order
  attribute.
- Avoid repeating whole order totals once for every category.

## Ask an AI tutor about this lesson

A tutor can help you reason about why an even-sized group has two candidate
medians, but the cube counts and percentiles must come from your own run. If
you use one, paste this prompt and read the
[study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-56: BI Project, Part 2: Percentiles and CUBE.

I have completed the direct catalog prerequisite: `sql-55`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day56_project4_bi_part2.md
- Answer-free learner SQL: sql/postgres-60day/day56_project4_bi_part2.sql

Key terms to teach in context: Dimensional explosion, Primary payment method, Continuous percentile. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate payments at `(order_id, method)`, select one method by greatest total with a stable tie-breaker, and only then join line revenue. Separately aggregate line value at `(month, category, order_id)` before computing p50/p90; whole order totals would repeat across categories.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-56/ working copy. Never point setup, reset, DDL, or DML
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
