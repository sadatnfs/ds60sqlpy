# Day 01 — SELECT, WHERE, ORDER BY, LIMIT/OFFSET (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** Complete
  [SQL-FOUND-02 — versioned migrations](../../professional/companion-guides/sql_found_02_versioned_migrations.md)
  and the [SQL track setup](../README.md), reset the disposable
  `advanced_sql_training` database, and know how to run a `.sql` file with
  `psql`.
- **Artifacts:** [learner SQL](../day01_select_where_orderby.sql) ·
  [solution reasoning](../solutions/day01_solutions.md) ·
  [executable solution](../solutions/day01_solutions.sql)

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

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List the 20 newest orders with customer ID and total amount.
   **Progressive hint:** Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.
   **Expected shape:** At most 20 rows; one row per order, newest first.
2. **Query writing:** Find the 10 most expensive products created in the last 90 days.
   **Progressive hint:** Filter the timestamp directly, then sort by price and a stable product key.
   **Expected shape:** At most 10 product rows; every row is in the 90-day window.
3. **Query writing:** Show customers from GB or DE created in the last year, newest first.
   **Progressive hint:** Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
   **Expected shape:** Only GB/DE customers from the declared window.
4. **Prediction:** Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
   **Progressive hint:** Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
   **Expected shape:** Exactly one summary row with counts whose sum equals all customers.
5. **Debugging:** Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
   **Progressive hint:** Define the business ranking first; use a unique final key for tied prices.
   **Expected shape:** At most 10 rows, highest prices first, stable across repeated runs on unchanged data.
6. **Extension:** Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.
   **Progressive hint:** Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.
   **Expected shape:** Up to 10 rows strictly after the first page with no overlap.

## Self-check

- Can you predict which clause runs logically before `SELECT` and which runs
  after it?
- Does the learner file complete under `psql -X -v ON_ERROR_STOP=1` and finish
  with `ROLLBACK`?

## Next step

Continue to [Day 02 — aggregations and grouping](day02_aggregates_groupby_having.md).

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
- Pagination (LIMIT/OFFSET): LIMIT n returns at most n rows; OFFSET skips rows first. For large tables, prefer keyset pagination (WHERE value < last_value ORDER BY value DESC) over OFFSET for performance.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Check your understanding
- In what order are WHERE and ORDER BY evaluated, and why does that matter for derived columns?
- How does SQL treat comparisons with NULL? Provide an example that filters out NULL values.

Further reading
- Postgres pattern matching: https://www.postgresql.org/docs/current/functions-matching.html
- NULLs and three-valued logic: https://www.postgresql.org/docs/current/functions-comparison.html
