# Day 27: Pivoting/Unpivoting: Crosstabs and Conditional Aggregation (Companion Guide)

## How to run this lesson

Open `./classroom`, select **sql-27** and choose **Whole SQL lesson (psql)**.
The classroom runs
`.learning/sql/sql-27/lesson/workspace/sql/postgres-60day/day27_pivot_unpivot.sql`
against `advanced_sql_training` between `BEGIN` and `ROLLBACK`. Both examples
filter on the current UTC year, so their numbers change with the date you
run them and the date your fixture was loaded. Steps shared by every lesson
are in [Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

A notebook is handy for printing the wide and long forms side by side
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-27
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 26; CTEs with window functions](day26_ctes_with_windows.md)
- **Artifacts:** [learner SQL](../day27_pivot_unpivot.sql) ·
  [solution reasoning](../solutions/day27_solutions.md) ·
  [executable solution](../solutions/day27_solutions.sql)

## A beginner's mental model for this lesson

A pivot turns values in a column into separate columns; an unpivot turns
columns back into rows. PostgreSQL has no `PIVOT` keyword, so both are built
from ordinary pieces:

- **Pivot:** group by the row label and write one aggregate per output
  column, each with its own `FILTER (WHERE ...)`. Example 1 groups by
  `p.category` and keeps three month columns, so six categories give six
  rows and three numbers each.
- **Unpivot:** `CROSS JOIN LATERAL (VALUES ...)` emits one row per listed
  column for every input row. Example 2 builds a two-column `wide` relation
  and turns each category back into a `jan` row and a `feb` row, 12 rows in
  total.

The pivot has a cost: you must know the column list when you write the
query. A new status or category does not appear as a new column; it is
simply not counted unless you also keep a total column. When the list is
open-ended, return the values as data instead, for example as a JSON object
(the fifth answer).

The second rule is about missing values. `COUNT(*) FILTER (...)` returns 0
when no row matches, but `SUM(x) FILTER (...)` returns `NULL`. Whether a
`NULL` cell should be shown as 0 is a reporting decision, not something the
SQL can decide for you.

## Two worked SQL examples

### Example 1

```sql
SELECT
  p.category,
  SUM(oi.quantity) FILTER (WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 1) AS jan_qty,
  SUM(oi.quantity) FILTER (WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 2) AS feb_qty,
  SUM(oi.quantity) FILTER (WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 3) AS mar_qty
FROM
  order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
WHERE
  o.order_date >= (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'UTC')
  AND o.order_date < (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '1 year') AT TIME ZONE 'UTC'
GROUP BY
  p.category
ORDER BY
  p.category;
```

**How to read it:** The `WHERE` clause keeps only orders from the
current UTC year, then each `FILTER` picks one month from what is left.
`EXTRACT(MONTH ...)` is applied to `order_date AT TIME ZONE 'UTC'`, so an
order placed late on 31 January in another time zone still counts as
January if it was January in UTC.

**Expected result/shape:** Six rows, Apparel to Sports, with
`jan_qty`, `feb_qty` and `mar_qty`. Run in 2026, Apparel showed 195, 240
and 256, and the 18 cells added to 4,342 units, the same as a plain
`SUM(quantity)` over January to March. Early in a year, the later columns are
`NULL` because no order has been placed in those months yet.

### Example 2

```sql
WITH source AS (
  SELECT
    p.category,
    EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC')::integer AS month_number,
    oi.quantity
  FROM
    order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
  WHERE
    o.order_date >= (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'UTC')
    AND o.order_date < (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '1 year') AT TIME ZONE 'UTC'
),
wide AS (
  SELECT
    category,
    SUM(quantity) FILTER (WHERE month_number = 1) AS jan_qty,
  SUM(quantity) FILTER (WHERE month_number = 2) AS feb_qty
FROM
  source
GROUP BY
  category
)
SELECT
  wide.category,
  month_value.month_name,
  month_value.quantity
FROM
  wide
  CROSS JOIN LATERAL (
    VALUES ('jan', wide.jan_qty),
      ('feb', wide.feb_qty)) AS month_value (month_name, quantity)
ORDER BY
  wide.category,
  month_value.month_name;
```

**How to read it:** `source` is detail rows, `wide` pivots them to one
row per category, and the lateral `VALUES` list unpivots `jan_qty` and
`feb_qty` back to rows. The literal labels `'jan'` and `'feb'` become the
`month_name` column, and the column the label came from becomes `quantity`.

**Expected result/shape:** 12 rows, two per category. Inside each
category `feb` comes before `jan` because `month_name` is text and sorts
alphabetically; order by a month number if you need calendar order. In 2026
the first rows were Apparel `feb` 240 and Apparel `jan` 195.

## Learning objectives

- Pivot controlled categories with portable conditional aggregation.
- Normalize wide values to a typed long-form relation.

## Vocabulary and concepts

- **Pivot:** turn row values into separate output columns.
- **Unpivot:** turn several columns into key/value rows.
- **Conditional aggregation:** aggregates restricted by `FILTER` or `CASE`.

## Worked example / walkthrough

At one row per quarter, calculate
`SUM(amount) FILTER (WHERE method = 'card')` and parallel columns for the other
known methods. Reconcile the sum of pivot columns to the long-form payment total
and decide whether absent combinations display as `NULL` or zero.

## Practice assumptions and review method

- **Focus:** Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
- **Assumptions:** PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
- **Failure to watch for:** Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.
- **Review loop:** for every pivot, add the pivoted columns across one row
  and compare with an unfiltered total; for every unpivot, check that the
  row count equals input rows times listed columns.

## Exercises

Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.

Before writing each pivot, list the values that will become
columns and decide what the report should show for a value that never
occurs. The two unpivot answers use small inline samples, so you can predict
every output row by hand.

1. **Query writing:** Pivot order counts by status into one summary row.
   **Progressive hint:** Use one filtered count per known status and keep an all-orders denominator.
   **Inputs/evidence:** For sql-27 Exercise 1, read from `orders` and pivot the status counts into one row, with one `COUNT(*) FILTER (WHERE status = ...)` column per known status plus `all_orders`.
   **Expected result/shape:** For sql-27 Exercise 1, expected output: Exactly one row. The final columns are `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`.
   **Verify:** For sql-27 Exercise 1, confirm one row with `placed_orders` 873, `paid_orders` 872, `shipped_orders` 873, `delivered_orders` 872, `returned_orders` 872, and `all_orders` 4362; the five status columns must add up to `all_orders`, or an unknown status exists.
2. **Query writing:** Pivot customer counts for US, CA, GB, and DE by segment.
   **Progressive hint:** Group at segment grain and use filtered counts for known country columns.
   **Inputs/evidence:** For sql-27 Exercise 2, read the 500 rows of `customers`, group by `segment`, and turn four countries into columns with `COUNT(*) FILTER (WHERE country = ...)`; `all_customers` counts every row in the segment, including the 312 customers in AU, BR, FR, and IN.
   **Expected result/shape:** For sql-27 Exercise 2, expected output: exactly 4 rows of 125 customers each, and every segment maps to one country in this seed: `gold` has 63 GB customers, `platinum` 63 DE, `silver` 63 CA, and `standard` 63 US, with 0 in the other three columns. The final columns are `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`. The final order is `c.segment NULLS LAST`.
   **Verify:** For sql-27 Exercise 2, confirm `all_customers` adds to 500 and that each country column adds to its `SELECT COUNT(*) FROM customers WHERE country = ...` count of 63; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET segment = NULL WHERE customer_id = 1` (a US customer) and confirm a fifth row with a NULL segment appears last with 1 US customer, while `standard` drops to 62 and 124.
3. **Query writing:** Unpivot a wide quarterly sample into quarter/amount rows.
   **Progressive hint:** Use a lateral `VALUES` relation with one output row per source column.
   **Inputs/evidence:** For sql-27 Exercise 3, no table is read: the `wide` CTE holds two `VALUES` rows, company A with 10, 20, 30, 40 and company B with 5, NULL, 15, 25, and `CROSS JOIN LATERAL (VALUES ...)` turns each row's four quarter columns into four `(quarter, amount)` rows.
   **Expected result/shape:** For sql-27 Exercise 3, expected output: exactly 8 rows, four per company, with B `Q2` kept as a row whose `amount` is NULL. The final columns are `company`, `quarter`, and `amount`. The final order is `w.company, unpivoted.quarter`.
   **Verify:** For sql-27 Exercise 3, confirm 8 rows, 4 per company, that `SUM(amount)` is 100 for A and 45 for B, and that exactly one row has `amount IS NULL`; adding `WHERE unpivoted.amount IS NOT NULL` would return 7 rows and lose the fact that B reported nothing for `Q2`.
4. **Prediction:** Compare a missing pivot combination with a real zero and preserve the distinction.
   **Progressive hint:** Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
   **Inputs/evidence:** For sql-27 Exercise 4, read the 10000 `expenses` rows (5 categories, 2000 each, dated over the two years before the load), group by `category`, and sum only January rows with `FILTER (WHERE EXTRACT(MONTH FROM expense_date) = 1)`, once raw and once wrapped in `COALESCE(..., 0)`.
   **Expected result/shape:** For sql-27 Exercise 4, expected output: exactly 5 rows; every category has January rows on this load (164 to 192 rows across two Januaries), so both columns match, for example COGS 856904.40 and Marketing 972676.11. The final columns are `category`, `january_observed_amount`, and `january_reported_zero_if_absent`. The final order is `e.category`.
   **Verify:** For sql-27 Exercise 4, confirm each category's January row count with `SELECT category, COUNT(*) FROM expenses WHERE EXTRACT(MONTH FROM expense_date) = 1 GROUP BY category`; then, inside `BEGIN ... ROLLBACK`, insert `('Legal', 100, '2026-03-01')` and `('Travel', 0, '2026-01-15')` and confirm Legal returns NULL and 0 (no January rows) while Travel returns 0.00 and 0.00 (a real zero).
5. **Debugging:** Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
   **Progressive hint:** Aggregate category/value pairs into data values so the result schema remains stable.
   **Inputs/evidence:** For sql-27 Exercise 5, read `orders`, `order_items`, and `products`, round net item revenue per UTC month and `category` in `category_month`, then fold each month's six rows into one JSONB value with `jsonb_object_agg(category, revenue ORDER BY category)`.
   **Expected result/shape:** For sql-27 Exercise 5, expected output: one row per UTC month (46 on this load), each object holding all 6 category keys; the first month is `{"Home": 30.20, "Books": 279.76, "Beauty": 94.00, "Sports": 175.41, "Apparel": 407.05, "Electronics": 216.84}`, because JSONB stores keys shorter first, not in the `ORDER BY` order. The final columns are `month_start`, and `revenue_by_category`. The final order is `month_start`.
   **Verify:** For sql-27 Exercise 5, confirm every object has 6 keys with `jsonb_object_keys`, and that summing `jsonb_each_text` values over all months gives 2355647.24, slightly above the unrounded 2355647.12 because each cell was rounded first; a missing key such as `revenue_by_category -> 'Toys'` returns NULL, and `jsonb_object_agg` over `VALUES ('a', 1), (NULL, 2)` fails with `field name must not be null`.
6. **Extension:** Round-trip a wide sample to long form and back, verifying values and NULLs.
   **Progressive hint:** Unpivot with lateral values, then use conditional aggregation keyed by company.
   **Inputs/evidence:** For sql-27 Exercise 6, no table is read: the `wide` CTE holds A with 10 and 20 and B with NULL and 5; `long` unpivots it into four `(company, quarter, amount)` rows, and the outer query pivots back with `MAX(amount) FILTER (WHERE quarter = ...)` grouped by `company`.
   **Expected result/shape:** For sql-27 Exercise 6, expected output: exactly 2 rows, A with 10 and 20 and B with NULL and 5, identical to `wide`. The final columns are `company`, `q1`, and `q2`. The final order is `company`.
   **Verify:** For sql-27 Exercise 6, confirm `long` has 4 rows with one NULL `amount`, and that both `SELECT * FROM wide EXCEPT SELECT ...` and the reverse return 0 rows, since `EXCEPT` treats the two NULLs as equal; then pivot `VALUES ('A', 'Q1', 10), ('A', 'Q1', 99), ('A', 'Q2', 20)` and confirm `q1` shows 99, because `MAX` silently hides a duplicate quarter that a `COUNT(*)` of 3 would reveal.

## Common mistakes and how to recover

- **Assuming the pivot adds up.** The segment pivot lists only US, CA, GB
  and DE, so each segment's four columns add to 63 while `all_customers` is
  125. The other 62 customers live in a country without a column. Keep a
  total column so the gap is visible.
- **Mixing up `COUNT` and `SUM` under `FILTER`.** A filtered `COUNT` gives 0
  when nothing matches, while a filtered `SUM` gives `NULL`. Only add
  `COALESCE(..., 0)` when the report really treats no data as zero.
- **Losing the year in `EXTRACT(MONTH ...)`.** The expense data covers two
  years, so a January column built with `EXTRACT(MONTH FROM expense_date) = 1`
  can add two Januaries together; a late-2026 load had 425 and 424 rows. Filter or
  group by year too when that matters.
- **Incompatible types in `VALUES`.** Every column listed in one lateral
  `VALUES` must share a type. `VALUES ('Q1', 1), ('Q2', 'x')` fails with
  `invalid input syntax for type integer: "x"`; cast to a common type first.
- **Expecting `jsonb` to keep key order.** `jsonb_object_agg(... ORDER BY
  category)` still prints keys shortest first (`Home`, `Books`, `Beauty`, and
  so on), because `jsonb` stores keys in its own order. Use `json_object_agg`
  if printed order matters.
- For general recovery steps, see
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Is the category domain controlled enough for fixed output columns?
- Do the wide and long forms reconcile without silently changing types?

## Next step

Continue to [Day 28; JSONB and XML](day28_json_xml.md).

## Deep dive and reference

Learning objectives
- Build pivot tables from row-form data using two approaches in Postgres
  - Conditional aggregation (portable SQL)
  - tablefunc.crosstab (extension) for tidy pivot syntax
- Unpivot wide tables back to long form for analysis

Why this matters
Reports often require metrics by columns (months across columns, categories as columns). Knowing when to pivot/unpivot keeps data pipelines flexible and analytics straightforward.

Core concepts and deep dive
- Conditional aggregation (portable)
  - SELECT key, SUM(CASE WHEN bucket='A' THEN val END) AS a, ... GROUP BY key
  - Pros: no extension; dynamic columns require generating SQL
  - Cons: verbose for many buckets
- crosstab (tablefunc)
  - CREATE EXTENSION IF NOT EXISTS tablefunc;
  - crosstab(text source_sql, text category_sql) → returns setof record with specified column layout
  - Requires declaring the output column types (key, val for each category)
  - Extension installation requires sufficient database privileges; the
    portable course answer does not depend on it
  - Pros: concise; Cons: requires predeclared categories (static schema) or dynamic SQL
- Unpivot
  - Use UNION ALL over columns or use jsonb_each/text arrays to normalize wide to long
  - Example pattern: SELECT id, 'jan' AS month, jan_val AS val FROM t UNION ALL SELECT id, 'feb', feb_val FROM t ...
  - For many columns, convert row to JSON and jsonb_each_text to key/value rows

Design decisions
- For dashboards with fixed categories/months, crosstab is ergonomic
- For ad-hoc analysis or dynamic categories, prefer conditional aggregates or generate SQL in the application

Pitfalls
- crosstab requires sorted input and category queries; mismatches yield misaligned columns
- NULLs vs zeroes: decide whether to COALESCE NULL to 0 for metrics
- Unpivoting monetary/numeric columns: ensure data types are preserved

Further reading
- tablefunc: https://www.postgresql.org/docs/17/tablefunc.html
- Crosstab examples: https://wiki.postgresql.org/wiki/Tablefunc

## Ask an AI tutor about this lesson

A tutor can generate small wide tables for you to unpivot by hand,
which is the quickest way to practice the lateral `VALUES` pattern
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-27: Pivoting and Unpivoting.

I have completed the direct catalog prerequisite: `sql-26`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day27_pivot_unpivot.md
- Answer-free learner SQL: sql/postgres-60day/day27_pivot_unpivot.sql

Key terms to teach in context: Pivot, Unpivot, Conditional aggregation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At one row per quarter, calculate `SUM(amount) FILTER (WHERE method = 'card')` and parallel columns for the other known methods. Reconcile the sum of pivot columns to the long-form payment total and decide whether absent combinations display as `NULL` or zero.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-27/ working copy. Never point setup, reset, DDL, or DML
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
