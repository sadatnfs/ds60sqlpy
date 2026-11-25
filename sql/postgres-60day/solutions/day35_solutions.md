# Day 35: Solutions: Avoiding Performance Pitfalls


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The executable file runs in a transaction that ends in `ROLLBACK`. Note the
row counts and the estimated rows on each scan before you look at timing.
General advice is in [Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day35_solutions.sql
```

## How these answers fit together

The six answers cover the pitfalls the guide names: functions on a
filtered column, per-row subqueries, leading wildcards, deep `OFFSET`
pages, fanout from joining two child tables and nullable counts. Each fix
keeps the answer and changes how much work PostgreSQL does, or how
accurately it can estimate that work.

The first answer compares three date filters under `EXPLAIN`, and the
second compares the correlated and grouped forms of lifetime revenue. The
learner file is
[day35_avoiding_pitfalls.sql](../day35_avoiding_pitfalls.sql).

## Exercise 1: Three sargable predicate rewrites

Each “better” predicate leaves `order_date` bare, allowing an index on that
column to define a contiguous range.

```sql
SET search_path TO training, public;

-- 1. One calendar day
EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id
FROM
  orders
WHERE
  date_trunc('day', order_date) = date_trunc('day', CURRENT_TIMESTAMP);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id
FROM
  orders
WHERE
  order_date >= date_trunc('day', CURRENT_TIMESTAMP)
  AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day';

-- 2. Current calendar year
EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id
FROM
  orders
WHERE
  EXTRACT(year FROM order_date) = EXTRACT(year FROM CURRENT_DATE);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id
FROM
  orders
WHERE
  order_date >= date_trunc('year', CURRENT_DATE)
  AND order_date < date_trunc('year', CURRENT_DATE) + interval '1 year';

-- 3. Last seven calendar dates, including today
EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id
FROM
  orders
WHERE
  order_date::date >= CURRENT_DATE -6;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id
FROM
  orders
WHERE
  order_date >= (CURRENT_DATE -6)::timestamptz
  AND order_date < (CURRENT_DATE +1)::timestamptz;
```

Expected result sets within each pair are equivalent under the session time
zone. Plan nodes can remain sequential scans because the dataset is small or
because the demonstration index from Day 32 was rolled back.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 1, read `orders` (4,362 rows on 65 pages, no index on `order_date`) and plan three pairs that filter `order_date`: `date_trunc('day', ...)` against a one-day range, `EXTRACT(year ...)` against a `date_trunc('year', CURRENT_DATE)` range, and `order_date::date >= CURRENT_DATE - 6` against `timestamptz` bounds.
- **Expected result/shape:** For sql-35 Exercise 1, expected output: each pair returns the same `order_id` set, which on this load is 0 orders for today, 2,393 for the current year, and 13 for the last seven dates; all six plans are a `Seq Scan`, but the function forms are estimated at a fixed 22 or 1,454 rows while the ranges get 2,396 and 20 from the histogram. The final columns are `order_id`.
- **Independent verification:** For sql-35 Exercise 1, confirm each pair with `EXCEPT` in both directions and matching `COUNT(*)` values; then, inside `BEGIN ... ROLLBACK`, create an index on `order_date` and confirm the range forms switch to a `Bitmap Index Scan` while the `date_trunc` and `::date` forms stay a `Seq Scan`, and insert one order dated tomorrow at midnight to see the open-ended `::date` form count 14 rows against 13 for the bounded range.

- **Intermediate relation check:** Each pair returns the same `order_id` set. The day pair usually returns no rows, since few seeded orders fall on the current day. On a late-2026 load the year pair returned 2,393 orders and the seven-date pair 13, so compare those two with `EXCEPT` in both directions.
- **Clause check:** `orders` has no index on `order_date`, so all six plans are `Seq Scan`s that read 65 buffers. The function forms get fixed guesses, 22 rows for an equality and 1,454 for `order_date::date >= CURRENT_DATE - 6`, while the ranges are estimated at 1, 2,396 and 20 from the column's histogram.
- **Alternative/trade-off:** An expression index on `date_trunc('day', order_date)` would make the first form searchable too, and gives the planner statistics for it. It helps only that exact expression; a plain index on `order_date` serves all three ranges.
- **Edge case:** `order_date` is a `timestamptz`, so "today" depends on the session time zone, `Etc/UTC` in the course container. The cast `order_date::date` and the bounds `(CURRENT_DATE - 6)::timestamptz` both follow that setting, which is why the pair agrees; a report for another zone must say which one.

## Exercise 2: Replace a per-customer correlated aggregate

```sql
SET search_path TO training, public;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  c.customer_id,
  (
    SELECT
      SUM(o.total_amount)
    FROM
      orders o
    WHERE
      o.customer_id = c.customer_id) AS lifetime_revenue
FROM
  customers c;

EXPLAIN (
  ANALYZE,
  BUFFERS
) WITH order_totals AS (
  SELECT
    customer_id,
    SUM(total_amount) AS lifetime_revenue
  FROM
    orders
  GROUP BY
    customer_id
)
SELECT
  c.customer_id,
  ot.lifetime_revenue
FROM
  customers c
  LEFT JOIN order_totals ot ON ot.customer_id = c.customer_id;
```

Expected shape: one row per customer in both forms. The `LEFT JOIN` is required
to retain customers with no orders; changing it to an inner join would alter
the answer.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 2, read `customers` (500 rows) and `orders`, and plan a correlated `SUM(total_amount)` subquery per customer against an `order_totals` CTE grouped once by `customer_id` (438 rows) and attached with a `LEFT JOIN`.
- **Expected result/shape:** For sql-35 Exercise 2, expected output: 500 rows in both forms, one per customer, with `NULL` `lifetime_revenue` for the 62 customers without orders; the correlated plan shows `SubPlan 1` with `loops=500`, and the grouped plan reads `orders` once into a `HashAggregate` under a `Hash Left Join`. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer. The final columns are `customer_id`, and `lifetime_revenue`.
- **Independent verification:** For sql-35 Exercise 2, confirm the two forms `EXCEPT` each other in both directions with no rows and that `SUM(lifetime_revenue)` is 2,355,646.89, the same as `SELECT SUM(total_amount) FROM orders`; then confirm an inner join returns only 438 rows, and, inside `BEGIN ... ROLLBACK`, give customer 8 one order with `total_amount = 0` and confirm its `lifetime_revenue` changes from `NULL` to 0.00.

- **Intermediate relation check:** `order_totals` has 438 rows, one per customer who has ordered. The join brings the result back to 500 rows, and the 62 customers without orders get `NULL` for `lifetime_revenue` in both forms.
- **Clause check:** The correlated form's plan shows `SubPlan 1` with `loops=500`: each loop scans `orders`, keeps about 9 rows and removes 4,353. The grouped form scans `orders` once into a `HashAggregate` and attaches it with a `Hash Left Join`. On the seed that is roughly 52 ms against 1.5 ms.
- **Alternative/trade-off:** Wrapping the measure in `COALESCE(ot.lifetime_revenue, 0)` would show 0.00 instead of `NULL` for the 62 customers without orders; whether that is right depends on whether the report means "no revenue" or "not applicable". The grand total, 2,355,646.89, matches `SUM(total_amount)` over `orders` either way, and sorting by `lifetime_revenue DESC NULLS LAST` puts customer 181 first at 9,502.21.
- **Edge case:** An inner join would drop the 62 customers, every one of them in Brazil. A row count of 438 instead of 500 is the quickest sign of that mistake.

## Pitfalls

- Sargability does not guarantee an index scan; it merely gives the planner the
  option.
- Timestamp-to-date conversion uses the session time zone. Define business
  timezone semantics before reporting calendar periods.
- PostgreSQL can decorrelate some subqueries. Confirm the plan instead of
  assuming every correlated expression runs once per outer row.
- Do not hide fanout with `DISTINCT`; fix the join grain.

## Exercise 3: Diagnose wildcard search

`LIKE 'A%'` has a fixed starting prefix; `LIKE '%A%'` does not. A normal B-tree
therefore has a more direct opportunity on the first pattern, subject to
collation/operator-class details.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 3, read `customers` (500 rows, every `full_name` of the form `Customer N`, database collation `en_US.utf8`, no index on `full_name`) and plan `LIKE 'A%'` against `LIKE '%A%'`.
- **Expected result/shape:** For sql-35 Exercise 3, expected output: both patterns return 0 rows on this load, because no name contains a capital A; both plans are a `Seq Scan` that removes all 500 rows. The final columns are `customer_id`.
- **Independent verification:** For sql-35 Exercise 3, confirm with `COUNT(*)` that `LIKE 'Customer 1%'` matches 111 rows and `LIKE 'Customer 42%'` matches 11; then, inside `BEGIN ... ROLLBACK`, show that a plain B-tree on `full_name` is not used for the prefix even with `enable_seqscan` off, while an index with `text_pattern_ops` gives a `Bitmap Index Scan` with `full_name ~>=~ 'Customer 42' AND full_name ~<~ 'Customer 43'` and `LIKE '%1%'` stays a `Seq Scan`.

- **Intermediate relation check:** Every customer is named `Customer` followed by a number, so `LIKE 'A%'` and `LIKE '%A%'` both return zero rows, and both plans are a `Seq Scan` removing 500. Use `'Customer 1%'` (111 rows) and `'%1%'` for a pattern that matches something.
- **Clause check:** There is no index on `full_name`. Even after creating a plain B-tree index on it, `LIKE 'Customer 1%'` cannot use it, because the database collation is `en_US.utf8`; the index serves `=` but not prefix matching.
- **Alternative/trade-off:** An index built with `text_pattern_ops` turns the prefix into a range, `full_name ~>=~ 'Customer 1' AND full_name ~<~ 'Customer 2'`, which the planner can search. A leading wildcard has no starting point, so `'%1%'` still needs a full scan or a trigram index from `pg_trgm`.
- **Edge case:** With 111 of 500 rows matching, the planner prefers a sequential scan even when the pattern index exists. You need `SET enable_seqscan = off` inside the transaction to see the index path; that setting is for experiments, not for production.

## Exercise 4: Replace OFFSET with a seek tuple

The boundary tuple comes from `(order_date DESC, order_id DESC)`. The next page
uses the matching tuple comparison and repeats that deterministic order.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 4, read `orders` (4,362 rows, no repeated `order_date`), take the 20th newest order as the one-row `boundary` CTE with `OFFSET 19 LIMIT 1`, and fetch the next page with the row comparison `(o.order_date, o.order_id) < (b.order_date, b.order_id)`.
- **Expected result/shape:** For sql-35 Exercise 4, expected output: exactly 20 rows on this load, starting with order 3056 and ending with order 3786, right after boundary order 743. The final columns are `order_id`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-35 Exercise 4, confirm the page has 20 distinct `order_id` values and that an `EXCEPT ALL` against `OFFSET 20 LIMIT 20` with the same `ORDER BY` returns no rows; then, inside `BEGIN ... ROLLBACK`, give order 3056 the same `order_date` as order 743 and confirm the boundary becomes 3056 and the page starts with 743, while a date-only `o.order_date < b.order_date` filter skips order 743.

- **Intermediate relation check:** `boundary` holds one row, the 20th newest order. The page that follows has 20 rows, and an `EXCEPT ALL` against `OFFSET 20 LIMIT 20` with the same `ORDER BY` returns nothing, so the two pagings agree.
- **Clause check:** The row comparison `(o.order_date, o.order_id) < (b.order_date, b.order_id)` means "earlier date, or the same date with a smaller id", which matches the `DESC, DESC` sort exactly. Every one of the 4,362 order dates is distinct, so `order_id` never decides on the seed, but it guarantees that tied rows are not skipped or repeated.
- **Alternative/trade-off:** Without an index the keyset query still scans and sorts all orders. With an index on `(order_date DESC, order_id DESC)`, a literal boundary becomes an `Index Cond` and the scan reads 20 entries, while `OFFSET 2000 LIMIT 20` reads 2,020.
- **Edge case:** This answer finds the boundary with `OFFSET 19`, which is only there to make a runnable example. An application passes the last `(order_date, order_id)` of the page the user already has.

## Exercise 5: Fix payment/item fanout

The answer groups each many-side by `order_id` before joining. `DISTINCT` would
only conceal duplicated output, not repair multiplied sums.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 5, read `payments` into `paid`, one `SUM(amount)` per order, and `order_items` into `sold`, one discounted line revenue per order, then `LEFT JOIN` both to `orders` and keep orders 1 to 20.
- **Expected result/shape:** For sql-35 Exercise 5, expected output: exactly 20 rows, orders 1 to 20; orders 5, 9, 14, and 20 have `NULL` `paid`, order 10 combines payments of 71.72 and 71.71 into 143.43 against 143.4290 sold, and order 17 shows 172.16 paid against 344.3105 sold. The final columns are `order_id`, `paid`, and `sold`. The final order is `o.order_id`.
- **Independent verification:** For sql-35 Exercise 5, confirm that joining both child tables before grouping changes 15 of the 20 rows, leaving only orders 5, 9, 14, 15, and 20 intact, and turns order 4's `paid` into 5,779.60 and order 10's `sold` into 286.858; then, inside `BEGIN ... ROLLBACK`, add a second item line to order 15 and confirm the grouped answer keeps `paid` at 28.14 while the raw join doubles it to 56.28.

- **Intermediate relation check:** `paid` and `sold` each have one row per `order_id`. Of the first 20 orders, 5, 9, 14 and 20 are `placed` and have no payment, so `paid` is `NULL`.
- **Clause check:** Grouping before the join keeps each sum at order grain. Order 10 has two payments, 71.72 and 71.71, which `paid` combines into 143.43, while `sold` stays 143.429 for its single item.
- **Alternative/trade-off:** Joining both child tables first and then grouping multiplies each side by the other. Order 4, with five items and one payment, reports `paid` 5,779.60, five times 1,155.92; order 10 reports `sold` 286.858, twice its real value. Only orders with exactly one item and one payment, such as order 15, come through unchanged.
- **Edge case:** `sold` keeps four decimals, for example 1,155.9185 for order 4, while payments are rounded to cents. Order 17 is a real mismatch, not rounding: 172.16 paid against 344.3105 sold.

## Exercise 6: Define nullable counts

`COUNT(*)` measures customer rows; `COUNT(email)` measures customers with a
non-NULL email. The difference is a useful missingness count, not a discrepancy.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 6, read from `customers` and count, in one aggregate, all rows, rows with an `email`, and rows without one.
- **Expected result/shape:** For sql-35 Exercise 6, expected output: one row with `customer_rows` 500, `customers_with_email` 500, and `customers_without_email` 0. The final columns are `customer_rows`, `customers_with_email`, and `customers_without_email`.
- **Independent verification:** For sql-35 Exercise 6, confirm `customers_with_email + customers_without_email = customer_rows`; in a transaction you roll back, set one `email` to NULL and expect 500, 499, and 1, because `COUNT(email)` skips NULL while `COUNT(*)` counts every row.

- **Intermediate relation check:** All 500 customers have an email, so the result is 500, 500 and 0. The column is nullable and unique; a unique constraint still allows any number of `NULL`s.
- **Clause check:** `COUNT(*)` counts rows and `COUNT(email)` counts non-`NULL` values, both in one pass over `customers`. Their difference is the missing-email count, which is why the answer computes it as `COUNT(*) - COUNT(email)`.
- **Alternative/trade-off:** `COUNT(*) FILTER (WHERE email IS NULL)` gives the same third column and states the intent directly. Either form avoids a second query.
- **Edge case:** An empty string is not `NULL`, so a blank email would count as present. The seed has none, but a quality check that treats blanks as missing should count `NULLIF(trim(email), '')` instead.

## Final self-check

1. Why does the planner estimate 22 rows for the function-wrapped year
   filter, and what is the real count on your run?
2. Why can a plain B-tree index on `full_name` not serve `LIKE 'Customer 1%'`
   in this database, and what index can?
3. What does the second key in `(order_date, order_id)` protect against in
   keyset paging?
4. Why does order 10's `sold` double when payments and items are joined
   before grouping?
