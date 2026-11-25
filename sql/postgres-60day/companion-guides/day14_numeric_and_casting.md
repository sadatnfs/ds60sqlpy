# Day 14: Numeric Types, Casting, and Precision (Companion Guide)

## How to run this lesson

From the repository root, start `./classroom`, select PostgreSQL and **sql-14**, then choose **Whole SQL lesson (psql)**. The file connects to `advanced_sql_training`, sets `search_path` to `training` inside a transaction that ends in `ROLLBACK`, and prints two results: the 50 largest orders with their totals rounded and cast to whole numbers, and the six product categories with units sold and the average net price per unit.

Your working copy lives at
`.learning/sql/sql-14/lesson/workspace/sql/postgres-60day/day14_numeric_and_casting.sql`.
Try adding `pg_typeof(round(total_amount, 0))` and `pg_typeof(cast(total_amount AS int))` to the first `SELECT`. The two columns print the same digits, but one is `numeric` and the other `integer`.

When `./classroom` will not start or cannot reach the database, the study guide's [classroom launch notes](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) cover the usual causes. A [notebook alternative](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is documented for contributors.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 13; date, time, and time zones](day13_date_time_functions.md)
- **Artifacts:** [learner SQL](../day14_numeric_and_casting.sql) ·
  [solution reasoning](../solutions/day14_solutions.md) ·
  [executable solution](../solutions/day14_solutions.sql)

## A beginner's mental model for this lesson

Every value in PostgreSQL has a type, and the type of an expression decides how its arithmetic works. This lesson meets three families. An **integer** holds whole numbers; `quantity` in `order_items` is one. **Numeric** stores exact decimals; `price`, `cost`, `total_amount`, `unit_price`, `discount` and `amount` are all `numeric`, which is why money adds up to the cent here. **Double precision** is binary floating point: fast, but `0.1 + 0.2` gives `0.30000000000000004`, so it is kept away from money.

When two integers are divided, the answer is an integer and the fraction is dropped: `1 / 4` is 0 and `-7 / 2` is -3. Making either side `numeric` keeps the fraction. A **cast** (`::numeric`, `CAST(... AS int)`) converts a value on purpose. Casting `numeric` to `int` rounds rather than truncates, so 873.50 becomes 874. Casting text such as `'many'` to `numeric` does not return `NULL`; it raises an error and stops the whole statement, which is why Exercise 2 tests the text before casting it.

The **scale** of a numeric value is the number of digits after the point. A line value such as `27.76 * 3 * (1 - 0.00)` has scale 4 (83.2800), and numeric division of small numbers gives scale 20. `ROUND(x, 2)` sets the scale for display, and where it sits matters: rounding before summing gives a different grand total from rounding after (Exercise 6).

## Two worked SQL examples

### Example 1

```sql
SELECT
  order_id,
  total_amount,
  round(total_amount, 0) AS rounded,
  cast(total_amount AS int) AS as_int
FROM
  orders
ORDER BY
  total_amount DESC,
  order_id
LIMIT 50;
```

**How to read it:** The query sets `round(total_amount, 0)` and `cast(total_amount AS int)` side by side for the 50 largest orders. `round` keeps the `numeric` type with zero decimal places, while the cast produces an `integer`. `ORDER BY total_amount DESC, order_id` puts the biggest orders first and uses the order ID to sort equal totals.

**Expected result/shape:** 50 rows. The first 16 all show 1,432.49, the largest total in the fixture, shared by orders 104, 379, 654 and thirteen more, so `order_id` alone fixes their order. The 50th row is order 734 at 1,312.39. `rounded` and `as_int` agree on every row because a `numeric` to `int` cast rounds half away from zero, just as `round` does. They agree on all 4,362 orders, including the 95 whose cents are exactly .50: order 27's 873.50 becomes 874 in both columns.

### Example 2

```sql
SELECT
  p.category,
  SUM(oi.quantity) AS qty,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) / NULLIF (SUM(oi.quantity), 0), 2) AS avg_price
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category
ORDER BY
  avg_price DESC,
  p.category;
```

**How to read it:** Each of the 13,085 order lines is joined to its product to find the category, and the lines are grouped into six categories. `qty` adds up units. `avg_price` divides net revenue (unit price times quantity, less the line discount) by units sold, so it is the average price actually paid per unit, weighted by quantity. `NULLIF(SUM(oi.quantity), 0)` would turn a category with no units into `NULL` instead of an error, and `ROUND(..., 2)` is applied once to the finished ratio.

**Expected result/shape:** Six rows, highest average first: Sports 60.66 (6,552 units), Beauty 60.16, Home 60.08, Electronics 59.97, Books 59.94 and Apparel 59.23 (6,591 units), 39,257 units in all. A plain `AVG(oi.unit_price)` gives higher numbers (61.78 for Sports) because it ignores both discounts and quantities, and it ranks Books third instead of fifth.

## Learning objectives

- Choose numeric types that preserve required precision.
- Cast deliberately and guard division, rounding, overflow, and malformed text.

## Vocabulary and concepts

- **Exact numeric:** `numeric`/`decimal`, which stores decimal values without
  binary floating-point approximation.
- **Scale:** digits to the right of the decimal point.
- **Type coercion:** PostgreSQL's conversion of values to a compatible type.

## Worked example / walkthrough

`SELECT 1 / 3` returns 0 of type `integer`. `SELECT 1::numeric / 3` returns 0.33333333333333333333 of type `numeric`. `ROUND(1::numeric / NULLIF(3, 0), 2)` returns 0.33. Swap the 3 for a 0 and `NULLIF(0, 0)` makes the divisor `NULL`, the division gives `NULL`, and `ROUND` passes the `NULL` through. The guard has to sit inside the division: `ROUND(1::numeric / 0, 2)` fails with `division by zero` before `ROUND` ever runs.

## Practice assumptions and review method

- **Focus:** Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
- **Assumptions:** Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
- **Failure to watch for:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
- **Review loop:** after a run, wrap any surprising expression in `pg_typeof(...)`, then recompute one row by hand: product 40's margin, order 1's two lines, or 1 divided by 4.

## Exercises

Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.

Before each exercise, write down the type of every column you use (`price`, `cost`, `unit_price`, `discount` and `amount` are `numeric`; `quantity` is `integer`) and the type you expect each expression to produce. Most surprises in this lesson are a type you did not see coming.

1. **Query writing:** Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
   **Forecast:** how many of the 300 products will get a `NULL` rate, and what is the highest rate you expect?
   **Progressive hint:** Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
   **Inputs/evidence:** For sql-14 Exercise 1, compute `price - cost` and `ROUND((price - cost) / NULLIF(price, 0), 4)` for each of the 300 `products`; no fixture price is 0 or `NULL`.
   **Expected result/shape:** For sql-14 Exercise 1, return 300 rows, one per product, led by seven products tied at a `margin_rate` of 0.6500 (40, 80, 120, 160, 200, 240, 280, in `product_id` order) and ending with product 83 at 0.2599. The final columns are `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`. The final order is `margin_rate DESC NULLS LAST, p.product_id`.
   **Verify:** For sql-14 Exercise 1, confirm 300 distinct `product_id` values and that product 40 shows 24.80 - 8.68 = 16.12 and 16.12 / 24.80 = 0.6500. Inside a rolled-back transaction, set product 40's price to 0; the query must not raise a division error, product 40 must move to row 300 with `margin_amount` -8.68 and a `NULL` `margin_rate`, and product 80 must lead.
2. **Query writing:** Safely cast a set of text values to numeric only when they match a numeric grammar.
   **Forecast:** which of the five strings would make a plain `::numeric` cast fail?
   **Progressive hint:** Validate with a regex before casting; otherwise return NULL.
   **Inputs/evidence:** For sql-14 Exercise 2, test five inline `VALUES` strings (`'42'`, `' 3.14 '`, `'-0.5'`, `'many'`, and the empty string) against `'^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'` after `btrim`, casting to `numeric` only when the pattern matches.
   **Expected result/shape:** For sql-14 Exercise 2, return 5 rows in `VALUES` order: 42, 3.14, -0.5, then `NULL` for `many` and `NULL` for the empty string; the query has no `ORDER BY`. The final columns are `raw_value`, and `parsed_numeric`.
   **Verify:** For sql-14 Exercise 2, confirm 5 rows with exactly 2 `NULL` values in `parsed_numeric`. Run `SELECT 'many'::numeric` and `SELECT ''::numeric` on their own; both must fail with `invalid input syntax for type numeric`, which the guard avoids. Note that `'1e3'::numeric` succeeds (1000) but the pattern rejects it, so the guard is stricter than the cast.
3. **Query writing:** Show order-item net revenue rounded only after summing.
   **Forecast:** order 1 has two lines, 3 units at 27.76 and 4 at 39.23, neither discounted. What should its total be?
   **Progressive hint:** Aggregate exact line expressions first; round the final display value.
   **Inputs/evidence:** For sql-14 Exercise 3, sum `unit_price * quantity * (1 - discount)` over the 13,085 `order_items` rows per `order_id` and round each order total to 2 places.
   **Expected result/shape:** For sql-14 Exercise 3, return 4,362 rows, one per order, starting with order 1 at 240.20 (two item lines) and order 2 at 417.94. The final columns are `order_id`, and `net_order_revenue`. The final order is `oi.order_id`.
   **Verify:** For sql-14 Exercise 3, confirm 4,362 distinct `order_id` values, matching `SELECT COUNT(DISTINCT order_id) FROM order_items`, and 0 rows where `net_order_revenue` differs from `orders.total_amount` after joining on `order_id`; the returned values add up to 2355646.89, the same as `SELECT SUM(total_amount) FROM orders`.
4. **Prediction:** Compare integer division with numeric division for 1 divided by 4.
   **Forecast:** write both answers and their types before running.
   **Progressive hint:** At least one operand must be numeric to preserve the fraction.
   **Inputs/evidence:** For sql-14 Exercise 4, evaluate the two constant expressions `1 / 4` and `1::numeric / 4` with no `FROM` clause; no table is read.
   **Expected result/shape:** For sql-14 Exercise 4, return one row: `integer_division` 0 and `numeric_division` 0.25000000000000000000. The final columns are `integer_division`, and `numeric_division`.
   **Verify:** For sql-14 Exercise 4, confirm one row with 0 and 0.25000000000000000000. Run `SELECT 7 / 2, -7 / 2, 1 / 4.0` and expect 3, -3, and 0.25000000000000000000, which shows integer division truncates toward zero; `SELECT 1 / 0` must fail with `division by zero`.
5. **Debugging:** Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
   **Forecast:** some orders were paid in two parts. Will dividing by payment rows give a higher or lower average than dividing by orders?
   **Progressive hint:** Aggregate payment amount and count distinct order IDs at one common scope.
   **Inputs/evidence:** For sql-14 Exercise 5, read from `payments` and divide the total paid amount by the number of distinct paid orders, `SUM(amount) / NULLIF(COUNT(DISTINCT order_id), 0)`, rounded to 2 places.
   **Expected result/shape:** For sql-14 Exercise 5, return one row, `average_paid_amount_per_order` 525.05. The final columns are `average_paid_amount_per_order`.
   **Verify:** For sql-14 Exercise 5, confirm one row with 525.05, which is 1831900.81 divided by 3489 distinct paid orders; compare it with `ROUND(AVG(amount), 2)` (477.55), which divides by the 3836 payment rows instead.
6. **Extension:** Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
   **Forecast:** with 13,085 lines each rounded to the cent, roughly how far apart can the two totals drift?
   **Progressive hint:** This diagnostic makes the consequence of early rounding visible.
   **Inputs/evidence:** For sql-14 Exercise 6, read from `order_items` and compare the sum of line totals rounded per line, `SUM(ROUND(unit_price * quantity * (1 - discount), 2))`, with the exact sum rounded once, `ROUND(SUM(unit_price * quantity * (1 - discount)), 2)`.
   **Expected result/shape:** For sql-14 Exercise 6, return one row: `sum_of_rounded_lines` 2355648.13, `rounded_exact_total` 2355647.12, and `rounding_difference` 1.01. The final columns are `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
   **Verify:** For sql-14 Exercise 6, confirm one row with 2355648.13, 2355647.12, and a `rounding_difference` of 1.01; the difference is the per-line rounding accumulated over 13085 lines, so a report must state which rounding rule it uses.

## Common mistakes and how to recover

- **Dividing two integers:** `SUM(quantity) / COUNT(*)` divides an integer sum by a count and silently drops the fraction. Cast one side, `SUM(quantity)::numeric / COUNT(*)`, or divide a numeric sum as Example 2 does.
- **Casting dirty text directly:** `'many'::numeric` and `''::numeric` both raise `invalid input syntax for type numeric`, and inside a transaction every later statement fails until `ROLLBACK`. Validate first, as in Exercise 2, or on PostgreSQL 16 and later test with `pg_input_is_valid(value, 'numeric')`.
- **Rounding each line before adding:** summing per-line rounded values gives 2,355,648.13, while adding the exact lines and rounding once gives 2,355,647.12. Round at the grain you report.
- **Averaging rows instead of orders:** `AVG(amount)` on `payments` returns 477.55 because 347 orders were paid in two parts and count twice. Divide by `COUNT(DISTINCT order_id)` when the question is per order.
- **Choosing a type too narrow:** `1432.49::numeric(5,2)` fails with `numeric field overflow`, because five digits with two after the point stop at 999.99. Check the largest value before fixing a precision.
- **Using floating point for money:** `0.1::float8 + 0.2::float8 = 0.3` is false. Keep amounts `numeric`.

A failed cast often leaves `psql` in an aborted transaction. The study guide's [steps for getting unstuck](../../STUDY-GUIDE.md#recover-from-common-failures) show how to clear it and rerun the file.

## Self-check

- Can you justify the type used for money-like values and ratios?
- Are division-by-zero and `NULL` behavior visible rather than silently
  misleading?

## Next step

Continue to [Day 15; Phase 1 project](day15_phase1_project.md).

## Deep dive and reference

Learning objectives
- Use integer, numeric/decimal, and floating types appropriately
- Control rounding and formatting; avoid integer division pitfalls
- Cast safely between types; handle NULLs and invalid text

Core concepts and deep dive
- Types: integer (fast, bounded), numeric(p,s) (exact decimal), double precision (approximate). Use numeric for money.
- Division: integer/int division truncates; cast to numeric for fractional results.
- Rounding: ROUND(x,2), CEIL/FLOOR; formatting with to_char for presentation.
- Casting: CAST(text AS numeric) or ::numeric; use to_number(text, format) for messy text.

Examples
- Compute gross_margin_pct = (price-cost)/NULLIF(price,0) casting to numeric with scale.
- Parse '1,234.50' with to_number and compare to numeric cast behavior.

Pitfalls
- Silent rounding when casting to narrower numeric precision.
- Dividing by zero; use NULLIF(den,0) to avoid errors.

Further reading
- Numeric types: https://www.postgresql.org/docs/17/datatype-numeric.html

## Ask an AI tutor about this lesson

You can finish this lesson without a tutor. If you use one, a good exercise is to give it `7 / 2`, `-7 / 2`, `7::numeric / 2`, `2.5::numeric::int` and `2.5::float8::int`, ask for each result and its type, and check the answers in `psql` (the last two give 3 and 2, because floating point rounds half to even). The study guide's [tutor guidance](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) suggests ways to keep it explaining rather than answering for you.

```text
Tutor me through sql-14: Numeric Types, Casting, and Precision.

I have completed the direct catalog prerequisite: `sql-13`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day14_numeric_and_casting.md
- Answer-free learner SQL: sql/postgres-60day/day14_numeric_and_casting.sql

Key terms to teach in context: Exact numeric, Scale, Type coercion. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Evaluate `1 / 3`, `1::numeric / 3`, and `ROUND(1::numeric / NULLIF(3, 0), 2)`. Explain the result type at each step and why guarding the denominator belongs before rounding.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-14/ working copy. Never point setup, reset, DDL, or DML
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
