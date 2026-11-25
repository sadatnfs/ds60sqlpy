# Day 01 - SELECT, WHERE, ORDER BY, LIMIT/OFFSET (Companion Guide)

## How to run this lesson

Open **sql-01** on the PostgreSQL side of `./classroom` and pick **Whole SQL lesson (psql)**, which feeds the entire file to `psql` against the disposable `advanced_sql_training` database. The script opens with `BEGIN`, points `search_path` at the `training` schema, and runs three read-only queries: the newest US and CA customers, products over 50 ranked by `price - cost`, and a pattern filter on `email` and `full_name` that prints 50 customers. Your six exercises sit below those queries as comments, and the file ends with `ROLLBACK`, so nothing you try here changes the course tables.

Edit your saved copy at
`.learning/sql/sql-01/lesson/workspace/sql/postgres-60day/day01_select_where_orderby.sql`.
It lives in the classroom's Docker volume, while the checked-in file stays answer-free. When one of your exercise queries has a typo, `ON_ERROR_STOP` halts the run at that statement and nothing after it prints, so repair the first error before reading anything below it.

The shared study guide covers [classroom steps, table loading and resets](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) and the [contributor notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Catalog prerequisites:** `sql-start-03`, the [query construction and debugging on-ramp](../../professional/companion-guides/sql_start_03_query_debugging.md).
- **Environment prerequisite:** follow the [SQL track setup](../README.md) so
  the Docker classroom and its disposable `advanced_sql_training` database
  are ready. You do not need to know DDL or migrations yet.
- **Artifacts:** [learner SQL](../day01_select_where_orderby.sql) ·
  [solution reasoning](../solutions/day01_solutions.md) ·
  [executable solution](../solutions/day01_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence of the
table's subject; in `training.customers`, one row represents one customer.
A **result set** is the temporary, table-shaped answer printed by a query. It
does not change stored rows. The **grain** says what one output row represents;
state it before writing a query.

For the opening query, imagine a pipeline:

1. `FROM training.customers` supplies candidate customer rows.
2. `WHERE country IN ('US', 'CA')` keeps only rows whose predicate is true.
   A predicate involving `NULL` can be unknown, so missing values need
   `IS NULL` or `IS NOT NULL`.
3. `SELECT` chooses the output columns. This is projection, not mutation.
4. `ORDER BY created_at DESC, customer_id DESC` creates a total order. The
   unique customer ID is the tie-breaker.
5. `LIMIT 10` keeps the first ten rows *after* sorting.

Before running, predict a result with the columns selected by the query, at
most ten rows, and one row per customer. After running, verify every country is
US or CA, timestamps never increase as you scan downward, and tied timestamps
have descending customer IDs. Without `ORDER BY`, PostgreSQL is free to return
rows in any convenient order; without a unique final sort key, tied rows may
swap places. `ROLLBACK` is the lesson's safety boundary even though today's
worked queries only read data.

## Two worked SQL examples

### Example 1

```sql
SELECT
  customer_id,
  full_name,
  country,
  created_at
FROM
  customers
WHERE
  country IN ('US', 'CA')
  -- `customer_id` makes ties on the timestamp deterministic before LIMIT.
ORDER BY
  created_at DESC,
  customer_id DESC
LIMIT 10;
```

**How to read it:** `WHERE country IN ('US', 'CA')` keeps 126 of the 500 customers (63 from each country) before any sorting happens. `ORDER BY created_at DESC` then lines those 126 rows up newest first, and `LIMIT 10` keeps the top ten. The `customer_id DESC` key never decides anything on this fixture, because no two customers share a `created_at` value, but it guarantees the same ten rows if a later load ever produces a tie.

**Expected result/shape:** Ten rows, one per customer, with every `country` equal to US or CA. On a fresh load the list starts with customer 258 (CA) and then customer 1 (US), and the dates fall as you read down. To confirm that the cap, not the filter, set the row count, run `SELECT count(*) FROM customers WHERE country IN ('US', 'CA')` and expect 126.

### Example 2

```sql
SELECT
  product_id,
  name,
  price,
  cost,
  (price -
    cost) AS gross_margin
FROM
  products
WHERE
  price > 50
ORDER BY
  gross_margin DESC,
  price DESC,
  product_id
LIMIT 15;
```

**How to read it:** `gross_margin` is computed for each row from `price - cost`, and because `ORDER BY` is evaluated after `SELECT`, it may sort by that alias. `WHERE price > 50` runs earlier, on the stored column, which is why the filter could not mention `gross_margin`. Of the 300 products, 192 pass the price filter. `price DESC` and then `product_id` settle any margin ties.

**Expected result/shape:** Fifteen product rows with five columns. Product 280 leads with a margin of 73.84 (price 113.60, cost 39.76), followed by 277 at 71.99 and 274 at 70.17; the remaining rows come from products in the 230 to 299 range. Recompute one row by hand: `price - cost` for product 280 must equal its printed `gross_margin`.

## Learning objectives

- Project named columns, filter rows, sort deterministically, and limit a result.
- Explain why `NULL` comparisons and an omitted `ORDER BY` can produce
  surprising results.

## Vocabulary and concepts

- **Projection:** the columns or expressions returned by `SELECT`.
- **Predicate:** a true/false/unknown condition used to filter rows.
- **Deterministic ordering:** an `ORDER BY` whose final tie-breaker uniquely
  orders the result.

## Worked example / walkthrough

Trace the first learner query in logical order: `FROM training.customers`
produces candidate rows, `WHERE country IN ('US', 'CA')` filters them,
`ORDER BY created_at DESC, customer_id DESC` fixes their order, and `LIMIT 10`
keeps the first ten. Remove the `customer_id` tie-breaker and explain why rows
with equal timestamps no longer have a guaranteed relative order.

## Practice assumptions and review method

- **Focus:** Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
- **Assumptions:** Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
- **Failure to watch for:** Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.

1. **Query writing:** List the 20 newest orders with customer ID and total amount.
   **Progressive hint:** Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.
   **Inputs/evidence:** For sql-01 Exercise 1, read the 4,362 `orders` rows, one per `order_id`; `order_date` is `NOT NULL` and holds 4,362 distinct timestamps, so `order_id` only breaks future ties. Project `order_id`, `customer_id`, `total_amount`, and `order_date`.
   **Expected result/shape:** For sql-01 Exercise 1, return exactly 20 rows, one per order, newest first; on a freshly loaded fixture the list starts with order 2258 and ends with order 743. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-01 Exercise 1, confirm 20 rows and 20 distinct `order_id` values, then compare them with `SELECT order_id FROM orders ORDER BY order_date DESC, order_id DESC LIMIT 20`. Inside a rolled-back transaction, copy order 2258's `order_date` onto order 1; the first rows must become 2258, 1, 745, showing the higher ID wins the tie.
2. **Query writing:** Find the 10 most expensive products created in the last 90 days.
   **Progressive hint:** Filter the timestamp directly, then sort by price and a stable product key.
   **Inputs/evidence:** For sql-01 Exercise 2, read `products` (300 rows, 300 distinct prices); 25 of them have `created_at` inside the last 90 days, priced from 112.12 to 121.00. Project `product_id`, `name`, `price`, and `created_at`.
   **Expected result/shape:** For sql-01 Exercise 2, return exactly 10 of those 25 recent products, highest price first: product 300 at 121.00 down to product 291 at 117.67. The final columns are `product_id`, `name`, `price`, and `created_at`. The final order is `p.price DESC, p.product_id`.
   **Verify:** For sql-01 Exercise 2, confirm `SELECT COUNT(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'` returns 25 and that every returned `created_at` passes that test. Inside a rolled-back transaction, set product 299's price to 121.00; the first two rows must then be 299 and 300, because `product_id` ascending breaks the price tie.
3. **Query writing:** Show customers from GB or DE created in the last year, newest first.
   **Progressive hint:** Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
   **Inputs/evidence:** For sql-01 Exercise 3, read `customers` (500 rows); 119 were created in the last year, of which 15 are `GB` and 14 are `DE`. Project `customer_id`, `full_name`, `country`, and `created_at`.
   **Expected result/shape:** For sql-01 Exercise 3, return 29 rows on a freshly loaded fixture, all `GB` or `DE` and all created within one year, newest first starting with customer 172. The final columns are `customer_id`, `full_name`, `country`, and `created_at`. The final order is `c.created_at DESC, c.customer_id`.
   **Verify:** For sql-01 Exercise 3, group the one-year window by `country` and confirm `GB` 15 plus `DE` 14 equals the 29 returned rows; grouping the output by `country` must show only those two values. The 29 rows carry 29 distinct `created_at` values, so `customer_id` only matters if a tie is added.
4. **Prediction:** Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
   **Progressive hint:** Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
   **Inputs/evidence:** For sql-01 Exercise 4, read all 500 `customers` rows; `email` is nullable but currently filled on every row. The query returns counts only, so no customer key appears.
   **Expected result/shape:** For sql-01 Exercise 4, return exactly one row: `missing_email_count` 0, `present_email_count` 500, `customer_count` 500. The final columns are `missing_email_count`, `present_email_count`, and `customer_count`.
   **Verify:** For sql-01 Exercise 4, confirm 0 + 500 equals `customer_count` and matches `SELECT COUNT(*) FROM customers`. Inside a rolled-back transaction, set customer 1's `email` to `NULL` and rerun; the counts must become 1, 499, and 500, proving `COUNT(email)` skips the `NULL` while `COUNT(*)` keeps the row.
5. **Debugging:** Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
   **Progressive hint:** Define the business ranking first; use a unique final key for tied prices.
   **Inputs/evidence:** For sql-01 Exercise 5, read all 300 `products` rows; every price is distinct, from product 1 up to product 300 at 121.00. Project `product_id`, `name`, and `price`.
   **Expected result/shape:** For sql-01 Exercise 5, return exactly 10 rows, products 300 down to 291 with prices 121.00 down to 117.67, identical on every rerun. The final columns are `product_id`, `name`, and `price`. The final order is `p.price DESC, p.product_id`.
   **Verify:** For sql-01 Exercise 5, confirm 10 distinct `product_id` values and that `SELECT COUNT(DISTINCT price) FROM products` returns 300, so the current fixture has no price tie. Inside a rolled-back transaction, set product 299's price to 121.00; the top three must read 299, 300, 298 on every run.
6. **Extension:** Return the second page of 10 newest orders using the same deterministic order, LIMIT 10 and OFFSET 10.
   **Progressive hint:** Sort by order_date DESC and order_id DESC; skip the first ten ordered rows and keep the next ten.
   **Inputs/evidence:** For sql-01 Exercise 6, read the 4,362 `orders` rows at one row per `order_id`, sorted by the Exercise 1 key, and compare pages only on an unchanged fixture.
   **Expected result/shape:** For sql-01 Exercise 6, return 10 rows equal to positions 11 through 20 of the ordered input, one row per `order_id`; on a freshly loaded fixture the page runs from order 1500 to order 743. The final columns are `order_id`, `customer_id`, `total_amount`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-01 Exercise 6, list the first 20 ordered IDs (2258 through 743) and confirm the page equals the last 10 of them, from 1500 to 743, with no ID shared with page one (2258 through 3014).

`OFFSET 10` skips the first ten rows after ordering; `LIMIT 10` bounds the
remaining result to ten rows. Keeping the same unique sort key is essential.
If rows change between requests, offset pages can shift. The later
`sql-scale-01` lesson explains cursor pagination for that separate setting.

## Common mistakes and how to recover

- **Writing `email = NULL`:** the comparison is unknown for every row, so the naive filter in Exercise 4 returns zero customers even though it reads sensibly. Use `email IS NULL`. All 500 fixture customers have an email, so the correct missing count is also 0; set one email to NULL inside the transaction to see the two forms disagree.
- **`LIMIT` without `ORDER BY`:** Exercise 5 starts from this bug. PostgreSQL returns whichever ten rows its plan produces first, which on a freshly loaded table is usually insertion order, so the output looks plausible until an update or a different plan reshuffles it.
- **Sorting the newest orders by `order_id`:** order IDs were assigned customer by customer, so the highest ID is not the latest order. Sort by `order_date` and use the ID only to break ties.
- **Changing the sort between pages:** Exercise 6 must reuse the exact `ORDER BY` of page one. A page sorted by `order_date DESC` alone could repeat or skip an order whenever two timestamps tie.
- **`LIKE` where you meant `ILIKE`:** names are stored as `Customer N`, so `full_name LIKE 'customer %1_'` matches nothing. The worked script uses `ILIKE` for exactly this reason.

For transcript errors and missing tables, see [recovering from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Can you predict which clause runs logically before `SELECT` and which runs
  after it?
- Does the learner file complete under `psql -X -v ON_ERROR_STOP=1` and finish
  with `ROLLBACK`?

## Next step

Continue to [Day 02 - aggregations and grouping](day02_aggregates_groupby_having.md).

## Deep dive and reference

Learning objectives
- Understand logical vs physical query execution order (FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT)
- Select specific columns; create derived columns with aliases
- Filter with comparison, IN, BETWEEN, LIKE/ILIKE; handle NULL semantics
- Sort by multiple keys, descending/ascending; apply LIMIT/OFFSET for pagination

Why this matters
These primitives underpin every SQL query you will write. Knowing evaluation order and NULL behavior prevents subtle bugs and makes queries predictable and performant.

Core concepts and deep dive
- Projection (SELECT): Choose only the columns you need; use column aliases for readability. Derived columns (expressions) compute values on the fly, e.g., (price - cost) AS gross_margin.
- Filtering (WHERE): Removes rows before projection and ordering. Remember three-valued logic: comparisons with NULL yield UNKNOWN and therefore fail the predicate.
- Pattern matching: LIKE is case-sensitive; ILIKE is case-insensitive (Postgres). Use % for any-length wildcard, _ for single-character. Escape literal %/_ via ESCAPE clause if necessary.
- Sorting (ORDER BY): Occurs after SELECT; you can sort by aliases. Ties are stable only by explicit secondary keys. NULLS FIRST/NULLS LAST gives control of null ordering.
- Pagination (`LIMIT`/`OFFSET`): `OFFSET` skips ordered rows and `LIMIT` bounds the remaining page. Compare pages on an unchanged fixture. The later `sql-scale-01` lesson investigates cursor semantics and measured access costs with its required prerequisites.

Walkthrough of the day’s script
- Customers by country with newest first: Filters by IN ('US','CA'), sorts by created_at DESC, limits to 10. Emphasizes how WHERE reduces the set before ORDER BY runs.
- Derived gross_margin for products: Computes price - cost as gross_margin, then orders by gross_margin DESC, price DESC. This shows sorting by computed aliases and multi-key ordering.
- Pattern filters: ILIKE/LIKE on email and full_name highlight pattern matching and case-insensitive search.

Postgres-specific notes
- ILIKE is a Postgres extension. For case-insensitive comparisons at scale, consider citext extension (case-insensitive text type) or full-text search for complex text queries.
- text pattern ops on leading wildcard ('%foo') cannot use btree indexes; consider trigram indexes (pg_trgm) or rewrite predicates.

Anti-patterns and pitfalls
- Selecting * in production queries; fetch only needed columns to reduce I/O.
- Assuming WHERE matches NULLs; use IS NULL/IS NOT NULL explicitly.
- Depending on implicit order without ORDER BY; SQL does not guarantee row order otherwise.

Check your understanding
- In what order are WHERE and ORDER BY evaluated, and why does that matter for derived columns?
- How does SQL treat comparisons with NULL? Provide an example that filters out NULL values.

Further reading
- Postgres pattern matching: https://www.postgresql.org/docs/17/functions-matching.html
- NULLs and three-valued logic: https://www.postgresql.org/docs/17/functions-comparison.html

## Ask an AI tutor about this lesson

The lesson is complete without a tutor. If you want one, paste the prompt below and ask it to quiz you on why the margin query can sort by `gross_margin` but cannot filter on it. The [tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) explain how it keeps `solutions/` closed until you ask.

```text
Tutor me through sql-01: SELECT, WHERE, ORDER BY, and LIMIT.

I am a beginner who completed the direct catalog prerequisite sql-start-03. Reuse its small-stage debugging workflow and explain new clauses before relying on them. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day01_select_where_orderby.md
- Answer-free learner SQL: sql/postgres-60day/day01_select_where_orderby.sql

Key terms to teach in context: Projection, Predicate, Deterministic ordering. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Trace the first learner query in logical order: `FROM training.customers` produces candidate rows, `WHERE country IN ('US', 'CA')` filters them, `ORDER BY created_at DESC, customer_id DESC` fixes their order, and `LIMIT 10` keeps the first ten. Remove the `customer_id` tie-breaker and explain why rows with equal timestamps no longer have a guaranteed relative order.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-01/ working copy. Never point setup, reset, DDL, or DML
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
