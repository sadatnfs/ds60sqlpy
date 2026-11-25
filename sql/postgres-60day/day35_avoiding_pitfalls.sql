-- Day 35: Avoiding Common Performance Pitfalls
-- BEGINNER WORKFLOW - sql-35: Avoiding Pitfalls
-- Guide: sql/postgres-60day/companion-guides/day35_avoiding_pitfalls.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-35.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Pitfall: function on column prevents index usage
EXPLAIN ANALYZE
SELECT
  *
FROM
  orders
WHERE
  date_trunc('day', order_date) = date_trunc('day', now());

-- Better:
EXPLAIN ANALYZE
SELECT
  *
FROM
  orders
WHERE
  order_date >= date_trunc('day', now())
  AND order_date < date_trunc('day', now()) + interval '1 day';

-- Pitfall: Correlated subquery per row
EXPLAIN ANALYZE
SELECT
  c.customer_id,
  (
    SELECT
      SUM(o.total_amount)
    FROM
      orders o
    WHERE
      o.customer_id = c.customer_id)
FROM
  customers c;

-- Better: pre-aggregate and join
EXPLAIN ANALYZE WITH agg AS (
  SELECT
    customer_id,
    SUM(total_amount) AS sum_total
  FROM
    orders
  GROUP BY
    customer_id
)
SELECT
  c.customer_id,
  a.sum_total
FROM
  customers c
  LEFT JOIN agg a ON a.customer_id = c.customer_id;

-- N+1 pattern in application layer (illustrated only)
-- Prefer set-based queries over per-row queries.
-- Exercises
-- 1. Rewrite 3 queries to avoid functions on indexed columns.
--    Inputs: For sql-35 Exercise 1, read `orders` (4,362 rows on 65 pages, no index on `order_date`) and plan three pairs that filter `order_date`: `date_trunc('day', ...)` against a one-day range, `EXTRACT(year ...)` against a `date_trunc('year', CURRENT_DATE)` range, and `order_date::date >= CURRENT_DATE - 6` against `timestamptz` bounds.
--    Expected result/shape: For sql-35 Exercise 1, expected output: each pair returns the same `order_id` set, which on this load is 0 orders for today, 2,393 for the current year, and 13 for the last seven dates; all six plans are a `Seq Scan`, but the function forms are estimated at a fixed 22 or 1,454 rows while the ranges get 2,396 and 20 from the histogram. The final columns are `order_id`.
--    Verify: For sql-35 Exercise 1, confirm each pair with `EXCEPT` in both directions and matching `COUNT(*)` values; then, inside `BEGIN ... ROLLBACK`, create an index on `order_date` and confirm the range forms switch to a `Bitmap Index Scan` while the `date_trunc` and `::date` forms stay a `Seq Scan`, and insert one order dated tomorrow at midnight to see the open-ended `::date` form count 14 rows against 13 for the bounded range.
--    Hint ladder, rung 1: For sql-35 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 2. Replace correlated subqueries with joins/CTEs.
--    Inputs: For sql-35 Exercise 2, read `customers` (500 rows) and `orders`, and plan a correlated `SUM(total_amount)` subquery per customer against an `order_totals` CTE grouped once by `customer_id` (438 rows) and attached with a `LEFT JOIN`.
--    Expected result/shape: For sql-35 Exercise 2, expected output: 500 rows in both forms, one per customer, with `NULL` `lifetime_revenue` for the 62 customers without orders; the correlated plan shows `SubPlan 1` with `loops=500`, and the grouped plan reads `orders` once into a `HashAggregate` under a `Hash Left Join`. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer. The final columns are `customer_id`, and `lifetime_revenue`.
--    Verify: For sql-35 Exercise 2, confirm the two forms `EXCEPT` each other in both directions with no rows and that `SUM(lifetime_revenue)` is 2,355,646.89, the same as `SELECT SUM(total_amount) FROM orders`; then confirm an inner join returns only 438 rows, and, inside `BEGIN ... ROLLBACK`, give customer 8 one order with `total_amount = 0` and confirm its `lifetime_revenue` changes from `NULL` to 0.00.
--    Hint ladder, rung 1: For sql-35 Exercise 2, run `order_totals` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 3. Prediction: compare LIKE 'A%' with LIKE '%A%'. State which pattern can use
--    a normal B-tree text index more directly and why the leading wildcard
--    changes the search.
--    Inputs: For sql-35 Exercise 3, read `customers` (500 rows, every `full_name` of the form `Customer N`, database collation `en_US.utf8`, no index on `full_name`) and plan `LIKE 'A%'` against `LIKE '%A%'`.
--    Expected result/shape: For sql-35 Exercise 3, expected output: both patterns return 0 rows on this load, because no name contains a capital A; both plans are a `Seq Scan` that removes all 500 rows. The final columns are `customer_id`.
--    Verify: For sql-35 Exercise 3, confirm with `COUNT(*)` that `LIKE 'Customer 1%'` matches 111 rows and `LIKE 'Customer 42%'` matches 11; then, inside `BEGIN ... ROLLBACK`, show that a plain B-tree on `full_name` is not used for the prefix even with `enable_seqscan` off, while an index with `text_pattern_ops` gives a `Bitmap Index Scan` with `full_name ~>=~ 'Customer 42' AND full_name ~<~ 'Customer 43'` and `LIKE '%1%'` stays a `Seq Scan`.
--    Hint ladder, rung 1: For sql-35 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
-- 4. Construction: replace an OFFSET-based “next page” query with keyset
--    pagination ordered by (order_date DESC, order_id DESC).
--    Inputs: For sql-35 Exercise 4, read `orders` (4,362 rows, no repeated `order_date`), take the 20th newest order as the one-row `boundary` CTE with `OFFSET 19 LIMIT 1`, and fetch the next page with the row comparison `(o.order_date, o.order_id) < (b.order_date, b.order_id)`.
--    Expected result/shape: For sql-35 Exercise 4, expected output: exactly 20 rows on this load, starting with order 3056 and ending with order 3786, right after boundary order 743. The final columns are `order_id`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-35 Exercise 4, confirm the page has 20 distinct `order_id` values and that an `EXCEPT ALL` against `OFFSET 20 LIMIT 20` with the same `ORDER BY` returns no rows; then, inside `BEGIN ... ROLLBACK`, give order 3056 the same `order_date` as order 743 and confirm the boundary becomes 3056 and the page starts with 743, while a date-only `o.order_date < b.order_date` filter skips order 743.
--    Hint ladder, rung 1: For sql-35 Exercise 4, run `boundary` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. Debugging: find and repair a join that calculates revenue after joining
--    both payments and order_items at their raw grains.
--    Inputs: For sql-35 Exercise 5, read `payments` into `paid`, one `SUM(amount)` per order, and `order_items` into `sold`, one discounted line revenue per order, then `LEFT JOIN` both to `orders` and keep orders 1 to 20.
--    Expected result/shape: For sql-35 Exercise 5, expected output: exactly 20 rows, orders 1 to 20; orders 5, 9, 14, and 20 have `NULL` `paid`, order 10 combines payments of 71.72 and 71.71 into 143.43 against 143.4290 sold, and order 17 shows 172.16 paid against 344.3105 sold. The final columns are `order_id`, `paid`, and `sold`. The final order is `o.order_id`.
--    Verify: For sql-35 Exercise 5, confirm that joining both child tables before grouping changes 15 of the 20 rows, leaving only orders 5, 9, 14, 15, and 20 intact, and turns order 4's `paid` into 5,779.60 and order 10's `sold` into 286.858; then, inside `BEGIN ... ROLLBACK`, add a second item line to order 15 and confirm the grouped answer keeps `paid` at 28.14 while the raw join doubles it to 56.28.
--    Hint ladder, rung 1: For sql-35 Exercise 5, run `paid`, and `sold` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. Edge case: compare COUNT(*) and COUNT(email) for customers, and explain
--    why nullable inputs make the two counts intentionally different.
--    Inputs: For sql-35 Exercise 6, read from `customers` and count, in one aggregate, all rows, rows with an `email`, and rows without one.
--    Expected result/shape: For sql-35 Exercise 6, expected output: one row with `customer_rows` 500, `customers_with_email` 500, and `customers_without_email` 0. The final columns are `customer_rows`, `customers_with_email`, and `customers_without_email`.
--    Verify: For sql-35 Exercise 6, confirm `customers_with_email + customers_without_email = customer_rows`; in a transaction you roll back, set one `email` to NULL and expect 500, 499, and 1, because `COUNT(email)` skips NULL while `COUNT(*)` counts every row.
--    Hint ladder, rung 1: For sql-35 Exercise 6, compare `COUNT(*)` with `COUNT(email)` first; the difference is the number of NULL emails.
ROLLBACK;
