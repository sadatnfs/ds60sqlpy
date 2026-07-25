# Day 01 — SELECT, WHERE, ORDER BY, LIMIT/OFFSET (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** Complete the [SQL track setup](../README.md), reset the
  disposable `advanced_sql_training` database, and know how to run a `.sql`
  file with `psql`.
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

## Exercises

Complete the three prompts in the [learner SQL](../day01_select_where_orderby.sql).
Then change one filter to include `NULL` deliberately with `IS NULL` or
`IS NOT NULL`; do not use `= NULL`.

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

Exercises from the learner script
1) List the 20 newest orders with `customer_id` and `total_amount`.
2) Find the top 10 most expensive products created in the last 90 days.
3) Show customers from GB or DE created within the last year, newest first.

Use `order_date DESC, order_id DESC` and `created_at DESC, customer_id DESC`
when you want deterministic ordering among timestamp ties.

Check your understanding
- In what order are WHERE and ORDER BY evaluated, and why does that matter for derived columns?
- How does SQL treat comparisons with NULL? Provide an example that filters out NULL values.

Further reading
- Postgres pattern matching: https://www.postgresql.org/docs/current/functions-matching.html
- NULLs and three-valued logic: https://www.postgresql.org/docs/current/functions-comparison.html
