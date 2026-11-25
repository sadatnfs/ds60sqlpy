# Day 41: Complex Aggregations

## How to run this lesson

Open **sql-41** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit your saved copy at
`.learning/sql/sql-41/lesson/workspace/sql/postgres-60day/day41_complex_aggregations.sql`.
The script only reads `orders`, `order_items`, `products` and `customers` from
the course load of `advanced_sql_training`, inside `BEGIN` ... `ROLLBACK`, so a
rerun never changes data. A clean `psql` transcript shows three worked result
sets (category FILTER metrics, country CASE metrics, category name labels) and
then one result set per finished exercise. The 30- and 90-day columns move
with `now()`, but the six categories and seven countries that have orders stay
fixed. Launcher steps, failure recovery and the optional notebook route live in
the [SQL study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) and
its [notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 40; advanced analytic functions](day40_analytic_functions_advanced.md)
- **Artifacts:** [learner SQL](../day41_complex_aggregations.sql) ·
  [solution reasoning](../solutions/day41_solutions.md) ·
  [executable solution](../solutions/day41_solutions.sql)

## A beginner's mental model for this lesson

Every query today collapses many order lines into a few summary rows, so first
ask which rows feed each aggregate. In Example 1 the joins produce one row per
order line. `SUM(oi.quantity)` adds every line in the category, while
`SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days')`
adds only lines whose parent order is recent. Old lines stay in the group for
`total_qty`; they are simply skipped by `qty_30d`. That is the whole point of a
**FILTER clause**: one grouped pass, with each measure choosing its own
population. A `CASE` inside `SUM` (Example 2) gives the same number but hides
the condition inside the expression.

A group can exist while one of its measures has no qualifying input. `SUM`
over zero filtered rows returns `NULL`, whereas `COUNT(*) FILTER (...)`
returns `0`, so decide which one your report means before adding `COALESCE`.
Exercises 3 and 5 add a third idea: `CUBE` and `GROUPING SETS` print several
grains in one result, so each row needs a `GROUPING` label that says which
grain it is. The [logical reading order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
still holds: the joins build line grain, `GROUP BY` collapses it, and each
`FILTER` acts inside its own aggregate.

## Two worked SQL examples

Both excerpts come from the learner script; its third worked query, a
`string_agg(DISTINCT p.name, ', ' ORDER BY p.name)` label per category, is
best read straight from the file.

### Example 1

```sql
SELECT
  p.category,
  SUM(oi.quantity) AS total_qty,
  SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
  SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) FILTER (WHERE o.order_date >= now() - interval '30 days'), 2) AS revenue_30d
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
GROUP BY
  p.category
ORDER BY
  revenue DESC;
```

**How to read it:** The three joins put each order line next to its product category and its
parent order's date. All five measures read the same rows. The two unfiltered
columns (`total_qty`, `revenue`) cover the whole history, and each `FILTER`
narrows only its own aggregate to orders placed in the last 30 or 90 days
relative to `now()`. Revenue is computed per line as
`unit_price * quantity * (1 - discount)`, which is why the query never touches
`orders.total_amount`: that order-level value would repeat once per line after
the join.

**Expected result/shape:** Six rows, one per category (Apparel, Beauty, Books, Electronics, Home,
Sports), ordered by all-time `revenue` from highest to lowest. For each row
`qty_30d <= qty_90d <= total_qty` must hold, because the windows are nested
subsets of the same lines. If a category had no recent lines its `qty_30d`
would print as an empty `NULL`, not `0`. To check one cell, rerun a plain
`SUM(oi.quantity)` for that category with the 30-day condition in `WHERE`.

### Example 2

```sql
SELECT
  c.country,
  SUM(
    CASE WHEN o.status IN ('paid', 'shipped', 'delivered') THEN
      1
    ELSE
      0
    END) AS successful_orders,
  SUM(
    CASE WHEN o.status = 'returned' THEN
      1
    ELSE
      0
    END) AS returned_orders,
  ROUND(SUM(
      CASE WHEN o.status <> 'returned' THEN
        o.total_amount
      ELSE
        0
      END), 2) AS net_revenue
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
GROUP BY
  c.country
ORDER BY
  net_revenue DESC;
```

**How to read it:** Here the grain is one row per order, not per line: `orders` joins only to
`customers`, so `o.total_amount` appears exactly once per order and can be
summed safely. Each `CASE` turns an order into a 1 or 0 (or into its amount or
0), and `SUM` counts or totals those values per country. Statuses `paid`,
`shipped` and `delivered` are successful, `returned` is counted separately, and
`placed` orders fall into neither count but still add to `net_revenue` because
the third `CASE` only excludes `returned`.

**Expected result/shape:** Seven rows, one per country that has orders (AU, CA, DE, FR, GB, IN, US),
sorted by `net_revenue` descending. BR customers exist but have no orders, so
the inner join leaves BR out entirely instead of printing a zero row. Note
that `successful_orders + returned_orders` is smaller than the country's order
count, and the gap is exactly its `placed` orders; that is a useful one-line
reconciliation.

## Learning objectives

- Produce several conditional measures from one controlled fact grain.
- Build deterministic ordered labels after ranking within a partition.
- Generate detail rows, one-dimensional subtotals, and a grand total with
  `CUBE`.
- Use `GROUPING` to identify the grain of every subtotal row without confusing
  a generated subtotal marker with a stored SQL `NULL`.

## Vocabulary and concepts

- **FILTER clause:** a per-aggregate condition written after the aggregate.
- **Conditional aggregate:** a measure calculated only for qualifying rows.
- **Ordered aggregation:** concatenation or collection under a specified order.
- **Grouping set:** one explicit list of columns that defines an aggregate
  grain. `GROUPING SETS` asks PostgreSQL for several such grains in one query.
- **CUBE:** shorthand for every grouping set that can be formed from the listed
  dimensions. Two dimensions produce four levels.
- **GROUPING:** a function evaluated on grouping expressions. It returns `1`
  when an expression was omitted to create the current subtotal and `0` when
  the expression participates in that row's grouping key.
- **Grouping mask:** the integer returned by multi-argument `GROUPING`. Read its
  bits from right to left in the same order as the arguments.

## How to read a two-dimensional CUBE

`CUBE(country, category)` is equivalent to:

```sql fragment
GROUP BY GROUPING SETS (
  (country, category), -- detail
  (country),           -- one country across all categories
  (category),          -- one category across all countries
  ()                   -- grand total
)
```

PostgreSQL encodes which expressions were omitted with
`GROUPING(country, category)`. The rightmost argument, `category`, is the
least-significant bit:

| `grouping_mask` | Included grouping key | Meaning |
|---:|---|---|
| `0` | `country, category` | detail |
| `1` | `country` | country subtotal |
| `2` | `category` | category subtotal |
| `3` | none | grand total |

This mask is a grain label, not a data-cleaning test. A stored `NULL` country
in a detail group still has a country grouping bit of `0`; a generated country
subtotal marker has that bit set to `1`. Test `GROUPING(country)`, not
`country IS NULL`, when you need to distinguish them.

## Worked example / walkthrough

Establish one order-line relation, then calculate 30-day revenue, 90-day
revenue, order count, and customer count in one category group using `FILTER`.
Reconcile each measure with a simpler single-purpose query before trusting the
combined dashboard.

## Exercises

Complete these in the [learner SQL](../day41_complex_aggregations.sql):

1. Build six category metrics with `FILTER`.
   **Inputs/evidence:** For sql-41 Exercise 1, join `orders`, `order_items`, and `products` once in a `lines` CTE (13,085 rows, one per order line) carrying `category`, `order_id`, `customer_id`, `order_date`, `quantity`, and line revenue `unit_price * quantity * (1 - discount)`; every metric is a `FILTER` over that relation with 30-day or 90-day windows anchored at `CURRENT_TIMESTAMP`.
   **Expected result/shape:** For sql-41 Exercise 1, return 6 rows, one per sold category (`Apparel`, `Beauty`, `Books`, `Electronics`, `Home`, `Sports`); the window values move with the load date because the seed dates are relative to it. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
   **Verify:** For sql-41 Exercise 1, confirm 6 rows with unique `category`, `revenue_90d >= revenue_30d` on every row, and `revenue_per_order_30d` within 0.01 of `revenue_30d / orders_30d`; recompute `Books` with a plain `WHERE p.category = 'Books' AND o.order_date >= CURRENT_TIMESTAMP - interval '30 days'` query and match `revenue_30d`, `orders_30d`, and `units_30d`; then, in a rolled-back transaction, insert a product in a new `Garden` category and confirm the result still has 6 rows, because categories come from order lines.
2. List each country's top five products with `string_agg`.
   **Inputs/evidence:** For sql-41 Exercise 2, join `customers`, `orders`, `order_items`, and `products`, sum line revenue at (`country`, `product_id`, `name`) grain in `product_revenue`, rank it with `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)` in `ranked`, and keep ranks 1 to 5 for `string_agg`.
   **Expected result/shape:** For sql-41 Exercise 2, return 7 rows, one per country with orders (`AU`, `CA`, `DE`, `FR`, `GB`, `IN`, `US`; `BR` has no orders), each listing exactly five names in rank order, for example `AU` = `Product 238, Product 207, Product 251, Product 261, Product 243`. The final columns are `country` and `top_five_products`. The final order is `country`.
   **Verify:** For sql-41 Exercise 2, rerun `ranked` alone with `WHERE country = 'AU' AND product_rank <= 5` and match the five `AU` names in order; confirm every country bought 275 distinct products, so no list is short; then add `WHERE o.order_id = 1` inside `product_revenue` and confirm one row whose list has only the order's two products, `Product 79, Product 48`, with no padding.
3. Predict explicit grouping sets versus a two-column `CUBE`.
   **Inputs/evidence:** For sql-41 Exercise 3, build a `lines` CTE of order-line revenue with each line's customer `country` and product `category` (13,085 rows), then aggregate it with `GROUP BY CUBE (country, category)` and label `GROUPING(country, category)` as `grouping_mask` and `grouping_level`.
   **Expected result/shape:** For sql-41 Exercise 3, return 56 rows: 42 detail rows (7 countries times 6 categories, mask `0`), 7 country subtotals (mask `1`), 6 category subtotals (mask `2`), and one grand total (mask `3`) of 2355647.1235. `grouping_mask` is `0` for detail, `1` for a country subtotal, `2` for a category subtotal, and `3` for the grand total. The final columns are `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`. The final order is `grouping_mask, country, category`.
   **Verify:** For sql-41 Exercise 3, count rows per `grouping_mask` (42, 7, 6, 1) and confirm that `revenue` sums to 2355647.1235 within each mask; check one cell such as `AU`/`Apparel` = 54277.4215 against a plain filtered sum; then replace `CUBE` with `GROUPING SETS ((country), (category), ())` and confirm 14 rows, because the 42 country-by-category detail rows are the level that list omits.
4. Build country status/revenue/customer metrics with `FILTER`.
   **Inputs/evidence:** For sql-41 Exercise 4, join `orders` to `customers` (4,362 order rows), group by `c.country`, and compute every measure with `COUNT` or `SUM` plus `FILTER (WHERE o.status = ...)` over the same rows; `status` has five values (`placed`, `paid`, `shipped`, `delivered`, `returned`).
   **Expected result/shape:** For sql-41 Exercise 4, return 7 rows, one per country with orders; `BR` is absent because none of its 62 customers ordered. `AU` shows 613 orders, 123 paid orders, 66338.06 paid revenue, 66707.95 returned revenue, and 62 customers. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
   **Verify:** For sql-41 Exercise 4, confirm `orders` sums to 4362, `paid_orders` to 872, and `paid_revenue` to 478068.36, matching `SELECT count(*), sum(total_amount) FROM orders WHERE status = 'paid'`; then rewrite the join as `customers LEFT JOIN orders` and observe that `BR` appears with `orders = 1` from `COUNT(*)` but `customers = 0`, so a left-join version must count `o.order_id`.
5. Distinguish stored NULLs from subtotal NULLs with `GROUPING`.
   **Inputs/evidence:** For sql-41 Exercise 5, read `customers.country` (500 rows) and append one controlled `NULL::text` row with `UNION ALL` in a `country_input` CTE; group by `GROUPING SETS ((country), ())`, and use `GROUPING(country)` to build `country_label`, `is_subtotal`, and `customers`.
   **Expected result/shape:** For sql-41 Exercise 5, return 10 rows: 8 country rows and one `(stored null)` row with 1 customer, all with `is_subtotal = 0`, plus one `ALL COUNTRIES` row with `is_subtotal = 1` and 501 customers. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
   **Verify:** For sql-41 Exercise 5, confirm exactly one row has `is_subtotal = 1` and that the nine detail `customers` values sum to its 501; confirm `(stored null)` carries `is_subtotal = 0`; then remove the `UNION ALL` branch and confirm 9 rows with a 500 total. `GROUPING` receives the grouped `country` expression; do not try to call `GROUPING(NULL)`.
6. Return a typed empty array for an empty aggregate input.
   **Inputs/evidence:** For sql-41 Exercise 6, read `customers.email` through `array_agg(email) FILTER (WHERE false)`, which sees all 500 rows but aggregates none, and wrap it in `COALESCE(..., '{}'::text[])` so both branches are `text[]`.
   **Expected result/shape:** For sql-41 Exercise 6, return exactly one row with one column, `empty_email_array`, whose value is the non-NULL empty `text[]` value `{}`. There is no customer-level key because the query has no `GROUP BY`.
   **Verify:** For sql-41 Exercise 6, select the uncoalesced filtered `array_agg` and confirm `IS NULL` is true, while the final result satisfies `empty_email_array IS NOT NULL` and `cardinality(empty_email_array) = 0`; then replace the fallback with a bare `ARRAY[]` and confirm the error `cannot determine type of empty array`.

Decide explicitly when an absent measure should be `NULL` or zero.

## Self-check

- Are order and customer counts protected from line-level fanout?
- Is the top-five label order stable under metric ties?
- Can you expand `CUBE(country, category)` into its four explicit grouping
  sets without looking?
- Can you explain why masks `1` and `2` mean different subtotal grains even
  though each prints one NULL dimension?
- If `country` contains a stored NULL, can you prove why
  `GROUPING(country) = 0` for that detail row?
- Why does a scalar aggregate over no qualifying rows return one row, and why
  must the empty-array fallback be typed as `text[]`?

## Next step

Continue to [Day 42; data quality and validation](day42_data_quality_validation.md).

## Deep dive and reference

## What you will learn

- Calculate several conditional metrics in one grouped query with `FILTER`.
- Express equivalent conditional aggregates with `CASE`.
- Build ordered labels with `string_agg`.

## How the learner script uses the current schema

The starter calculates category units and revenue over all history, 30 days, and
90 days by joining `orders`, `order_items`, and `products`. It also reports
successful/returned orders by `customers.country`, then demonstrates
`string_agg(DISTINCT products.name, ...)` by category.

The valid successful status set used by the script is `paid`, `shipped`, and
`delivered`; `returned` is reported separately. Use only the statuses supplied
by the course setup.

## Multi-metric design

- Establish line-item grain before summing net revenue.
- Use `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT customer_id)` when a join
  has expanded each order to multiple item rows.
- Guard every denominator with `NULLIF`.
- Conditional sums can be `NULL` when no row qualifies; decide whether display
  policy should use `COALESCE`.

## Practice map

Exercises 1 and 4 rebuild the two worked shapes with `FILTER`, Exercise 2 ranks
before aggregating, Exercises 3 and 5 make subtotal grain visible with
`GROUPING`, and Exercise 6 isolates the empty-input case. The numbered list
above is the contract; the learner SQL repeats it unchanged.

## Pitfalls and validation

- Applying a global `LIMIT 5` does not produce five products per country; rank
  within country first.
- Do not sum `orders.total_amount` after joining to item rows.
- Add a deterministic tie-break such as `product_id`.
- Validate dashboard totals against a simpler single-metric query before
  trusting the combined report.

## Expanded practice lab

Prompts 3-6 make aggregate grain and subtotal identity explicit. A two-column
`CUBE` emits detail, both one-dimensional subtotals, and a grand total; the
listed `GROUPING SETS` intentionally omits detail. Use `GROUPING(column)` rather
than `column IS NULL` to detect a subtotal.

`FILTER` keeps several metric definitions readable in one grouped query.
Aggregates over no input rows often return NULL, so `COALESCE(array_agg(...),
'{}'::text[])` needs an explicit type matching the aggregate result.

## Ask an AI tutor about this lesson

The tutor is optional; the guide, the learner SQL and PostgreSQL are enough.
To use one, paste this prompt (see
[the study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)):

```text
Tutor me through sql-41: Complex Aggregations: FILTER, String Aggregation, and CUBE.

I have completed the direct catalog prerequisite: `sql-40`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day41_complex_aggregations.md
- Answer-free learner SQL: sql/postgres-60day/day41_complex_aggregations.sql

Key terms to teach in context: FILTER clause, Conditional aggregate, Ordered aggregation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using `FILTER`. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-41/ working copy. Never point setup, reset, DDL, or DML
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
