# Day 35: Avoiding Common Performance Pitfalls

## How to run this lesson

Open `./classroom`, select **sql-35** and run **Whole SQL lesson (psql)**.
The learner file runs four `EXPLAIN ANALYZE` statements, two pitfalls and
their fixes, inside a transaction that rolls back. Your editable copy is
`.learning/sql/sql-35/lesson/workspace/sql/postgres-60day/day35_avoiding_pitfalls.sql`
and it runs against `advanced_sql_training`. Launch details are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Before you read any plan, check which indexes exist: `\d orders` lists only
`orders_pkey`, so every date predicate in this lesson is answered by a
sequential scan. That makes the estimates, not the scan type, the first
thing to compare.

### Optional contributor notebook route

A notebook keeps each pitfall and its fix side by side
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-35
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 34; query optimization](day34_query_optimization.md)
- **Artifacts:** [learner SQL](../day35_avoiding_pitfalls.sql) ·
  [solution reasoning](../solutions/day35_solutions.md) ·
  [executable solution](../solutions/day35_solutions.sql)

## A beginner's mental model for this lesson

A predicate is **sargable** when the column stands alone on one side of the
comparison, so an index on that column, or the column's statistics, can be
used directly. `date_trunc('day', order_date) = ...` hides `order_date`
inside a function. The planner cannot search a plain `order_date` index for
it, and it has no statistics for the function's output, so it guesses.

The guesses are fixed fractions. For an equality on an expression the
planner assumes 0.5% of the table, which is 22 of the 4,362 orders, whatever
the real count is. For a range on an expression it assumes one third, 1,454
rows. The raw-column version of the same filter is costed from the
`order_date` histogram instead. So even before you add an index, the
sargable form gives the planner better numbers for every node above the
scan.

The second pitfall is repeated work. The learner file sums `total_amount`
for each customer with a correlated subquery, and the plan runs that
subquery 500 times, once per customer, scanning all 4,362 orders each time.
Grouping `orders` once and joining the 438 totals back to `customers`
returns the same 500 rows. The 62 customers with no orders get `NULL` from
both versions.

## Two worked SQL examples

### Example 1

```sql
EXPLAIN ANALYZE
SELECT
  *
FROM
  orders
WHERE
  date_trunc('day', order_date) = date_trunc('day', now());
```

**How to read it:** The filter compares `date_trunc('day',
order_date)` with the start of today. The plan is a `Seq Scan on orders`
with an estimate of 22 rows: the 0.5% guess, because the planner cannot see
through the function.

**Expected result/shape:** A plan whose scan usually reports zero
actual rows, with nearly all 4,362 orders under `Rows Removed by Filter`.
The seed spreads each customer's orders between signup and the load time,
so few if any land on the current day. An empty result is weak evidence
that two filters agree; repeat the comparison with the seven-day pair in
the solution, which returns rows.

### Example 2

```sql
EXPLAIN ANALYZE
SELECT
  *
FROM
  orders
WHERE
  order_date >= date_trunc('day', now())
  AND order_date < date_trunc('day', now()) + interval '1 day';
```

**How to read it:** The same day is written as a half-open
range on the bare column: from midnight up to, but not including, the next
midnight. The upper bound uses `<`, so an order stamped exactly at the next
midnight belongs to tomorrow.

**Expected result/shape:** Again a `Seq Scan` with zero
rows, because `orders` has no index on `order_date`. The difference is the
estimate, 1 row instead of 22, taken from the column's statistics. Create an
index on `order_date` inside the transaction and only this version can use
it.

## Learning objectives

- Rewrite non-sargable temporal predicates as correct raw-column ranges.
- Replace repeated correlated work with one set-based aggregation.

## Vocabulary and concepts

- **Sargability:** whether a predicate can use an index's search ordering.
- **Half-open range:** `>= start AND < end`, suitable for adjacent periods.
- **Set-based rewrite:** compute a relation once rather than once per outer row.

## Worked example / walkthrough

Compare `date_trunc('day', order_date) = target_day` with
`order_date >= target_day AND order_date < target_day + interval '1 day'`.
Test timestamps at both boundaries, reconcile row IDs, and compare plans with a
matching `order_date` index.

## Exercises

Complete these in the [learner SQL](../day35_avoiding_pitfalls.sql):

1. Rewrite three non-sargable predicates.
   **Inputs/evidence:** For sql-35 Exercise 1, read `orders` (4,362 rows on 65 pages, no index on `order_date`) and plan three pairs that filter `order_date`: `date_trunc('day', ...)` against a one-day range, `EXTRACT(year ...)` against a `date_trunc('year', CURRENT_DATE)` range, and `order_date::date >= CURRENT_DATE - 6` against `timestamptz` bounds.
   **Expected result/shape:** For sql-35 Exercise 1, expected output: each pair returns the same `order_id` set, which on this load is 0 orders for today, 2,393 for the current year, and 13 for the last seven dates; all six plans are a `Seq Scan`, but the function forms are estimated at a fixed 22 or 1,454 rows while the ranges get 2,396 and 20 from the histogram. The final columns are `order_id`.
   **Verify:** For sql-35 Exercise 1, confirm each pair with `EXCEPT` in both directions and matching `COUNT(*)` values; then, inside `BEGIN ... ROLLBACK`, create an index on `order_date` and confirm the range forms switch to a `Bitmap Index Scan` while the `date_trunc` and `::date` forms stay a `Seq Scan`, and insert one order dated tomorrow at midnight to see the open-ended `::date` form count 14 rows against 13 for the bounded range.
2. Replace correlated aggregates with one pre-aggregation and join.
   **Inputs/evidence:** For sql-35 Exercise 2, read `customers` (500 rows) and `orders`, and plan a correlated `SUM(total_amount)` subquery per customer against an `order_totals` CTE grouped once by `customer_id` (438 rows) and attached with a `LEFT JOIN`.
   **Expected result/shape:** For sql-35 Exercise 2, expected output: 500 rows in both forms, one per customer, with `NULL` `lifetime_revenue` for the 62 customers without orders; the correlated plan shows `SubPlan 1` with `loops=500`, and the grouped plan reads `orders` once into a `HashAggregate` under a `Hash Left Join`. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer. The final columns are `customer_id`, and `lifetime_revenue`.
   **Verify:** For sql-35 Exercise 2, confirm the two forms `EXCEPT` each other in both directions with no rows and that `SUM(lifetime_revenue)` is 2,355,646.89, the same as `SELECT SUM(total_amount) FROM orders`; then confirm an inner join returns only 438 rows, and, inside `BEGIN ... ROLLBACK`, give customer 8 one order with `total_amount = 0` and confirm its `lifetime_revenue` changes from `NULL` to 0.00.
3. Predict B-tree usefulness for prefix versus leading-wildcard patterns.
   **Inputs/evidence:** For sql-35 Exercise 3, read `customers` (500 rows, every `full_name` of the form `Customer N`, database collation `en_US.utf8`, no index on `full_name`) and plan `LIKE 'A%'` against `LIKE '%A%'`.
   **Expected result/shape:** For sql-35 Exercise 3, expected output: both patterns return 0 rows on this load, because no name contains a capital A; both plans are a `Seq Scan` that removes all 500 rows. The final columns are `customer_id`.
   **Verify:** For sql-35 Exercise 3, confirm with `COUNT(*)` that `LIKE 'Customer 1%'` matches 111 rows and `LIKE 'Customer 42%'` matches 11; then, inside `BEGIN ... ROLLBACK`, show that a plain B-tree on `full_name` is not used for the prefix even with `enable_seqscan` off, while an index with `text_pattern_ops` gives a `Bitmap Index Scan` with `full_name ~>=~ 'Customer 42' AND full_name ~<~ 'Customer 43'` and `LIKE '%1%'` stays a `Seq Scan`.
4. Replace `OFFSET` paging with deterministic keyset paging.
   **Inputs/evidence:** For sql-35 Exercise 4, read `orders` (4,362 rows, no repeated `order_date`), take the 20th newest order as the one-row `boundary` CTE with `OFFSET 19 LIMIT 1`, and fetch the next page with the row comparison `(o.order_date, o.order_id) < (b.order_date, b.order_id)`.
   **Expected result/shape:** For sql-35 Exercise 4, expected output: exactly 20 rows on this load, starting with order 3056 and ending with order 3786, right after boundary order 743. The final columns are `order_id`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-35 Exercise 4, confirm the page has 20 distinct `order_id` values and that an `EXCEPT ALL` against `OFFSET 20 LIMIT 20` with the same `ORDER BY` returns no rows; then, inside `BEGIN ... ROLLBACK`, give order 3056 the same `order_date` as order 743 and confirm the boundary becomes 3056 and the page starts with 743, while a date-only `o.order_date < b.order_date` filter skips order 743.
5. Repair payment/item fanout.
   **Inputs/evidence:** For sql-35 Exercise 5, read `payments` into `paid`, one `SUM(amount)` per order, and `order_items` into `sold`, one discounted line revenue per order, then `LEFT JOIN` both to `orders` and keep orders 1 to 20.
   **Expected result/shape:** For sql-35 Exercise 5, expected output: exactly 20 rows, orders 1 to 20; orders 5, 9, 14, and 20 have `NULL` `paid`, order 10 combines payments of 71.72 and 71.71 into 143.43 against 143.4290 sold, and order 17 shows 172.16 paid against 344.3105 sold. The final columns are `order_id`, `paid`, and `sold`. The final order is `o.order_id`.
   **Verify:** For sql-35 Exercise 5, confirm that joining both child tables before grouping changes 15 of the 20 rows, leaving only orders 5, 9, 14, 15, and 20 intact, and turns order 4's `paid` into 5,779.60 and order 10's `sold` into 286.858; then, inside `BEGIN ... ROLLBACK`, add a second item line to order 15 and confirm the grouped answer keeps `paid` at 28.14 while the raw join doubles it to 56.28.
6. Explain `COUNT(*)` versus `COUNT(email)` with NULLs.
   **Inputs/evidence:** For sql-35 Exercise 6, read from `customers` and count, in one aggregate, all rows, rows with an `email`, and rows without one.
   **Expected result/shape:** For sql-35 Exercise 6, expected output: one row with `customer_rows` 500, `customers_with_email` 500, and `customers_without_email` 0. The final columns are `customer_rows`, `customers_with_email`, and `customers_without_email`.
   **Verify:** For sql-35 Exercise 6, confirm `customers_with_email + customers_without_email = customer_rows`; in a transaction you roll back, set one `email` to NULL and expect 500, 499, and 1, because `COUNT(email)` skips NULL while `COUNT(*)` counts every row.

Add an edge-case result check before every performance comparison.

## Self-check

- Does the range preserve the intended time-zone and boundary semantics?
- Does a set-based rewrite retain outer entities with no matching facts when
  required?

## Next step

Continue to [Day 36; materialized views](day36_materialized_views.md).

## Deep dive and reference

## What you will learn

- Recognize function-wrapped predicates that are hard to index.
- Replace per-row correlated aggregation with one set-based aggregation.
- Preserve correctness while reducing repeated work.

## How the learner script uses the current schema

The first pair compares `date_trunc('day', order_date) = ...` with a half-open
range on raw `orders.order_date`. The second pair compares a customer-by-customer
correlated sum with one grouped `orders` CTE joined to `customers`.

The half-open range is:

`order_date >= start_of_day AND order_date < start_of_next_day`

It handles every timestamp in the day and can match a normal B-tree index on
`order_date`.

## Why the set-based rewrite helps

The correlated form can execute an order scan once per customer. The grouped
form scans and aggregates orders once, then joins one row per customer. A
`LEFT JOIN` retains customers with no orders; decide whether the displayed
value should remain `NULL` or become zero.

## Estimates with and without a function

The solution's first exercise runs three predicate pairs. All six plans are
sequential scans, yet the estimates differ sharply. The actual counts below
come from a late-2026 load; they move with the calendar, but the
function-wrapped estimates do not.

| Filter | Function form estimate | Range form estimate | Actual rows |
|---|---|---|---|
| Today | 22 | 1 | 0 |
| This calendar year | 22 | 2,396 | 2,393 |
| Last seven dates | 1,454 | 20 | 13 |

The year filter shows the danger: the function form expects 22 rows and
gets 2,393. A join planned for 22 rows might choose a nested loop that is a
poor fit for 2,393.

## Practice map

Several prompts above ask for an `EXPLAIN`; run each query once without
`EXPLAIN` first and keep its keys, so the plan comparison is between two
queries known to agree.

## Pitfalls and validation

- Do not rewrite a predicate unless time zone and inclusive/exclusive boundaries
  remain correct.
- Functions are not universally bad; a matching expression index can be valid
  when the expression is the real search key.
- Preserve outer-join behavior for entities with no facts.
- Compare result keys and totals before comparing timing.

## Expanded practice lab

Prompts 3-6 cover four common production surprises: leading-wildcard searches,
deep `OFFSET` pages, fanout, and nullable counts. Keyset pagination must use a
unique deterministic tuple such as `(order_date, order_id)` and repeat the same
ordering in the seek predicate.

Fix fanout at the grain boundary instead of hiding it with `DISTINCT`.
`COUNT(*)` counts rows; `COUNT(email)` counts only non-NULL emails. Neither is
universally “correct”, the metric definition decides.

## Ask an AI tutor about this lesson

A tutor is useful for predicting the planner's guesses: give it a filter
and the table size and ask it to estimate the row count before you run
`EXPLAIN`
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-35: Avoiding Common Performance Pitfalls.

I have completed the direct catalog prerequisite: `sql-34`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day35_avoiding_pitfalls.md
- Answer-free learner SQL: sql/postgres-60day/day35_avoiding_pitfalls.sql

Key terms to teach in context: Sargability, Half-open range, Set-based rewrite. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare `date_trunc('day', order_date) = target_day` with `order_date >= target_day AND order_date < target_day + interval '1 day'`. Test timestamps at both boundaries, reconcile row IDs, and compare plans with a matching `order_date` index.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-35/ working copy. Never point setup, reset, DDL, or DML
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
