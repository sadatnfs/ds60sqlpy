# Day 55: Complex BI Project, Part 1: Drill-downs

## How to run this lesson

Open **sql-55** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit your saved copy at
`.learning/sql/sql-55/lesson/workspace/sql/postgres-60day/day55_project4_bi_part1.sql`.
It needs only the course tables in `advanced_sql_training` (`orders`,
`customers`, `order_items`, `products` and `payments`); the file wraps every
query in `BEGIN` ... `ROLLBACK`, so it leaves nothing behind. A clean `psql`
transcript prints the four-level `ROLLUP` report, the 210-row top-five product
list and then one result per finished exercise. Month buckets follow the
current date, so the first report's row count drifts slightly between runs
while the country and category totals do not. Launcher steps and recovery are
in the [SQL study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom);
the notebook alternative is in its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 54; warehouse aggregates](day54_project3_dwh_part3_aggregations.md) From Day 54 you need the habit of computing revenue at line grain before any rollup, so subtotals add up to the same grand total.
- **Artifacts:** [learner SQL](../day55_project4_bi_part1.sql) ·
  [solution reasoning](../solutions/day55_solutions.md) ·
  [executable solution](../solutions/day55_solutions.sql)

## A beginner's mental model for this lesson

A BI report usually wants totals at several levels at once: each country and
category, each country, and everything. `GROUP BY ROLLUP (country, category)`
asks PostgreSQL for exactly those three **grouping sets** in one pass, and it
fills the column that a level leaves out with `NULL`. That `NULL` is generated,
not stored, so the lesson pairs every rolled-up column with `GROUPING(column)`,
which is `1` when the column was left out and `0` when it is a real value.
`CUBE (country, category)` adds the fourth set, category without country.

The second idea is dimension hygiene. Example 1 adds payment method as a
dimension, but 347 orders were paid with two different methods, so joining
`payments` straight onto order lines would count those lines twice. The
`primary_payment_method` CTE first reduces payments to one method per order
(largest amount wins, method name breaks ties) and labels the 873 `placed`
orders as `unpaid`. Only then is it safe to roll up. Read every query with the
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
and ask what one row of each CTE represents before the `GROUP BY` collapses it.

## Two worked SQL examples

Both excerpts come from the learner script and run in order.

### Example 1

```sql
WITH payment_by_method AS (
  SELECT
    order_id,
    method,
    SUM(amount) AS method_amount
  FROM
    payments
  GROUP BY
    order_id,
    method
),
primary_payment_method AS (
  SELECT
    order_id,
    method
  FROM (
    SELECT
      order_id,
      method,
      ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY method_amount DESC,
        method) AS method_rank
  FROM
    payment_by_method) ranked_methods
  WHERE
    method_rank = 1
),
line AS (
  SELECT
    c.country,
    p.category,
    COALESCE(pm.method, 'unpaid') AS payment_method,
    date_trunc('month', o.order_date)::date AS month,
    (oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue,
    oi.quantity AS qty
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN primary_payment_method pm ON pm.order_id = o.order_id
)
SELECT
  country,
  category,
  payment_method,
  month,
  ROUND(SUM(revenue), 2) AS revenue,
  SUM(qty) AS units,
  GROUPING (country) AS g_country,
  GROUPING (category) AS g_category,
  GROUPING (payment_method) AS g_method,
  GROUPING (month) AS g_month
FROM
  line
GROUP BY
  ROLLUP (country, category, payment_method, month)
ORDER BY
  country NULLS FIRST,
  category NULLS FIRST,
  payment_method NULLS FIRST,
  month NULLS FIRST;
```

**How to read it:** `payment_by_method` sums payments per (order, method), the inner
`ROW_NUMBER` keeps the method with the largest amount, and `line` attaches that
single method (or `unpaid`) to every order line together with country,
category, month and line revenue. `ROLLUP (country, category, payment_method,
month)` then produces five levels, from full detail down to the grand total,
and the four `GROUPING` columns tell you which level each row is.

**Expected result/shape:** About six thousand rows (the exact count depends on how many months the data
spans today). Because the sort uses `NULLS FIRST`, the first row is the grand
total, 2,355,647.12 revenue and 39,257 units with all four flags at `1`, then
AU's country subtotal of 330,947.70 with `g_country = 0` and the other flags
at `1`. A row with `g_month = 1` is a subtotal over all months, never "unknown
month".

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
    RANK() OVER (PARTITION BY country,
      category ORDER BY revenue DESC) AS rnk
  FROM
    prod_rev
)
SELECT
  *
FROM
  ranked
WHERE
  rnk <= 5
ORDER BY
  country,
  category,
  rnk;
```

**How to read it:** `prod_rev` collapses lines to one row per (country, category, product), and
`RANK()` numbers products inside each (country, category) pair by revenue.
Filtering `rnk <= 5` happens in the outer query because a window result cannot
be used in the `WHERE` of the same `SELECT`.

**Expected result/shape:** 210 rows on the course data: 7 countries with orders times 6 categories times
5 products. AU Apparel starts with Product 271 at 2,646.48. `RANK` gives tied
products the same rank, so a tie at fifth place would add a sixth row to that
group; Exercise 5 shows the deterministic fix.

## Learning objectives

- Generate hierarchical subtotal levels with `ROLLUP` and distinguish them from
  all-combination `CUBE` output.
- Rank deterministic top products within several dimensions.

## Vocabulary and concepts

- **ROLLUP:** hierarchical grouping sets from detail through grand total.
- **CUBE:** every grouping-key subset for the supplied dimensions.
- **GROUPING flag:** an indicator separating generated subtotal `NULL`s from
  data `NULL`s.

## Worked example / walkthrough

Compare `ROLLUP(country, category)` with `CUBE(country, category)`. Both include
detail, country subtotal, and grand total; `CUBE` also adds category-only
subtotals. Use `GROUPING(country)` and `GROUPING(category)` to label each level,
then reconcile the grand total with source line revenue.

## Exercises

Complete these in the [learner SQL](../day55_project4_bi_part1.sql):

1. Replace `ROLLUP` with `CUBE` and compare row counts.
   **Inputs/evidence:** For sql-55 Exercise 1, join `orders`, `customers`, `order_items`, and `products` into one revenue line per order item (13,085 lines carrying `country` and `category`), group those lines once with `ROLLUP (country, category)` and once with `CUBE (country, category)`, and count the rows each grouping produces.
   **Expected result/shape:** For sql-55 Exercise 1, expected output: one row with `rollup_row_count` 50 and `cube_row_count` 56. Both share the 42 country and category detail rows, the 7 country subtotals, and the grand total; the 6 extra `CUBE` rows are the category-only subtotals. BR has no orders, so it appears in neither grouping.
   **Verify:** For sql-55 Exercise 1, rebuild both counts from distinct values: 42 distinct (country, category) pairs plus 7 countries plus 1 total gives 50, and adding the 6 categories gives 56. In a rolled-back transaction, give BR customer 8 one order with a single Apparel line: both counts rise by 2 (52 and 58), one BR detail row and one BR subtotal, while the category-only subtotal count stays 6.
   **Data check:** On the course data the counts are 50 and 56. Both outputs share the 42 country/category detail rows, the 7 country subtotals and the grand total; the six extra cube rows are the category-only subtotals (Apparel, Beauty, Books, Electronics, Home, Sports across all countries). BR has no orders, so it never appears in either grouping.
2. Add status to an exact top-five drill-down.
   **Inputs/evidence:** For sql-55 Exercise 2, sum line revenue (`unit_price * quantity * (1 - discount)`) per `country`, `category`, `status`, `product_id`, and `name` (7,566 product rows), then number the products inside each (country, category, status) group with `ROW_NUMBER()` ordered by `revenue DESC, product_id` and keep numbers 1 to 5.
   **Expected result/shape:** For sql-55 Exercise 2, expected output: 1,050 rows, exactly five for each of the 210 (country, category, status) groups (7 countries, 6 categories, 5 statuses, each group holding 30 to 42 products), with columns `country`, `category`, `status`, `product_id`, `name`, `revenue` (rounded to 2 places), and `product_rank`. The final order is `country, category, status, product_rank`; the first group is AU, Apparel, `delivered`, led by product 241 at 793.36.
   **Verify:** For sql-55 Exercise 2, check that AU, Apparel, `delivered` lists products 241, 223, 163, 121, and 97 (793.36 down to 727.36), with product 109 sixth at 651.77, and that no (country, category, status, `product_id`) repeats. In a rolled-back transaction, add a 150.00 line for product 109 to AU order 47 (delivered): product 109 moves to rank 1 at 801.77, product 97 drops out, and the group still returns five rows.
   **Data check:** Expect 1,050 rows, because every one of the 210 (country, category, status) groups (7 countries, 6 categories, 5 statuses) has at least five products. The first group in sort order is AU, Apparel, `delivered`, led by product 241 at 793.36. If one group returned six rows, look for a `RANK` or a missing `product_id` tie-breaker.
3. Predict `ROLLUP(country, category, month)` grouping sets.
   **Inputs/evidence:** For sql-55 Exercise 3, first write down the grouping sets of `ROLLUP (country, category, month)` (4 sets, from full detail to the grand total) and of `CUBE` on the same columns (8 sets), then run `ROLLUP (country, category)` over the order-item revenue lines and expose `GROUPING (country, category)` as `grouping_mask`.
   **Expected result/shape:** For sql-55 Exercise 3, expected output: 50 rows with columns `country`, `category`, `revenue`, and `grouping_mask`, ordered by `grouping_mask, country, category`: 42 detail rows with mask 0 (AU Apparel 54,277.4215), 7 country subtotals with mask 1 (AU 330,947.6960), and 1 grand total with mask 3 (2,355,647.1235). No row has mask 2, because `ROLLUP` never totals a category across countries.
   **Verify:** For sql-55 Exercise 3, count the rows per mask (42, 7, 1) and confirm that the 7 mask 1 rows add up to the mask 3 total of 2,355,647.1235. In a rolled-back transaction, give BR customer 8 one order with a 20.00 Apparel line: the result grows to 52 rows (43 with mask 0, 8 with mask 1), and BR shows 20.0000 at both the detail and subtotal level.
   **Data check:** Expect 50 rows: 42 with mask `0`, 7 with mask `1` and 1 with mask `3`. The AU Apparel detail row shows 54,277.42 (unrounded in the solution), and the single mask `3` row must match the 2,355,647.12 grand total from Example 1. Ask yourself why no row can carry mask `2` under `ROLLUP`.
4. Label levels with PostgreSQL's `GROUPING(country, category)` bit mask.
   **Inputs/evidence:** For sql-55 Exercise 4, group the same order-item revenue lines with `ROLLUP (country, category)` and return `GROUPING (country, category)` as `level_id`, plus a `CASE` on that same mask that maps 0, 1, and 3 to `level_name` values 'country/category detail', 'country subtotal', and 'grand total'.
   **Expected result/shape:** For sql-55 Exercise 4, expected output: the same 50 rows as Exercise 3 with columns `level_id`, `level_name`, `country`, `category`, and `revenue`, ordered by `level_id, country, category`: 42 rows at level 0, 7 at level 1, and 1 at level 3, and no `NULL` `level_name`.
   **Verify:** For sql-55 Exercise 4, count rows per `level_id` and `level_name` (42, 7, 1) and confirm each `level_id` maps to exactly one name. In a rolled-back transaction, run `ALTER TABLE products ALTER COLUMN category DROP NOT NULL` and set product 241's category to `NULL`: level 0 grows to 49 rows, 7 of them with a stored `NULL` category, and all 7 still say 'country/category detail' because the label reads the mask, not the column.
   **Data check:** The labels sit on the same 50 rows as Exercise 3: 42 rows named for country/category detail, 7 country subtotals and 1 grand total. Sorting by the level id puts all detail rows first, so a correct run ends with the subtotals and the total, and no label is ever `NULL`.
5. Use deterministic `ROW_NUMBER` for exactly five results.
   **Inputs/evidence:** For sql-55 Exercise 5, sum order-item revenue per `country`, `product_id`, and `name` (1,925 rows, 275 products in each of 7 countries), then number the products inside each country with `ROW_NUMBER()` ordered by `revenue DESC, product_id` as `position` and keep positions 1 to 5.
   **Expected result/shape:** For sql-55 Exercise 5, expected output: 35 rows, one per country and `position` 1 to 5, with columns `country`, `product_id`, `name`, `revenue`, and `position`. The final order is `country, position`; AU starts with product 238 at 3,319.3310, followed by products 207, 251, 261, and 243 (2,692.5745).
   **Verify:** For sql-55 Exercise 5, confirm that no (country, `product_id`) repeats and that AU product 233 sits sixth at 2,684.2590. In a rolled-back transaction, add a line for product 233 to AU order 46 with `unit_price` 166.31 and `discount` 0.95 (8.3155): products 233 and 243 tie at 2,692.5745, `RANK() <= 5` now returns 36 rows, and `ROW_NUMBER` still returns 35, giving position 5 to product 233 because it has the lower `product_id`.
   **Data check:** Expect 35 rows, exactly five per country for the seven countries with orders, and a position column running 1 to 5 in each. The AU list starts with product 238 at 3,319.33. The rows are products, so check for duplicate (country, product) pairs rather than duplicate orders.
6. Separate real unknown members from generated subtotals.
   **Inputs/evidence:** For sql-55 Exercise 6, read the 500 `customers` rows and group them with `GROUPING SETS ((country), ())`, returning `GROUPING (country)` as `is_generated_total` and a `display_country` that says 'ALL' only when that flag is 1 and '(unknown member)' for a stored `NULL` country.
   **Expected result/shape:** For sql-55 Exercise 6, expected output: 9 rows with columns `display_country`, `is_generated_total`, and `customers`, ordered by `is_generated_total, display_country`: eight countries including BR (62 or 63 customers each, flag 0), then `ALL` with 500 and flag 1.
   **Verify:** For sql-55 Exercise 6, compare each country row with `SELECT country, COUNT(*) FROM customers GROUP BY country` and confirm the eight counts add up to the `ALL` row. `country` is `NOT NULL` (default 'US'), so in a rolled-back transaction run `ALTER TABLE customers ALTER COLUMN country DROP NOT NULL` and insert one customer with a `NULL` country: the result has 10 rows, a '(unknown member)' row with 1 customer and flag 0, and `ALL` at 501.
   **Data check:** Expect nine rows: eight countries, BR included because this query reads `customers` rather than orders, each with 62 or 63 customers, plus one `ALL` row of 500. The course data has no stored `NULL` country, and `country` is declared `NOT NULL`, so the unknown label only appears if a transaction first drops that constraint and then adds such a customer; that run returns 10 rows and an `ALL` of 501.

Test one real NULL/unknown dimension value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A raw payment join fans out
  split-payment orders. Keep the declared primary method policy, or document a
  different allocation, before using that dimension.
- **Grand total larger than the line revenue:** you joined `payments` before
  reducing it to one method per order. Compare `SUM(revenue)` from `line` with
  a plain line-revenue sum; they must both be 2,355,647.12 (rounded).
- **Subtotal rows treated as missing data:** a blank `country` with
  `g_country = 1` is the generated total; test `GROUPING(...)`, never
  `country IS NULL`, before labeling it.
- **Six rows in a top-five group:** `RANK` repeats a rank on ties. Use
  `ROW_NUMBER()` with `product_id` as the last sort key when the report
  promises exactly five.
- General recovery steps (fanout, unexpected `NULL`, `psql` stopping) are in
  the [study guide](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Is payment method reduced to one declared row per order before joining lines?
- Does top-five ranking partition by every requested dimension and break ties
  deterministically?

## Next step

Continue to [Day 56; percentiles and CUBE](day56_project4_bi_part2.md).

## Deep dive and reference

## Project focus

- Generate hierarchical subtotals with `ROLLUP`.
- Compare hierarchical subtotal rows with all-combination `CUBE`.
- Rank top products within country, category, and order status.

## How the learner script uses the current schema

The starter builds line revenue from `orders`, `customers`, `order_items`, and
`products`, chooses one primary payment method per order by greatest paid
amount (method name breaks ties), and rolls up country, category, payment
method, and month. Unpaid orders receive the `unpaid` label.
`GROUPING(column)` distinguishes subtotal nulls from detail values.

It separately ranks product revenue within `(country, category)`.

## Practice map

Exercises 1, 3 and 4 explore which grouping sets `ROLLUP` and `CUBE` emit and
how to name them, Exercises 2 and 5 make the top-five drill-down exact, and Exercise 6 keeps a stored unknown apart from the generated `ALL` row. The
numbered list above is the contract, repeated unchanged in the learner SQL.

## BI reasoning

- `ROLLUP(a, b)` returns `(a,b)`, `(a)`, and grand total.
- `CUBE(a, b)` also returns the `(b)` subtotal.
- Use `GROUPING` flags when real dimension nulls are possible.
- Aggregate revenue before ranking; use `ROW_NUMBER` plus `product_id` for
  exactly five deterministic results.

## Validation and limits

- A raw payment join fans out split-payment orders. Keep the declared primary
  method policy, or document a different allocation, before using that dimension.
- Cube row counts grow rapidly with dimensions and distinct values.
- Reconcile grand-total cube revenue to source line revenue.

## Ask an AI tutor about this lesson

Ask a tutor to predict which subtotal rows `CUBE` adds before you run it,
then let PostgreSQL settle the argument. To use one, paste this prompt and
read the [study guide's tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional):

```text
Tutor me through sql-55: BI Project, Part 1: Drill-Downs and Subtotals.

I have completed the direct catalog prerequisite: `sql-54`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day55_project4_bi_part1.md
- Answer-free learner SQL: sql/postgres-60day/day55_project4_bi_part1.sql

Key terms to teach in context: ROLLUP, CUBE, GROUPING flag. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare `ROLLUP(country, category)` with `CUBE(country, category)`. Both include detail, country subtotal, and grand total; `CUBE` also adds category-only subtotals. Use `GROUPING(country)` and `GROUPING(category)` to label each level, then reconcile the grand total with source line revenue.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-55/ working copy. Never point setup, reset, DDL, or DML
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
